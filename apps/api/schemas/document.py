from datetime import datetime
from pydantic import BaseModel, ConfigDict
from enum import Enum

class IngestionStatus(str, Enum):
    QUEUED = "queued"
    UPLOADING = "UPLOADING"
    PARSING = "PARSING"
    CLEANING = "CLEANING"
    CHUNKING = "CHUNKING"
    EMBEDDING = "EMBEDDING"
    INDEXING = "INDEXING"
    ANALYZING = "ANALYZING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    # Legacy fallbacks
    PROCESSING = "processing"
    PROCESSED = "processed"
    failed = "failed"

class DocumentMetadataSchema(BaseModel):
    title: str
    author: str | None = None
    pageCount: int | None = None
    fileSize: int
    mimeType: str
    checksum: str

class DocumentBase(BaseModel):
    name: str

class DocumentResponse(DocumentBase):
    id: str
    storageUrl: str
    status: IngestionStatus
    metadata: DocumentMetadataSchema
    createdAt: datetime
    updatedAt: datetime
    userId: str
    progress_percentage: int = 0
    error: str | None = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class UploadParams(BaseModel):
    name: str
    fileSize: int
    mimeType: str
