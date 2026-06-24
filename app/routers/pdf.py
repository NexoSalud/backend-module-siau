"""Router: PDF generation endpoints."""
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import PdfResumenRequest
from app.services import pdf_service

router = APIRouter(prefix="/api/v1/siau", tags=["PDF"])


@router.get("/pqrsdf/{pqrsdf_id}/pdf")
async def descargar_pdf_resumen(
    pqrsdf_id: int,
    incluir_trazabilidad: bool = Query(True, alias="incluirTrazabilidad"),
    incluir_asignaciones: bool = Query(True, alias="incluirAsignaciones"),
    session: AsyncSession = Depends(get_db),
):
    """Download PQRSDF summary PDF."""
    pdf_bytes = await pdf_service.generate_summary(
        session, pqrsdf_id, incluir_trazabilidad, incluir_asignaciones,
    )
    if not pdf_bytes:
        raise HTTPException(status_code=404, detail="PQRSDF no encontrado")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="pqrsdf_{pqrsdf_id}.pdf"',
        },
    )


@router.post("/pqrsdf/{pqrsdf_id}/pdf")
async def generar_pdf_resumen(
    pqrsdf_id: int,
    body: PdfResumenRequest,
    session: AsyncSession = Depends(get_db),
):
    """Generate PQRSDF summary PDF with custom options."""
    pdf_bytes = await pdf_service.generate_summary(
        session,
        body.pqrsdf_id,
        body.incluir_trazabilidad,
        body.incluir_asignaciones,
    )
    if not pdf_bytes:
        raise HTTPException(status_code=404, detail="PQRSDF no encontrado")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="pqrsdf_{body.pqrsdf_id}.pdf"',
        },
    )
