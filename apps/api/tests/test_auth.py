import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_signup_and_login(client: AsyncClient):
    signup_data = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "password123"
    }
    res = await client.post("/api/v1/auth/signup", json=signup_data)
    assert res.status_code == 201
    user = res.json()
    assert user["email"] == "testuser@example.com"
    assert "password" not in user

    login_data = {
        "email": "testuser@example.com",
        "password": "password123"
    }
    res = await client.post("/api/v1/auth/login", json=login_data)
    assert res.status_code == 200
    token = res.json()
    assert "access_token" in token

    # test me
    res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token['access_token']}"})
    assert res.status_code == 200
    assert res.json()["email"] == "testuser@example.com"
