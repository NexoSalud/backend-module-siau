"""Service layer for ActaBuzon — registro de apertura de buzones de sugerencias."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import acta_buzon_repo, pqrsdf_repo
from app.schemas import ActaBuzonRequest, ActaBuzonResponse
from app.models import ActaBuzon


def _map_to_response(entity: ActaBuzon) -> ActaBuzonResponse:
    """Mapea entidad ActaBuzon a ActaBuzonResponse."""
    return ActaBuzonResponse(
        id=entity.id,
        fechaApertura=entity.fecha_apertura,
        ubicacion=entity.ubicacion,
        servicio=entity.servicio,
        totalPqrsdf=entity.total_pqrsdf or 0,
        detallePorTipo=entity.detalle_por_tipo,
        observaciones=entity.observaciones,
        createdAt=entity.created_at,
        createdBy=entity.created_by,
    )


async def create(
    session: AsyncSession,
    req: ActaBuzonRequest,
    employee_id: int,
) -> ActaBuzonResponse:
    """Crea un acta de apertura de buzón."""
    entity = ActaBuzon(
        fecha_apertura=req.fechaApertura,
        ubicacion=req.ubicacion,
        servicio=req.servicio,
        total_pqrsdf=req.totalPqrsdf,
        detalle_por_tipo=req.detallePorTipo,
        observaciones=req.observaciones,
        created_at=datetime.now(timezone.utc),
        created_by=req.createdBy or employee_id,
    )
    saved = await acta_buzon_repo.save(session, entity)
    return _map_to_response(saved)


async def list_all(
    session: AsyncSession,
) -> list[ActaBuzonResponse]:
    """Alias router-compatible para find_all."""
    return await find_all(session)


async def find_all(
    session: AsyncSession,
) -> list[ActaBuzonResponse]:
    """Retorna todas las actas de buzón ordenadas por fecha descendente."""
    entities = await acta_buzon_repo.find_all(session)
    # Ordenar por fecha descendente (repositorio podría ya ordenar)
    sorted_entities = sorted(
        entities, key=lambda x: x.created_at or datetime.min, reverse=True
    )
    return [_map_to_response(e) for e in sorted_entities]


async def get_by_id(
    session: AsyncSession,
    id: int,
) -> ActaBuzonResponse | None:
    """Alias router-compatible para find_by_id."""
    return await find_by_id(session, id)


async def get_pqrsdf_counts_by_tipo(
    session: AsyncSession,
    acta_buzon_id: int,
) -> dict[str, int]:
    """Obtiene conteo de PQRSDF agrupado por tipo para un acta."""
    tipos = ["P", "Q", "R", "S", "D", "F"]
    result = {}
    for tipo in tipos:
        count = await pqrsdf_repo.count_by_tipo_and_acta(session, tipo, acta_buzon_id)
        if count > 0:
            result[tipo] = count
    return result


async def find_by_id(
    session: AsyncSession,
    id: int,
) -> ActaBuzonResponse | None:
    """Busca un acta de buzón por ID."""
    entity = await acta_buzon_repo.find_by_id(session, id)
    if entity is None:
        return None
    return _map_to_response(entity)
