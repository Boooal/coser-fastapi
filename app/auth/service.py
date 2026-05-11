from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, verify_password
from app.users.models import User


async def authenticate_user(db: AsyncSession, phone: str, password: str) -> User | None:
    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()

    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def login(db: AsyncSession, phone: str, password: str) -> str | None:
    user = await authenticate_user(db, phone, password)
    if user is None:
        return None
    return create_access_token(subject=str(user.id))
