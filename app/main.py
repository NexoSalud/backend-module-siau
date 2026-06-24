"""NexoSalud SIAU API — FastAPI application entrypoint."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.database import engine

logger = logging.getLogger(__name__)
from app.routers import (
    actas_buzon,
    asignaciones,
    catalogos,
    departamentos,
    email_inbound,
    external,
    pdf,
    pqrsdf,
)


import asyncio

from app.services import imap_poller


_POLL_INTERVAL_SECONDS = 3600  # 1 hour


async def _imap_polling_loop():
    """Background task that polls IMAP for email replies every hour."""
    # Wait a bit on startup to let the app initialize fully
    await asyncio.sleep(30)
    while True:
        try:
            await imap_poller.poll_replies()
        except Exception as e:
            logger.exception("IMAP polling error: %s", e)
        await asyncio.sleep(_POLL_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Verify DB connectivity on startup, start IMAP poller, dispose on shutdown."""
    async with engine.connect() as conn:
        await conn.run_sync(lambda _: None)

    poll_task = asyncio.create_task(_imap_polling_loop())

    yield

    poll_task.cancel()
    try:
        await poll_task
    except asyncio.CancelledError:
        pass
    await engine.dispose()


app = FastAPI(
    title="NexoSalud SIAU API",
    version="0.1.0",
    lifespan=lifespan,
)

# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(pqrsdf.router)
app.include_router(departamentos.router)
app.include_router(asignaciones.router)
app.include_router(external.router)
app.include_router(actas_buzon.router)
app.include_router(catalogos.router)
app.include_router(email_inbound.router)
app.include_router(pdf.router)


@app.get("/health")
async def health():
    """Basic health check endpoint."""
    return {"status": "ok"}
