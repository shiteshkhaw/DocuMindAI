import uuid
import json
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from models.chat import ChatSessionModel, MessageModel
from repositories.chat import ChatSessionRepository, MessageRepository
from services.dependencies import get_retrieval_service
from orchestration.rag import RAGOrchestrator
from llm.base import LLMMessage

logger = logging.getLogger("documind.services.chat")

class ChatService:
    def __init__(self, db: AsyncSession):
        self.session_repo = ChatSessionRepository(db)
        self.message_repo = MessageRepository(db)

    async def list_sessions(self) -> list[ChatSessionModel]:
        return await self.session_repo.list()

    async def get_session(self, id: str) -> ChatSessionModel | None:
        return await self.session_repo.get(id)

    async def create_session(self, title: str | None, document_ids: list[str], user_id: str | None = None, workspace_id: str | None = None) -> ChatSessionModel:
        sess_id = f"sess-{uuid.uuid4()}"
        session = ChatSessionModel(
            id=sess_id,
            title=title or f"Conversation {sess_id[:8]}",
            document_ids=document_ids,
            user_id=user_id,
            workspace_id=workspace_id
        )
        created_session = await self.session_repo.create(session)

        # Generate a default greeting message
        greeting = MessageModel(
            id=f"msg-{uuid.uuid4()}",
            session_id=sess_id,
            role="assistant",
            content="Hello! I am ready to analyze your selected documents. What would you like to know?"
        )
        await self.message_repo.create(greeting)

        # Commit then refresh to populate the messages relationship with selectin loading
        await self.session_repo.db.flush()
        await self.session_repo.db.refresh(created_session, attribute_names=["messages"])
        return created_session

    async def send_message(self, session_id: str, content: str, model_name: str | None = None) -> MessageModel:
        # Create user message
        user_msg = MessageModel(
            id=f"msg-{uuid.uuid4()}",
            session_id=session_id,
            role="user",
            content=content
        )
        await self.message_repo.create(user_msg)
        await self.message_repo.db.flush()

        # Retrieve session to find linked documents
        session = await self.session_repo.get(session_id)
        document_ids = session.document_ids if session else []
        model = model_name or "documind-v3"

        # Fetch messages history
        db_messages = await self.message_repo.get_session_messages(session_id)
        # Exclude the user message we just added when constructing history
        history_msgs = [
            LLMMessage(role=m.role, content=m.content)
            for m in db_messages
            if m.role in ("user", "assistant", "system") and m.id != user_msg.id
        ]

        retrieval_service = get_retrieval_service()
        orchestrator = RAGOrchestrator(self.session_repo.db, retrieval_service)

        # Generate response using orchestrator
        full_content = ""
        citations = []
        async for chunk in orchestrator.execute_stream(
            session_id=session_id,
            query=content,
            document_ids=document_ids,
            model_name=model,
            chat_history=history_msgs
        ):
            if chunk["type"] == "token":
                full_content += chunk["content"]
            elif chunk["type"] == "citations":
                citations = chunk["citations"]
            elif chunk["type"] == "metrics":
                citations = chunk.get("citations", citations)
                if "full_content" in chunk:
                    full_content = chunk["full_content"]

        assistant_msg = MessageModel(
            id=f"msg-{uuid.uuid4()}",
            session_id=session_id,
            role="assistant",
            content=full_content,
            citations_json=citations if citations else None
        )
        await self.message_repo.create(assistant_msg)
        await self.session_repo.db.flush()

        return assistant_msg

    async def stream_message(self, session_id: str, content: str, model_name: str | None = None) -> AsyncGenerator[str, None]:
        # Validate session exists BEFORE any DB writes to avoid FK constraint violations
        session = await self.session_repo.get(session_id)
        if not session:
            logger.error(f"stream_message: session '{session_id}' not found in DB.")
            yield f"data: {json.dumps({'type': 'error', 'content': f'Session {session_id!r} not found. Please start a new chat session.'})}\n\n"
            yield "data: [DONE]\n\n"
            return

        document_ids = session.document_ids
        model = model_name or "documind-v3"

        # Save user message (session verified, FK is safe)
        user_msg = MessageModel(
            id=f"msg-{uuid.uuid4()}",
            session_id=session_id,
            role="user",
            content=content
        )
        await self.message_repo.create(user_msg)
        await self.message_repo.db.flush()

        # Fetch messages history
        db_messages = await self.message_repo.get_session_messages(session_id)
        history_msgs = [
            LLMMessage(role=m.role, content=m.content)
            for m in db_messages
            if m.role in ("user", "assistant", "system") and m.id != user_msg.id
        ]

        retrieval_service = get_retrieval_service()
        orchestrator = RAGOrchestrator(self.session_repo.db, retrieval_service)

        full_content = ""
        citations = []

        try:
            async for chunk in orchestrator.execute_stream(
                session_id=session_id,
                query=content,
                document_ids=document_ids,
                model_name=model,
                chat_history=history_msgs
            ):
                if chunk["type"] == "token":
                    token = chunk["content"]
                    full_content += token
                    # Include type=token so the SDK can distinguish from other events
                    yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
                elif chunk["type"] == "citations":
                    citations = chunk["citations"]
                    yield f"data: {json.dumps({'type': 'citations', 'citations': citations})}\n\n"
                elif chunk["type"] == "error":
                    # Propagate LLM/retrieval errors to the client
                    error_content = chunk.get("content", "Unknown error during generation.")
                    logger.error(f"Stream error event received: {error_content}")
                    yield f"data: {json.dumps({'type': 'error', 'content': error_content})}\n\n"
                    yield "data: [DONE]\n\n"
                    return
                elif chunk["type"] == "metrics":
                    citations = chunk.get("citations", citations)
                    if "full_content" in chunk:
                        full_content = chunk["full_content"]

        except Exception as e:
            error_msg = f"Streaming generation failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"
            yield "data: [DONE]\n\n"
            return

        # Save assistant message after stream completes
        assistant_msg = MessageModel(
            id=f"msg-{uuid.uuid4()}",
            session_id=session_id,
            role="assistant",
            content=full_content,
            citations_json=citations if citations else None
        )
        await self.message_repo.create(assistant_msg)
        await self.session_repo.db.flush()

        yield "data: [DONE]\n\n"

