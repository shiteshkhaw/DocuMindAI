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
    maintaining a unified interface with graceful fallback degradation.
    """

    def __init__(
        self,
        provider: BaseStorageProvider,
        fallback_provider: BaseStorageProvider | None = None,
    ) -> None:
        self.provider = provider
        self.fallback_provider = fallback_provider

    async def upload_file(
        self, key: str, data: bytes, content_type: str, metadata: dict | None = None
    ) -> StorageResult:
        try:
            return await self.provider.upload_file(key, data, content_type, metadata)
        except Exception as e:
            if self.fallback_provider and self.provider != self.fallback_provider:
                logger.warning(
                    f"[Storage] Primary storage provider upload failed ({e}). "
                    "Falling back to local storage provider."
                )
                return await self.fallback_provider.upload_file(key, data, content_type, metadata)
            raise

    async def download_file(self, key: str) -> bytes:
        try:
            return await self.provider.download_file(key)
        except Exception as e:
            if self.fallback_provider and self.provider != self.fallback_provider:
                try:
                    return await self.fallback_provider.download_file(key)
                except Exception:
                    pass
            raise

    async def delete_file(self, key: str) -> bool:
        try:
            return await self.provider.delete_file(key)
        except Exception as e:
            if self.fallback_provider and self.provider != self.fallback_provider:
                try:
                    return await self.fallback_provider.delete_file(key)
                except Exception:
                    pass
            raise

    async def generate_signed_url(self, key: str, expires_in: int = 3600) -> str:
        try:
            return await self.provider.generate_signed_url(key, expires_in)
        except Exception:
            if self.fallback_provider and self.provider != self.fallback_provider:
                return await self.fallback_provider.generate_signed_url(key, expires_in)
            raise

    async def generate_public_url(self, key: str) -> str:
        try:
            return await self.provider.generate_public_url(key)
        except Exception:
            if self.fallback_provider and self.provider != self.fallback_provider:
                return await self.fallback_provider.generate_public_url(key)
            raise

    async def file_exists(self, key: str) -> bool:
        try:
            return await self.provider.file_exists(key)
        except Exception:
            if self.fallback_provider and self.provider != self.fallback_provider:
                return await self.fallback_provider.file_exists(key)
            raise

    async def replace_existing(
        self, key: str, data: bytes, content_type: str
    ) -> StorageResult:
        try:
            return await self.provider.replace_existing(key, data, content_type)
        except Exception as e:
            if self.fallback_provider and self.provider != self.fallback_provider:
                logger.warning(f"[Storage] Primary replace failed ({e}). Falling back to local.")
                return await self.fallback_provider.replace_existing(key, data, content_type)
            raise

    async def safe_delete(self, key: str) -> bool:
        try:
            return await self.provider.safe_delete(key)
        except Exception:
            if self.fallback_provider and self.provider != self.fallback_provider:
                return await self.fallback_provider.safe_delete(key)
            raise

    async def list_files(self, prefix: str | None = None) -> list[str]:
        try:
            return await self.provider.list_files(prefix)
        except Exception:
            if self.fallback_provider and self.provider != self.fallback_provider:
                return await self.fallback_provider.list_files(prefix)
            raise


_storage_service: StorageService | None = None


def get_storage_provider() -> StorageService:
    """
    Dependency injection provider function for file storage layer.
    If Supabase credentials are configured, returns the Supabase Storage Service
    with LocalStorageProvider as a fallback.
    Otherwise, uses local development storage directly.
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
        fallback = LocalStorageProvider()
    else:
        logger.info(
            "[Storage] Missing Supabase credentials in environment configurations. "
            "Using Local Storage Provider."
        )
        provider = LocalStorageProvider()
        fallback = None

    _storage_service = StorageService(provider=provider, fallback_provider=fallback)
    return _storage_service
