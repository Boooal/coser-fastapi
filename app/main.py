from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.auth.router import router as auth_router
from app.core.exceptions import AppException
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

app.include_router(auth_router)
app.include_router(users_router)