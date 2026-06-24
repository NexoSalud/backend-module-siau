"""Catálogos estáticos del sistema SIAU (PQRSDF)."""

TIPOS_PQRSDF = [
    {"codigo": "P", "nombre": "Petición", "descripcion": "Solicitud de información o documentos"},
    {"codigo": "Q", "nombre": "Queja", "descripcion": "Inconformidad por mala prestación del servicio"},
    {"codigo": "R", "nombre": "Reclamo", "descripcion": "Exigencia por incumplimiento de obligaciones"},
    {"codigo": "S", "nombre": "Sugerencia", "descripcion": "Propuesta para mejorar el servicio"},
    {"codigo": "D", "nombre": "Denuncia", "descripcion": "Informe sobre hechos presuntamente irregulares"},
    {"codigo": "F", "nombre": "Felicitación", "descripcion": "Reconocimiento por buen servicio"},
]

MEDIOS_RECEPCION = [
    {"codigo": "BUZON", "nombre": "Buzón de sugerencias"},
    {"codigo": "OFICIO", "nombre": "Oficio escrito"},
    {"codigo": "EMAIL", "nombre": "Correo electrónico"},
    {"codigo": "WEB", "nombre": "Página web"},
    {"codigo": "PRESENCIAL", "nombre": "Presencial / Ventanilla"},
    {"codigo": "TELEFONO", "nombre": "Teléfono"},
    {"codigo": "RADICADO", "nombre": "Radicado físico"},
]

CLASIFICACIONES = [
    {"codigo": "01", "nombre": "Acceso a servicios de salud"},
    {"codigo": "02", "nombre": "Calidad e idoneidad profesional"},
    {"codigo": "03", "nombre": "Oportunidad en la prestación"},
    {"codigo": "04", "nombre": "Información al usuario"},
    {"codigo": "05", "nombre": "Facturación y aspectos financieros"},
    {"codigo": "06", "nombre": "Negación del servicio"},
    {"codigo": "07", "nombre": "Discriminación"},
    {"codigo": "08", "nombre": "Trato digno y respeto"},
    {"codigo": "09", "nombre": "Confidencialidad de la información"},
    {"codigo": "10", "nombre": "Seguridad del paciente"},
    {"codigo": "11", "nombre": "Continuidad del servicio"},
    {"codigo": "12", "nombre": "Otros motivos"},
]

PLAZOS_RESPUESTA = [
    {"tipo": "P", "diasHabiles": 15, "descripcion": "Petición - 15 días hábiles"},
    {"tipo": "Q", "diasHabiles": 15, "descripcion": "Queja - 15 días hábiles"},
    {"tipo": "R", "diasHabiles": 15, "descripcion": "Reclamo - 15 días hábiles"},
    {"tipo": "S", "diasHabiles": 15, "descripcion": "Sugerencia - 15 días hábiles"},
    {"tipo": "D", "diasHabiles": 15, "descripcion": "Denuncia - 15 días hábiles"},
    {"tipo": "F", "diasHabiles": 15, "descripcion": "Felicitación - 15 días hábiles"},
]

ESTADOS_PQRSDF = [
    {"codigo": "RECIBIDO", "nombre": "Recibido"},
    {"codigo": "ASIGNADO", "nombre": "Asignado"},
    {"codigo": "EN_GESTION", "nombre": "En gestión"},
    {"codigo": "RESPONDIDO", "nombre": "Respondido"},
    {"codigo": "CERRADO", "nombre": "Cerrado"},
]

ESTADOS_ASIGNACION = [
    {"codigo": "PENDIENTE", "nombre": "Pendiente"},
    {"codigo": "EN_PROCESO", "nombre": "En proceso"},
    {"codigo": "RESPONDIDA", "nombre": "Respondida"},
    {"codigo": "VENCIDA", "nombre": "Vencida"},
]


def get_tipos_pqrsdf() -> list[dict]:
    """Retorna los 6 tipos de PQRSDF."""
    return TIPOS_PQRSDF


def get_medios_recepcion() -> list[dict]:
    """Retorna los medios de recepción disponibles."""
    return MEDIOS_RECEPCION


def get_clasificaciones() -> list[dict]:
    """Retorna las 12 clasificaciones definidas por Supersalud."""
    return CLASIFICACIONES


def get_plazos_respuesta() -> list[dict]:
    """Retorna los plazos legales de respuesta por tipo."""
    return PLAZOS_RESPUESTA


def get_estados_pqrsdf() -> list[dict]:
    """Retorna los estados posibles de una PQRSDF."""
    return ESTADOS_PQRSDF


def get_estados_asignacion() -> list[dict]:
    """Retorna los estados posibles de una asignación."""
    return ESTADOS_ASIGNACION


def get_tipo_nombre(codigo: str) -> str | None:
    """Obtiene el nombre del tipo PQRSDF a partir de su código."""
    for t in TIPOS_PQRSDF:
        if t["codigo"] == codigo:
            return t["nombre"]
    return None


def get_plazo_por_tipo(tipo: str) -> int:
    """Obtiene el plazo en días hábiles para un tipo de PQRSDF."""
    for p in PLAZOS_RESPUESTA:
        if p["tipo"] == tipo:
            return p["diasHabiles"]
    return 15
