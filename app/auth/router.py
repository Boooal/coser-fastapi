from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import LoginRequest, TokenResponse
from app.auth.service import login
from app.core.dependencies import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=TokenResponse)
async def get_token(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    token = await login(db, data.phone, data.password)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return TokenResponse(access_token=token)