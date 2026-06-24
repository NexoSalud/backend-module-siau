"""NexoSalud SIAU API — FastAPI application entrypoint."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.database import engine
from app.routers import (
    actas_buzon,
    asignaciones,
    catalogos,
    departamentos,
    email_inbound,
    pdf,
    pqrsdf,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Verify DB connectivity on startup, then dispose on shutdown."""
    async with engine.connect() as conn:
        await conn.run_sync(lambda _: None)
    yield
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
app.include_router(actas_buzon.router)
app.include_router(catalogos.router)
app.include_router(email_inbound.router)
app.include_router(pdf.router)


@app.get("/health")
async def health():
    """Basic health check endpoint."""
    return {"status": "ok"}
