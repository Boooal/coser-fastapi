from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.users.models import User
from app.users.schemas import UserCreate


async def create_user(db: AsyncSession, data: UserCreate) -> User:
    user = User(
        phone=data.phone,
        hashed_password=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
