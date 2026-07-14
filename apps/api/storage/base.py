from abc import ABC, abstractmethod
from pydantic import BaseModel


class StorageResult(BaseModel):
    key: str
    storage_url: str
    size: int
    checksum: str
    content_type: str


class BaseStorageProvider(ABC):
    """
    Abstract interface defining storage service operations.
    Hides all S3/local-disk logic from the business layers.
    """

    @abstractmethod
    async def upload_file(
        self, key: str, data: bytes, content_type: str, metadata: dict | None = None
    ) -> StorageResult:
        """Upload file content to storage."""
        pass

    @abstractmethod
    async def download_file(self, key: str) -> bytes:
        """Download file content from storage."""
        pass

    @abstractmethod
    async def delete_file(self, key: str) -> bool:
        """Delete file from storage. Returns True if successfully deleted."""
        pass

    @abstractmethod
    async def generate_signed_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a temporary signed URL to download the file."""
        pass

    @abstractmethod
    async def generate_public_url(self, key: str) -> str:
        """Generate a permanent public URL if bucket/key is public."""
        pass

    @abstractmethod
    async def file_exists(self, key: str) -> bool:
        """Check if file exists in storage."""
        pass

    @abstractmethod
    async def replace_existing(
        self, key: str, data: bytes, content_type: str
    ) -> StorageResult:
        """Replace file if it exists, otherwise upload."""
        pass

    @abstractmethod
    async def safe_delete(self, key: str) -> bool:
        """Checks if file exists before deleting it to avoid raising errors."""
        pass

    @abstractmethod
    async def list_files(self, prefix: str | None = None) -> list[str]:
        """List files in storage, optionally filtered by prefix. Returns a list of keys."""
        pass
