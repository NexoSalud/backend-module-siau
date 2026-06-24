"""Repository for Trazabilidad model — ordered reads and create."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Trazabilidad


async def find_by_pqrsdf_id_order_by_created_at(
    session: AsyncSession, pqrsdf_id: int
) -> list[Trazabilidad]:
    result = await session.execute(
        select(Trazabilidad)
        .where(Trazabilidad.pqrsdf_id == pqrsdf_id)
        .order_by(Trazabilidad.created_at.asc())
    )
    return list(result.scalars().all())


async def save(session: AsyncSession, entity: Trazabilidad) -> Trazabilidad:
    session.add(entity)
    await session.flush()
    await session.refresh(entity)
    return entity
