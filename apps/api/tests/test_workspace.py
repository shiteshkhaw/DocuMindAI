import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_workspace_crud(client: AsyncClient):
    # First signup and login
    await client.post("/api/v1/auth/signup", json={"name": "Ws User", "email": "wsuser@example.com", "password": "abc"})
    token_res = await client.post("/api/v1/auth/login", json={"email": "wsuser@example.com", "password": "abc"})
    token = token_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # create workspace
    res = await client.post("/api/v1/workspaces", json={"name": "Test Workspace"}, headers=headers)
    assert res.status_code == 201
    ws = res.json()
    assert ws["name"] == "Test Workspace"
    ws_id = ws["id"]

    # list workspaces
    res = await client.get("/api/v1/workspaces", headers=headers)
    assert res.status_code == 200
    workspaces = res.json()
    assert len(workspaces) == 2
    assert any(w["id"] == ws_id for w in workspaces)

    # patch workspace
    res = await client.patch(f"/api/v1/workspaces/{ws_id}", json={"name": "Updated Workspace"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["name"] == "Updated Workspace"

    # delete workspace
    res = await client.delete(f"/api/v1/workspaces/{ws_id}", headers=headers)
    assert res.status_code == 200

    # verify deleted (only default workspace remains)
    res = await client.get("/api/v1/workspaces", headers=headers)
    assert len(res.json()) == 1
