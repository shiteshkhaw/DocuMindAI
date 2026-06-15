import logging
from typing import AsyncGenerator, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

# Re-expose custom exception hierarchy for test compatibility
class ContradictionError(Exception):
    """Base exception for contradiction orchestration errors."""

class DocumentNotFoundError(ContradictionError):
    """Raised when the target document metadata is not found."""

class EmptyCollectionError(ContradictionError):
    """Raised when Chroma DB retrieval returns empty results."""

class LLMProviderError(ContradictionError):
    """Raised when the LLM provider fails after all retries."""


class ContradictionOrchestrator:
    """
    Orchestration layer delegating to the domain service ContradictionEngine.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute_stream(
        self,
        document_id: str,
        model_name: str = "documind-v3",
    ) -> AsyncGenerator[Dict[str, Any], None]:
        from services.contradiction_v2 import ContradictionEngine
        from services.dependencies import get_vector_store, get_embedding_provider

        vector_store = get_vector_store()
        embedding_provider = get_embedding_provider()

        engine = ContradictionEngine(self.db, vector_store, embedding_provider)
        async for event in engine.detect_contradictions(document_id, model_name):
            yield event
