from uuid import UUID

from pydantic import BaseModel, Field

from app.users.models import Role


class CompanyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class CompanyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    is_active: bool | None = None


class CompanyResponse(BaseModel):
    id: UUID
    name: str
    is_active: bool

    model_config = {"from_attributes": True}


class CompanyMembership(BaseModel):
    id: UUID
    name: str
    is_active: bool
    roles: list[Role]
