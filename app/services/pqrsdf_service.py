"""Service layer for PQRSDF entity — creation, search, response, closure, and history tracking."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from sqlalchemy.orm import selectinload

from app.repositories import pqrsdf_repo, trazabilidad_repo, asignacion_repo
from app.schemas import (
    CreatePqrsdfRequest,
    UpdatePqrsdfRequest,
    ResponderPqrsdfRequest,
    PagedResponse,
    PqrsdfResponse,
    TrazabilidadResponse,
)
from app.models import Pqrsdf, Asignacion, Trazabilidad
from app.services.catalogos import get_tipo_nombre


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _generar_consecutivo(tipo: str, next_id: int) -> str:
    """Genera consecutivo con formato PQRS-{tipo}-{anio}-{id:04d}."""
    anio = date.today().year
    return f"PQRS-{tipo}-{anio}-{next_id:04d}"


async def _registrar_trazabilidad(
    session: AsyncSession,
    pqrsdf_id: int,
    accion: str,
    descripcion: str,
    usuario_id: int | None = None,
    usuario_nombre: str | None = None,
    metadata_json: str | None = None,
) -> Trazabilidad:
    """Registra una entrada de trazabilidad para una PQRSDF."""
    trazabilidad = Trazabilidad(
        pqrsdf_id=pqrsdf_id,
        accion=accion,
        descripcion=descripcion,
        usuario_id=usuario_id,
        usuario_nombre=usuario_nombre,
        metadata_json=metadata_json,
        created_at=datetime.now(timezone.utc),
    )
    return await trazabilidad_repo.save(session, trazabilidad)


def _map_to_response(
    pqrsdf: Pqrsdf,
    ultimo_depto: str | None = None,
    ultimo_estado_asig: str | None = None,
    dias: int = 0,
) -> PqrsdfResponse:
    """Mapea una entidad Pqrsdf a PqrsdfResponse con datos de asignación."""
    return PqrsdfResponse(
        id=pqrsdf.id,
        consecutivo=pqrsdf.consecutivo,
        tipo=pqrsdf.tipo,
        tipoNombre=get_tipo_nombre(pqrsdf.tipo),
        fechaRadicado=pqrsdf.fecha_radicado if isinstance(pqrsdf.fecha_radicado, date) else None,
        horaRadicado=pqrsdf.hora_radicado,
        nombresUsuario=pqrsdf.nombres_usuario,
        tipoDocumento=pqrsdf.tipo_documento,
        numeroDocumento=pqrsdf.numero_documento,
        telefono=pqrsdf.telefono,
        email=pqrsdf.email,
        direccion=pqrsdf.direccion,
        eps=pqrsdf.eps,
        regimen=pqrsdf.regimen,
        medioRecepcion=pqrsdf.medio_recepcion,
        servicioInvolucrado=pqrsdf.servicio_involucrado,
        funcionarioInvolucrado=pqrsdf.funcionario_involucrado,
        descripcion=pqrsdf.descripcion,
        clasificacion=pqrsdf.clasificacion,
        estado=pqrsdf.estado,
        fechaRespuesta=pqrsdf.fecha_respuesta if isinstance(pqrsdf.fecha_respuesta, date) else None,
        medioRespuesta=pqrsdf.medio_respuesta,
        respuestaFinal=pqrsdf.respuesta_final,
        observaciones=pqrsdf.observaciones,
        createdAt=pqrsdf.created_at,
        updatedAt=pqrsdf.updated_at,
        createdBy=pqrsdf.created_by,
        updatedBy=pqrsdf.updated_by,
        ultimoDepartamentoAsignado=ultimo_depto,
        ultimoEstadoAsignacion=ultimo_estado_asig,
        diasTranscurridos=dias,
    )


async def _get_ultima_asignacion_info(
    session: AsyncSession, pqrsdf_id: int
) -> tuple[str | None, str | None, int]:
    """Obtiene el último departamento, estado de asignación y días transcurridos."""
    stmt = (
        select(Asignacion)
        .where(Asignacion.pqrsdf_id == pqrsdf_id)
        .order_by(Asignacion.created_at.desc())
        .limit(1)
    )
    result = await session.execute(stmt)
    asignacion = result.scalar_one_or_none()

    if asignacion is None:
        return None, None, 0

    dias = 0
    if (
        asignacion.fecha_asignacion
        and asignacion.estado
        and asignacion.estado not in ("RESPONDIDA", "CERRADA")
    ):
        delta = date.today() - asignacion.fecha_asignacion.date()
        dias = delta.days

    depto_nombre = None
    if asignacion.departamento_rel:
        depto_nombre = asignacion.departamento_rel.nombre

    return depto_nombre, asignacion.estado, dias


# ──────────────────────────────────────────────
# CRUD principal
# ──────────────────────────────────────────────

async def create(
    session: AsyncSession,
    req: CreatePqrsdfRequest,
    employee_id: int,
) -> PqrsdfResponse:
    """Crea una nueva PQRSDF con estado RECIBIDO y registra trazabilidad."""
    # Obtener el próximo ID para el consecutivo
    result = await session.execute(select(func.max(Pqrsdf.id)))
    max_id = result.scalar() or 0
    next_id = max_id + 1

    consecutivo = _generar_consecutivo(req.tipo, next_id)

    entity = Pqrsdf(
        consecutivo=consecutivo,
        tipo=req.tipo,
        fecha_radicado=req.fechaRadicado or date.today(),
        hora_radicado=req.horaRadicado
        or datetime.now(timezone.utc).strftime("%H:%M"),
        nombres_usuario=req.nombresUsuario,
        tipo_documento=req.tipoDocumento,
        numero_documento=req.numeroDocumento,
        telefono=req.telefono,
        email=req.email,
        direccion=req.direccion,
        eps=req.eps,
        regimen=req.regimen,
        medio_recepcion=req.medioRecepcion,
        servicio_involucrado=req.servicioInvolucrado,
        funcionario_involucrado=req.funcionarioInvolucrado,
        descripcion=req.descripcion,
        clasificacion=req.clasificacion,
        estado="RECIBIDO",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        created_by=employee_id,
        updated_by=employee_id,
        acta_buzon_id=req.actaBuzonId,
    )

    saved = await pqrsdf_repo.save(session, entity)

    await _registrar_trazabilidad(
        session,
        saved.id,
        "CREACION",
        f"PQRSDF creada con consecutivo {consecutivo}",
        employee_id,
    )

    tipo_nombre = get_tipo_nombre(req.tipo)
    return _map_to_response(saved, ultimo_depto=None, ultimo_estado_asig=None, dias=0)


async def get_by_id(
    session: AsyncSession,
    id: int,
) -> PqrsdfResponse | None:
    """Alias router-compatible para find_by_id."""
    return await find_by_id(session, id)


async def find_by_id(
    session: AsyncSession,
    id: int,
) -> PqrsdfResponse | None:
    """Busca una PQRSDF por ID con información de última asignación."""
    entity = await pqrsdf_repo.find_by_id(session, id)
    if entity is None:
        return None

    depto, estado_asig, dias = await _get_ultima_asignacion_info(session, id)
    return _map_to_response(entity, depto, estado_asig, dias)


async def list_all(
    session: AsyncSession,
    page: int = 0,
    size: int = 10,
    estado: str | None = None,
    tipo: str | None = None,
    numero_documento: str | None = None,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
) -> PagedResponse:
    """Lista PQRSDF con filtros opcionales y paginación (wrapper router-compatible)."""
    filters = {}
    if estado:
        filters["estado"] = estado
    if tipo:
        filters["tipo"] = tipo
    if numero_documento:
        filters["numeroDocumento"] = numero_documento
    if fecha_desde:
        filters["fechaDesde"] = fecha_desde
    if fecha_hasta:
        filters["fechaHasta"] = fecha_hasta
    items = await search(session, filters, page, size)
    total = await count(session, filters)
    return PagedResponse(
        content=items,
        page=page,
        size=size,
        totalElements=total,
        totalPages=max(1, (total + size - 1) // size),
        last=(page + 1) * size >= total,
    )


async def search(
    session: AsyncSession,
    filters: dict[str, Any],
    page: int = 0,
    size: int = 10,
) -> list[PqrsdfResponse]:
    """Busca PQRSDF con filtros, paginación y orden descendente por created_at."""
    query = select(Pqrsdf)

    if filters.get("estado"):
        query = query.where(Pqrsdf.estado == filters["estado"])
    if filters.get("tipo"):
        query = query.where(Pqrsdf.tipo == filters["tipo"])
    if filters.get("numeroDocumento"):
        query = query.where(Pqrsdf.numero_documento == filters["numeroDocumento"])
    if filters.get("fechaDesde"):
        query = query.where(Pqrsdf.fecha_radicado >= filters["fechaDesde"])
    if filters.get("fechaHasta"):
        query = query.where(Pqrsdf.fecha_radicado <= filters["fechaHasta"])
    if filters.get("consecutivo"):
        query = query.where(Pqrsdf.consecutivo.ilike(f'%{filters["consecutivo"]}%'))

    query = query.order_by(Pqrsdf.created_at.desc())
    query = query.offset(page * size).limit(size)

    result = await session.execute(query)
    entities = result.scalars().all()

    responses = []
    for entity in entities:
        depto, estado_asig, dias = await _get_ultima_asignacion_info(session, entity.id)
        responses.append(_map_to_response(entity, depto, estado_asig, dias))
    return responses


async def count(
    session: AsyncSession,
    filters: dict[str, Any],
) -> int:
    """Cuenta PQRSDF con los filtros aplicados."""
    query = select(func.count(Pqrsdf.id))

    if filters.get("estado"):
        query = query.where(Pqrsdf.estado == filters["estado"])
    if filters.get("tipo"):
        query = query.where(Pqrsdf.tipo == filters["tipo"])
    if filters.get("numeroDocumento"):
        query = query.where(Pqrsdf.numero_documento == filters["numeroDocumento"])
    if filters.get("fechaDesde"):
        query = query.where(Pqrsdf.fecha_radicado >= filters["fechaDesde"])
    if filters.get("fechaHasta"):
        query = query.where(Pqrsdf.fecha_radicado <= filters["fechaHasta"])
    if filters.get("consecutivo"):
        query = query.where(Pqrsdf.consecutivo.ilike(f'%{filters["consecutivo"]}%'))

    result = await session.execute(query)
    return result.scalar() or 0


async def update(
    session: AsyncSession,
    id: int,
    req: UpdatePqrsdfRequest,
    employee_id: int,
) -> PqrsdfResponse | None:
    """Actualiza clasificación y observaciones de una PQRSDF."""
    entity = await pqrsdf_repo.find_by_id(session, id)
    if entity is None:
        return None

    if req.clasificacion is not None:
        entity.clasificacion = req.clasificacion
    if req.observaciones is not None:
        entity.observaciones = req.observaciones

    entity.updated_by = req.updatedBy or employee_id
    entity.updated_at = datetime.now(timezone.utc)

    await pqrsdf_repo.save(session, entity)

    await _registrar_trazabilidad(
        session,
        id,
        "ACTUALIZACION",
        "PQRSDF actualizada",
        employee_id,
    )

    depto, estado_asig, dias = await _get_ultima_asignacion_info(session, id)
    return _map_to_response(entity, depto, estado_asig, dias)


async def responder(
    session: AsyncSession,
    id: int,
    req: ResponderPqrsdfRequest,
    employee_id: int,
) -> PqrsdfResponse | None:
    """Responde una PQRSDF: actualiza respuesta, cambia estado a RESPONDIDO."""
    entity = await pqrsdf_repo.find_by_id(session, id)
    if entity is None:
        return None

    entity.respuesta_final = req.respuestaFinal
    entity.medio_respuesta = req.medioRespuesta
    entity.fecha_respuesta = date.today()
    entity.estado = "RESPONDIDO"
    if req.clasificacion is not None:
        entity.clasificacion = req.clasificacion
    entity.updated_by = req.updatedBy or employee_id
    entity.updated_at = datetime.now(timezone.utc)

    await pqrsdf_repo.save(session, entity)

    # Marcar asignaciones activas como RESPONDIDA
    asignaciones = await asignacion_repo.find_by_pqrsdf_id(session, id)
    for asig in asignaciones:
        if asig.estado in ("PENDIENTE", "EN_PROCESO"):
            asig.estado = "RESPONDIDA"
            asig.fecha_respuesta_area = datetime.now(timezone.utc)
            await asignacion_repo.save(session, asig)

    await _registrar_trazabilidad(
        session,
        id,
        "RESPUESTA",
        f"PQRSDF respondida vía {req.medioRespuesta}",
        employee_id,
    )

    depto, estado_asig, dias = await _get_ultima_asignacion_info(session, id)
    return _map_to_response(entity, depto, estado_asig, dias)


async def cerrar(
    session: AsyncSession,
    id: int,
    employee_id: int,
) -> PqrsdfResponse | None:
    """Cierra una PQRSDF cambiando estado a CERRADO."""
    entity = await pqrsdf_repo.find_by_id(session, id)
    if entity is None:
        return None

    entity.estado = "CERRADO"
    entity.updated_by = employee_id
    entity.updated_at = datetime.now(timezone.utc)

    await pqrsdf_repo.save(session, entity)

    await _registrar_trazabilidad(
        session,
        id,
        "CIERRE",
        "PQRSDF cerrada",
        employee_id,
    )

    depto, estado_asig, dias = await _get_ultima_asignacion_info(session, id)
    return _map_to_response(entity, depto, estado_asig, dias)


async def get_trazabilidad(
    session: AsyncSession,
    pqrsdf_id: int,
) -> list[TrazabilidadResponse]:
    """Obtiene el historial de trazabilidad de una PQRSDF."""
    trazabilidad_list = await trazabilidad_repo.find_by_pqrsdf_id(session, pqrsdf_id)
    return [
        TrazabilidadResponse(
            id=t.id,
            pqrsdfId=t.pqrsdf_id,
            accion=t.accion,
            descripcion=t.descripcion,
            usuarioId=t.usuario_id,
            usuarioNombre=t.usuario_nombre,
            metadataJson=t.metadata_json,
            createdAt=t.created_at,
        )
        for t in sorted(trazabilidad_list, key=lambda x: x.created_at or datetime.min)
    ]
