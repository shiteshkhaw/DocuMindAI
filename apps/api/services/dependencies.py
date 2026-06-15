import logging
from config import settings
from embeddings.base import BaseEmbeddingProvider
from embeddings.providers import (
    MockEmbeddingProvider,
    OpenAIEmbeddingProvider,
    GeminiEmbeddingProvider,
    HuggingFaceInferenceProvider
)
from vectorstore.base import BaseVectorStore
from vectorstore.chroma import ChromaVectorStore
from retrieval.service import RetrievalService

logger = logging.getLogger(__name__)

# Singletons — instantiated once and reused across requests
_embedding_provider: BaseEmbeddingProvider | None = None
_vector_store: BaseVectorStore | None = None


def get_embedding_provider() -> BaseEmbeddingProvider:
    global _embedding_provider
    if _embedding_provider is not None:
        return _embedding_provider

    provider = settings.EMBEDDING_PROVIDER.lower()
    if provider == "mock":
        _embedding_provider = MockEmbeddingProvider()
    elif provider == "openai":
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured but provider 'openai' was requested.")
        _embedding_provider = OpenAIEmbeddingProvider(api_key=settings.OPENAI_API_KEY)
    elif provider == "gemini":
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured but provider 'gemini' was requested.")
        _embedding_provider = GeminiEmbeddingProvider(api_key=settings.GEMINI_API_KEY)
    elif provider == "huggingface":
        _embedding_provider = HuggingFaceInferenceProvider(api_key=settings.HF_API_KEY)
    else:
        logger.warning(
            f"[Dependencies] Unknown embedding provider '{provider}'. Falling back to Mock. "
            f"Set EMBEDDING_PROVIDER to one of: mock, openai, gemini, huggingface"
        )
        _embedding_provider = MockEmbeddingProvider()

    logger.info(f"[Dependencies] Embedding provider: {type(_embedding_provider).__name__}")
    return _embedding_provider


def get_vector_store() -> BaseVectorStore:
    global _vector_store
    if _vector_store is not None:
        return _vector_store
    _vector_store = ChromaVectorStore()
    return _vector_store


def get_retrieval_service() -> RetrievalService:
    provider = get_embedding_provider()
    store = get_vector_store()
    return RetrievalService(embedding_provider=provider, vector_store=store)

