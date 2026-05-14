from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.auth.router import router as auth_router
from app.core.exceptions import AppException, ErrorCode
from app.core.schemas import ErrorDetail, ErrorResponse
from app.users.router import router as users_router

app = FastAPI(title="Coser API")


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    body = ErrorResponse(
        error=ErrorDetail(code=exc.code, message=exc.message)
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=body.model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    fields: dict[str, list[str]] = {}
    for error in exc.errors():
        loc = error.get("loc", [])
        field = str(loc[-1]) if loc else "unknown"
        msg = error.get("msg", "Invalid value")
        fields.setdefault(field, []).append(msg)

    body = ErrorResponse(
        error=ErrorDetail(
            code=ErrorCode.VALIDATION_ERROR,
            message="Validation failed",
            fields=fields
        )
    )
    return JSONResponse(status_code=200, content=body.model_dump())


app.include_router(auth_router)
app.include_router(users_router)
