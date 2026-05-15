from collections.abc import AsyncGenerator
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException, ErrorCode
from app.core.security import decode_access_token
from app.db.session import AsyncSessionLocal
from app.users.models import User

bearer_scheme = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
        db: AsyncSession = Depends(get_db)) -> User:
    if credentials is None:
        raise AppException(
            code=ErrorCode.UNAUTHENTICATED,
            message="Token is missing",
            status_code=401,
        )

    try:
        user_id = decode_access_token(credentials.credentials)
    except ExpiredSignatureError:
        raise AppException(
            code=ErrorCode.TOKEN_EXPIRED,
            message="Access token has expired",
            status_code=401,
        )
    except JWTError:
        raise AppException(
            code=ErrorCode.TOKEN_INVALID,
            message="Token is malformed or invalid",
            status_code=401,
        )

    try:
        user_uuid = UUID(user_id)
    except (ValueError, TypeError):
        raise AppException(
            code=ErrorCode.TOKEN_INVALID,
            message="Token payload is malformed",
            status_code=401,
        )

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise AppException(
            code=ErrorCode.UNAUTHENTICATED,
            message="User not found or inactive",
            status_code=401,
        )

    return user


async def get_current_company_user(
        current_user: User = Depends(get_current_user),
) -> User:
    if current_user.active_company_id is None:
        raise AppException(
            code=ErrorCode.PERMISSION_DENIED,
            message="No active company. Create or switch to a company first"
        )
    return current_user


async def get_company_id(
        current_user: User = Depends(get_current_company_user),
) -> UUID:
    return current_user.active_company_id
