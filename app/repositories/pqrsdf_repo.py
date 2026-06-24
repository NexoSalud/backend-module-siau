"""Repository for Pqrsdf model — CRUD and counter queries."""
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Pqrsdf


async def find_all(session: AsyncSession) -> list[Pqrsdf]:
    result = await session.execute(select(Pqrsdf).order_by(Pqrsdf.id.desc()))
    return list(result.scalars().all())


async def find_by_id(session: AsyncSession, id: int) -> Pqrsdf | None:
    result = await session.execute(select(Pqrsdf).where(Pqrsdf.id == id))
    return result.scalar_one_or_none()


async def save(session: AsyncSession, entity: Pqrsdf) -> Pqrsdf:
    session.add(entity)
    await session.flush()
    await session.refresh(entity)
    return entity


async def count_total(session: AsyncSession) -> int:
    result = await session.execute(select(func.count(Pqrsdf.id)))
    return result.scalar() or 0


async def count_by_estado(session: AsyncSession, estado: str) -> int:
    result = await session.execute(
        select(func.count(Pqrsdf.id)).where(Pqrsdf.estado == estado)
    )
    return result.scalar() or 0


async def count_by_tipo(session: AsyncSession, tipo: str) -> int:
    result = await session.execute(
        select(func.count(Pqrsdf.id)).where(Pqrsdf.tipo == tipo)
    )
    return result.scalar() or 0


async def find_max_id(session: AsyncSession) -> int:
    result = await session.execute(select(func.coalesce(func.max(Pqrsdf.id), 0)))
    return result.scalar() or 0
