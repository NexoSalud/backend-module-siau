"""Router: Departamentos endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import CreateDepartamentoRequest, DepartamentoResponse
from app.services import departamento_service

router = APIRouter(prefix="/api/v1/siau/departamentos", tags=["Departamentos"])


@router.post("/", response_model=DepartamentoResponse, status_code=201)
async def create(
    body: CreateDepartamentoRequest,
    session: AsyncSession = Depends(get_db),
):
    """Create a new departamento."""
    return await departamento_service.create(session, body)


@router.get("/", response_model=list[DepartamentoResponse])
async def list_departamentos(
    session: AsyncSession = Depends(get_db),
):
    """List all departamentos."""
    return await departamento_service.list_all(session)


@router.get("/activos", response_model=list[DepartamentoResponse])
async def list_activos(
    session: AsyncSession = Depends(get_db),
):
    """List only active departamentos."""
    return await departamento_service.list_activos(session)


@router.get("/{departamento_id}", response_model=DepartamentoResponse)
async def get_departamento(
    departamento_id: int,
    session: AsyncSession = Depends(get_db),
):
    """Get a single departamento by ID."""
    result = await departamento_service.get_by_id(session, departamento_id)
    if not result:
        raise HTTPException(status_code=404, detail="Departamento no encontrado")
    return result


@router.put("/{departamento_id}", response_model=DepartamentoResponse)
async def update_departamento(
    departamento_id: int,
    body: CreateDepartamentoRequest,
    session: AsyncSession = Depends(get_db),
):
    """Update a departamento."""
    result = await departamento_service.update(session, departamento_id, body)
    if not result:
        raise HTTPException(status_code=404, detail="Departamento no encontrado")
    return result


@router.patch("/{departamento_id}/toggle", status_code=204)
async def toggle_departamento(
    departamento_id: int,
    session: AsyncSession = Depends(get_db),
):
    """Toggle active/inactive state of a departamento."""
    result = await departamento_service.toggle(session, departamento_id)
    if not result:
        raise HTTPException(status_code=404, detail="Departamento no encontrado")
    return Response(status_code=204)


@router.delete("/{departamento_id}", status_code=204)
async def delete_departamento(
    departamento_id: int,
    session: AsyncSession = Depends(get_db),
):
    """Delete a departamento."""
    result = await departamento_service.delete(session, departamento_id)
    if not result:
        raise HTTPException(status_code=404, detail="Departamento no encontrado")
    return Response(status_code=204)
