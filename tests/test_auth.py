import pytest_asyncio
from httpx import AsyncClient


@pytest_asyncio.fixture
async def registered_credentials(client: AsyncClient) -> dict[str, str]:
    payload = {
        "phone": "+79001234567",
        "password": "secret123",
        "first_name": "Ivan",
        "last_name": "Petrov",
    }
    response = await client.post("/api/v1/registerUser", json=payload)
    assert response.status_code == 200
    return {"phone": payload["phone"], "password": payload["password"]}


async def test_login_happy_path(client: AsyncClient, registered_credentials: dict[str, str]) -> None:
    response = await client.post("/api/v1/login", json=registered_credentials)

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["result"]["access_token"]
    assert body["result"]["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient, registered_credentials: dict[str, str]) -> None:
    response = await client.post(
        "/api/v1/login",
        json={"phone": registered_credentials["phone"], "password": "wrong-password"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "invalid_credentials"


async def test_login_unknown_phone(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/login",
        json={"phone": "+79009999999", "password": "secret123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "invalid_credentials"


async def test_login_missing_fields(client: AsyncClient) -> None:
    response = await client.post("/api/v1/login", json={})

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "validation_error"
    assert set(body["error"]["fields"].keys()) == {"phone", "password"}