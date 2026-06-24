"""Router: Actas de Buzón endpoints."""
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import ActaBuzonRequest, ActaBuzonResponse
from app.services import acta_buzon_service

router = APIRouter(prefix="/api/v1/siau/actas-buzon", tags=["Actas Buzón"])


@router.post("", response_model=ActaBuzonResponse, status_code=201)
async def create(
    body: ActaBuzonRequest,
    x_employee_id: int | None = Header(default=None, alias="x-employee-id"),
    session: AsyncSession = Depends(get_db),
):
    """Create a new acta de buzón."""
    return await acta_buzon_service.create(session, body, x_employee_id)


@router.get("", response_model=list[ActaBuzonResponse])
async def list_actas(
    session: AsyncSession = Depends(get_db),
):
    """List all actas de buzón."""
    return await acta_buzon_service.list_all(session)


@router.get("/{acta_id}", response_model=ActaBuzonResponse)
async def get_acta(
    acta_id: int,
    session: AsyncSession = Depends(get_db),
):
    """Get a single acta by ID."""
    result = await acta_buzon_service.get_by_id(session, acta_id)
    if not result:
        raise HTTPException(status_code=404, detail="Acta de buzón no encontrada")
    return result
