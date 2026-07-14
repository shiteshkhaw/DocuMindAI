import os
import shutil
import hashlib
import logging
from pathlib import Path

from storage.base import BaseStorageProvider, StorageResult

logger = logging.getLogger("documind.storage.local")


class LocalStorageProvider(BaseStorageProvider):
    """
    Local filesystem storage fallback for local development.
    Stores all uploaded files inside a local directory and emulates S3 behavior.
    """

    def __init__(self, base_dir: str = "local_storage") -> None:
        self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"[LocalStorage] Root path set to: {self.base_dir}")

    def _get_path(self, key: str) -> Path:
        # Prevent directory traversal attacks
        safe_key = key.replace("..", "").lstrip("/")
        return self.base_dir / safe_key

    async def upload_file(
        self, key: str, data: bytes, content_type: str, metadata: dict | None = None
    ) -> StorageResult:
        logger.info(f"[LocalStorage] Uploading key={key} size={len(data)} bytes")
        file_path = self._get_path(key)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write synchronously since local dev disk operations are lightweight
        file_path.write_bytes(data)

        checksum = hashlib.sha256(data).hexdigest()
        # Dev local URL pointing to backend local file serving or static path representation
        storage_url = f"file:///{file_path.as_posix()}"

        return StorageResult(
            key=key,
            storage_url=storage_url,
            size=len(data),
            checksum=checksum,
            content_type=content_type,
        )

    async def download_file(self, key: str) -> bytes:
        logger.info(f"[LocalStorage] Downloading key={key}")
        file_path = self._get_path(key)
        if file_path.is_file():
            return file_path.read_bytes()
        raise FileNotFoundError(f"Local file not found for key: {key}")

    async def delete_file(self, key: str) -> bool:
        logger.info(f"[LocalStorage] Deleting key={key}")
        file_path = self._get_path(key)
        if file_path.is_file():
            file_path.unlink()
            return True
        return False

    async def generate_signed_url(self, key: str, expires_in: int = 3600) -> str:
        # Local fallback signed URL is simply the local file URL
        return await self.generate_public_url(key)

    async def generate_public_url(self, key: str) -> str:
        file_path = self._get_path(key)
        return f"file:///{file_path.as_posix()}"

    async def file_exists(self, key: str) -> bool:
        file_path = self._get_path(key)
        return file_path.is_file()

    async def replace_existing(
        self, key: str, data: bytes, content_type: str
    ) -> StorageResult:
        return await self.upload_file(key, data, content_type)

    async def safe_delete(self, key: str) -> bool:
        try:
            if await self.file_exists(key):
                return await self.delete_file(key)
            return True
        except Exception as exc:
            logger.warning(f"[LocalStorage] Safe delete skipped/failed for key={key}: {exc}")
            return False

    async def list_files(self, prefix: str | None = None) -> list[str]:
        logger.info(f"[LocalStorage] Listing files with prefix={prefix}")
        results = []
        if not self.base_dir.exists():
            return results

        # Walk directories recursively
        for root, dirs, files in os.walk(self.base_dir):
            for file in files:
                full_path = Path(root) / file
                # Get key relative to base_dir
                relative_key = full_path.relative_to(self.base_dir).as_posix()
                if not prefix or relative_key.startswith(prefix.lstrip("/")):
                    results.append(relative_key)
        return results
