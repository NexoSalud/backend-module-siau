"""Router: PQRSDF endpoints."""
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import (
    CreatePqrsdfRequest,
    PagedResponse,
    PqrsdfResponse,
    ResponderPqrsdfRequest,
    TrazabilidadResponse,
    UpdatePqrsdfRequest,
)
from app.services import pqrsdf_service

router = APIRouter(prefix="/api/v1/siau/pqrsdf", tags=["PQRSDF"])


@router.post("", response_model=PqrsdfResponse, status_code=201)
async def create_pqrsdf(
    body: CreatePqrsdfRequest,
    x_employee_id: int | None = Header(default=None, alias="x-employee-id"),
    session: AsyncSession = Depends(get_db),
):
    """Create a new PQRSDF."""
    return await pqrsdf_service.create(session, body, x_employee_id)


@router.get("", response_model=PagedResponse)
async def list_pqrsdf(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1, le=100),
    estado: str | None = Query(None),
    tipo: str | None = Query(None),
    numero_documento: str | None = Query(None, alias="numeroDocumento"),
    fecha_desde: str | None = Query(None, alias="fechaDesde"),
    fecha_hasta: str | None = Query(None, alias="fechaHasta"),
    session: AsyncSession = Depends(get_db),
):
    """List PQRSDF with optional filters."""
    return await pqrsdf_service.list_all(
        session, page, size, estado, tipo, numero_documento, fecha_desde, fecha_hasta,
    )


@router.get("/{pqrsdf_id}", response_model=PqrsdfResponse)
async def get_pqrsdf(
    pqrsdf_id: int,
    session: AsyncSession = Depends(get_db),
):
    """Get a single PQRSDF by ID."""
    result = await pqrsdf_service.get_by_id(session, pqrsdf_id)
    if not result:
        raise HTTPException(status_code=404, detail="PQRSDF no encontrado")
    return result


@router.patch("/{pqrsdf_id}", response_model=PqrsdfResponse)
async def update_pqrsdf(
    pqrsdf_id: int,
    body: UpdatePqrsdfRequest,
    x_employee_id: int | None = Header(default=None, alias="x-employee-id"),
    session: AsyncSession = Depends(get_db),
):
    """Update a PQRSDF."""
    result = await pqrsdf_service.update(session, pqrsdf_id, body, x_employee_id)
    if not result:
        raise HTTPException(status_code=404, detail="PQRSDF no encontrado")
    return result


@router.post("/{pqrsdf_id}/responder", response_model=PqrsdfResponse)
async def responder_pqrsdf(
    pqrsdf_id: int,
    body: ResponderPqrsdfRequest,
    x_employee_id: int | None = Header(default=None, alias="x-employee-id"),
    session: AsyncSession = Depends(get_db),
):
    """Respond to a PQRSDF (final answer)."""
    result = await pqrsdf_service.responder(session, pqrsdf_id, body, x_employee_id)
    if not result:
        raise HTTPException(status_code=404, detail="PQRSDF no encontrado")
    return result


@router.post("/{pqrsdf_id}/cerrar", response_model=PqrsdfResponse)
async def cerrar_pqrsdf(
    pqrsdf_id: int,
    x_employee_id: int | None = Header(default=None, alias="x-employee-id"),
    session: AsyncSession = Depends(get_db),
):
    """Close a PQRSDF."""
    result = await pqrsdf_service.cerrar(session, pqrsdf_id, x_employee_id)
    if not result:
        raise HTTPException(status_code=404, detail="PQRSDF no encontrado")
    return result


@router.get("/{pqrsdf_id}/trazabilidad", response_model=list[TrazabilidadResponse])
async def trazabilidad_pqrsdf(
    pqrsdf_id: int,
    session: AsyncSession = Depends(get_db),
):
    """Get traceability for a PQRSDF."""
    return await pqrsdf_service.get_trazabilidad(session, pqrsdf_id)
