from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.schemas import OkResponse
from app.users.models import User
from app.users.schemas import MeResponse, UserCreate, UserResponse
from app.users.service import create_user, get_me

router = APIRouter(prefix="/api/v1", tags=["users"])


@router.post("/registerUser")
async def register_user(data: UserCreate, db: AsyncSession = Depends(get_db)) -> OkResponse[UserResponse]:
    user = await create_user(db, data)
    return OkResponse(result=UserResponse.model_validate(user))


@router.post("/getMe")
async def get_me_handler(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
) -> OkResponse[MeResponse]:
    me = await get_me(db, current_user)
    return OkResponse(result=me)
