"""Pydantic schemas for SIAU request/response serialization."""
from datetime import date, datetime
from typing import Any
from pydantic import BaseModel


class ApiResponse(BaseModel):
    success: bool = True
    message: str = ""
    data: Any = None


# === PQRSDF ===

class CreatePqrsdfRequest(BaseModel):
    tipo: str
    nombresUsuario: str
    tipoDocumento: str | None = None
    numeroDocumento: str | None = None
    telefono: str | None = None
    email: str | None = None
    direccion: str | None = None
    eps: str | None = None
    regimen: str | None = None
    medioRecepcion: str
    servicioInvolucrado: str | None = None
    funcionarioInvolucrado: str | None = None
    descripcion: str
    clasificacion: str | None = None
    horaRadicado: str | None = None
    fechaRadicado: date | None = None
    createdBy: int | None = None
    actaBuzonId: int | None = None


class UpdatePqrsdfRequest(BaseModel):
    clasificacion: str | None = None
    observaciones: str | None = None
    updatedBy: int | None = None


class ResponderPqrsdfRequest(BaseModel):
    respuestaFinal: str
    medioRespuesta: str
    clasificacion: str | None = None
    updatedBy: int | None = None


class PqrsdfResponse(BaseModel):
    id: int
    consecutivo: str
    tipo: str
    tipoNombre: str | None = None
    fechaRadicado: date | None = None
    horaRadicado: str | None = None
    nombresUsuario: str | None = None
    tipoDocumento: str | None = None
    numeroDocumento: str | None = None
    telefono: str | None = None
    email: str | None = None
    direccion: str | None = None
    eps: str | None = None
    regimen: str | None = None
    medioRecepcion: str | None = None
    servicioInvolucrado: str | None = None
    funcionarioInvolucrado: str | None = None
    descripcion: str | None = None
    clasificacion: str | None = None
    estado: str | None = None
    fechaRespuesta: date | None = None
    medioRespuesta: str | None = None
    respuestaFinal: str | None = None
    observaciones: str | None = None
    createdAt: datetime | None = None
    updatedAt: datetime | None = None
    createdBy: int | None = None
    updatedBy: int | None = None
    ultimoDepartamentoAsignado: str | None = None
    ultimoEstadoAsignacion: str | None = None
    diasTranscurridos: int = 0

    class Config:
        from_attributes = True


class TrazabilidadResponse(BaseModel):
    id: int
    pqrsdfId: int
    accion: str
    descripcion: str | None = None
    usuarioId: int | None = None
    usuarioNombre: str | None = None
    metadataJson: str | None = None
    createdAt: datetime | None = None


class PagedResponse(BaseModel):
    content: list = []
    page: int = 0
    size: int = 10
    totalElements: int = 0
    totalPages: int = 0
    last: bool = True


# === DEPARTAMENTOS ===

class CreateDepartamentoRequest(BaseModel):
    nombre: str
    descripcion: str | None = None
    responsable: str | None = None
    responsableId: int | None = None
    email: str | None = None


class DepartamentoResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str | None = None
    responsable: str | None = None
    responsableId: int | None = None
    email: str | None = None
    activo: bool = True
    createdAt: datetime | None = None
    updatedAt: datetime | None = None
    pqrsdfPendientes: int = 0

    class Config:
        from_attributes = True


# === ASIGNACIONES ===

class CreateAsignacionRequest(BaseModel):
    pqrsdfId: int
    departamentoId: int
    funcionarioId: int | None = None
    funcionarioNombre: str | None = None
    fechaLimiteRespuesta: date | None = None
    observaciones: str | None = None


class AsignacionResponse(BaseModel):
    id: int
    pqrsdfId: int
    pqrsdfConsecutivo: str | None = None
    departamentoId: int
    departamentoNombre: str | None = None
    funcionarioId: int | None = None
    funcionarioNombre: str | None = None
    fechaAsignacion: datetime | None = None
    fechaLimiteRespuesta: date | None = None
    estado: str | None = None
    respuestaArea: str | None = None
    observaciones: str | None = None
    fechaRespuestaArea: datetime | None = None
    createdAt: datetime | None = None
    vencida: bool = False
    diasRestantes: int = 0

    class Config:
        from_attributes = True


# === ACTAS BUZON ===

class ActaBuzonRequest(BaseModel):
    fechaApertura: date
    ubicacion: str
    servicio: str | None = None
    totalPqrsdf: int = 0
    detallePorTipo: str | None = None
    observaciones: str | None = None
    createdBy: int | None = None


class ActaBuzonResponse(BaseModel):
    id: int
    fechaApertura: date | None = None
    ubicacion: str | None = None
    servicio: str | None = None
    totalPqrsdf: int = 0
    detallePorTipo: str | None = None
    observaciones: str | None = None
    createdAt: datetime | None = None
    createdBy: int | None = None

    class Config:
        from_attributes = True


# === DASHBOARD ===

class DashboardStatsResponse(BaseModel):
    totalPqrsdf: int = 0
    pendientes: int = 0
    enGestion: int = 0
    respondidas: int = 0
    cerradas: int = 0
    vencidas: int = 0
    porTipo: dict[str, int] = {}
    porDepartamento: dict[str, int] = {}
    ultimos30Dias: dict[str, int] = {}


# === PDF ===

class PdfResumenRequest(BaseModel):
    pqrsdf_id: int
    incluir_trazabilidad: bool = True
    incluir_asignaciones: bool = True
