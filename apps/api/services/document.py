import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
from models.document import DocumentModel
from repositories.document import DocumentRepository
from schemas.document import IngestionStatus

class DocumentService:
    def __init__(self, db: AsyncSession):
        self.repo = DocumentRepository(db)

    async def list_documents(self, user_id: str, workspace_id: str | None = None) -> list[DocumentModel]:
        return await self.repo.list_by_user_and_workspace(user_id=user_id, workspace_id=workspace_id)

    async def get_document(self, id: str) -> DocumentModel | None:
        return await self.repo.get(id)

    async def upload_document(self, file: UploadFile, user_id: str, workspace_id: str | None = None) -> DocumentModel:
        # Read contents for checksum and metadata validation
        contents = await file.read()
        file_size = len(contents)
        
        import hashlib
        checksum = hashlib.sha256(contents).hexdigest()

        doc_id = f"doc-{uuid.uuid4()}"
        filename = file.filename or "unknown"
        content_type = file.content_type or "application/octet-stream"
        storage_key = f"documents/{doc_id}/{filename}"

        # Upload file using abstract storage provider
        from storage import get_storage_provider
        storage_provider = get_storage_provider()
        storage_result = await storage_provider.upload_file(
            key=storage_key,
            data=contents,
            content_type=content_type,
            metadata={"user_id": user_id, "doc_id": doc_id}
        )

        # Create model in queued status
        doc_model = DocumentModel(
            id=doc_id,
            name=filename,
            storage_url=storage_result.storage_url,
            status=IngestionStatus.QUEUED.value,
            metadata_json={
                "title": filename.split(".")[0] if filename else "document",
                "fileSize": file_size,
                "mimeType": content_type,
                "checksum": checksum,
                "storage_key": storage_key
            },
            user_id=user_id,
            workspace_id=workspace_id
        )

        created_doc = await self.repo.create(doc_model)
        await self.repo.db.flush()

        # Dispatch background ingestion task to Dramatiq queue broker passing storage_key
        from workers import ingest_document_worker
        ingest_document_worker.send(
            document_id=doc_id,
            storage_key=storage_key,
            filename=filename,
            mime_type=content_type,
            user_id=user_id,
            workspace_id=workspace_id,
        )

        # Fallback/In-Process Execution: Run in-process asynchronously to ensure the document
        # gets fully chunked, vector indexed, and analyzed even if the background Dramatiq
        # worker is not running (common in local dev and single-instance deployments like Render/Railway).
        from config import settings
        from workers.broker import is_stub_broker
        import os
        run_in_process = os.getenv("RUN_WORKERS_IN_PROCESS", "true").lower() == "true"
        if is_stub_broker() or settings.SENTRY_ENVIRONMENT == "development" or run_in_process:
            from workers.document_ingestion import _run_async_ingestion
            import asyncio
            asyncio.create_task(
                _run_async_ingestion(
                    document_id=doc_id,
                    storage_key=storage_key,
                    filename=filename,
                    mime_type=content_type,
                    user_id=user_id,
                    workspace_id=workspace_id,
                )
            )

        return created_doc

    async def delete_document(self, id: str) -> bool:
        doc = await self.repo.get(id)
        if not doc:
            return False

        # Attempt to delete file from storage provider
        storage_key = None
        if isinstance(doc.metadata_json, dict):
            storage_key = doc.metadata_json.get("storage_key")

        if not storage_key and doc.storage_url:
            # Fallback parsing in case storage_key is missing
            # e.g., s3://documind-vault/doc-id_filename or http://.../documents/doc-id/filename
            if "documents/" in doc.storage_url:
                storage_key = "documents/" + doc.storage_url.split("documents/")[-1]
            elif "documind-vault/" in doc.storage_url:
                storage_key = doc.storage_url.split("documind-vault/")[-1]

        if storage_key:
            try:
                from storage import get_storage_provider
                storage_provider = get_storage_provider()
                await storage_provider.safe_delete(storage_key)
            except Exception as exc:
                # Log but do not block DB deletion
                import logging
                logging.getLogger("documind.services.document").warning(
                    f"Failed to delete storage file for key {storage_key}: {exc}"
                )

        # Invalidate Redis Analysis cache for document (Section 7 Requirements)
        try:
            from services.cache import cache_service
            await cache_service.delete("analysis", "document", id)
        except Exception as exc:
            import logging
            logging.getLogger("documind.services.document").warning(
                f"Failed to invalidate analysis cache for doc={id}: {exc}"
            )

        return await self.repo.delete(id)
