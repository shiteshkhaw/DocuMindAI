import pytest
from typing import AsyncGenerator, List
from sqlalchemy.ext.asyncio import AsyncSession
from models.document import DocumentModel
from models.chat import ChatSessionModel
from schemas.document import IngestionStatus
from orchestration.service import IngestionOrchestrator
from orchestration.rag import RAGOrchestrator
from retrieval.service import RetrievalService
from embeddings.providers import MockEmbeddingProvider
from vectorstore.chroma import ChromaVectorStore
from llm.base import BaseLLMProvider, LLMMessage, StreamingChunk
from llm.registry import llm_registry


class DummyLLMProvider(BaseLLMProvider):
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.2
    ) -> AsyncGenerator[StreamingChunk, None]:
        yield StreamingChunk(token="According ", prompt_tokens=50, completion_tokens=1)
        yield StreamingChunk(token="to the provided contract, ", prompt_tokens=50, completion_tokens=5)
        yield StreamingChunk(token="the service fee is indeed $50 monthly.", prompt_tokens=50, completion_tokens=12)


async def test_rag_orchestrator_execution(test_db: AsyncSession) -> None:
    # Register dummy LLM provider for OpenAI fallback
    dummy_provider = DummyLLMProvider()
    llm_registry.register_provider("openai", dummy_provider)

    # Setup dependencies
    embedding_provider = MockEmbeddingProvider()
    vector_store = ChromaVectorStore()

    ingest_orchestrator = IngestionOrchestrator(
        db=test_db,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    # 1. Seed document
    doc_id = "test-rag-doc-555"
    doc_model = DocumentModel(
        id=doc_id,
        name="test_contract.txt",
        storage_url="s3://vault/test_contract.txt",
        status=IngestionStatus.QUEUED.value,
        metadata_json={"mimeType": "text/plain", "fileSize": 250},
        user_id="usr-test",
    )
    test_db.add(doc_model)
    await test_db.commit()

    file_content = (
        b"DocuMind Agreement. Section 1. The service fee is $50 per month. "
        b"Section 2. All payments are non-refundable. Section 3. Term is 12 months."
    )
    await ingest_orchestrator.ingest_document(
        document_id=doc_id,
        file_content=file_content,
        filename="test_contract.txt",
        mime_type="text/plain",
    )

    # 2. Create Chat Session
    sess_id = "sess-rag-test"
    chat_session = ChatSessionModel(
        id=sess_id,
        title="Test RAG session",
        document_ids=[doc_id]
    )
    test_db.add(chat_session)
    await test_db.commit()

    # 3. Setup RAG orchestrator
    retrieval_service = RetrievalService(embedding_provider, vector_store)
    orchestrator = RAGOrchestrator(test_db, retrieval_service)

    # 4. Stream response and assert stream shapes
    stream = orchestrator.execute_stream(
        session_id=sess_id,
        query="What is the monthly service fee?",
        document_ids=[doc_id],
        model_name="documind-v3",
        chat_history=[]
    )

    chunks = []
    async for chunk in stream:
        chunks.append(chunk)

    # Assertions
    assert len(chunks) >= 3  # Citations + tokens + metrics
    
    # Verify Citations chunk (usually index 0)
    citations_chunk = chunks[0]
    assert citations_chunk["type"] == "citations"
    assert len(citations_chunk["citations"]) > 0
    assert citations_chunk["citations"][0]["documentId"] == doc_id
    assert citations_chunk["citations"][0]["documentName"] == "test_contract.txt"

    # Verify Token chunks
    token_chunks = [c for c in chunks if c["type"] == "token"]
    assert len(token_chunks) == 3
    assert token_chunks[0]["content"] == "According "
    assert token_chunks[2]["content"] == "the service fee is indeed $50 monthly."

    # Verify Metrics chunk (usually last)
    metrics_chunk = chunks[-1]
    assert metrics_chunk["type"] == "metrics"
    assert metrics_chunk["prompt_tokens"] == 50
    assert metrics_chunk["completion_tokens"] == 12
    assert metrics_chunk["duration_seconds"] > 0
    assert len(metrics_chunk["citations"]) > 0

    # Cleanup chroma collection
    await vector_store.delete_collection(ingest_orchestrator.collection_name)
