"""Repositories for SIAU data access layer.

Each submodule exposes async functions (CRUD) as top-level symbols.
Import via `from app.repositories import acta_buzon_repo` and call like
`await acta_buzon_repo.save(session, entity)`.
"""

from app.repositories import (
    acta_buzon_repo,
    asignacion_repo,
    departamento_repo,
    pqrsdf_repo,
    trazabilidad_repo,
)

__all__ = [
    "acta_buzon_repo",
    "asignacion_repo",
    "departamento_repo",
    "pqrsdf_repo",
    "trazabilidad_repo",
]
