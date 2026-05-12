from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.schemas import OkResponse
from app.users.schemas import UserCreate, UserResponse
from app.users.service import create_user

router = APIRouter(prefix="/api/v1", tags=["users"])


@router.post("/registerUser")
async def register_user(data: UserCreate, db: AsyncSession = Depends(get_db)) -> OkResponse[UserResponse]:
    user = await create_user(db, data)
    return OkResponse(result=UserResponse.model_validate(user))