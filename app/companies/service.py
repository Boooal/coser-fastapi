from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.companies.models import Company
from app.companies.schemas import CompanyCreate, CompanyUpdate
from app.core.exceptions import AppException, ErrorCode
from app.users.models import User, UserRole, Role


async def create_company(db: AsyncSession, user: User, data: CompanyCreate) -> Company:
    company = Company(name=data.name)
    db.add(company)
    await db.flush()

    user_role = UserRole(user_id=user.id, company_id=company.id, role=Role.ADMIN)
    db.add(user_role)

    user.active_company_id = company.id

    await db.commit()
    await db.refresh(company)
    return company


async def get_company(db: AsyncSession, company_id: UUID) -> Company:
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if company is None:
        raise AppException(code=ErrorCode.NOT_FOUND, message="Company not found")
    return company


async def update_company(db: AsyncSession, company_id: UUID, data: CompanyUpdate) -> Company:
    company = await get_company(db, company_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(company, field, value)
    await db.commit()
    await db.refresh(company)
    return company
