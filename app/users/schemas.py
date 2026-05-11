from uuid import UUID
from pydantic import BaseModel


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
