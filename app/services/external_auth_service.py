"""External auth service — email + 2FA code for external response authentication."""
from __future__ import annotations

import logging
import os
import random
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import EmailAuthCode
from app.services.email_service import send_email

logger = logging.getLogger(__name__)

CODE_EXPIRY_MINUTES = 10
TOKEN_EXPIRY_HOURS = 2


async def request_code(session: AsyncSession, email: str) -> bool:
    """Generate and send a 2FA code to the given email.

    Returns True if sent successfully.
    """
    # Generate 6-digit code
    code = f"{random.randint(100000, 999999)}"
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=CODE_EXPIRY_MINUTES)

    # Save to DB
    entity = EmailAuthCode(
        email=email,
        code=code,
        expires_at=expires_at,
    )
    session.add(entity)
    await session.commit()

    # Send email
    subject = "Código de verificación — Sistema SIAU NexoSalud"
    body = (
        f"Su código de verificación es:\n\n"
        f"   {code}\n\n"
        f"Este código expira en {CODE_EXPIRY_MINUTES} minutos.\n\n"
        f"Ingrese este código en el formulario para responder la PQRSDF.\n\n"
        f"Atentamente,\nSistema SIAU — NexoSalud"
    )

    sent = send_email(email, subject, body)
    if not sent:
        logger.error("Failed to send verification code to %s", email)
        return False

    logger.info("Verification code sent to %s (code: %s)", email, code)
    return True


async def verify_code(
    session: AsyncSession,
    email: str,
    code: str,
) -> str | None:
    """Verify a 2FA code and return an access token if valid.

    Returns the access token, or None if invalid/expired.
    """
    now = datetime.now(timezone.utc)

    # Find valid unused code for this email
    result = await session.execute(
        select(EmailAuthCode)
        .where(
            EmailAuthCode.email == email,
            EmailAuthCode.code == code,
            EmailAuthCode.used == False,
            EmailAuthCode.expires_at > now,
        )
        .order_by(EmailAuthCode.created_at.desc())
        .limit(1)
    )
    auth_code = result.scalar_one_or_none()

    if not auth_code:
        logger.warning("Invalid/expired code for %s", email)
        return None

    # Mark as used
    auth_code.used = True

    # Generate access token
    token = secrets.token_urlsafe(32)
    auth_code.access_token = token
    auth_code.token_expires_at = now + timedelta(hours=TOKEN_EXPIRY_HOURS)
    await session.commit()

    logger.info("Code verified for %s, token issued", email)
    return token


async def validate_token(session: AsyncSession, token: str) -> str | None:
    """Validate an access token and return the associated email.

    Returns email if valid, None otherwise.
    """
    now = datetime.now(timezone.utc)
    result = await session.execute(
        select(EmailAuthCode)
        .where(
            EmailAuthCode.access_token == token,
            EmailAuthCode.token_expires_at > now,
        )
        .limit(1)
    )
    record = result.scalar_one_or_none()
    if not record:
        return None
    return record.email
