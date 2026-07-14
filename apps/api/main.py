import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import settings
from routers import document, chat, search, contradiction, health, auth, workspace, testing, organization
from db.session import engine
from db.base import Base

logger = logging.getLogger("documind.startup")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Sentry initialization ────────────────────────────────────────────
    from core import init_sentry
    init_sentry()

    # ── DB: auto-create tables and migrate columns ───────────────────────
    async with engine.begin() as conn:
        from models.auth import UserModel, SessionModel
        from models.workspace import WorkspaceModel
        from models.document import DocumentModel
        from models.analysis import DocumentAnalysisModel
        from models.chat import ChatSessionModel, MessageModel
        from models.organization import OrganizationModel, OrganizationMemberModel
        from models.audit import AuditLogModel
        await conn.run_sync(Base.metadata.create_all)
        
        # Safe column backfilling migration
        from sqlalchemy import inspect, text
        def run_migrations(connection):
            inspector = inspect(connection)
            tables = inspector.get_table_names()
            if "document_analyses" in tables:
                columns = [col["name"] for col in inspector.get_columns("document_analyses")]
                new_columns = {
                    "entity_conflicts_json": "JSON",
                    "facts_json": "JSON",
                    "semantic_conflicts_json": "JSON",
                    "ambiguities_json": "JSON",
                    "references_json": "JSON",
                    "requirements_json": "JSON",
                    "trust_score_json": "JSON",
                    "executive_summary_json": "JSON",
                    "review_json": "JSON",
                }
                for col_name, col_type in new_columns.items():
                    if col_name not in columns:
                        logger.info(f"[Migration] Adding missing column {col_name} to document_analyses")
                        connection.execute(text(f"ALTER TABLE document_analyses ADD COLUMN {col_name} {col_type}"))
            
            if "documents" in tables:
                columns = [col["name"] for col in inspector.get_columns("documents")]
                new_cols = {
                    "workspace_id": "VARCHAR REFERENCES workspaces(id) ON DELETE CASCADE",
                    "progress_percentage": "INTEGER DEFAULT 0",
                    "started_at": "TIMESTAMP",
                    "completed_at": "TIMESTAMP",
                    "failure_reason": "VARCHAR",
                }
                for col_name, col_def in new_cols.items():
                    if col_name not in columns:
                        logger.info(f"[Migration] Adding missing column {col_name} to documents")
                        connection.execute(text(f"ALTER TABLE documents ADD COLUMN {col_name} {col_def}"))

            if "chat_sessions" in tables:
                columns = [col["name"] for col in inspector.get_columns("chat_sessions")]
                new_cols = {
                    "user_id": "VARCHAR REFERENCES users(id) ON DELETE CASCADE",
                    "workspace_id": "VARCHAR REFERENCES workspaces(id) ON DELETE CASCADE",
                }
                for col_name, col_def in new_cols.items():
                    if col_name not in columns:
                        logger.info(f"[Migration] Adding missing column {col_name} to chat_sessions")
                        connection.execute(text(f"ALTER TABLE chat_sessions ADD COLUMN {col_name} {col_def}"))

            if "workspaces" in tables:
                columns = [col["name"] for col in inspector.get_columns("workspaces")]
                if "organization_id" not in columns:
                    logger.info("[Migration] Adding organization_id to workspaces")
                    connection.execute(text("ALTER TABLE workspaces ADD COLUMN organization_id VARCHAR(255) REFERENCES organizations(id) ON DELETE SET NULL"))
        await conn.run_sync(run_migrations)
    logger.info("[Startup] Database tables verified / created / migrated.")

    # ── Redis: connect and validate ──────────────────────────────────────
    from core.redis import redis_manager
    await redis_manager.connect()
    redis_health = await redis_manager.health_check()
    if redis_health.get("status") == "connected":
        logger.info(f"[Startup] Redis OK | version={redis_health.get('version')}")
    elif redis_health.get("status") == "not_configured":
        logger.info("[Startup] Redis not configured — running without Redis.")
    else:
        logger.warning(f"[Startup] Redis DEGRADED | {redis_health.get('error', 'unknown')}")

    # ── Chroma: startup health check ─────────────────────────────────────
    try:
        from services.dependencies import get_vector_store
        store = get_vector_store()
        info = await store.heartbeat()  # type: ignore[attr-defined]
        if info.get("status") == "connected":
            logger.info(
                f"[Startup] ChromaDB OK | backend={info.get('backend')} | "
                f"tenant={info.get('tenant')} | database={info.get('database')} | "
                f"collections={info.get('collection_count')}"
            )
        else:
            logger.error(
                f"[Startup] ChromaDB DEGRADED | backend={info.get('backend')} | "
                f"tenant={info.get('tenant')} | database={info.get('database')} | "
                f"error={info.get('error')}"
            )
    except Exception as e:
        logger.error(
            f"[Startup] ChromaDB health check failed on startup: {e}"
        )

    # ── Storage: validate and create bucket ──────────────────────────────
    try:
        from storage import get_storage_provider
        storage_service = get_storage_provider()
        provider = storage_service.provider
        if hasattr(provider, "initialize"):
            await provider.initialize()
    except Exception as e:
        logger.error(f"[Startup] Storage initialization/validation failed: {e}")

    yield

    # ── Shutdown: Redis disconnect ────────────────────────────────────────
    from core.redis import redis_manager as _redis_mgr
    await _redis_mgr.disconnect()
    logger.info("[Shutdown] DocuMind AI shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Enterprise-grade Document Intelligence SaaS API",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(document.router, prefix=settings.API_V1_STR)
app.include_router(chat.router, prefix=settings.API_V1_STR)
app.include_router(search.router, prefix=settings.API_V1_STR)
app.include_router(contradiction.router, prefix=settings.API_V1_STR)
app.include_router(workspace.router, prefix=settings.API_V1_STR)
app.include_router(testing.router, prefix=settings.API_V1_STR)
app.include_router(organization.router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_url": "/health",
    }
