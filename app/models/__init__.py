"""SQLAlchemy async models for all SIAU tables."""
from datetime import datetime, date
from sqlalchemy import Column, BigInteger, String, Text, Boolean, Date, TIMESTAMP, ForeignKey, Integer, Sequence
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Pqrsdf(Base):
    __tablename__ = "siau_pqrsdf"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    consecutivo = Column(String(30), unique=True, nullable=False)
    tipo = Column(String(2), nullable=False)
    fecha_radicado = Column(Date, nullable=False, default=date.today)
    hora_radicado = Column(String(10))

    nombres_usuario = Column(String(300), nullable=False)
    tipo_documento = Column(String(20))
    numero_documento = Column(String(30))
    telefono = Column(String(30))
    email = Column(String(200))
    direccion = Column(String(300))
    eps = Column(String(200))
    regimen = Column(String(50))

    medio_recepcion = Column(String(30), nullable=False)
    servicio_involucrado = Column(String(200))
    funcionario_involucrado = Column(String(200))
    descripcion = Column(Text, nullable=False)
    clasificacion = Column(String(100))

    estado = Column(String(20), nullable=False, default="RECIBIDO")
    fecha_respuesta = Column(Date)
    medio_respuesta = Column(String(30))
    respuesta_final = Column(Text)
    observaciones = Column(Text)

    created_at = Column(TIMESTAMP, default=datetime.now)
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    created_by = Column(BigInteger)
    updated_by = Column(BigInteger)
    acta_buzon_id = Column(BigInteger)

    trazabilidad = relationship("Trazabilidad", back_populates="pqrsdf_rel", cascade="all, delete-orphan")
    asignaciones = relationship("Asignacion", back_populates="pqrsdf_rel", cascade="all, delete-orphan")


class Departamento(Base):
    __tablename__ = "siau_departamentos"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text)
    responsable = Column(String(200))
    responsable_id = Column(BigInteger)
    activo = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.now)
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    asignaciones = relationship("Asignacion", back_populates="departamento_rel")


class Asignacion(Base):
    __tablename__ = "siau_asignaciones"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    pqrsdf_id = Column(BigInteger, ForeignKey("siau_pqrsdf.id"), nullable=False)
    departamento_id = Column(BigInteger, ForeignKey("siau_departamentos.id"), nullable=False)
    funcionario_id = Column(BigInteger)
    funcionario_nombre = Column(String(300))
    fecha_asignacion = Column(TIMESTAMP, default=datetime.now)
    fecha_limite_respuesta = Column(Date, nullable=False)
    estado = Column(String(20), nullable=False, default="PENDIENTE")
    respuesta_area = Column(Text)
    observaciones = Column(Text)
    fecha_respuesta_area = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default=datetime.now)
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    pqrsdf_rel = relationship("Pqrsdf", back_populates="asignaciones")
    departamento_rel = relationship("Departamento", back_populates="asignaciones")


class Trazabilidad(Base):
    __tablename__ = "siau_trazabilidad"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    pqrsdf_id = Column(BigInteger, ForeignKey("siau_pqrsdf.id"), nullable=False)
    accion = Column(String(100), nullable=False)
    descripcion = Column(Text)
    usuario_id = Column(BigInteger)
    usuario_nombre = Column(String(300))
    metadata_json = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.now)

    pqrsdf_rel = relationship("Pqrsdf", back_populates="trazabilidad")


class ActaBuzon(Base):
    __tablename__ = "siau_actas_buzon"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    fecha_apertura = Column(Date, nullable=False)
    ubicacion = Column(String(200), nullable=False)
    servicio = Column(String(200))
    total_pqrsdf = Column(Integer, default=0)
    detalle_por_tipo = Column(Text)
    observaciones = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.now)
    created_by = Column(BigInteger)
