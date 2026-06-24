"""PDF generation service — renders PQRSDF summaries as PDF via Jinja2 + WeasyPrint."""

from __future__ import annotations

import os
from datetime import date
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from app.repositories import pqrsdf_repo, trazabilidad_repo, asignacion_repo
from app.models import ActaBuzon
from app.services.catalogos import get_tipo_nombre

# ── Tipo names for report ──────────────────────────────────
_TIPO_DESCRIPCION = {
    "P": "Petición",
    "Q": "Queja",
    "R": "Reclamo de riesgo simple",
    "S": "Sugerencia",
    "D": "Reclamo de riesgo priorizado",
    "F": "Felicitación",
}

# ──────────────────────────────────────────────
# Jinja2 environment
# ──────────────────────────────────────────────

_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")

_env = Environment(
    loader=FileSystemLoader(_TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"]),
    enable_async=False,  # WeasyPrint's HTML.write_pdf is synchronous internally
)

_FILTERS_TO_REGISTER: dict[str, Any] = {}

# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

async def generate_acta_buzon_pdf(
    session: AsyncSession,
    acta: ActaBuzon,
    counts: dict[str, int],
) -> bytes:
    """Genera el PDF del Acta de Apertura de Buzón según formato PM-S-FR04."""
    from datetime import date

    # Parse date parts
    fa = acta.fecha_apertura
    if isinstance(fa, date):
        dia = str(fa.day)
        meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
        ]
        mes = meses[fa.month - 1]
        anio = str(fa.year)
    else:
        dia = "___"; mes = "_______________"; anio = "______"

    ubicacion = acta.ubicacion or "_____________________"
    servicio = acta.servicio or "________________________________"

    # Map tipo codes to form labels
    tipo_labels = {
        "P": "Peticiones",
        "Q": "Quejas",
        "R": "Reclamo de riesgo simple",
        "D": "Reclamo de riesgo priorizado",
        "V": "Reclamo de riesgo vital",
        "S": "Sugerencias",
        "F": "Felicitaciones",
    }
    tipo_descs = {
        "P": "Solicitud de información, documentos o intervención",
        "Q": "Inconformidad con el actuar de un funcionario",
        "R": "Insatisfacción sin riesgo inminente (72h respuesta)",
        "D": "Riesgo para integridad o población vulnerable (48h)",
        "V": "Riesgo inminente para la vida (24h respuesta)",
        "S": "Recomendación para mejorar el servicio",
        "F": "Manifestación positiva del usuario",
    }

    rows = []
    for tipo_code in ["P", "Q", "R", "V", "D", "S", "F"]:
        total = counts.get(tipo_code, 0)
        if total > 0 or tipo_code in ("P", "Q", "R", "S"):  # Show common types always
            rows.append({
                "tipo": tipo_labels.get(tipo_code, tipo_code),
                "total": total,
                "descripcion": tipo_descs.get(tipo_code, ""),
            })

    # Render template
    template = _env.get_template("acta_apertura_buzon.html")
    html_str = template.render(
        acta_id=acta.id,
        dia=dia,
        mes=mes,
        anio=anio,
        ubicacion=ubicacion,
        servicio=servicio,
        total_pqrsdf=acta.total_pqrsdf or sum(counts.values()),
        rows=rows,
    )

    pdf_bytes = HTML(string=html_str).write_pdf()
    return pdf_bytes


async def generate_summary(
    session: AsyncSession,
    pqrsdf_id: int,
    incluir_trazabilidad: bool = True,
    incluir_asignaciones: bool = True,
) -> bytes:
    """Alias router-compatible para generar_pdf_resumen."""
    return await generar_pdf_resumen(session, pqrsdf_id, incluir_trazabilidad, incluir_asignaciones)


async def generar_pdf_resumen(
    session: AsyncSession,
    pqrsdf_id: int,
    incluir_trazabilidad: bool = True,
    incluir_asignaciones: bool = True,
) -> bytes:
    """Genera un PDF con el resumen completo de una PQRSDF.

    Carga la entidad junto con su trazabilidad y asignaciones,
    renderiza el template HTML y genera el PDF con WeasyPrint.

    Args:
        session: Sesión de base de datos.
        pqrsdf_id: ID de la PQRSDF a imprimir.
        incluir_trazabilidad: Incluye tabla de trazabilidad.
        incluir_asignaciones: Incluye tabla de asignaciones.

    Returns:
        bytes del PDF generado.

    Raises:
        ValueError: Si la PQRSDF no existe.
    """
    # ── Cargar datos ──────────────────────────
    pqrsdf_raw = await pqrsdf_repo.find_by_id(session, pqrsdf_id)
    if pqrsdf_raw is None:
        raise ValueError(f"PQRSDF con ID {pqrsdf_id} no encontrada")

    # ── Preparar datos para el template ───────
    pqrsdf_data = _entity_to_dict(pqrsdf_raw)

    trazabilidad = []
    if incluir_trazabilidad:
        traz_raw = await trazabilidad_repo.find_by_pqrsdf_id(session, pqrsdf_id)
        traz_raw.sort(key=lambda x: x.created_at or __import__("datetime").datetime.min)
        for t in traz_raw:
            trazabilidad.append({
                "accion": t.accion,
                "descripcion": t.descripcion,
                "usuarioNombre": t.usuario_nombre,
                "createdAt": t.created_at,
            })

    asignaciones = []
    if incluir_asignaciones:
        asig_raw = await asignacion_repo.find_by_pqrsdf_id(session, pqrsdf_id)
        asig_raw.sort(key=lambda x: x.created_at or __import__("datetime").datetime.min)
        for a in asig_raw:
            depto_nombre = (
                a.departamento_rel.nombre if a.departamento_rel else None
            )
            asignaciones.append({
                "departamentoId": a.departamento_id,
                "departamentoNombre": depto_nombre,
                "estado": a.estado,
                "fechaAsignacion": a.fecha_asignacion,
                "fechaLimiteRespuesta": a.fecha_limite_respuesta,
                "respuestaArea": a.respuesta_area,
            })

    # ── Renderizar HTML ──────────────────────
    template = _env.get_template("resumen_pqrsdf.html")
    html_str = template.render(
        pqrsdf=pqrsdf_data,
        trazabilidad=trazabilidad,
        asignaciones=asignaciones,
        incluir_trazabilidad=incluir_trazabilidad,
        incluir_asignaciones=incluir_asignaciones,
        generation_date=date.today().isoformat(),
    )

    # ── Generar PDF ──────────────────────────
    pdf_bytes = HTML(string=html_str).write_pdf()

    return pdf_bytes


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _entity_to_dict(pqrsdf: Any) -> dict[str, Any]:
    """Convierte una entidad Pqrsdf en un diccionario plano para el template."""
    return {
        "id": pqrsdf.id,
        "consecutivo": pqrsdf.consecutivo,
        "tipo": pqrsdf.tipo,
        "tipoNombre": get_tipo_nombre(pqrsdf.tipo),
        "fechaRadicado": (
            pqrsdf.fecha_radicado.isoformat()
            if hasattr(pqrsdf.fecha_radicado, "isoformat")
            else str(pqrsdf.fecha_radicado or "")
        ),
        "horaRadicado": pqrsdf.hora_radicado,
        "nombresUsuario": pqrsdf.nombres_usuario,
        "tipoDocumento": pqrsdf.tipo_documento,
        "numeroDocumento": pqrsdf.numero_documento,
        "telefono": pqrsdf.telefono,
        "email": pqrsdf.email,
        "direccion": pqrsdf.direccion,
        "eps": pqrsdf.eps,
        "regimen": pqrsdf.regimen,
        "medioRecepcion": pqrsdf.medio_recepcion,
        "servicioInvolucrado": pqrsdf.servicio_involucrado,
        "funcionarioInvolucrado": pqrsdf.funcionario_involucrado,
        "descripcion": pqrsdf.descripcion,
        "clasificacion": pqrsdf.clasificacion,
        "estado": pqrsdf.estado,
        "fechaRespuesta": (
            pqrsdf.fecha_respuesta.isoformat()
            if hasattr(pqrsdf.fecha_respuesta, "isoformat")
            else str(pqrsdf.fecha_respuesta or "")
        ),
        "medioRespuesta": pqrsdf.medio_respuesta,
        "respuestaFinal": pqrsdf.respuesta_final,
        "observaciones": pqrsdf.observaciones,
        "createdAt": pqrsdf.created_at,
        "updatedAt": pqrsdf.updated_at,
        "createdBy": pqrsdf.created_by,
        "updatedBy": pqrsdf.updated_by,
    }
