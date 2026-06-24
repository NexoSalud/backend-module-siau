"""Router: inbound email replies webhook for SIAU."""
from __future__ import annotations

import logging
import re
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories import email_notification_repo, pqrsdf_repo, trazabilidad_repo
from app.models import Trazabilidad

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/siau/email", tags=["Email"])

# Pattern to extract notification_id from siau+{NOTIF_ID}@domain.com
_REPLY_TO_PATTERN = re.compile(r"siau\+([a-f0-9\-]+)@")


@router.post("/inbound")
async def inbound_email_webhook(
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    """Webhook to receive email replies.

    Accepts form-encoded or JSON POST from an email forwarding service
    (e.g., SendGrid Inbound Parse, Mailgun, Cloudflare Email Routing).

    Expected fields (form-encoded or JSON):
      - to: the original Reply-To address (siau+{UUID}@domain.com)
      - from: sender email
      - subject: reply subject
      - text: plain text body of the reply
      - html: HTML body (optional)
    """
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        body = await request.json()
    else:
        form = await request.form()
        body = dict(form)

    to_addr = (body.get("to") or body.get("recipient") or "").strip()
    from_addr = (body.get("from") or body.get("sender") or "").strip()
    subject = (body.get("subject") or "").strip()
    text_body = (body.get("text") or body.get("plain") or body.get("body") or "").strip()

    if not to_addr:
        raise HTTPException(status_code=400, detail="Missing 'to' field")

    # Extract notification ID from Reply-To
    match = _REPLY_TO_PATTERN.search(to_addr)
    if not match:
        logger.warning("Inbound email has no valid notification ID: to=%s", to_addr)
        # Return 200 so email provider doesn't retry
        return {"status": "ignored", "reason": "no notification_id found"}

    notif_id = match.group(1)
    notification = await email_notification_repo.find_by_id(session, notif_id)
    if not notification:
        logger.warning("Notification %s not found in DB", notif_id)
        return {"status": "ignored", "reason": "notification not found"}

    if notification.reply_received:
        logger.info("Notification %s already replied — ignoring duplicate", notif_id)
        return {"status": "ignored", "reason": "already replied"}

    # Agregar a trazabilidad
    reply_text = text_body or subject or "(sin contenido)"
    await trazabilidad_repo.save(
        session,
        Trazabilidad(
            pqrsdf_id=notification.pqrsdf_id,
            accion="RESPUESTA_EMAIL",
            descripcion=f"Respuesta recibida por email de {from_addr}: {reply_text[:500]}",
            created_at=datetime.now(timezone.utc),
        ),
    )

    # Marcar notificación como respondida
    await email_notification_repo.mark_reply_received(session, notif_id, reply_text)

    logger.info(
        "Email reply processed: notif=%s pqrsdf=%s from=%s",
        notif_id, notification.pqrsdf_id, from_addr,
    )

    return {"status": "ok", "pqrsdf_id": notification.pqrsdf_id}
