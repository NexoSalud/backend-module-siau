"""Repositories for SIAU data access layer.

Each module exposes singleton instances:
- pqrsdf_repo: PqrsdfRepository
- departamento_repo: DepartamentoRepository
- asignacion_repo: AsignacionRepository
- trazabilidad_repo: TrazabilidadRepository
- acta_buzon_repo: ActaBuzonRepository
"""

from app.repositories.pqrsdf_repo import PqrsdfRepository
from app.repositories.departamento_repo import DepartamentoRepository
from app.repositories.asignacion_repo import AsignacionRepository
from app.repositories.trazabilidad_repo import TrazabilidadRepository
from app.repositories.acta_buzon_repo import ActaBuzonRepository

pqrsdf_repo = PqrsdfRepository()
departamento_repo = DepartamentoRepository()
asignacion_repo = AsignacionRepository()
trazabilidad_repo = TrazabilidadRepository()
acta_buzon_repo = ActaBuzonRepository()

__all__ = [
    "pqrsdf_repo",
    "departamento_repo",
    "asignacion_repo",
    "trazabilidad_repo",
    "acta_buzon_repo",
]
