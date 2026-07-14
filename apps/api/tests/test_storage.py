import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from storage.base import StorageResult
from storage.local import LocalStorageProvider
from storage.supabase import SupabaseStorageProvider
from storage.service import get_storage_provider


@pytest.mark.asyncio
async def test_local_storage_provider(tmp_path) -> None:
    """Test LocalStorageProvider behaviors including listing files."""
    provider = LocalStorageProvider(base_dir=str(tmp_path))
    key = "documents/test_file.txt"
    data = b"Hello DocuMind local storage"
    content_type = "text/plain"

    # 1. Upload
    result = await provider.upload_file(key, data, content_type)
    assert isinstance(result, StorageResult)
    assert result.key == key
    assert result.size == len(data)
    assert result.content_type == content_type
    assert result.storage_url.startswith("file://")

    # 2. Exists
    assert await provider.file_exists(key) is True

    # 3. Signed and public URL
    url = await provider.generate_signed_url(key)
    assert url.startswith("file://")
    pub_url = await provider.generate_public_url(key)
    assert pub_url == url

    # 4. List Files
    files = await provider.list_files("documents")
    assert key in files

    # 5. Safe delete
    assert await provider.safe_delete(key) is True
    assert await provider.file_exists(key) is False


@pytest.mark.asyncio
@patch("httpx.AsyncClient")
async def test_supabase_storage_provider(mock_client_cls) -> None:
    """Test SupabaseStorageProvider with mocked HTTP REST exchanges."""
    with patch("storage.supabase.settings") as mock_settings:
        mock_settings.SUPABASE_URL = "https://mock-supabase.co"
        mock_settings.SUPABASE_ANON_KEY = "anon-key"
        mock_settings.SUPABASE_SERVICE_ROLE_KEY = "service-role-key"
        mock_settings.SUPABASE_STORAGE_BUCKET = "documind-vault"

        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client

        provider = SupabaseStorageProvider()
        key = "documents/test_supabase.txt"
        data = b"Hello Supabase storage"
        content_type = "text/plain"

        # 1. Initialize (Bucket exists)
        mock_client.get.return_value = MagicMock(status_code=200)
        await provider.initialize()
        mock_client.get.assert_called_once_with(
            "https://mock-supabase.co/storage/v1/bucket/documind-vault",
            headers={"Authorization": "Bearer service-role-key"}
        )

        # Reset mocks
        mock_client.get.reset_mock()

        # 2. Initialize (Bucket does not exist -> Create)
        mock_get_response = MagicMock(status_code=404)
        mock_create_response = MagicMock(status_code=200)
        # Side effect for client get and client post
        mock_client.get.return_value = mock_get_response
        mock_client.post.return_value = mock_create_response
        await provider.initialize()
        mock_client.get.assert_called_once_with(
            "https://mock-supabase.co/storage/v1/bucket/documind-vault",
            headers={"Authorization": "Bearer service-role-key"}
        )
        mock_client.post.assert_called_once_with(
            "https://mock-supabase.co/storage/v1/bucket",
            json={"id": "documind-vault", "name": "documind-vault", "public": False},
            headers={"Authorization": "Bearer service-role-key"}
        )

        # 3. Upload File
        mock_client.post.reset_mock()
        mock_client.post.return_value = MagicMock(status_code=200)
        result = await provider.upload_file(key, data, content_type)
        assert result.key == key
        assert result.size == len(data)
        assert result.content_type == content_type
        assert result.storage_url == "https://mock-supabase.co/storage/v1/object/public/documind-vault/documents/test_supabase.txt"
        mock_client.post.assert_called_once_with(
            "https://mock-supabase.co/storage/v1/object/documind-vault/documents/test_supabase.txt",
            content=data,
            headers={
                "Authorization": "Bearer service-role-key",
                "Content-Type": content_type,
                "x-upsert": "true"
            }
        )

        # 4. Download File
        mock_client.get.reset_mock()
        mock_client.get.return_value = MagicMock(status_code=200, content=data)
        downloaded = await provider.download_file(key)
        assert downloaded == data
        mock_client.get.assert_called_once_with(
            "https://mock-supabase.co/storage/v1/object/authenticated/documents/test_supabase.txt",
            headers={"Authorization": "Bearer service-role-key"}
        )

        # 5. File Exists (True via info endpoint)
        mock_client.get.reset_mock()
        mock_client.get.return_value = MagicMock(status_code=200)
        exists = await provider.file_exists(key)
        assert exists is True
        mock_client.get.assert_called_once_with(
            "https://mock-supabase.co/storage/v1/object/info/authenticated/documents/test_supabase.txt",
            headers={"Authorization": "Bearer service-role-key"}
        )

        # 6. File Exists (False via info endpoint)
        mock_client.get.reset_mock()
        mock_client.get.return_value = MagicMock(status_code=404)
        exists = await provider.file_exists(key)
        assert exists is False

        # 7. Generate Signed URL
        mock_client.post.reset_mock()
        mock_sign_response = MagicMock(status_code=200)
        mock_sign_response.json.return_value = {"signedURL": "/storage/v1/object/sign/bucket/key?token=123"}
        mock_client.post.return_value = mock_sign_response
        signed_url = await provider.generate_signed_url(key)
        assert signed_url == "https://mock-supabase.co/storage/v1/object/sign/bucket/key?token=123"
        mock_client.post.assert_called_once_with(
            "https://mock-supabase.co/storage/v1/object/sign/documind-vault/documents/test_supabase.txt",
            json={"expiresIn": 3600},
            headers={
                "Authorization": "Bearer service-role-key",
                "Content-Type": "application/json"
            }
        )

        # 8. List Files
        mock_client.post.reset_mock()
        mock_list_response = MagicMock(status_code=200)
        mock_list_response.json.return_value = [{"name": "test_supabase.txt"}]
        mock_client.post.return_value = mock_list_response
        files = await provider.list_files("documents")
        assert files == ["documents/test_supabase.txt"]
        mock_client.post.assert_called_once_with(
            "https://mock-supabase.co/storage/v1/object/list/documind-vault",
            json={"prefix": "documents"},
            headers={
                "Authorization": "Bearer service-role-key",
                "Content-Type": "application/json"
            }
        )

        # 9. Delete File
        mock_client.request.return_value = MagicMock(status_code=200)
        deleted = await provider.delete_file(key)
        assert deleted is True
        mock_client.request.assert_called_once_with(
            "DELETE",
            "https://mock-supabase.co/storage/v1/object/documind-vault",
            json={"prefixes": ["documents/test_supabase.txt"]},
            headers={
                "Authorization": "Bearer service-role-key",
                "Content-Type": "application/json"
            }
        )


@pytest.mark.asyncio
async def test_get_storage_provider() -> None:
    """Test storage provider dependency injection resolved correctly."""
    with patch("storage.service.settings") as mock_settings, \
         patch("storage.supabase.settings") as mock_supabase_settings:
        # Without credentials -> should return LocalStorageProvider wrapping StorageService
        mock_settings.SUPABASE_URL = None
        mock_settings.SUPABASE_SERVICE_ROLE_KEY = None
        mock_supabase_settings.SUPABASE_URL = None
        mock_supabase_settings.SUPABASE_SERVICE_ROLE_KEY = None
        
        # Reset local cache
        from storage import service
        service._storage_service = None
        
        storage_service = get_storage_provider()
        assert storage_service.__class__.__name__ == "StorageService"
        assert storage_service.provider.__class__.__name__ == "LocalStorageProvider"
        
        # With credentials -> should return SupabaseStorageProvider wrapping StorageService
        mock_settings.SUPABASE_URL = "https://mock.supabase.co"
        mock_settings.SUPABASE_SERVICE_ROLE_KEY = "role-key"
        mock_settings.SUPABASE_STORAGE_BUCKET = "bucket"
        mock_supabase_settings.SUPABASE_URL = "https://mock.supabase.co"
        mock_supabase_settings.SUPABASE_SERVICE_ROLE_KEY = "role-key"
        mock_supabase_settings.SUPABASE_STORAGE_BUCKET = "bucket"
        
        service._storage_service = None
        storage_service = get_storage_provider()
        assert storage_service.__class__.__name__ == "StorageService"
        assert storage_service.provider.__class__.__name__ == "SupabaseStorageProvider"
        
        # Clean up global state to prevent test pollution
        service._storage_service = None
