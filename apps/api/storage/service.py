import logging

from config import settings
from storage.base import BaseStorageProvider, StorageResult
from storage.supabase import SupabaseStorageProvider
from storage.local import LocalStorageProvider

logger = logging.getLogger("documind.storage.service")


class StorageService:
    """
    StorageService abstraction wrapping the active storage provider.
    Ensures storage providers can be easily swapped in the future while
    maintaining a unified interface.
    """

    def __init__(self, provider: BaseStorageProvider) -> None:
        self.provider = provider

    async def upload_file(
        self, key: str, data: bytes, content_type: str, metadata: dict | None = None
    ) -> StorageResult:
        return await self.provider.upload_file(key, data, content_type, metadata)

    async def download_file(self, key: str) -> bytes:
        return await self.provider.download_file(key)

    async def delete_file(self, key: str) -> bool:
        return await self.provider.delete_file(key)

    async def generate_signed_url(self, key: str, expires_in: int = 3600) -> str:
        return await self.provider.generate_signed_url(key, expires_in)

    async def generate_public_url(self, key: str) -> str:
        return await self.provider.generate_public_url(key)

    async def file_exists(self, key: str) -> bool:
        return await self.provider.file_exists(key)

    async def replace_existing(
        self, key: str, data: bytes, content_type: str
    ) -> StorageResult:
        return await self.provider.replace_existing(key, data, content_type)

    async def safe_delete(self, key: str) -> bool:
        return await self.provider.safe_delete(key)

    async def list_files(self, prefix: str | None = None) -> list[str]:
        return await self.provider.list_files(prefix)


_storage_service: StorageService | None = None


def get_storage_provider() -> StorageService:
    """
    Dependency injection provider function for file storage layer.
    If Supabase credentials are configured, returns the Supabase Storage Service.
    Otherwise, falls back to local development storage gracefully.
    """
    global _storage_service
    if _storage_service is not None:
        return _storage_service

    # Check if necessary credentials for Supabase exist
    has_credentials = (
        settings.SUPABASE_URL
        and settings.SUPABASE_SERVICE_ROLE_KEY
        and settings.SUPABASE_STORAGE_BUCKET
    )

    if has_credentials:
        logger.info(
            f"[Storage] Initialising Supabase Storage Provider. "
            f"URL: {settings.SUPABASE_URL} | Bucket: {settings.SUPABASE_STORAGE_BUCKET}"
        )
        provider = SupabaseStorageProvider()
    else:
        logger.info(
            "[Storage] Missing Supabase credentials in environment configurations. "
            "Falling back to Local Storage Provider."
        )
        provider = LocalStorageProvider()

    _storage_service = StorageService(provider)
    return _storage_service
