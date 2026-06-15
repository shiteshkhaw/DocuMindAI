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

        # Create model in queued status
        doc_id = f"doc-{uuid.uuid4()}"
        doc_model = DocumentModel(
            id=doc_id,
            name=file.filename or "unknown",
            storage_url=f"s3://documind-vault/{doc_id}_{file.filename}",
            status=IngestionStatus.QUEUED.value,
            metadata_json={
                "title": file.filename.split(".")[0] if file.filename else "document",
                "fileSize": file_size,
                "mimeType": file.content_type or "application/octet-stream",
                "checksum": checksum
            },
            user_id=user_id,
            workspace_id=workspace_id
        )

        created_doc = await self.repo.create(doc_model)
        await self.repo.db.flush()

        # Spawn asynchronous background task for ingestion pipeline
        import asyncio
        from orchestration.tasks import run_ingestion_task
        asyncio.create_task(
            run_ingestion_task(
                document_id=doc_id,
                file_content=contents,
                filename=file.filename or "unknown",
                mime_type=file.content_type
            )
        )

        return created_doc

    async def delete_document(self, id: str) -> bool:
        return await self.repo.delete(id)
