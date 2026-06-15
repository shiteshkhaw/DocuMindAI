import pytest
from httpx import AsyncClient
from schemas.document import IngestionStatus

@pytest.mark.asyncio
async def test_generate_test_dataset(client: AsyncClient):
    # First signup and login
    await client.post("/api/v1/auth/signup", json={"name": "Test Lab", "email": "lab@example.com", "password": "abc"})
    token_res = await client.post("/api/v1/auth/login", json={"email": "lab@example.com", "password": "abc"})
    token = token_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # test easy
    res = await client.post("/api/v1/testing/generate?level=easy", headers=headers)
    assert res.status_code == 200
    docs = res.json()
    assert len(docs) == 1
    assert "easy" in docs[0]["name"].lower()

    # check status
    assert docs[0]["status"] in (IngestionStatus.QUEUED, IngestionStatus.UPLOADING, IngestionStatus.COMPLETED)
