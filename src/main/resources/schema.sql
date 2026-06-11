-- ============================================================
-- SIAU - Sistema de Información y Atención al Usuario
-- Módulo: PQRSDF (Peticiones, Quejas, Reclamos, Sugerencias,
--         Denuncias y Felicitaciones)
-- ESE Norte 3 - NexoSalud
-- ============================================================

-- Departamentos / Áreas de la ESE
CREATE TABLE IF NOT EXISTS siau_departamentos (
    id BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    responsable VARCHAR(200),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Registro principal de PQRSDF
CREATE TABLE IF NOT EXISTS siau_pqrsdf (
    id BIGSERIAL PRIMARY KEY,
    consecutivo VARCHAR(30) UNIQUE NOT NULL,
    tipo VARCHAR(2) NOT NULL,
    fecha_radicado DATE NOT NULL DEFAULT CURRENT_DATE,
    hora_radicado VARCHAR(10),

    -- Datos del usuario/ciudadano
    nombres_usuario VARCHAR(300) NOT NULL,
    tipo_documento VARCHAR(20),
    numero_documento VARCHAR(30),
    telefono VARCHAR(30),
    email VARCHAR(200),
    direccion VARCHAR(300),
    eps VARCHAR(200),
    regimen VARCHAR(50),

    -- Detalle de la solicitud
    medio_recepcion VARCHAR(30) NOT NULL,
    servicio_involucrado VARCHAR(200),
    funcionario_involucrado VARCHAR(200),
    descripcion TEXT NOT NULL,
    clasificacion VARCHAR(100),

    -- Gestión y respuesta
    estado VARCHAR(20) NOT NULL DEFAULT 'RECIBIDO',
    fecha_respuesta DATE,
    medio_respuesta VARCHAR(30),
    respuesta_final TEXT,
    observaciones TEXT,

    -- Metadatos
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    updated_by BIGINT,

    -- Relación con acta de buzón (opcional)
    acta_buzon_id BIGINT
);

-- Asignaciones a departamentos/áreas
CREATE TABLE IF NOT EXISTS siau_asignaciones (
    id BIGSERIAL PRIMARY KEY,
    pqrsdf_id BIGINT NOT NULL REFERENCES siau_pqrsdf(id),
    departamento_id BIGINT NOT NULL REFERENCES siau_departamentos(id),
    funcionario_id BIGINT,
    funcionario_nombre VARCHAR(300),
    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_limite_respuesta DATE NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
    respuesta_area TEXT,
    observaciones TEXT,
    fecha_respuesta_area TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trazabilidad / Auditoría
CREATE TABLE IF NOT EXISTS siau_trazabilidad (
    id BIGSERIAL PRIMARY KEY,
    pqrsdf_id BIGINT NOT NULL REFERENCES siau_pqrsdf(id),
    accion VARCHAR(100) NOT NULL,
    descripcion TEXT,
    usuario_id BIGINT,
    usuario_nombre VARCHAR(300),
    metadata_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Actas de apertura de buzón
CREATE TABLE IF NOT EXISTS siau_actas_buzon (
    id BIGSERIAL PRIMARY KEY,
    fecha_apertura DATE NOT NULL,
    ubicacion VARCHAR(200) NOT NULL,
    servicio VARCHAR(200),
    total_pqrsdf INTEGER DEFAULT 0,
    detalle_por_tipo TEXT,
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT
);

-- Secuencia para consecutivos
CREATE SEQUENCE IF NOT EXISTS siau_consecutivo_seq START 1;

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_siau_pqrsdf_estado ON siau_pqrsdf(estado);
CREATE INDEX IF NOT EXISTS idx_siau_pqrsdf_tipo ON siau_pqrsdf(tipo);
CREATE INDEX IF NOT EXISTS idx_siau_pqrsdf_fecha ON siau_pqrsdf(fecha_radicado);
CREATE INDEX IF NOT EXISTS idx_siau_pqrsdf_documento ON siau_pqrsdf(numero_documento);
CREATE INDEX IF NOT EXISTS idx_siau_asignaciones_pqrsdf ON siau_asignaciones(pqrsdf_id);
CREATE INDEX IF NOT EXISTS idx_siau_asignaciones_depto ON siau_asignaciones(departamento_id);
CREATE INDEX IF NOT EXISTS idx_siau_asignaciones_estado ON siau_asignaciones(estado);
CREATE INDEX IF NOT EXISTS idx_siau_trazabilidad_pqrsdf ON siau_trazabilidad(pqrsdf_id);
CREATE INDEX IF NOT EXISTS idx_siau_trazabilidad_fecha ON siau_trazabilidad(created_at);
CREATE INDEX IF NOT EXISTS idx_siau_actas_buzon_fecha ON siau_actas_buzon(fecha_apertura);

-- ============================================================
-- Datos semilla: Departamentos típicos de una ESE
-- ============================================================
INSERT INTO siau_departamentos (nombre, descripcion, responsable, activo) VALUES
    ('SIAU', 'Sistema de Información y Atención al Usuario', NULL, TRUE),
    ('Facturación', 'Gestión de facturación y cartera', NULL, TRUE),
    ('Urgencias', 'Servicio de urgencias', NULL, TRUE),
    ('Consultas', 'Consultas médicas externas', NULL, TRUE),
    ('Hospitalización', 'Servicio de hospitalización', NULL, TRUE),
    ('Laboratorio', 'Servicio de laboratorio clínico', NULL, TRUE),
    ('Coordinación Médica', 'Coordinación de servicios médicos', NULL, TRUE),
    ('Administración', 'Dirección y administración general', NULL, TRUE),
    ('Odontología', 'Servicio odontológico', NULL, TRUE),
    ('Subgerencia Científica', 'Subgerencia científica y calidad', NULL, TRUE)
ON CONFLICT DO NOTHING;
