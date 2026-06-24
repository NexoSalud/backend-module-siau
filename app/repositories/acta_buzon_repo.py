"""Repository for ActaBuzon model — CRUD."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ActaBuzon


async def find_all(session: AsyncSession) -> list[ActaBuzon]:
    result = await session.execute(
        select(ActaBuzon).order_by(ActaBuzon.created_at.desc())
    )
    return list(result.scalars().all())


async def find_by_id(session: AsyncSession, id: int) -> ActaBuzon | None:
    result = await session.execute(select(ActaBuzon).where(ActaBuzon.id == id))
    return result.scalar_one_or_none()


async def save(session: AsyncSession, entity: ActaBuzon) -> ActaBuzon:
    session.add(entity)
    await session.flush()
    await session.refresh(entity)
    return entity
