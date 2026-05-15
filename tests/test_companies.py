from uuid import UUID

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.companies.models import Company
from app.users.models import Role, User, UserRole


async def test_create_company_happy_path(
    client: AsyncClient, db_session: AsyncSession, authed_user: dict
) -> None:
    response = await client.post(
        "/api/v1/createCompany",
        json={"name": "Acme Coffee"},
        headers=authed_user["headers"],
    )

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["result"]["name"] == "Acme Coffee"
    assert body["result"]["is_active"] is True
    assert "id" in body["result"]

    company_id = UUID(body["result"]["id"])
    user_id = UUID(authed_user["user_id"])

    company = await db_session.get(Company, company_id)
    assert company is not None
    assert company.name == "Acme Coffee"

    roles_result = await db_session.execute(
        select(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.company_id == company_id,
        )
    )
    roles = roles_result.scalars().all()
    assert len(roles) == 1
    assert roles[0].role == Role.ADMIN

    user = await db_session.get(User, user_id)
    assert user.active_company_id == company_id


async def test_create_company_empty_name(client: AsyncClient, authed_user: dict) -> None:
    response = await client.post(
        "/api/v1/createCompany",
        json={"name": ""},
        headers=authed_user["headers"],
    )

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "validation_error"
    assert "name" in body["error"]["fields"]


async def test_create_company_missing_name(client: AsyncClient, authed_user: dict) -> None:
    response = await client.post(
        "/api/v1/createCompany",
        json={},
        headers=authed_user["headers"],
    )

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "validation_error"
    assert set(body["error"]["fields"].keys()) == {"name"}


async def test_get_my_companies_empty(client: AsyncClient, authed_user: dict) -> None:
    response = await client.post("/api/v1/getMyCompanies", headers=authed_user["headers"])

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["result"] == []


async def test_get_my_companies_multiple(client: AsyncClient, authed_user: dict) -> None:
    first = await client.post(
        "/api/v1/createCompany",
        json={"name": "Alpha"},
        headers=authed_user["headers"],
    )
    second = await client.post(
        "/api/v1/createCompany",
        json={"name": "Beta"},
        headers=authed_user["headers"],
    )
    assert first.status_code == 200 and first.json()["ok"] is True
    assert second.status_code == 200 and second.json()["ok"] is True

    response = await client.post("/api/v1/getMyCompanies", headers=authed_user["headers"])

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert len(body["result"]) == 2
    names = {item["name"] for item in body["result"]}
    assert names == {"Alpha", "Beta"}
    for membership in body["result"]:
        assert membership["roles"] == ["admin"]


async def test_get_me_after_register_has_no_companies(client: AsyncClient, authed_user: dict) -> None:
    response = await client.post("/api/v1/getMe", headers=authed_user["headers"])

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["result"]["active_company_id"] is None
    assert body["result"]["companies"] == []


async def test_get_me_reflects_active_company(client: AsyncClient, authed_user: dict) -> None:
    create = await client.post(
        "/api/v1/createCompany",
        json={"name": "Acme"},
        headers=authed_user["headers"],
    )
    company_id = create.json()["result"]["id"]

    response = await client.post("/api/v1/getMe", headers=authed_user["headers"])

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["result"]["active_company_id"] == company_id
    assert len(body["result"]["companies"]) == 1
    assert body["result"]["companies"][0]["id"] == company_id
    assert body["result"]["companies"][0]["name"] == "Acme"
    assert body["result"]["companies"][0]["roles"] == ["admin"]


async def test_get_company_happy_path(client: AsyncClient, authed_user: dict) -> None:
    create = await client.post(
        "/api/v1/createCompany",
        json={"name": "Acme"},
        headers=authed_user["headers"],
    )
    company_id = create.json()["result"]["id"]

    response = await client.post("/api/v1/getCompany", headers=authed_user["headers"])

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["result"]["id"] == company_id
    assert body["result"]["name"] == "Acme"
    assert body["result"]["is_active"] is True


async def test_get_company_without_active_company(client: AsyncClient, authed_user: dict) -> None:
    response = await client.post("/api/v1/getCompany", headers=authed_user["headers"])

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "permission_denied"


async def test_update_company_happy_path(
    client: AsyncClient, db_session: AsyncSession, authed_user: dict
) -> None:
    create = await client.post(
        "/api/v1/createCompany",
        json={"name": "Acme"},
        headers=authed_user["headers"],
    )
    company_id = UUID(create.json()["result"]["id"])

    response = await client.post(
        "/api/v1/updateCompany",
        json={"name": "Acme Coffee", "is_active": False},
        headers=authed_user["headers"],
    )

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["result"]["name"] == "Acme Coffee"
    assert body["result"]["is_active"] is False

    company = await db_session.get(Company, company_id)
    assert company.name == "Acme Coffee"
    assert company.is_active is False


async def test_update_company_without_active_company(client: AsyncClient, authed_user: dict) -> None:
    response = await client.post(
        "/api/v1/updateCompany",
        json={"name": "Acme Coffee"},
        headers=authed_user["headers"],
    )

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "permission_denied"