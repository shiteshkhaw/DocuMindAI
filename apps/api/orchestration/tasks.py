import logging
from db.session import async_session_factory
from orchestration.service import IngestionOrchestrator
from services.dependencies import get_embedding_provider, get_vector_store

logger = logging.getLogger(__name__)

async def run_ingestion_task(
    document_id: str,
    file_content: bytes,
    filename: str,
    mime_type: str | None = None
) -> None:
    """
    Background worker function executing the document ingestion orchestration.
    Maintains a dedicated AsyncSession connection instance for the task runtime.
    """
    logger.info(f"Background ingestion worker triggered for document {document_id}")
    
    async with async_session_factory() as db:
        try:
            provider = get_embedding_provider()
            store = get_vector_store()
            
            orchestrator = IngestionOrchestrator(
                db=db,
                embedding_provider=provider,
                vector_store=store
            )
            
            await orchestrator.ingest_document(
                document_id=document_id,
                file_content=file_content,
                filename=filename,
                mime_type=mime_type
            )
        except Exception as e:
            logger.error(f"Background task failed for document {document_id}: {type(e).__name__} - {str(e)}")
