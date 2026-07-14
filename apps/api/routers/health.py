import logging
from fastapi import APIRouter
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """
    System health check endpoint.
    Returns connectivity status for all core infrastructure components.
    """
    from services.dependencies import get_vector_store, get_embedding_provider
    from db.session import engine
    import sqlalchemy

    result: dict = {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
    }

    # ── Postgres ──────────────────────────────────────────────────────────
    try:
        async with engine.connect() as conn:
            await conn.execute(sqlalchemy.text("SELECT 1"))
        result["postgres"] = "connected"
    except Exception as e:
        result["postgres"] = f"disconnected: {str(e)}"
        result["status"] = "degraded"
        logger.warning(f"[Health] Postgres check failed: {e}")

    # ── Redis ─────────────────────────────────────────────────────────────
    try:
        from core.redis import redis_manager
        redis_health = await redis_manager.health_check()
        result["redis"] = redis_health.get("status", "unknown")
        if redis_health.get("version"):
            result["redis_version"] = redis_health["version"]
        if redis_health.get("status") == "disconnected":
            result["status"] = "degraded"
    except Exception as e:
        result["redis"] = f"error: {str(e)}"
        result["status"] = "degraded"
        logger.warning(f"[Health] Redis check failed: {e}")

    # ── Chroma ────────────────────────────────────────────────────────────
    try:
        store = get_vector_store()
        chroma_info = await store.heartbeat()  # type: ignore[attr-defined]
        result["chroma"] = chroma_info.get("status", "unknown")
        result["chroma_backend"] = chroma_info.get("backend", "unknown")
        result["chroma_collection_count"] = chroma_info.get("collection_count", -1)
        if chroma_info.get("status") != "connected":
            result["status"] = "degraded"
    except Exception as e:
        result["chroma"] = f"disconnected: {str(e)}"
        result["chroma_backend"] = "unknown"
        result["chroma_collection_count"] = -1
        result["status"] = "degraded"
        logger.warning(f"[Health] Chroma check failed: {e}")

    # ── Embedding Provider status ──────────────────────────────────────────
    embedding_prov = settings.EMBEDDING_PROVIDER.lower()
    emb_key_exists = False
    if embedding_prov == "openai" and settings.OPENAI_API_KEY:
        emb_key_exists = True
    elif embedding_prov == "gemini" and settings.GEMINI_API_KEY:
        emb_key_exists = True
    elif embedding_prov == "huggingface" and settings.HF_API_KEY:
        emb_key_exists = True
    elif embedding_prov == "mock":
        emb_key_exists = True

    if emb_key_exists:
        result["embedding_provider"] = f"{settings.EMBEDDING_PROVIDER} (connected)"
    else:
        result["embedding_provider"] = f"{settings.EMBEDDING_PROVIDER} (degraded: key missing)"
        result["status"] = "degraded"

    # ── LLM Providers status ──────────────────────────────────────────────
    llms = []
    if settings.OPENAI_API_KEY:
        llms.append("openai (active)")
    else:
        llms.append("openai (missing key)")

    if settings.GROQ_API_KEY:
        llms.append("groq (active)")
    else:
        llms.append("groq (missing key)")

    if settings.GEMINI_API_KEY:
        llms.append("gemini (active)")
    else:
        llms.append("gemini (missing key)")

    result["llm_providers"] = llms

    return result
