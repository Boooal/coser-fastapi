from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str
    fields: dict[str, list[str]] | None = None


class OkResponse(BaseModel, Generic[T]):
    ok: bool = True
    result: T


class ErrorResponse(BaseModel):
    ok: bool = False
    error: ErrorDetail
