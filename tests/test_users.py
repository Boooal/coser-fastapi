from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.models import User


async def test_register_user_happy_path(client: AsyncClient, db_session: AsyncSession) -> None:
    payload = {
        "phone": "+79001234567",
        "password": "secret123",
        "first_name": "Ivan",
        "last_name": "Petrov",
    }

    response = await client.post("/api/v1/registerUser", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["result"]["phone"] == payload["phone"]
    assert body["result"]["first_name"] == payload["first_name"]
    assert body["result"]["last_name"] == payload["last_name"]
    assert body["result"]["is_active"] is True
    assert "id" in body["result"]

    result = await db_session.execute(select(User).where(User.phone == payload["phone"]))
    user = result.scalar_one()
    assert user.first_name == "Ivan"
    assert user.hashed_password != "secret123"


async def test_register_user_duplicate_phone(client: AsyncClient, db_session: AsyncSession) -> None:
    payload = {
        "phone": "+79001234567",
        "password": "secret123",
        "first_name": "Ivan",
        "last_name": "Petrov",
    }
    first = await client.post("/api/v1/registerUser", json=payload)
    assert first.status_code == 200
    assert first.json()["ok"] is True

    second = await client.post("/api/v1/registerUser", json=payload)

    assert second.status_code == 200
    body = second.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "already_exists"

    result = await db_session.execute(select(User).where(User.phone == payload["phone"]))
    users = result.scalars().all()
    assert len(users) == 1


async def test_register_user_missing_required_fields(client: AsyncClient) -> None:
    response = await client.post("/api/v1/registerUser", json={"phone": "+79001234567"})

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "validation_error"
    assert set(body["error"]["fields"].keys()) == {"password", "first_name", "last_name"}