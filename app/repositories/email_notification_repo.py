"""Repository for EmailNotification model — CRUD + lookup by notification ID."""
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import EmailNotification


async def save(session: AsyncSession, entity: EmailNotification) -> EmailNotification:
    session.add(entity)
    await session.flush()
    await session.refresh(entity)
    return entity


async def find_by_id(session: AsyncSession, notif_id: str) -> EmailNotification | None:
    result = await session.execute(
        select(EmailNotification).where(EmailNotification.id == notif_id)
    )
    return result.scalar_one_or_none()


async def mark_reply_received(
    session: AsyncSession,
    notif_id: str,
    reply_body: str,
) -> bool:
    """Marks a notification as having received a reply."""
    from datetime import datetime, timezone
    result = await session.execute(
        update(EmailNotification)
        .where(EmailNotification.id == notif_id)
        .values(reply_received=True, reply_body=reply_body, replied_at=datetime.now(timezone.utc))
    )
    await session.commit()
    return result.rowcount > 0
