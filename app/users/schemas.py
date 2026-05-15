from uuid import UUID

from pydantic import BaseModel

from app.companies.schemas import CompanyMembership


class UserCreate(BaseModel):
    phone: str
    password: str
    first_name: str
    last_name: str


class UserResponse(BaseModel):
    id: UUID
    phone: str
    first_name: str
    last_name: str
    is_active: bool

    model_config = {"from_attributes": True}


class MeResponse(BaseModel):
    id: UUID
    phone: str
    email: str | None
    first_name: str
    last_name: str
    avatar: str | None
    active_company_id: UUID | None
    companies: list[CompanyMembership]
