"""IMAP email reply polling service for SIAU.

Checks an inbox periodically for replies to notification emails
and processes them into trazabilidad.

Reuses the same email credentials as SMTP (EMAIL_USERNAME, EMAIL_PASSWORD).
Gmail IMAP requires IMAP enabled + App Password.
"""
from __future__ import annotations

import email
import logging
import os
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from imaplib import IMAP4_SSL
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.repositories import email_notification_repo, trazabilidad_repo
from app.models import Trazabilidad

logger = logging.getLogger(__name__)

# Regex to extract notification ID from siau+{UUID}@domain
_REPLY_TO_PATTERN = re.compile(r"siau\+([a-f0-9\-]+)@", re.IGNORECASE)
# Match siau+{UUID}@ in any header
_SIAU_PLUS_PATTERN = re.compile(r"siau\+([a-f0-9\-]+)@", re.IGNORECASE)

_IMAP_CONFIG: dict[str, Any] | None = None


def _get_imap_config() -> dict[str, Any]:
    """Read IMAP config from environment (reuses same creds as SMTP)."""
    global _IMAP_CONFIG
    if _IMAP_CONFIG is not None:
        return _IMAP_CONFIG

    cfg = {
        "host": os.environ.get("IMAP_HOST", "imap.gmail.com"),
        "port": int(os.environ.get("IMAP_PORT", "993")),
        "username": os.environ.get("EMAIL_USERNAME", ""),
        "password": os.environ.get("EMAIL_PASSWORD", ""),
        "from_domain": os.environ.get("EMAIL_FROM", "no-reply@nexosalud.com").split("@")[-1],
    }
    _IMAP_CONFIG = cfg
    return cfg


def is_configured() -> bool:
    """Check if IMAP credentials are available."""
    cfg = _get_imap_config()
    return bool(cfg["username"] and cfg["password"])


def _search_reply_emails(
    host: str,
    port: int,
    username: str,
    password: str,
    from_domain: str,
) -> list[dict[str, Any]]:
    """Connect to IMAP, search for SIAU reply emails, return parsed results.

    This is synchronous (IMAP4_SSL is blocking) — run in a thread.
    """
    replies: list[dict[str, Any]] = []
    email_ids: list[str] = []

    try:
        mail = IMAP4_SSL(host, port)
        mail.login(username, password)
        mail.select("INBOX")

        # Search for unseen emails (or all recent ones) with siau+ in headers
        # Gmail: we search ALL recent unseen messages
        status, messages = mail.search(None, "UNSEEN")
        if status != "OK":
            mail.logout()
            return []

        email_ids = messages[0].split() if messages[0] else []
        # Also search seen but recent (last 7 days) to catch any missed
        if not email_ids:
            # Try ALL to be safe, but limit
            status, messages = mail.search(None, "ALL")
            if status == "OK" and messages[0]:
                all_ids = messages[0].split()
                email_ids = all_ids[-10:]  # Last 10 only

        for eid in email_ids[-20:]:  # Max 20 emails per poll
            status, msg_data = mail.fetch(eid, "(RFC822)")
            if status != "OK":
                continue

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    raw_email = response_part[1]
                    parsed = email.message_from_bytes(raw_email)

                    # Extract headers
                    to_addr = parsed.get("To", "") or ""
                    from_addr = parsed.get("From", "") or ""
                    subject = parsed.get("Subject", "") or ""
                    reply_to = parsed.get("Reply-To", "") or ""
                    # Also check Delivered-To, X-Original-To, etc.
                    delivered_to = parsed.get("Delivered-To", "") or ""
                    received_to = parsed.get("X-Original-To", "") or ""

                    # Search for notification ID in To/Reply-To headers
                    combined_to = f"{to_addr} {reply_to} {delivered_to} {received_to}".lower()
                    match = _SIAU_PLUS_PATTERN.search(combined_to)
                    if not match:
                        continue

                    notif_id = match.group(1)

                    # Extract body (plain text)
                    body_text = _get_email_body(parsed)

                    # Extract date
                    date_header = parsed.get("Date")
                    received_at = datetime.now(timezone.utc)
                    if date_header:
                        try:
                            received_at = parsedate_to_datetime(date_header)
                        except Exception:
                            pass

                    replies.append({
                        "notification_id": notif_id,
                        "from": from_addr,
                        "subject": subject,
                        "body": body_text,
                        "received_at": received_at,
                    })

                    # Mark as read so we don't re-process
                    mail.store(eid, "+FLAGS", "\\Seen")

        mail.close()
        mail.logout()

    except Exception as e:
        logger.error("IMAP polling error: %s", e)

    return replies


def _get_email_body(parsed: email.message.Message) -> str:
    """Extract plain text body from an email message."""
    if parsed.is_multipart():
        for part in parsed.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode("utf-8", errors="replace")
            elif content_type == "text/html":
                pass  # Skip HTML in favor of plain text
        # Fallback: try any text part
        for part in parsed.walk():
            if part.get_content_maintype() == "text":
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode("utf-8", errors="replace")
    else:
        payload = parsed.get_payload(decode=True)
        if payload:
            return payload.decode("utf-8", errors="replace")
    return "(sin contenido)"


async def poll_replies() -> int:
    """Main polling function — connects to IMAP, processes replies into trazabilidad.

    Returns the number of new replies processed.
    """
    if not is_configured():
        logger.info("IMAP not configured — skipping poll")
        return 0

    cfg = _get_imap_config()
    logger.info("Starting IMAP poll for %s...", cfg["username"])

    import asyncio
    loop = asyncio.get_event_loop()
    replies = await loop.run_in_executor(
        None,
        _search_reply_emails,
        cfg["host"],
        cfg["port"],
        cfg["username"],
        cfg["password"],
        cfg["from_domain"],
    )

    if not replies:
        logger.info("No SIAU reply emails found")
        return 0

    processed = 0
    async with async_session_factory() as session:
        for reply in replies:
            notif_id = reply["notification_id"]
            notif = await email_notification_repo.find_by_id(session, notif_id)
            if not notif:
                logger.info("Notification %s not found — skipping", notif_id)
                continue

            if notif.reply_received:
                logger.info("Notification %s already replied — skipping", notif_id)
                continue

            reply_body = reply["body"]
            if len(reply_body) > 500:
                reply_body = reply_body[:500] + "..."

            # Add to trazabilidad
            await trazabilidad_repo.save(
                session,
                Trazabilidad(
                    pqrsdf_id=notif.pqrsdf_id,
                    accion="RESPUESTA_EMAIL",
                    descripcion=(
                        f"Respuesta recibida por email de {reply['from']}: {reply_body}"
                    ),
                    created_at=datetime.now(timezone.utc),
                ),
            )

            # Mark notification as replied
            await email_notification_repo.mark_reply_received(
                session, notif_id, reply["body"]
            )

            logger.info(
                "Reply processed: notif=%s pqrsdf=%s from=%s",
                notif_id, notif.pqrsdf_id, reply["from"],
            )
            processed += 1

    logger.info("IMAP poll complete — processed %d replies", processed)
    return processed
