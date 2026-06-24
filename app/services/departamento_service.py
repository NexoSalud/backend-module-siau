"""Service layer for Departamentos — CRUD de áreas/dependencias de respuesta."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.repositories import departamento_repo, asignacion_repo
from app.schemas import CreateDepartamentoRequest, DepartamentoResponse
from app.models import Departamento, Asignacion


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

async def _contar_pqrsdf_pendientes(
    session: AsyncSession, departamento_id: int
) -> int:
    """Cuenta asignaciones activas (PENDIENTE/EN_PROCESO) para un departamento."""
    stmt = select(func.count(Asignacion.id)).where(
        Asignacion.departamento_id == departamento_id,
        Asignacion.estado.in_(["PENDIENTE", "EN_PROCESO"]),
    )
    result = await session.execute(stmt)
    return result.scalar() or 0


def _map_to_response(
    depto: Departamento, pqrsdf_pendientes: int = 0
) -> DepartamentoResponse:
    """Mapea entidad Departamento a DepartamentoResponse."""
    return DepartamentoResponse(
        id=depto.id,
        nombre=depto.nombre,
        descripcion=depto.descripcion,
        responsable=depto.responsable,
        responsableId=depto.responsable_id,
        email=depto.email,
        activo=depto.activo if depto.activo is not None else True,
        createdAt=depto.created_at,
        updatedAt=depto.updated_at,
        pqrsdfPendientes=pqrsdf_pendientes,
    )


# ──────────────────────────────────────────────
# CRUD
# ──────────────────────────────────────────────

async def create(
    session: AsyncSession,
    req: CreateDepartamentoRequest,
) -> DepartamentoResponse:
    """Crea un nuevo departamento."""
    entity = Departamento(
        nombre=req.nombre,
        descripcion=req.descripcion,
        responsable=req.responsable,
        responsable_id=req.responsableId,
        email=req.email,
        activo=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    saved = await departamento_repo.save(session, entity)
    return _map_to_response(saved)


async def get_by_id(
    session: AsyncSession,
    id: int,
) -> DepartamentoResponse | None:
    """Alias router-compatible para find_by_id."""
    return await find_by_id(session, id)


async def find_by_id(
    session: AsyncSession,
    id: int,
) -> DepartamentoResponse | None:
    """Busca un departamento por ID con conteo de PQRSDF pendientes."""
    entity = await departamento_repo.find_by_id(session, id)
    if entity is None:
        return None
    pendientes = await _contar_pqrsdf_pendientes(session, id)
    return _map_to_response(entity, pendientes)


async def list_all(
    session: AsyncSession,
) -> list[DepartamentoResponse]:
    """Alias router-compatible para find_all."""
    return await find_all(session)


async def find_all(
    session: AsyncSession,
) -> list[DepartamentoResponse]:
    """Retorna todos los departamentos ordenados por nombre."""
    entities = await departamento_repo.find_all(session)
    responses = []
    for e in entities:
        pendientes = await _contar_pqrsdf_pendientes(session, e.id)
        responses.append(_map_to_response(e, pendientes))
    return responses


async def list_activos(
    session: AsyncSession,
) -> list[DepartamentoResponse]:
    """Alias router-compatible para find_activos."""
    return await find_activos(session)


async def find_activos(
    session: AsyncSession,
) -> list[DepartamentoResponse]:
    """Retorna solo departamentos activos."""
    entities = await departamento_repo.find_activos(session)
    responses = []
    for e in entities:
        pendientes = await _contar_pqrsdf_pendientes(session, e.id)
        responses.append(_map_to_response(e, pendientes))
    return responses


async def update(
    session: AsyncSession,
    id: int,
    req: CreateDepartamentoRequest,
) -> DepartamentoResponse | None:
    """Actualiza los datos de un departamento."""
    entity = await departamento_repo.find_by_id(session, id)
    if entity is None:
        return None

    if req.nombre is not None:
        entity.nombre = req.nombre
    if req.descripcion is not None:
        entity.descripcion = req.descripcion
    if req.responsable is not None:
        entity.responsable = req.responsable
    if req.responsableId is not None:
        entity.responsable_id = req.responsableId
    if req.email is not None:
        entity.email = req.email

    entity.updated_at = datetime.now(timezone.utc)
    await departamento_repo.save(session, entity)

    pendientes = await _contar_pqrsdf_pendientes(session, id)
    return _map_to_response(entity, pendientes)


async def toggle(
    session: AsyncSession,
    id: int,
) -> DepartamentoResponse | None:
    """Alias router-compatible para toggle_activo."""
    return await toggle_activo(session, id)


async def toggle_activo(
    session: AsyncSession,
    id: int,
) -> DepartamentoResponse | None:
    """Alterna el estado activo/inactivo de un departamento."""
    entity = await departamento_repo.find_by_id(session, id)
    if entity is None:
        return None

    entity.activo = not (entity.activo if entity.activo is not None else True)
    entity.updated_at = datetime.now(timezone.utc)
    await departamento_repo.save(session, entity)

    pendientes = await _contar_pqrsdf_pendientes(session, id)
    return _map_to_response(entity, pendientes)


async def delete(
    session: AsyncSession,
    id: int,
) -> bool:
    """Elimina un departamento si no tiene asignaciones activas.
    
    Returns:
        True si se eliminó, False si tenía asignaciones activas o no existía.
    """
    entity = await departamento_repo.find_by_id(session, id)
    if entity is None:
        return False

    # Verificar asignaciones activas
    pendientes = await _contar_pqrsdf_pendientes(session, id)
    if pendientes > 0:
        raise ValueError(
            f"No se puede eliminar el departamento: tiene {pendientes} PQRSDF pendientes"
        )

    await departamento_repo.delete(session, entity)
    return True
