from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from schemas.chat import ChatSessionResponse, CreateSessionRequest, CreateMessageRequest, MessageResponse
from services.chat import ChatService
from routers.auth import get_current_user
from models.auth import UserModel
from observability.rate_limiter import rate_limit

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.get("/sessions", response_model=list[ChatSessionResponse], dependencies=[Depends(rate_limit("standard"))])
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = ChatService(db)
    sessions = await service.list_sessions()
    return [
        ChatSessionResponse(
            id=s.id,
            title=s.title,
            documentIds=s.document_ids,
            messages=[
                MessageResponse(
                    id=m.id,
                    role=m.role,
                    content=m.content,
                    citations=m.citations_json,  # type: ignore
                    createdAt=m.created_at
                ) for m in s.messages
            ],
            createdAt=s.created_at,
            updatedAt=s.updated_at
        ) for s in sessions if s.user_id == current_user.id
    ]

@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(rate_limit("standard"))])
async def create_session(
    req: CreateSessionRequest, 
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = ChatService(db)
    # Get workspace from the first document (or assume personal default if not passed)
    # Ideally, req would include workspace_id. We'll add it if it's there.
    workspace_id = getattr(req, "workspace_id", None)
    s = await service.create_session(
        title=req.title, 
        document_ids=req.documentIds, 
        user_id=current_user.id,
        workspace_id=workspace_id
    )
    return ChatSessionResponse(
        id=s.id,
        title=s.title,
        documentIds=s.document_ids,
        messages=[
            MessageResponse(
                id=m.id,
                role=m.role,
                content=m.content,
                citations=m.citations_json,  # type: ignore
                createdAt=m.created_at
            ) for m in s.messages
        ],
        createdAt=s.created_at,
        updatedAt=s.updated_at
    )

@router.get("/sessions/{id}", response_model=ChatSessionResponse, dependencies=[Depends(rate_limit("standard"))])
async def get_session(
    id: str, 
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = ChatService(db)
    s = await service.get_session(id)
    if not s or s.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    return ChatSessionResponse(
        id=s.id,
        title=s.title,
        documentIds=s.document_ids,
        messages=[
            MessageResponse(
                id=m.id,
                role=m.role,
                content=m.content,
                citations=m.citations_json,  # type: ignore
                createdAt=m.created_at
            ) for m in s.messages
        ],
        createdAt=s.created_at,
        updatedAt=s.updated_at
    )

@router.post("/messages", response_model=MessageResponse, dependencies=[Depends(rate_limit("heavy"))])
async def send_message(
    req: CreateMessageRequest, 
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = ChatService(db)
    # Verify session ownership
    sess = await service.get_session(req.sessionId)
    if not sess or sess.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found")
        
    m = await service.send_message(req.sessionId, req.content, req.model)
    return MessageResponse(
        id=m.id,
        role=m.role,
        content=m.content,
        citations=m.citations_json,  # type: ignore
        createdAt=m.created_at
    )

@router.post("/messages/stream", dependencies=[Depends(rate_limit("heavy"))])
async def stream_message(
    req: CreateMessageRequest, 
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    service = ChatService(db)
    # Verify session ownership
    sess = await service.get_session(req.sessionId)
    if not sess or sess.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found")
        
    return StreamingResponse(
        service.stream_message(req.sessionId, req.content, req.model),
        media_type="text/event-stream",
        headers={
            # Disable proxy/nginx buffering so tokens arrive at the client in real-time
            "X-Accel-Buffering": "no",
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
        }
    )
