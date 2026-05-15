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