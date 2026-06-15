import pytest
import json
from typing import AsyncGenerator, List
from sqlalchemy.ext.asyncio import AsyncSession
from models.document import DocumentModel
from schemas.document import IngestionStatus
from orchestration.service import IngestionOrchestrator
from orchestration.contradiction import ContradictionOrchestrator
from embeddings.providers import MockEmbeddingProvider
from vectorstore.chroma import ChromaVectorStore
from llm.base import BaseLLMProvider, LLMMessage, StreamingChunk
from llm.registry import llm_registry

class ContradictionDummyLLMProvider(BaseLLMProvider):
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.2,
        *args,
        **kwargs
    ) -> AsyncGenerator[StreamingChunk, None]:
        # Return a contradiction JSON matching our expected output format
        response_json = {
            "contradictions": [
                {
                    "type": "timeline",
                    "severity": "high",
                    "confidence": 0.95,
                    "summary": "Project completion timeline conflict",
                    "explanation": "Page 1 states completion is October 15, 2026, while Page 3 states it is August 5, 2026.",
                    "conflictingStatements": [
                        {
                            "text": "The project completion date is set for October 15, 2026.",
                            "page": 1
                        },
                        {
                            "text": "align with the final project completion date of August 5, 2026.",
                            "page": 3
                        }
                    ]
                }
            ]
        }
        yield StreamingChunk(token=json.dumps(response_json))

@pytest.mark.asyncio
async def test_contradiction_pipeline(test_db: AsyncSession) -> None:
    # Register dummy LLM provider for OpenAI fallback
    dummy_provider = ContradictionDummyLLMProvider()
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
    doc_id = "test-contr-doc-999"
    doc_model = DocumentModel(
        id=doc_id,
        name="test_timeline.txt",
        storage_url="s3://vault/test_timeline.txt",
        status=IngestionStatus.QUEUED.value,
        metadata_json={"mimeType": "text/plain", "fileSize": 300},
        user_id="usr-test",
    )
    test_db.add(doc_model)
    await test_db.commit()

    file_content = (
        b"Project timeline planning. The project completion date is set for October 15, 2026. "
        b"We must deliver all artifacts by September 10, 2026 to align with the final project completion date of August 5, 2026."
    )
    await ingest_orchestrator.ingest_document(
        document_id=doc_id,
        file_content=file_content,
        filename="test_timeline.txt",
        mime_type="text/plain",
    )

    # 2. Run contradiction orchestrator
    orchestrator = ContradictionOrchestrator(test_db)
    stream = orchestrator.execute_stream(document_id=doc_id, model_name="documind-v3")

    events = []
    async for event in stream:
        events.append(event)

    # 3. Assertions
    # We expect status events, at least one insight, and a telemetry event
    assert len(events) >= 3
    
    # Check status events
    status_events = [e for e in events if e["type"] == "status"]
    assert len(status_events) > 0

    # Check insight events
    insight_events = [e for e in events if e["type"] == "insight"]
    assert len(insight_events) == 1
    
    insight = insight_events[0]["insight"]
    assert insight["type"] == "timeline"
    assert insight["severity"] == "critical"
    assert insight["confidence"] == 0.95
    assert len(insight["conflictingStatements"]) == 2
    assert insight["conflictingStatements"][0]["documentId"] == doc_id
    assert insight["conflictingStatements"][0]["page"] == 1
    assert len(insight["citations"]) == 2
    assert insight["citations"][0]["documentId"] == doc_id
    assert insight["citations"][0]["documentName"] == "test_timeline.txt"

    # Check telemetry event
    telemetry_events = [e for e in events if e["type"] == "telemetry"]
    assert len(telemetry_events) == 1
    metrics = telemetry_events[0]["metrics"]
    assert metrics["retrievalCount"] > 0
    assert metrics["contradictionCount"] == 1
    assert metrics["reasoningLatency"] >= 0
    assert metrics["orchestrationLatency"] >= 0
    assert metrics["providerLatency"] >= 0

    # Cleanup chroma collection
    await vector_store.delete_collection(ingest_orchestrator.collection_name)
