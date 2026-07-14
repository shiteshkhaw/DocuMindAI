import asyncio
import logging
import dramatiq

from db.session import async_session_factory
from orchestration.service import IngestionOrchestrator
from services.dependencies import get_embedding_provider, get_vector_store
from workers.broker import broker

logger = logging.getLogger("documind.workers.document_ingestion")


async def _run_async_ingestion(
    document_id: str,
    storage_key: str,
    filename: str,
    mime_type: str | None,
    user_id: str | None = None,
    workspace_id: str | None = None,
) -> None:
    """Async engine execution helper for ingestion task runtime."""
    # Download file contents from storage provider
    from storage import get_storage_provider
    storage_provider = get_storage_provider()
    file_content = await storage_provider.download_file(storage_key)

    async with async_session_factory() as db:
        provider = get_embedding_provider()
        store = get_vector_store()
        
        # 1. Run Ingestion Pipeline (Queued -> Ingestion Statuses -> Ingested)
        orchestrator = IngestionOrchestrator(
            db=db,
            embedding_provider=provider,
            vector_store=store,
        )
        await orchestrator.ingest_document(
            document_id=document_id,
            file_content=file_content,
            filename=filename,
            mime_type=mime_type,
            user_id=user_id,
            workspace_id=workspace_id,
        )

        # ── Trigger Analysis Pre-computation (Section 6 Requirements) ──────
        logger.info(f"[Worker] Ingestion complete. Pre-computing analysis for doc={document_id}")
        from services.analysis import AnalysisService
        
        # Set status to ANALYZING
        from repositories.document import DocumentRepository
        doc_repo = DocumentRepository(db)
        doc_model = await doc_repo.get(document_id)
        if doc_model:
            doc_model.status = "ANALYZING"
            doc_model.progress_percentage = 90
            await db.commit()

        analysis_service = AnalysisService(db)
        analysis_result = await analysis_service.get_or_create_analysis(document_id)
        
        # Ingestion completes and status transitions to COMPLETED
        if doc_model:
            doc_model.status = "COMPLETED"
            doc_model.progress_percentage = 100
            await db.commit()
            
            # Retrieve owner email if available to send completion notification
            from models.auth import UserModel
            from sqlalchemy import select
            user_query = select(UserModel).where(UserModel.id == doc_model.user_id)
            user_res = await db.execute(user_query)
            user = user_res.scalar_one_or_none()
            
            if user and user.email:
                # Trigger async email notification send via email worker
                from workers.email import send_email_notification
                trust_score = float(analysis_result.trust_score_json.get("score", 100.0) if analysis_result.trust_score_json else 100.0)
                dashboard_url = f"http://localhost:3000/workspaces/{doc_model.workspace_id or 'default'}"
                
                # Send email
                send_email_notification.send(
                    email_type="analysis_completed",
                    recipient=user.email,
                    params={
                        "doc_name": doc_model.name,
                        "score": trust_score,
                        "dashboard_url": dashboard_url,
                    }
                )


@dramatiq.actor(max_retries=3, min_backoff=5000, max_backoff=60000)
def ingest_document_worker(
    document_id: str,
    storage_key: str,
    filename: str,
    mime_type: str | None,
    user_id: str | None = None,
    workspace_id: str | None = None,
) -> None:
    """Dramatiq task actor wrapping ingestion pipeline."""
    logger.info(f"[Dramatiq] Received ingestion request for document {document_id}")
    
    from workers.broker import run_async
    run_async(
        _run_async_ingestion(
            document_id=document_id,
            storage_key=storage_key,
            filename=filename,
            mime_type=mime_type,
            user_id=user_id,
            workspace_id=workspace_id,
        )
    )
