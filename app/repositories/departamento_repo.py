"""Repository for Departamento model — CRUD and active filter."""
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Departamento


async def find_all(session: AsyncSession) -> list[Departamento]:
    result = await session.execute(select(Departamento).order_by(Departamento.nombre))
    return list(result.scalars().all())


async def find_by_id(session: AsyncSession, id: int) -> Departamento | None:
    result = await session.execute(select(Departamento).where(Departamento.id == id))
    return result.scalar_one_or_none()


async def find_by_activo_true(session: AsyncSession) -> list[Departamento]:
    result = await session.execute(
        select(Departamento)
        .where(Departamento.activo.is_(True))
        .order_by(Departamento.nombre)
    )
    return list(result.scalars().all())


async def save(session: AsyncSession, entity: Departamento) -> Departamento:
    session.add(entity)
    await session.flush()
    await session.refresh(entity)
    return entity


async def delete_by_id(session: AsyncSession, id: int) -> bool:
    result = await session.execute(
        delete(Departamento).where(Departamento.id == id)
    )
    return result.rowcount > 0
