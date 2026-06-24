"""Router: Catálogos (hardcoded enum data)."""
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/siau/catalogos", tags=["Catálogos"])

# ── Tipos de PQRSDF ──────────────────────────────────────────────────────────

TIPOS_PQRSDF = [
    {"codigo": "PQ", "nombre": "Petición", "plazoHoras": 168},
    {"codigo": "QC", "nombre": "Queja", "plazoHoras": 168},
    {"codigo": "RS", "nombre": "Reclamo", "plazoHoras": 168},
    {"codigo": "SG", "nombre": "Sugerencia", "plazoHoras": 168},
    {"codigo": "DF", "nombre": "Denuncia", "plazoHoras": 168},
    {"codigo": "FL", "nombre": "Felicitación", "plazoHoras": 168},
]

MEDIOS_RECEPCION = [
    {"codigo": "WEB", "nombre": "Portal Web"},
    {"codigo": "CORREO", "nombre": "Correo Electrónico"},
    {"codigo": "FISICO", "nombre": "Oficio Físico"},
    {"codigo": "TELEFONO", "nombre": "Telefónico"},
    {"codigo": "PRESENCIAL", "nombre": "Presencial / Ventanilla"},
    {"codigo": "BUZON", "nombre": "Buzón de Sugerencias"},
    {"codigo": "REDES", "nombre": "Redes Sociales"},
]

CLASIFICACIONES = [
    {"codigo": "INFORMACION", "nombre": "Solicitud de Información"},
    {"codigo": "ORIENTACION", "nombre": "Orientación al Usuario"},
    {"codigo": "TRAMITE", "nombre": "Solicitud de Trámite"},
    {"codigo": "INCONFORMIDAD", "nombre": "Inconformidad con el Servicio"},
    {"codigo": "INCUMPLIMIENTO", "nombre": "Incumplimiento de Cita/Procedimiento"},
    {"codigo": "ACCESO", "nombre": "Barreras de Acceso"},
    {"codigo": "CALIDAD", "nombre": "Calidad en la Atención"},
    {"codigo": "OTRO", "nombre": "Otro"},
]

PLAZOS_RESPUESTA = [
    {"codigo": "INMEDIATO", "nombre": "Inmediato", "dias": 0},
    {"codigo": "5_DIAS", "nombre": "5 Días Hábiles", "dias": 5},
    {"codigo": "10_DIAS", "nombre": "10 Días Hábiles", "dias": 10},
    {"codigo": "15_DIAS", "nombre": "15 Días Hábiles", "dias": 15},
    {"codigo": "30_DIAS", "nombre": "30 Días Calendario", "dias": 30},
]


@router.get("/tipos-pqrsdf")
async def get_tipos():
    """List available PQRSDF types."""
    return TIPOS_PQRSDF


@router.get("/medios-recepcion")
async def get_medios():
    """List available reception means."""
    return MEDIOS_RECEPCION


@router.get("/clasificaciones")
async def get_clasificaciones():
    """List available classifications."""
    return CLASIFICACIONES


@router.get("/plazos-respuesta")
async def get_plazos():
    """List available response deadlines."""
    return PLAZOS_RESPUESTA
