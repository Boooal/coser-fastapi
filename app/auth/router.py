from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import LoginRequest, TokenResponse
from app.auth.service import login
from app.core.exceptions import AppException, ErrorCode
from app.core.schemas import OkResponse
from app.core.dependencies import get_db

router = APIRouter(prefix="/api/v1", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login_handler(data: LoginRequest, db: AsyncSession = Depends(get_db)) -> OkResponse[TokenResponse]:
    token = await login(db, data.phone, data.password)
    if token is None:
        raise AppException(
            code=ErrorCode.INVALID_CREDENTIALS,
            message="Invalid phone or password",
            status_code=200
        )
    return OkResponse(result=TokenResponse(access_token=token))