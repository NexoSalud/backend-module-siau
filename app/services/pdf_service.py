"""PDF generation service — renders PQRSDF summaries as PDF via Jinja2 + WeasyPrint."""

from __future__ import annotations

import os
from datetime import date
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from app.repositories import pqrsdf_repo, trazabilidad_repo, asignacion_repo
from app.services.catalogos import get_tipo_nombre

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
