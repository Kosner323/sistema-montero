# -*- coding: utf-8 -*-
"""
Modelos SQLAlchemy para el Sistema Montero.
Define la estructura de la base de datos usando SQLAlchemy ORM.
"""
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    ForeignKey,
    Boolean,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Base declarativa de SQLAlchemy
Base = declarative_base()


# =============================================================================
# TABLA: Empresas
# =============================================================================
class Empresa(Base):
    """Modelo para la tabla empresas."""

    __tablename__ = "empresas"

    # Identificación
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_empresa = Column(String, nullable=False)
    tipo_identificacion_empresa = Column(String)
    nit = Column(String, nullable=False, unique=True)

    # Información de contacto
    direccion_empresa = Column(String)
    telefono_empresa = Column(String)
    correo_empresa = Column(String)
    departamento_empresa = Column(String)
    ciudad_empresa = Column(String)

    # Información financiera/laboral
    ibc_empresa = Column(Float)
    afp_empresa = Column(String)
    arl_empresa = Column(String)

    # Representante legal
    rep_legal_nombre = Column(String)
    rep_legal_tipo_id = Column(String)
    rep_legal_numero_id = Column(String)

    # Estado
    estado = Column(String, default="Activo")

    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    usuarios = relationship("Usuario", back_populates="empresa")

    def __repr__(self):
        return f"<Empresa {self.nombre_empresa} (NIT: {self.nit})>"


# =============================================================================
# TABLA: Usuarios (Empleados)
# =============================================================================
class Usuario(Base):
    """Modelo para la tabla usuarios."""

    __tablename__ = "usuarios"

    # Identificación
    id = Column(Integer, primary_key=True, autoincrement=True)
    empresa_nit = Column(String, ForeignKey("empresas.nit"), nullable=False)
    tipoId = Column(String, nullable=False)
    numeroId = Column(String, nullable=False)

    # Información personal
    primerNombre = Column(String, nullable=False)
    segundoNombre = Column(String)
    primerApellido = Column(String, nullable=False)
    segundoApellido = Column(String)
    sexoBiologico = Column(String)
    sexoIdentificacion = Column(String)
    nacionalidad = Column(String)

    # Información de nacimiento
    fechaNacimiento = Column(String)
    paisNacimiento = Column(String)
    departamentoNacimiento = Column(String)
    municipioNacimiento = Column(String)

    # Información de contacto
    direccion = Column(String)
    telefonoCelular = Column(String)
    telefonoFijo = Column(String)
    correoElectronico = Column(String)
    comunaBarrio = Column(String)

    # Información de seguridad social
    afpNombre = Column(String)
    afpCosto = Column(Float, default=0)
    epsNombre = Column(String)
    epsCosto = Column(Float, default=0)
    arlNombre = Column(String)
    arlCosto = Column(Float, default=0)
    ccfNombre = Column(String)
    ccfCosto = Column(Float, default=0)

    # Información laboral
    administracion = Column(String)
    ibc = Column(Float)
    claseRiesgoARL = Column(String)
    fechaIngreso = Column(String)
    tiempoServicio = Column(String)
    cargo = Column(String)
    salarioMensual = Column(Float)
    aux_transporte = Column(Float, default=0)
    bonificacion_mensual = Column(Float, default=0)
    aux_alimentacion = Column(Float, default=0)
    aux_rodamiento = Column(Float, default=0)

    # Información adicional
    estado_civil = Column(String)
    nivel_estudios = Column(String)
    es_cabeza_familia = Column(String)
    contacto_emergencia_nombre = Column(String)
    contacto_emergencia_telefono = Column(String)
    contacto_emergencia_parentesco = Column(String)

    # Autenticación y roles
    password_hash = Column(String)
    role = Column(String, default="empleado")
    estado = Column(String, default="activo")

    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    empresa = relationship("Empresa", back_populates="usuarios")
    pagos = relationship("Pago", back_populates="usuario")
    tutelas = relationship("Tutela", back_populates="usuario")
    incapacidades = relationship("Incapacidad", back_populates="usuario")

    def __repr__(self):
        return f"<Usuario {self.primerNombre} {self.primerApellido} ({self.numeroId})>"


# =============================================================================
# TABLA: Pagos
# =============================================================================
class Pago(Base):
    """Modelo para la tabla pagos."""

    __tablename__ = "pagos"

    # Identificación
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    # Información del pago
    periodo = Column(String, nullable=False)  # Ej: "2025-01"
    fecha_pago = Column(String)
    tipo_pago = Column(String)  # nomina, prima, cesantias, etc.

    # Montos
    salario_base = Column(Float, default=0)
    aux_transporte = Column(Float, default=0)
    bonificaciones = Column(Float, default=0)
    horas_extras = Column(Float, default=0)
    comisiones = Column(Float, default=0)
    total_devengado = Column(Float, default=0)

    # Deducciones
    salud = Column(Float, default=0)
    pension = Column(Float, default=0)
    fondo_solidaridad = Column(Float, default=0)
    retencion_fuente = Column(Float, default=0)
    otras_deducciones = Column(Float, default=0)
    total_deducciones = Column(Float, default=0)

    # Neto
    neto_pagar = Column(Float, default=0)

    # Estado
    estado = Column(String, default="pendiente")  # pendiente, pagado, anulado
    metodo_pago = Column(String)  # efectivo, transferencia, cheque
    comprobante = Column(String)  # Referencia o número de comprobante

    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    usuario = relationship("Usuario", back_populates="pagos")

    def __repr__(self):
        return f"<Pago {self.periodo} - Usuario {self.usuario_id} - ${self.neto_pagar}>"


# =============================================================================
# TABLA: Tutelas
# =============================================================================
class Tutela(Base):
    """Modelo para la tabla tutelas."""

    __tablename__ = "tutelas"

    # Identificación
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    # Información de la tutela
    numero_tutela = Column(String, unique=True)
    juzgado = Column(String)
    fecha_notificacion = Column(String)
    fecha_inicio = Column(String)
    fecha_fin = Column(String)

    # Detalle del descuento
    valor_total = Column(Float, default=0)
    valor_cuota = Column(Float, default=0)
    numero_cuotas = Column(Integer, default=0)
    cuotas_pagadas = Column(Integer, default=0)
    saldo_pendiente = Column(Float, default=0)

    # Estado
    estado = Column(String, default="activa")  # activa, finalizada, suspendida
    observaciones = Column(Text)

    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    usuario = relationship("Usuario", back_populates="tutelas")

    def __repr__(self):
        return f"<Tutela {self.numero_tutela} - Usuario {self.usuario_id}>"


# =============================================================================
# TABLA: Cotizaciones
# =============================================================================
class Cotizacion(Base):
    """Modelo para la tabla cotizaciones."""

    __tablename__ = "cotizaciones"

    # Identificación
    id = Column(Integer, primary_key=True, autoincrement=True)
    empresa_nit = Column(String, ForeignKey("empresas.nit"))

    # Información de la cotización
    periodo = Column(String, nullable=False)
    tipo_cotizacion = Column(String)  # salud, pension, arl, ccf, etc.

    # Montos
    base_cotizacion = Column(Float, default=0)
    porcentaje = Column(Float, default=0)
    valor_empresa = Column(Float, default=0)
    valor_empleado = Column(Float, default=0)
    total = Column(Float, default=0)

    # Estado
    estado = Column(String, default="pendiente")  # pendiente, pagado, vencido
    fecha_pago = Column(String)
    comprobante = Column(String)

    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Cotizacion {self.tipo_cotizacion} {self.periodo} - ${self.total}>"


# =============================================================================
# TABLA: Incapacidades
# =============================================================================
class Incapacidad(Base):
    """Modelo para la tabla incapacidades."""

    __tablename__ = "incapacidades"

    # Identificación
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    # Información de la incapacidad
    numero_incapacidad = Column(String)
    tipo_incapacidad = Column(String)  # enfermedad_general, laboral, maternidad, etc.
    diagnostico = Column(Text)

    # Fechas
    fecha_inicio = Column(String, nullable=False)
    fecha_fin = Column(String)
    dias_incapacidad = Column(Integer, default=0)

    # Información financiera
    ibc_incapacidad = Column(Float, default=0)
    porcentaje_pago = Column(Float, default=0)  # 66.67%, 100%, etc.
    valor_dia = Column(Float, default=0)
    valor_total = Column(Float, default=0)

    # Responsable del pago
    paga_empresa = Column(Boolean, default=False)
    paga_eps = Column(Boolean, default=False)
    paga_arl = Column(Boolean, default=False)

    # Estado
    estado = Column(String, default="activa")  # activa, finalizada, rechazada
    documento_soporte = Column(String)  # Path al documento escaneado
    observaciones = Column(Text)

    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    usuario = relationship("Usuario", back_populates="incapacidades")

    def __repr__(self):
        return f"<Incapacidad {self.tipo_incapacidad} - Usuario {self.usuario_id} - {self.dias_incapacidad} días>"


# =============================================================================
# TABLA: Notificaciones
# =============================================================================
class Notificacion(Base):
    """Modelo para la tabla notificaciones."""

    __tablename__ = "notificaciones"

    # Identificación
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))

    # Contenido
    titulo = Column(String, nullable=False)
    mensaje = Column(Text, nullable=False)
    tipo = Column(String, default="info")  # info, warning, error, success
    categoria = Column(String)  # pago, tutela, incapacidad, sistema, etc.

    # Estado
    leida = Column(Boolean, default=False)
    fecha_lectura = Column(DateTime)

    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Notificacion {self.titulo} - Usuario {self.usuario_id}>"


# =============================================================================
# Función de ayuda para crear engine y session
# =============================================================================
def get_engine(database_url="sqlite:///data/mi_sistema.db"):
    """Crea y retorna un engine de SQLAlchemy."""
    return create_engine(database_url, echo=False)


def get_session(engine):
    """Crea y retorna una sesión de SQLAlchemy."""
    Session = sessionmaker(bind=engine)
    return Session()


def init_db(database_url="sqlite:///data/mi_sistema.db"):
    """Inicializa la base de datos creando todas las tablas."""
    engine = get_engine(database_url)
    Base.metadata.create_all(engine)
    return engine
