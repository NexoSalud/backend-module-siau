"""Repository for Asignacion model — CRUD and aggregations."""
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Asignacion


async def find_by_id(session: AsyncSession, id: int) -> Asignacion | None:
    result = await session.execute(select(Asignacion).where(Asignacion.id == id))
    return result.scalar_one_or_none()


async def find_by_pqrsdf_id(
    session: AsyncSession, pqrsdf_id: int
) -> list[Asignacion]:
    result = await session.execute(
        select(Asignacion)
        .where(Asignacion.pqrsdf_id == pqrsdf_id)
        .order_by(Asignacion.created_at.desc())
    )
    return list(result.scalars().all())


async def find_by_departamento_id(
    session: AsyncSession, depto_id: int
) -> list[Asignacion]:
    result = await session.execute(
        select(Asignacion)
        .where(Asignacion.departamento_id == depto_id)
        .order_by(Asignacion.created_at.desc())
    )
    return list(result.scalars().all())


async def find_ultima_by_pqrsdf_id(
    session: AsyncSession, pqrsdf_id: int
) -> Asignacion | None:
    result = await session.execute(
        select(Asignacion)
        .where(Asignacion.pqrsdf_id == pqrsdf_id)
        .order_by(Asignacion.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def save(session: AsyncSession, entity: Asignacion) -> Asignacion:
    session.add(entity)
    await session.flush()
    await session.refresh(entity)
    return entity


async def count_by_estado(session: AsyncSession, estado: str) -> int:
    result = await session.execute(
        select(func.count(Asignacion.id)).where(Asignacion.estado == estado)
    )
    return result.scalar() or 0


async def count_by_departamento(session: AsyncSession, depto_id: int) -> int:
    result = await session.execute(
        select(func.count(Asignacion.id)).where(
            Asignacion.departamento_id == depto_id
        )
    )
    return result.scalar() or 0


async def count_by_departamento_and_estado(
    session: AsyncSession, depto_id: int, estado: str
) -> int:
    result = await session.execute(
        select(func.count(Asignacion.id)).where(
            Asignacion.departamento_id == depto_id,
            Asignacion.estado == estado,
        )
    )
    return result.scalar() or 0
