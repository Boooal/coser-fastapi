from sqlalchemy.ext.asyncio import AsyncSession

from app.companies.models import Company
from app.companies.schemas import CompanyCreate
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
