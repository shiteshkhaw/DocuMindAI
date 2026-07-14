import logging
import hashlib
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings
from storage.base import BaseStorageProvider, StorageResult

logger = logging.getLogger("documind.storage.supabase")


class SupabaseStorageProvider(BaseStorageProvider):
    """
    Supabase Storage Provider utilizing HTTP REST API for operations.
    Leverages httpx for async non-blocking requests and tenacity for retries.
    """

    def __init__(self) -> None:
        self.supabase_url: str = settings.SUPABASE_URL or ""
        self.anon_key: str = settings.SUPABASE_ANON_KEY or ""
        self.service_role_key: str = settings.SUPABASE_SERVICE_ROLE_KEY or ""
        self.bucket_name: str = settings.SUPABASE_STORAGE_BUCKET

        if not self.supabase_url or not self.service_role_key:
            logger.warning(
                "[SupabaseStorage] SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY is not configured."
            )

    async def initialize(self) -> None:
        """
        Validates whether the bucket exists on startup.
        If it doesn't exist, attempts to create it administratively.
        """
        if not self.supabase_url or not self.service_role_key:
            logger.error("[SupabaseStorage] Cannot initialize: credentials missing.")
            return

        url = f"{self.supabase_url.rstrip('/')}/storage/v1/bucket/{self.bucket_name}"
        headers = {"Authorization": f"Bearer {self.service_role_key}"}

        logger.info(f"[SupabaseStorage] Verifying bucket '{self.bucket_name}'...")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    logger.info(f"[SupabaseStorage] Bucket '{self.bucket_name}' verified and exists.")
                    return

                if response.status_code == 404:
                    logger.info(f"[SupabaseStorage] Bucket '{self.bucket_name}' not found. Creating bucket...")
                    create_url = f"{self.supabase_url.rstrip('/')}/storage/v1/bucket"
                    payload = {
                        "id": self.bucket_name,
                        "name": self.bucket_name,
                        "public": False  # Private by default
                    }
                    create_response = await client.post(create_url, json=payload, headers=headers)
                    if create_response.status_code == 200:
                        logger.info(f"[SupabaseStorage] Bucket '{self.bucket_name}' created successfully.")
                    else:
                        logger.error(
                            f"[SupabaseStorage] Failed to create bucket '{self.bucket_name}': "
                            f"{create_response.status_code} - {create_response.text}"
                        )
                        create_response.raise_for_status()
                else:
                    logger.error(
                        f"[SupabaseStorage] Failed to verify bucket '{self.bucket_name}': "
                        f"{response.status_code} - {response.text}"
                    )
                    response.raise_for_status()
        except Exception as exc:
            logger.error(f"[SupabaseStorage] Initialization/validation failed: {exc}")
            # Do not raise to prevent application crash if service is temporarily unavailable
            # but log clearly.

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def upload_file(
        self, key: str, data: bytes, content_type: str, metadata: dict | None = None
    ) -> StorageResult:
        logger.info(f"[SupabaseStorage] Uploading key={key} size={len(data)} bytes")
        checksum = hashlib.sha256(data).hexdigest()

        clean_key = key.lstrip("/")
        url = f"{self.supabase_url.rstrip('/')}/storage/v1/object/{self.bucket_name}/{clean_key}"
        headers = {
            "Authorization": f"Bearer {self.service_role_key}",
            "Content-Type": content_type,
            "x-upsert": "true"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, content=data, headers=headers)
            if response.status_code != 200:
                logger.error(
                    f"[SupabaseStorage] Upload failed for key={key}: "
                    f"{response.status_code} - {response.text}"
                )
                response.raise_for_status()

        storage_url = await self.generate_public_url(key)

        return StorageResult(
            key=key,
            storage_url=storage_url,
            size=len(data),
            checksum=checksum,
            content_type=content_type,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def download_file(self, key: str) -> bytes:
        logger.info(f"[SupabaseStorage] Downloading key={key}")
        clean_key = key.lstrip("/")
        url = f"{self.supabase_url.rstrip('/')}/storage/v1/object/authenticated/{clean_key}"
        headers = {"Authorization": f"Bearer {self.service_role_key}"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                logger.error(
                    f"[SupabaseStorage] Download failed for key={key}: "
                    f"{response.status_code} - {response.text}"
                )
                response.raise_for_status()
            return response.content

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def delete_file(self, key: str) -> bool:
        logger.info(f"[SupabaseStorage] Deleting key={key}")
        clean_key = key.lstrip("/")
        url = f"{self.supabase_url.rstrip('/')}/storage/v1/object/{self.bucket_name}"
        headers = {
            "Authorization": f"Bearer {self.service_role_key}",
            "Content-Type": "application/json"
        }
        payload = {"prefixes": [clean_key]}

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request("DELETE", url, json=payload, headers=headers)
            if response.status_code != 200:
                logger.error(
                    f"[SupabaseStorage] Delete failed for key={key}: "
                    f"{response.status_code} - {response.text}"
                )
                return False
            return True

    async def generate_signed_url(self, key: str, expires_in: int = 3600) -> str:
        clean_key = key.lstrip("/")
        url = f"{self.supabase_url.rstrip('/')}/storage/v1/object/sign/{self.bucket_name}/{clean_key}"
        headers = {
            "Authorization": f"Bearer {self.service_role_key}",
            "Content-Type": "application/json"
        }
        payload = {"expiresIn": expires_in}

        logger.info(f"[SupabaseStorage] Generating signed URL for key={key}")
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code != 200:
                logger.error(
                    f"[SupabaseStorage] Signed URL generation failed for key={key}: "
                    f"{response.status_code} - {response.text}"
                )
                response.raise_for_status()

            signed_url_path = response.json().get("signedURL") or response.json().get("signedUrl")
            if not signed_url_path:
                raise ValueError("No signedURL returned in Supabase response")

            if signed_url_path.startswith("http://") or signed_url_path.startswith("https://"):
                return signed_url_path

            base_url = self.supabase_url.rstrip("/")
            return f"{base_url}/{signed_url_path.lstrip('/')}"

    async def generate_public_url(self, key: str) -> str:
        clean_key = key.lstrip("/")
        base_url = self.supabase_url.rstrip("/")
        return f"{base_url}/storage/v1/object/public/{self.bucket_name}/{clean_key}"

    async def file_exists(self, key: str) -> bool:
        clean_key = key.lstrip("/")
        url = f"{self.supabase_url.rstrip('/')}/storage/v1/object/info/authenticated/{clean_key}"
        headers = {"Authorization": f"Bearer {self.service_role_key}"}

        logger.info(f"[SupabaseStorage] Checking existence of key={key}")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    return True
                elif response.status_code == 404:
                    return False
                else:
                    return await self._file_exists_fallback(clean_key)
        except Exception as exc:
            logger.warning(f"[SupabaseStorage] Exists check failed via info endpoint: {exc}. Trying fallback...")
            return await self._file_exists_fallback(clean_key)

    async def _file_exists_fallback(self, clean_key: str) -> bool:
        parts = clean_key.rsplit("/", 1)
        prefix = parts[0] + "/" if len(parts) > 1 else ""
        filename = parts[-1]

        url = f"{self.supabase_url.rstrip('/')}/storage/v1/object/list/{self.bucket_name}"
        headers = {
            "Authorization": f"Bearer {self.service_role_key}",
            "Content-Type": "application/json"
        }
        payload = {"prefix": prefix}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    for item in response.json():
                        if item.get("name") == filename:
                            return True
        except Exception as exc:
            logger.error(f"[SupabaseStorage] Fallback exists check failed: {exc}")
        return False

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
            logger.warning(f"[SupabaseStorage] Safe delete skipped/failed for key={key}: {exc}")
            return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def list_files(self, prefix: str | None = None) -> list[str]:
        logger.info(f"[SupabaseStorage] Listing files with prefix={prefix}")
        url = f"{self.supabase_url.rstrip('/')}/storage/v1/object/list/{self.bucket_name}"
        payload = {"prefix": prefix or ""}
        headers = {
            "Authorization": f"Bearer {self.service_role_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code != 200:
                logger.error(f"[SupabaseStorage] List failed: {response.status_code} - {response.text}")
                response.raise_for_status()

            results = []
            for item in response.json():
                name = item.get("name")
                if name:
                    if prefix:
                        p = prefix.rstrip('/')
                        full_key = f"{p}/{name}"
                    else:
                        full_key = name
                    results.append(full_key)
            return results
