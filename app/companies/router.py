from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.companies.schemas import CompanyCreate, CompanyResponse
from app.companies.service import create_company
from app.core.dependencies import get_db, get_current_user
from app.core.schemas import OkResponse
from app.users.models import User

router = APIRouter(prefix="/api/v1", tags=["companies"])


@router.post("/createCompany")
async def create_company_handler(
        data: CompanyCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> OkResponse[CompanyResponse]:
    company = await create_company(db, current_user, data)
    return OkResponse(result=CompanyResponse.model_validate(company))