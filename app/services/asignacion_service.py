"""Service layer for Asignacion — assignment of PQRSDF to departments."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.repositories import asignacion_repo, pqrsdf_repo, departamento_repo, trazabilidad_repo
from app.schemas import (
    CreateAsignacionRequest,
    AsignacionResponse,
    DashboardStatsResponse,
)
from app.models import Asignacion, Pqrsdf, Trazabilidad


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _calcular_fecha_limite(desde: date, dias_habiles: int = 15) -> date:
    """Calcula una fecha límite sumando días hábiles (salta sábados y domingos)."""
    dias_agregados = 0
    fecha = desde
    while dias_agregados < dias_habiles:
        fecha += timedelta(days=1)
        if fecha.weekday() < 5:  # 0=Lun ... 4=Vie
            dias_agregados += 1
    return fecha


def _map_to_response(
    asignacion: Asignacion,
    consecutivo: str | None = None,
    depto_nombre: str | None = None,
) -> AsignacionResponse:
    """Mapea entidad Asignacion a AsignacionResponse."""
    vencida = False
    dias_restantes = 0
    if (
        asignacion.estado
        and asignacion.estado not in ("RESPONDIDA", "CERRADA")
        and asignacion.fecha_limite_respuesta
    ):
        hoy = date.today()
        dias_restantes = (asignacion.fecha_limite_respuesta - hoy).days
        vencida = dias_restantes < 0
        if vencida:
            dias_restantes = abs(dias_restantes)

    return AsignacionResponse(
        id=asignacion.id,
        pqrsdfId=asignacion.pqrsdf_id,
        pqrsdfConsecutivo=consecutivo,
        departamentoId=asignacion.departamento_id,
        departamentoNombre=depto_nombre or (
            asignacion.departamento_rel.nombre
            if asignacion.departamento_rel
            else None
        ),
        funcionarioId=asignacion.funcionario_id,
        funcionarioNombre=asignacion.funcionario_nombre,
        fechaAsignacion=asignacion.fecha_asignacion,
        fechaLimiteRespuesta=asignacion.fecha_limite_respuesta,
        estado=asignacion.estado,
        respuestaArea=asignacion.respuesta_area,
        observaciones=asignacion.observaciones,
        fechaRespuestaArea=asignacion.fecha_respuesta_area,
        createdAt=asignacion.created_at,
        vencida=vencida,
        diasRestantes=dias_restantes,
    )


def _get_departamento_nombre(asignacion: Asignacion) -> str | None:
    """Obtiene nombre del departamento desde la relación cargada."""
    if asignacion.departamento_rel:
        return asignacion.departamento_rel.nombre
    return None


# ──────────────────────────────────────────────
# CRUD
# ──────────────────────────────────────────────

async def create(
    session: AsyncSession,
    req: CreateAsignacionRequest,
    employee_id: int,
) -> AsignacionResponse:
    """Crea una nueva asignación y actualiza estado de PQRSDF a ASIGNADO."""
    # Validar que PQRSDF exista
    pqrsdf = await pqrsdf_repo.find_by_id(session, req.pqrsdfId)
    if pqrsdf is None:
        raise ValueError(f"PQRSDF con ID {req.pqrsdfId} no encontrada")

    # Validar que departamento exista
    depto = await departamento_repo.find_by_id(session, req.departamentoId)
    if depto is None:
        raise ValueError(f"Departamento con ID {req.departamentoId} no encontrado")

    # Calcular fecha límite
    fecha_limite = req.fechaLimiteRespuesta or _calcular_fecha_limite(date.today())

    entity = Asignacion(
        pqrsdf_id=req.pqrsdfId,
        departamento_id=req.departamentoId,
        funcionario_id=req.funcionarioId,
        funcionario_nombre=req.funcionarioNombre,
        fecha_asignacion=datetime.now(timezone.utc),
        fecha_limite_respuesta=fecha_limite,
        estado="PENDIENTE",
        observaciones=req.observaciones,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    saved = await asignacion_repo.save(session, entity)

    # Actualizar estado de PQRSDF
    if pqrsdf.estado in ("RECIBIDO", "PENDIENTE"):
        pqrsdf.estado = "ASIGNADO"
        pqrsdf.updated_by = employee_id
        pqrsdf.updated_at = datetime.now(timezone.utc)
        await pqrsdf_repo.save(session, pqrsdf)

    # Registrar trazabilidad
    trazabilidad = Trazabilidad(
        pqrsdf_id=req.pqrsdfId,
        accion="ASIGNACION",
        descripcion=f"Asignada a {depto.nombre} — vence {fecha_limite.isoformat()}",
        usuario_id=employee_id,
        created_at=datetime.now(timezone.utc),
    )
    await trazabilidad_repo.save(session, trazabilidad)

    return _map_to_response(
        saved,
        consecutivo=pqrsdf.consecutivo,
        depto_nombre=depto.nombre,
    )


async def get_by_id(
    session: AsyncSession,
    id: int,
) -> AsignacionResponse | None:
    """Alias router-compatible para find_by_id."""
    return await find_by_id(session, id)


async def find_by_id(
    session: AsyncSession,
    id: int,
) -> AsignacionResponse | None:
    """Busca una asignación por ID."""
    entity = await asignacion_repo.find_by_id(session, id)
    if entity is None:
        return None
    return _map_to_response(entity)


async def list_by_pqrsdf(
    session: AsyncSession,
    pqrsdf_id: int,
) -> list[AsignacionResponse]:
    """Alias router-compatible para find_by_pqrsdf_id."""
    return await find_by_pqrsdf_id(session, pqrsdf_id)


async def find_by_pqrsdf_id(
    session: AsyncSession,
    pqrsdf_id: int,
) -> list[AsignacionResponse]:
    """Retorna todas las asignaciones de una PQRSDF."""
    entities = await asignacion_repo.find_by_pqrsdf_id(session, pqrsdf_id)
    pqrsdf = await pqrsdf_repo.find_by_id(session, pqrsdf_id)
    consecutivo = pqrsdf.consecutivo if pqrsdf else None

    responses = []
    for e in entities:
        depto_nombre = _get_departamento_nombre(e)
        responses.append(_map_to_response(e, consecutivo=consecutivo, depto_nombre=depto_nombre))
    return responses


async def list_by_departamento(
    session: AsyncSession,
    departamento_id: int,
) -> list[AsignacionResponse]:
    """Alias router-compatible para find_by_departamento_id."""
    return await find_by_departamento_id(session, departamento_id)


async def find_by_departamento_id(
    session: AsyncSession,
    departamento_id: int,
) -> list[AsignacionResponse]:
    """Retorna asignaciones activas de un departamento."""
    entities = await asignacion_repo.find_by_departamento_id(session, departamento_id)

    responses = []
    for e in entities:
        consecutivo = e.pqrsdf_rel.consecutivo if e.pqrsdf_rel else None
        depto_nombre = _get_departamento_nombre(e)
        responses.append(_map_to_response(e, consecutivo=consecutivo, depto_nombre=depto_nombre))
    return responses


async def responder(
    session: AsyncSession,
    id: int,
    body: dict,
    employee_id: int,
) -> AsignacionResponse | None:
    """Alias router-compatible para responder_asignacion (body es dict con campo 'respuesta')."""
    return await responder_asignacion(session, id, body.get("respuesta", ""), employee_id)


async def responder_asignacion(
    session: AsyncSession,
    id: int,
    respuesta: str,
    employee_id: int,
) -> AsignacionResponse | None:
    """Registra respuesta del área sobre una asignación."""
    entity = await asignacion_repo.find_by_id(session, id)
    if entity is None:
        return None

    entity.respuesta_area = respuesta
    entity.estado = "RESPONDIDA"
    entity.fecha_respuesta_area = datetime.now(timezone.utc)
    entity.updated_at = datetime.now(timezone.utc)

    await asignacion_repo.save(session, entity)

    # Registrar trazabilidad
    pqrsdf = await pqrsdf_repo.find_by_id(session, entity.pqrsdf_id)
    depto_nombre = entity.departamento_rel.nombre if entity.departamento_rel else "desconocido"

    trazabilidad = Trazabilidad(
        pqrsdf_id=entity.pqrsdf_id,
        accion="RESPUESTA_AREA",
        descripcion=f"Respuesta recibida del área {depto_nombre}",
        usuario_id=employee_id,
        created_at=datetime.now(timezone.utc),
    )
    await trazabilidad_repo.save(session, trazabilidad)

    return _map_to_response(
        entity,
        consecutivo=pqrsdf.consecutivo if pqrsdf else None,
        depto_nombre=depto_nombre,
    )


async def get_dashboard_stats(
    session: AsyncSession,
) -> DashboardStatsResponse:
    """Calcula estadísticas para el dashboard: conteo por estado, tipo y departamento."""

    # Totales por estado
    stmt_estados = select(Pqrsdf.estado, func.count(Pqrsdf.id).label("total")).group_by(Pqrsdf.estado)
    result = await session.execute(stmt_estados)
    estado_counts = dict(result.all())

    # Totales por tipo
    stmt_tipos = select(Pqrsdf.tipo, func.count(Pqrsdf.id).label("total")).group_by(Pqrsdf.tipo)
    result = await session.execute(stmt_tipos)
    tipo_counts = dict(result.all())

    # Totales por departamento (asignaciones activas)
    stmt_deptos = select(
        Asignacion.departamento_id, func.count(Asignacion.id).label("total")
    ).where(
        Asignacion.estado.in_(["PENDIENTE", "EN_PROCESO"])
    ).group_by(Asignacion.departamento_id)
    result = await session.execute(stmt_deptos)
    depto_counts_raw = dict(result.all())

    # Mapear IDs de departamento a nombres
    depto_counts: dict[str, int] = {}
    for depto_id, count in depto_counts_raw.items():
        depto = await departamento_repo.find_by_id(session, depto_id)
        nombre = depto.nombre if depto else f"ID {depto_id}"
        depto_counts[nombre] = count

    # Últimos 30 días
    hace_30 = date.today() - timedelta(days=30)
    stmt_30d = select(
        func.date(Pqrsdf.created_at).label("dia"),
        func.count(Pqrsdf.id).label("total"),
    ).where(
        Pqrsdf.created_at >= hace_30
    ).group_by(
        func.date(Pqrsdf.created_at)
    ).order_by(
        func.date(Pqrsdf.created_at)
    )
    result = await session.execute(stmt_30d)
    ultimos_30dias = {str(row.dia): row.total for row in result}

    total = sum(estado_counts.values())
    pendientes = estado_counts.get("RECIBIDO", 0) + estado_counts.get("PENDIENTE", 0)
    en_gestion = estado_counts.get("ASIGNADO", 0) + estado_counts.get("EN_GESTION", 0)
    respondidas = estado_counts.get("RESPONDIDO", 0)

    # Vencidas: asignaciones con fecha_limite_respuesta < today y estado activo
    stmt_vencidas = select(func.count(Asignacion.id)).where(
        Asignacion.fecha_limite_respuesta < date.today(),
        Asignacion.estado.in_(["PENDIENTE", "EN_PROCESO"]),
    )
    result = await session.execute(stmt_vencidas)
    vencidas = result.scalar() or 0

    return DashboardStatsResponse(
        totalPqrsdf=total,
        pendientes=pendientes,
        enGestion=en_gestion,
        respondidas=respondidas,
        cerradas=estado_counts.get("CERRADO", 0),
        vencidas=vencidas,
        porTipo=dict(tipo_counts),
        porDepartamento=depto_counts,
        ultimos30Dias=ultimos_30dias,
    )
