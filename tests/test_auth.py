from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest_asyncio
from httpx import AsyncClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.users.models import User


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


def _forge_token(user_id: str, expires_in: timedelta = timedelta(minutes=30)) -> str:
    payload = {"sub": user_id, "exp": datetime.now(UTC) + expires_in}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


async def test_get_me_without_token(client: AsyncClient) -> None:
    response = await client.post("/api/v1/getMe")

    assert response.status_code == 401
    body = response.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "unauthenticated"


async def test_get_me_with_malformed_token(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/getMe",
        headers={"Authorization": "Bearer not-a-valid-jwt"},
    )

    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "token_invalid"


async def test_get_me_with_expired_token(client: AsyncClient) -> None:
    token = _forge_token(str(uuid4()), expires_in=timedelta(seconds=-10))

    response = await client.post(
        "/api/v1/getMe",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "token_expired"


async def test_get_me_for_unknown_user(client: AsyncClient) -> None:
    token = _forge_token(str(uuid4()))

    response = await client.post(
        "/api/v1/getMe",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "unauthenticated"


async def test_get_me_for_inactive_user(client: AsyncClient, db_session: AsyncSession) -> None:
    payload = {
        "phone": "+79001234567",
        "password": "secret123",
        "first_name": "Ivan",
        "last_name": "Petrov",
    }
    register = await client.post("/api/v1/registerUser", json=payload)
    user_id_str = register.json()["result"]["id"]

    user = await db_session.get(User, UUID(user_id_str))
    user.is_active = False
    await db_session.commit()

    token = _forge_token(user_id_str)
    response = await client.post(
        "/api/v1/getMe",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "unauthenticated"