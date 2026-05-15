from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str
    fields: dict[str, list[str]] | None = None


class OkResponse[T](BaseModel):
    ok: bool = True
    result: T


class ErrorResponse(BaseModel):
    ok: bool = False
    error: ErrorDetail
