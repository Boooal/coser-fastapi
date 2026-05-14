from uuid import UUID

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.companies.schemas import CompanyCreate, CompanyResponse, CompanyUpdate
from app.companies.service import create_company, get_company, update_company
from app.core.dependencies import get_db, get_current_user, get_company_id
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


@router.post("/getCompany")
async def get_company_handler(
        db: AsyncSession = Depends(get_db),
        company_id: UUID = Depends(get_company_id),
) -> OkResponse[CompanyResponse]:
    company = await get_company(db, company_id)
    return OkResponse(result=CompanyResponse.model_validate(company))


@router.post("/updateCompany")
async def update_company_handler(
        data: CompanyUpdate,
        db: AsyncSession = Depends(get_db),
        company_id: UUID = Depends(get_company_id)
) -> OkResponse[CompanyResponse]:
    company = await update_company(db, company_id, data)
    return OkResponse(result=CompanyResponse.model_validate(company))
