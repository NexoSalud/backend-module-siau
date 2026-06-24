"""Router: External/public endpoints for PQRSDF response (email + 2FA auth)."""
from __future__ import annotations

import logging
from datetime import date

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories import pqrsdf_repo, trazabilidad_repo
from app.models import Trazabilidad
from app.schemas import PqrsdfResponse
from app.services import external_auth_service, pqrsdf_service
from app.services.catalogos import get_tipo_nombre

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/siau/external", tags=["Externo"])


# ── DTOs ─────────────────────────────────────────────────────────────────────

from pydantic import BaseModel


class RequestCodeBody(BaseModel):
    email: str


class VerifyCodeBody(BaseModel):
    email: str
    code: str


class ExternalResponderBody(BaseModel):
    respuestaFinal: str
    medioRespuesta: str = "EMAIL"
    clasificacion: str | None = None


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post("/request-code")
async def request_code(
    body: RequestCodeBody,
    session: AsyncSession = Depends(get_db),
):
    """Request a 2FA verification code sent to the given email."""
    sent = await external_auth_service.request_code(session, body.email.strip().lower())
    if not sent:
        raise HTTPException(status_code=500, detail="Error al enviar el código")
    return {"message": "Código enviado al correo", "email": body.email}


@router.post("/verify-code")
async def verify_code(
    body: VerifyCodeBody,
    session: AsyncSession = Depends(get_db),
):
    """Verify the 2FA code and get an access token."""
    token = await external_auth_service.verify_code(
        session, body.email.strip().lower(), body.code.strip()
    )
    if not token:
        raise HTTPException(status_code=401, detail="Código inválido o expirado")
    return {"access_token": token, "expires_in": 7200}


@router.get("/pqrsdf/{pqrsdf_id}")
async def get_pqrsdf_public(
    pqrsdf_id: int,
    authorization: str | None = Header(default=None, alias="authorization"),
    session: AsyncSession = Depends(get_db),
):
    """Get public PQRSDF info needed to respond (requires access_token)."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Se requiere token de acceso")
    token = authorization.replace("Bearer ", "")

    email = await external_auth_service.validate_token(session, token)
    if not email:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    entity = await pqrsdf_repo.find_by_id(session, pqrsdf_id)
    if not entity:
        raise HTTPException(status_code=404, detail="PQRSDF no encontrada")

    return {
        "id": entity.id,
        "consecutivo": entity.consecutivo,
        "tipo": entity.tipo,
        "tipoNombre": get_tipo_nombre(entity.tipo) or entity.tipo,
        "fechaRadicado": (
            entity.fecha_radicado.isoformat()
            if isinstance(entity.fecha_radicado, date)
            else str(entity.fecha_radicado or "")
        ),
        "nombresUsuario": entity.nombres_usuario,
        "descripcion": entity.descripcion,
        "estado": entity.estado,
        "email_responsable": email,
    }


@router.post("/pqrsdf/{pqrsdf_id}/responder")
async def responder_pqrsdf_external(
    pqrsdf_id: int,
    body: ExternalResponderBody,
    authorization: str | None = Header(default=None, alias="authorization"),
    session: AsyncSession = Depends(get_db),
):
    """Submit a response to a PQRSDF from an external user (email + 2FA)."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Se requiere token de acceso")
    token = authorization.replace("Bearer ", "")

    email = await external_auth_service.validate_token(session, token)
    if not email:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    entity = await pqrsdf_repo.find_by_id(session, pqrsdf_id)
    if not entity:
        raise HTTPException(status_code=404, detail="PQRSDF no encontrada")

    if entity.estado in ("CERRADO", "RESPONDIDO"):
        raise HTTPException(status_code=400, detail="Esta PQRSDF ya fue respondida")

    # Update PQRSDF
    from datetime import datetime, timezone
    entity.respuesta_final = body.respuestaFinal
    entity.medio_respuesta = body.medioRespuesta or "EMAIL"
    entity.fecha_respuesta = date.today()
    entity.estado = "RESPONDIDO"
    if body.clasificacion:
        entity.clasificacion = body.clasificacion
    entity.updated_at = datetime.now(timezone.utc)

    await pqrsdf_repo.save(session, entity)

    # Add trazabilidad
    await trazabilidad_repo.save(
        session,
        Trazabilidad(
            pqrsdf_id=pqrsdf_id,
            accion="RESPUESTA_EXTERNA",
            descripcion=f"Respuesta ingresada vía enlace externo por {email}: {body.respuestaFinal[:300]}",
            created_at=datetime.now(timezone.utc),
        ),
    )

    logger.info("External response for PQRSDF %d by %s", pqrsdf_id, email)
    return {"message": "Respuesta registrada exitosamente", "pqrsdf_id": pqrsdf_id}
