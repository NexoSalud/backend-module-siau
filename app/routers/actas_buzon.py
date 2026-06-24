"""Router: Actas de Buzón endpoints."""
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.responses import Response

from app.database import get_db
from app.schemas import ActaBuzonRequest, ActaBuzonResponse
from app.services import acta_buzon_service, pdf_service

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


@router.get("/{acta_id}/pdf")
async def descargar_acta_pdf(
    acta_id: int,
    session: AsyncSession = Depends(get_db),
):
    """Download Acta de Apertura de Buzón as PDF (formato PM-S-FR04)."""
    # Get the acta entity directly from repo
    from app.repositories import acta_buzon_repo
    from app.models import ActaBuzon

    acta = await acta_buzon_repo.find_by_id(session, acta_id)
    if not acta:
        raise HTTPException(status_code=404, detail="Acta de buzón no encontrada")

    counts = await acta_buzon_service.get_pqrsdf_counts_by_tipo(session, acta_id)
    pdf_bytes = await pdf_service.generate_acta_buzon_pdf(session, acta, counts)

    filename = f"acta_apertura_buzon_{acta_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
