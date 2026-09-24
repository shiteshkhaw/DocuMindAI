import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from models.document import DocumentModel
from vectorstore.chroma import ChromaVectorStore


@pytest.mark.asyncio
async def test_chromadb_multi_filter_and_operator():
    """Verify that ChromaVectorStore builds valid $and clauses for multi-attribute filtering."""
    store = ChromaVectorStore()

    # Empty filter
    assert store._build_where_clause(None) is None
    assert store._build_where_clause({}) is None

    # Single attribute filter (Chroma requires flat dict for single condition)
    single = store._build_where_clause({"document_id": "doc-123"})
    assert single == {"document_id": "doc-123"}

    # Multi-attribute filter (Chroma requires $and wrapper for >1 condition)
    multi = store._build_where_clause({"document_id": "doc-123", "user_id": "usr-456"})
    assert isinstance(multi, dict)
    and_conditions = multi.get("$and")
    assert isinstance(and_conditions, list)
    assert len(and_conditions) == 2
    assert {"document_id": "doc-123"} in and_conditions
    assert {"user_id": "usr-456"} in and_conditions


@pytest.mark.asyncio
async def test_tenant_document_isolation(client: AsyncClient, test_db: AsyncSession):
    """User B must never access or delete User A's document."""
    # Register User A
    res_signup_a = await client.post("/api/v1/auth/signup", json={
        "name": "User A",
        "email": "user_a@tenant.com",
        "password": "Password123!"
    })
    assert res_signup_a.status_code == 201
    user_a_data = res_signup_a.json()
    token_a = user_a_data["access_token"]
    user_a_id = user_a_data["id"]

    # Register User B
    res_signup_b = await client.post("/api/v1/auth/signup", json={
        "name": "User B",
        "email": "user_b@tenant.com",
        "password": "Password123!"
    })
    assert res_signup_b.status_code == 201
    token_b = res_signup_b.json()["access_token"]

    # User A creates a document
    doc_a = DocumentModel(
        id="doc-aaa-1",
        name="confidential_a.pdf",
        storage_url="file:///tmp/doc_a.pdf",
        status="COMPLETED",
        metadata_json={
            "title": "confidential_a",
            "fileSize": 1024,
            "mimeType": "application/pdf",
            "checksum": "abc12345"
        },
        user_id=user_a_id,
    )
    test_db.add(doc_a)
    await test_db.commit()

    # User A can get their document
    res_a = await client.get("/api/v1/documents/doc-aaa-1", headers={"Authorization": f"Bearer {token_a}"})
    assert res_a.status_code == 200
    assert res_a.json()["id"] == "doc-aaa-1"

    # User B CANNOT get User A's document (returns 404 to avoid leaking existence)
    res_b = await client.get("/api/v1/documents/doc-aaa-1", headers={"Authorization": f"Bearer {token_b}"})
    assert res_b.status_code == 404

    # User B CANNOT delete User A's document
    res_del = await client.delete("/api/v1/documents/doc-aaa-1", headers={"Authorization": f"Bearer {token_b}"})
    assert res_del.status_code == 404

    # User B CANNOT view User A's document analysis
    res_an = await client.get("/api/v1/documents/doc-aaa-1/analysis", headers={"Authorization": f"Bearer {token_b}"})
    assert res_an.status_code == 404


@pytest.mark.asyncio
async def test_chat_session_idor_prevention(client: AsyncClient, test_db: AsyncSession):
    """User B cannot create a chat session attaching User A's document."""
    # Register User A
    res_a = await client.post("/api/v1/auth/signup", json={
        "name": "User A2",
        "email": "user_a2@tenant.com",
        "password": "Password123!"
    })
    user_a_id = res_a.json()["id"]

    # Register User B
    res_b = await client.post("/api/v1/auth/signup", json={
        "name": "User B2",
        "email": "user_b2@tenant.com",
        "password": "Password123!"
    })
    token_b = res_b.json()["access_token"]

    doc_a = DocumentModel(
        id="doc-private-a",
        name="private.pdf",
        storage_url="file:///tmp/priv.pdf",
        status="COMPLETED",
        metadata_json={},
        user_id=user_a_id,
    )
    test_db.add(doc_a)
    await test_db.commit()

    # User B attempts to attach User A's document to a new chat session -> 403 Forbidden
    res = await client.post(
        "/api/v1/chat/sessions",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"title": "Unauthorized Session", "documentIds": ["doc-private-a"]}
    )
    assert res.status_code == 403
    assert "denied" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_file_upload_validation(client: AsyncClient, test_db: AsyncSession):
    """File upload rejects disallowed file types."""
    res_u = await client.post("/api/v1/auth/signup", json={
        "name": "Uploader",
        "email": "uploader@tenant.com",
        "password": "Password123!"
    })
    token = res_u.json()["access_token"]

    # Disallowed extension (.exe)
    res = await client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("malware.exe", b"MZexecutable", "application/octet-stream")}
    )
    assert res.status_code == 400
    assert "unsupported file format" in res.json()["detail"].lower()
