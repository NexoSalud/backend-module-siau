"""Email notification service for SIAU — sends and processes emails via SMTP.

Reuses the same environment variables as the existing Java email system
(configured via Coolify for backend-module-employees):
  EMAIL_HOST, EMAIL_PORT, EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_FROM
"""
from __future__ import annotations

import logging
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Any

logger = logging.getLogger(__name__)


def _get_smtp_config() -> dict[str, Any]:
    """Read SMTP config from env (shared with Java backend-module-employees)."""
    return {
        "host": os.environ.get("EMAIL_HOST", "smtp.gmail.com"),
        "port": int(os.environ.get("EMAIL_PORT", "587")),
        "username": os.environ.get("EMAIL_USERNAME", ""),
        "password": os.environ.get("EMAIL_PASSWORD", ""),
        "from_addr": os.environ.get("EMAIL_FROM", "no-reply@nexosalud.com"),
    }


def send_email(
    to_email: str,
    subject: str,
    body_text: str,
    notification_id: str | None = None,
) -> bool:
    """Send an email via SMTP (synchronous, runs in thread).

    Args:
        to_email: Recipient email address.
        subject: Email subject line.
        body_text: Plain text body.
        notification_id: Optional unique ID for reply tracking.
                         If set, the Reply-To header includes siau+{id}@...

    Returns:
        True if sent successfully, False otherwise.
    """
    cfg = _get_smtp_config()

    if not cfg["username"] or not cfg["password"]:
        logger.warning("EMAIL_USERNAME/EMAIL_PASSWORD not configured — skipping email")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = cfg["from_addr"]
        msg["To"] = to_email
        msg["Subject"] = subject

        if notification_id:
            # Use custom Reply-To with notification ID for tracking replies
            from_domain = cfg["from_addr"].split("@")[-1]
            reply_to = f"siau+{notification_id}@{from_domain}"
            msg["Reply-To"] = reply_to

        msg.attach(MIMEText(body_text, "plain"))

        context = ssl.create_default_context()
        with smtplib.SMTP(cfg["host"], cfg["port"]) as server:
            server.starttls(context=context)
            server.login(cfg["username"], cfg["password"])
            server.sendmail(cfg["from_addr"], [to_email], msg.as_string())

        logger.info("Email sent to %s — subject: %s", to_email, subject)
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed — check EMAIL_USERNAME/EMAIL_PASSWORD")
        return False
    except smtplib.SMTPException as e:
        logger.error("SMTP error sending to %s: %s", to_email, e)
        return False
    except Exception as e:
        logger.error("Unexpected error sending email to %s: %s", to_email, e)
        return False


def build_notification_body(
    consecutivo: str,
    tipo_nombre: str,
    descripcion: str,
    ubicacion: str,
    fecha_limite: str,
    pqrsdf_id: int,
    base_url: str = "",
) -> str:
    """Build plain-text notification body for an assignment."""
    lines = [
        f"Se le ha asignado una PQRSDF para atención:",
        "",
        f"  Consecutivo: {consecutivo}",
        f"  Tipo: {tipo_nombre}",
        f"  Descripción: {descripcion[:200]}{'...' if len(descripcion) > 200 else ''}",
        f"  Ubicación: {ubicacion}",
        f"  Fecha límite de respuesta: {fecha_limite}",
        "",
        "Por favor ingrese al sistema para gestionar esta solicitud.",
        "",
    ]
    if base_url:
        lines.append(f"Enlace directo: {base_url}/dashboard/siau/{pqrsdf_id}")
    lines.extend([
        "",
        "Atentamente,",
        "Sistema SIAU — NexoSalud",
        "",
        "---",
        "Este es un mensaje automático. Por favor no responda directamente a este correo.",
    ])
    return "\n".join(lines)
