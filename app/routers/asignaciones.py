"""Router: Asignaciones endpoints."""
from fastapi import APIRouter, Depends, Header, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import (
    AsignacionResponse,
    CreateAsignacionRequest,
    DashboardStatsResponse,
)
from app.services import asignacion_service

router = APIRouter(prefix="/api/v1/siau", tags=["Asignaciones"])


@router.post("/asignaciones", response_model=AsignacionResponse, status_code=201)
async def create_asignacion(
    body: CreateAsignacionRequest,
    x_employee_id: int | None = Header(default=None, alias="x-employee-id"),
    session: AsyncSession = Depends(get_db),
):
    """Create a new asignacion."""
    return await asignacion_service.create(session, body, x_employee_id)


@router.get("/asignaciones/{asignacion_id}", response_model=AsignacionResponse)
async def get_asignacion(
    asignacion_id: int,
    session: AsyncSession = Depends(get_db),
):
    """Get a single asignacion by ID."""
    result = await asignacion_service.get_by_id(session, asignacion_id)
    if not result:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    return result


@router.get("/pqrsdf/{pqrsdf_id}/asignaciones", response_model=list[AsignacionResponse])
async def list_by_pqrsdf(
    pqrsdf_id: int,
    session: AsyncSession = Depends(get_db),
):
    """List asignaciones for a PQRSDF."""
    return await asignacion_service.list_by_pqrsdf(session, pqrsdf_id)


@router.get("/departamentos/{depto_id}/asignaciones", response_model=list[AsignacionResponse])
async def list_by_departamento(
    depto_id: int,
    session: AsyncSession = Depends(get_db),
):
    """List asignaciones for a departamento."""
    return await asignacion_service.list_by_departamento(session, depto_id)


@router.post("/asignaciones/{asignacion_id}/responder", response_model=AsignacionResponse)
async def responder_asignacion(
    asignacion_id: int,
    body: dict,
    x_employee_id: int | None = Header(default=None, alias="x-employee-id"),
    session: AsyncSession = Depends(get_db),
):
    """Respond to an asignacion (area response)."""
    result = await asignacion_service.responder(session, asignacion_id, body, x_employee_id)
    if not result:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    return result


@router.get("/dashboard", response_model=DashboardStatsResponse)
async def dashboard_stats(
    session: AsyncSession = Depends(get_db),
):
    """Get dashboard statistics."""
    return await asignacion_service.get_dashboard_stats(session)
