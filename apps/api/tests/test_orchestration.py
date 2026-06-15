import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from models.document import DocumentModel
from schemas.document import IngestionStatus
from orchestration.service import IngestionOrchestrator
from retrieval.service import RetrievalService
from embeddings.providers import MockEmbeddingProvider
from vectorstore.chroma import ChromaVectorStore


async def test_orchestrator_success_and_retrieval(test_db: AsyncSession) -> None:
    embedding_provider = MockEmbeddingProvider()
    vector_store = ChromaVectorStore()

    orchestrator = IngestionOrchestrator(
        db=test_db,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    doc_id = "test-orchestrator-doc-123"
    doc_model = DocumentModel(
        id=doc_id,
        name="pytest_guide.txt",
        storage_url="s3://vault/pytest_guide.txt",
        status=IngestionStatus.QUEUED.value,
        metadata_json={"mimeType": "text/plain", "fileSize": 100},
        user_id="usr-test",
    )
    test_db.add(doc_model)
    await test_db.commit()

    file_content = (
        b"DocuMind AI is a production-grade AI intelligence system."
        b" It handles parsing and storage.\n\n"
        b"It has robust async capabilities."
    )
    await orchestrator.ingest_document(
        document_id=doc_id,
        file_content=file_content,
        filename="pytest_guide.txt",
        mime_type="text/plain",
    )

    await test_db.refresh(doc_model)

    assert doc_model.status == IngestionStatus.COMPLETED.value
    assert doc_model.error is None
    assert doc_model.metadata_json["chunks_count"] == 1
    assert "ingestion_duration_ms" in doc_model.metadata_json

    # --- Retrieval ---
    retrieval_service = RetrievalService(embedding_provider, vector_store)
    retrieval_res = await retrieval_service.retrieve(
        query="What is DocuMind?",
        document_ids=[doc_id],
        limit=2,
        min_score=0.0,
    )

    assert retrieval_res.query == "What is DocuMind?"
    assert len(retrieval_res.results) == 1

    merged_context = retrieval_res.merged_context
    assert f"Source: Doc ID {doc_id}" in merged_context
    assert "DocuMind AI" in merged_context

    await vector_store.delete_collection(orchestrator.collection_name)


async def test_orchestrator_failure_state(test_db: AsyncSession) -> None:
    embedding_provider = MockEmbeddingProvider()
    vector_store = ChromaVectorStore()

    orchestrator = IngestionOrchestrator(
        db=test_db,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    doc_id = "test-failed-doc"
    doc_model = DocumentModel(
        id=doc_id,
        name="empty.txt",
        storage_url="s3://vault/empty.txt",
        status=IngestionStatus.QUEUED.value,
        metadata_json={"mimeType": "text/plain"},
        user_id="usr-test",
    )
    test_db.add(doc_model)
    await test_db.commit()

    with pytest.raises(ValueError):
        await orchestrator.ingest_document(
            document_id=doc_id,
            file_content=b"   ",  # whitespace-only → triggers readable-text guard
            filename="empty.txt",
            mime_type="text/plain",
        )

    await test_db.refresh(doc_model)

    assert doc_model.status == IngestionStatus.FAILED.value
    assert doc_model.error is not None
    assert "ValueError" in doc_model.error
