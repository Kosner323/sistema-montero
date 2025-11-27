# -*- coding: utf-8 -*-
"""
Modelos ORM SQLAlchemy para el Sistema Montero - REFACTORIZADO
================================================================
Basado exactamente en database_schema_COMPLETO.py
Objetivo: Eliminar SQL manual y usar SQLAlchemy ORM al 100%

Autor: Ingeniero Backend Senior
Fecha: 2025-11-26
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, Index
from sqlalchemy.orm import relationship

# Importar db desde extensions para evitar instancias duplicadas
from extensions import db


# =============================================================================
# MÓDULO: GESTIÓN DE EMPRESAS
# =============================================================================

class Empresa(db.Model):
    """
    Modelo ORM para la tabla 'empresas'
    Almacena información de empresas cliente con información legal y de contacto
    """
    __tablename__ = 'empresas'

    # Identificación
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_empresa = Column(Text, nullable=True)
    tipo_identificacion_empresa = Column(Text, nullable=True)
    nit = Column(Text, nullable=True, unique=True)  # ✅ UNIQUE constraint

    # Información de contacto
    direccion_empresa = Column(Text, nullable=True)
    telefono_empresa = Column(Text, nullable=True)
    correo_empresa = Column(Text, nullable=True)
    departamento_empresa = Column(Text, nullable=True)
    ciudad_empresa = Column(Text, nullable=True)

    # Información financiera/laboral
    ibc_empresa = Column(Float, nullable=True)
    afp_empresa = Column(Text, nullable=True)
    arl_empresa = Column(Text, nullable=True)

    # Representante legal
    rep_legal_nombre = Column(Text, nullable=True)
    rep_legal_tipo_id = Column(Text, nullable=True)
    rep_legal_numero_id = Column(Text, nullable=True)

    # Auditoría
    created_at = Column(Text, nullable=True, default=datetime.utcnow)

    # Relaciones (1:N)
    usuarios = relationship('Usuario', back_populates='empresa', lazy='dynamic')
    incapacidades = relationship('Incapacidad', back_populates='empresa', lazy='dynamic')
    # tutelas: Relación eliminada - tabla tutelas no tiene empresa_nit en la BD real
    pago_impuestos = relationship('PagoImpuesto', back_populates='empresa', lazy='dynamic')
    envios_planillas = relationship('EnvioPlanilla', back_populates='empresa', lazy='dynamic')
    credenciales = relationship('CredencialPlataforma', back_populates='empresa', lazy='dynamic')

    def __repr__(self):
        return f"<Empresa {self.nombre_empresa} NIT:{self.nit}>"

    def to_dict(self):
        """Convierte el objeto a diccionario para JSON"""
        return {
            'id': self.id,
            'nombre_empresa': self.nombre_empresa,
            'tipo_identificacion_empresa': self.tipo_identificacion_empresa,
            'nit': self.nit,
            'direccion_empresa': self.direccion_empresa,
            'telefono_empresa': self.telefono_empresa,
            'correo_empresa': self.correo_empresa,
            'departamento_empresa': self.departamento_empresa,
            'ciudad_empresa': self.ciudad_empresa,
            'ibc_empresa': self.ibc_empresa,
            'afp_empresa': self.afp_empresa,
            'arl_empresa': self.arl_empresa,
            'rep_legal_nombre': self.rep_legal_nombre,
            'rep_legal_tipo_id': self.rep_legal_tipo_id,
            'rep_legal_numero_id': self.rep_legal_numero_id,
            'created_at': self.created_at
        }


class Usuario(db.Model):
    """
    Modelo ORM para la tabla 'usuarios'
    Registro de empleados con información personal, laboral y de seguridad social
    """
    __tablename__ = 'usuarios'

    # Identificación
    id = Column(Integer, primary_key=True, autoincrement=True)
    empresa_nit = Column(Text, ForeignKey('empresas.nit'), nullable=True)
    tipoId = Column(Text, nullable=True)
    numeroId = Column(Text, nullable=True)

    # Información personal
    primerNombre = Column(Text, nullable=True)
    segundoNombre = Column(Text, nullable=True)
    primerApellido = Column(Text, nullable=True)
    segundoApellido = Column(Text, nullable=True)
    sexoBiologico = Column(Text, nullable=True)
    sexoIdentificacion = Column(Text, nullable=True)
    nacionalidad = Column(Text, nullable=True)

    # Información de nacimiento
    fechaNacimiento = Column(Text, nullable=True)
    paisNacimiento = Column(Text, nullable=True)
    departamentoNacimiento = Column(Text, nullable=True)
    municipioNacimiento = Column(Text, nullable=True)

    # Información de contacto
    direccion = Column(Text, nullable=True)
    telefonoCelular = Column(Text, nullable=True)
    telefonoFijo = Column(Text, nullable=True)
    correoElectronico = Column(Text, nullable=True)
    comunaBarrio = Column(Text, nullable=True)

    # Información de seguridad social
    afpNombre = Column(Text, nullable=True)
    afpCosto = Column(Float, nullable=True)
    epsNombre = Column(Text, nullable=True)
    epsCosto = Column(Float, nullable=True)
    arlNombre = Column(Text, nullable=True)
    arlCosto = Column(Float, nullable=True)
    ccfNombre = Column(Text, nullable=True)
    ccfCosto = Column(Float, nullable=True)

    # Información laboral
    administracion = Column(Text, nullable=True)
    ibc = Column(Float, nullable=True)
    claseRiesgoARL = Column(Text, nullable=True)
    fechaIngreso = Column(Text, nullable=True)

    # Auditoría
    created_at = Column(Text, nullable=True, default=datetime.utcnow)

    # Relaciones
    empresa = relationship('Empresa', back_populates='usuarios')

    # Índices (se definen al final con __table_args__)
    __table_args__ = (
        Index('sqlite_autoindex_usuarios_1', 'tipoId', 'numeroId', unique=True),
    )

    def __repr__(self):
        return f"<Usuario {self.primerNombre} {self.primerApellido} ({self.numeroId})>"

    def to_dict(self):
        """Convierte el objeto a diccionario para JSON"""
        return {
            'id': self.id,
            'empresa_nit': self.empresa_nit,
            'tipoId': self.tipoId,
            'numeroId': self.numeroId,
            'primerNombre': self.primerNombre,
            'segundoNombre': self.segundoNombre,
            'primerApellido': self.primerApellido,
            'segundoApellido': self.segundoApellido,
            'sexoBiologico': self.sexoBiologico,
            'sexoIdentificacion': self.sexoIdentificacion,
            'nacionalidad': self.nacionalidad,
            'fechaNacimiento': self.fechaNacimiento,
            'paisNacimiento': self.paisNacimiento,
            'departamentoNacimiento': self.departamentoNacimiento,
            'municipioNacimiento': self.municipioNacimiento,
            'direccion': self.direccion,
            'telefonoCelular': self.telefonoCelular,
            'telefonoFijo': self.telefonoFijo,
            'correoElectronico': self.correoElectronico,
            'comunaBarrio': self.comunaBarrio,
            'afpNombre': self.afpNombre,
            'afpCosto': self.afpCosto,
            'epsNombre': self.epsNombre,
            'epsCosto': self.epsCosto,
            'arlNombre': self.arlNombre,
            'arlCosto': self.arlCosto,
            'ccfNombre': self.ccfNombre,
            'ccfCosto': self.ccfCosto,
            'administracion': self.administracion,
            'ibc': self.ibc,
            'claseRiesgoARL': self.claseRiesgoARL,
            'fechaIngreso': self.fechaIngreso,
            'created_at': self.created_at
        }


# =============================================================================
# MÓDULO: AUTENTICACIÓN
# =============================================================================

class PortalUser(db.Model):
    """
    Modelo ORM para la tabla 'portal_users'
    Usuarios del sistema con autenticación web (hashing de contraseñas)
    """
    __tablename__ = 'portal_users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    created_at = Column(Text, nullable=True, default=datetime.utcnow)

    def __repr__(self):
        return f"<PortalUser {self.nombre} ({self.email})>"

    def to_dict(self):
        """Convierte el objeto a diccionario para JSON (sin password_hash)"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'created_at': self.created_at
        }


# =============================================================================
# MÓDULO: GESTIÓN LABORAL
# =============================================================================

class Incapacidad(db.Model):
    """
    Modelo ORM para la tabla 'incapacidades'
    Registro y seguimiento de incapacidades médicas de empleados
    """
    __tablename__ = 'incapacidades'

    id = Column(Integer, primary_key=True, autoincrement=True)
    empresa_nit = Column(Text, ForeignKey('empresas.nit'), nullable=False)
    usuario_id = Column(Text, nullable=False)
    diagnostico = Column(Text, nullable=False)
    fecha_inicio = Column(Text, nullable=False)
    fecha_fin = Column(Text, nullable=False)
    estado = Column(Text, nullable=True, default='En Proceso')
    archivos_info = Column(Text, nullable=True)  # JSON
    created_at = Column(Text, nullable=True, default=datetime.utcnow)

    # Relaciones
    empresa = relationship('Empresa', back_populates='incapacidades')

    def __repr__(self):
        return f"<Incapacidad {self.diagnostico} - Usuario {self.usuario_id}>"

    def to_dict(self):
        return {
            'id': self.id,
            'empresa_nit': self.empresa_nit,
            'usuario_id': self.usuario_id,
            'diagnostico': self.diagnostico,
            'fecha_inicio': self.fecha_inicio,
            'fecha_fin': self.fecha_fin,
            'estado': self.estado,
            'archivos_info': self.archivos_info,
            'created_at': self.created_at
        }


class Tutela(db.Model):
    """
    Modelo ORM para la tabla 'tutelas'
    Registro y seguimiento de tutelas laborales
    ACTUALIZADO para reflejar la estructura real de la tabla en la base de datos
    """
    __tablename__ = 'tutelas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, nullable=False)  # ID del empleado/usuario afectado
    numero_tutela = Column(String, nullable=True)  # Número de radicado de la tutela
    juzgado = Column(String, nullable=True)  # Juzgado que tramita la tutela
    fecha_notificacion = Column(String, nullable=True)
    fecha_inicio = Column(String, nullable=True)
    fecha_fin = Column(String, nullable=True)  # Fecha de vencimiento de la tutela
    valor_total = Column(Float, nullable=True)
    valor_cuota = Column(Float, nullable=True)
    numero_cuotas = Column(Integer, nullable=True)
    cuotas_pagadas = Column(Integer, nullable=True)
    saldo_pendiente = Column(Float, nullable=True)
    estado = Column(String, nullable=True, default='En Proceso')
    observaciones = Column(Text, nullable=True)
    created_at = Column(String, nullable=True)
    updated_at = Column(String, nullable=True)
    documento_soporte = Column(Text, nullable=True)

    # Índices
    __table_args__ = (
        Index('idx_tutelas_estado', 'estado'),
        Index('idx_tutelas_usuario_id', 'usuario_id'),
        Index('idx_tutelas_fecha_fin', 'fecha_fin'),
    )

    def __repr__(self):
        return f"<Tutela {self.numero_tutela} - Juzgado {self.juzgado}>"

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'numero_tutela': self.numero_tutela,
            'juzgado': self.juzgado,
            'fecha_notificacion': self.fecha_notificacion,
            'fecha_inicio': self.fecha_inicio,
            'fecha_fin': self.fecha_fin,
            'valor_total': self.valor_total,
            'valor_cuota': self.valor_cuota,
            'numero_cuotas': self.numero_cuotas,
            'cuotas_pagadas': self.cuotas_pagadas,
            'saldo_pendiente': self.saldo_pendiente,
            'estado': self.estado,
            'observaciones': self.observaciones,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'documento_soporte': self.documento_soporte
        }


# =============================================================================
# MÓDULO: FINANZAS
# =============================================================================

class Pago(db.Model):
    """
    Modelo ORM para la tabla 'pagos'
    Registro de pagos de nómina y otros pagos a empleados
    """
    __tablename__ = 'pagos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Text, nullable=False)
    empresa_nit = Column(Text, nullable=False)
    monto = Column(Float, nullable=False)
    tipo_pago = Column(Text, nullable=False)  # nomina, prima, cesantias, etc.
    fecha_pago = Column(Text, nullable=False)
    referencia = Column(Text, nullable=True)
    created_at = Column(Text, nullable=True, default=datetime.utcnow)

    def __repr__(self):
        return f"<Pago {self.tipo_pago} - Usuario {self.usuario_id} - ${self.monto}>"

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'empresa_nit': self.empresa_nit,
            'monto': self.monto,
            'tipo_pago': self.tipo_pago,
            'fecha_pago': self.fecha_pago,
            'referencia': self.referencia,
            'created_at': self.created_at
        }


class PagoImpuesto(db.Model):
    """
    Modelo ORM para la tabla 'pago_impuestos'
    Control y seguimiento de pagos de impuestos por empresa
    """
    __tablename__ = 'pago_impuestos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    empresa_nit = Column(Text, ForeignKey('empresas.nit'), nullable=False)
    empresa_nombre = Column(Text, nullable=False)
    tipo_impuesto = Column(Text, nullable=False)
    periodo = Column(Text, nullable=False)
    fecha_limite = Column(Text, nullable=False)
    estado = Column(Text, nullable=True, default='Pendiente de Pago')
    ruta_archivo = Column(Text, nullable=True)
    ruta_soporte_pago = Column(Text, nullable=True)
    created_at = Column(Text, nullable=True, default=datetime.utcnow)

    # Relaciones
    empresa = relationship('Empresa', back_populates='pago_impuestos')

    # Índices
    __table_args__ = (
        Index('idx_impuestos_estado', 'estado'),
        Index('idx_impuestos_empresa_nit', 'empresa_nit'),
    )

    def __repr__(self):
        return f"<PagoImpuesto {self.tipo_impuesto} - {self.empresa_nombre}>"

    def to_dict(self):
        return {
            'id': self.id,
            'empresa_nit': self.empresa_nit,
            'empresa_nombre': self.empresa_nombre,
            'tipo_impuesto': self.tipo_impuesto,
            'periodo': self.periodo,
            'fecha_limite': self.fecha_limite,
            'estado': self.estado,
            'ruta_archivo': self.ruta_archivo,
            'ruta_soporte_pago': self.ruta_soporte_pago,
            'created_at': self.created_at
        }


class Cotizacion(db.Model):
    """
    Modelo ORM para la tabla 'cotizaciones'
    Gestión de cotizaciones comerciales
    """
    __tablename__ = 'cotizaciones'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_cotizacion = Column(Text, nullable=False, unique=True)
    cliente = Column(Text, nullable=False)
    email = Column(Text, nullable=True)
    servicio = Column(Text, nullable=False)
    monto = Column(Float, nullable=False)
    notas = Column(Text, nullable=True)
    fecha_creacion = Column(Text, nullable=False)
    estado = Column(Text, nullable=True, default='Enviada')

    # Índices
    __table_args__ = (
        Index('idx_cotizaciones_fecha', 'fecha_creacion'),
        Index('idx_cotizaciones_cliente', 'cliente'),
    )

    def __repr__(self):
        return f"<Cotizacion {self.id_cotizacion} - {self.cliente} - ${self.monto}>"

    def to_dict(self):
        return {
            'id': self.id,
            'id_cotizacion': self.id_cotizacion,
            'cliente': self.cliente,
            'email': self.email,
            'servicio': self.servicio,
            'monto': self.monto,
            'notas': self.notas,
            'fecha_creacion': self.fecha_creacion,
            'estado': self.estado
        }


# =============================================================================
# MÓDULO: COMUNICACIONES
# =============================================================================

class EnvioPlanilla(db.Model):
    """
    Modelo ORM para la tabla 'envios_planillas'
    Control de envío de planillas a entidades
    """
    __tablename__ = 'envios_planillas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    empresa_nit = Column(Text, ForeignKey('empresas.nit'), nullable=False)
    empresa_nombre = Column(Text, nullable=False)
    periodo = Column(Text, nullable=False)
    tipo_id = Column(Text, nullable=True)
    numero_id = Column(Text, nullable=True)
    documento = Column(Text, nullable=True)
    contacto = Column(Text, nullable=True)
    telefono = Column(Text, nullable=True)
    correo = Column(Text, nullable=True)
    canal = Column(Text, nullable=True, default='Correo')
    mensaje = Column(Text, nullable=True)
    estado = Column(Text, nullable=True, default='Pendiente')
    fecha_envio = Column(Text, nullable=True)
    created_at = Column(Text, nullable=True, default=datetime.utcnow)

    # Relaciones
    empresa = relationship('Empresa', back_populates='envios_planillas')

    # Índices
    __table_args__ = (
        Index('idx_envios_estado', 'estado'),
        Index('idx_envios_empresa_periodo', 'empresa_nit', 'periodo'),
    )

    def __repr__(self):
        return f"<EnvioPlanilla {self.empresa_nombre} - {self.periodo}>"

    def to_dict(self):
        return {
            'id': self.id,
            'empresa_nit': self.empresa_nit,
            'empresa_nombre': self.empresa_nombre,
            'periodo': self.periodo,
            'tipo_id': self.tipo_id,
            'numero_id': self.numero_id,
            'documento': self.documento,
            'contacto': self.contacto,
            'telefono': self.telefono,
            'correo': self.correo,
            'canal': self.canal,
            'mensaje': self.mensaje,
            'estado': self.estado,
            'fecha_envio': self.fecha_envio,
            'created_at': self.created_at
        }


from sqlalchemy.types import TypeDecorator
import json

class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.

    Usage::

        JSONEncodedDict(255)

    """

    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

class Novedad(db.Model):
    """
    Modelo ORM para la tabla 'novedades'
    Sistema completo de tickets/novedades
    """
    __tablename__ = 'novedades'

    id = Column(Integer, primary_key=True, autoincrement=True)
    client = Column(Text, nullable=True)
    subject = Column(Text, nullable=True)
    priority = Column(Integer, nullable=True)
    status = Column(Text, nullable=True)
    priorityText = Column(Text, nullable=True)
    idType = Column(Text, nullable=True)
    idNumber = Column(Text, nullable=True)
    firstName = Column(Text, nullable=True)
    lastName = Column(Text, nullable=True)
    nationality = Column(Text, nullable=True)
    gender = Column(Text, nullable=True)
    birthDate = Column(Text, nullable=True)
    phone = Column(Text, nullable=True)
    department = Column(Text, nullable=True)
    city = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    neighborhood = Column(Text, nullable=True)
    email = Column(Text, nullable=True)
    beneficiaries = Column(JSONEncodedDict, nullable=True)
    eps = Column(Text, nullable=True)
    arl = Column(Text, nullable=True)
    arlClass = Column(Text, nullable=True)
    ccf = Column(Text, nullable=True)
    pensionFund = Column(Text, nullable=True)
    ibc = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    radicado = Column(Text, nullable=True)
    solutionDescription = Column(Text, nullable=True)
    creationDate = Column(Text, nullable=True, default=datetime.utcnow)
    updateDate = Column(Text, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    assignedTo = Column(Text, nullable=True)
    history = Column(JSONEncodedDict, nullable=True)

    def __repr__(self):
        return f"<Novedad {self.subject} - Cliente: {self.client}>"

    def to_dict(self):
        return {
            'id': self.id,
            'client': self.client,
            'subject': self.subject,
            'priority': self.priority,
            'status': self.status,
            'priorityText': self.priorityText,
            'idType': self.idType,
            'idNumber': self.idNumber,
            'firstName': self.firstName,
            'lastName': self.lastName,
            'nationality': self.nationality,
            'gender': self.gender,
            'birthDate': self.birthDate,
            'phone': self.phone,
            'department': self.department,
            'city': self.city,
            'address': self.address,
            'neighborhood': self.neighborhood,
            'email': self.email,
            'beneficiaries': self.beneficiaries,

            'eps': self.eps,
            'arl': self.arl,
            'arlClass': self.arlClass,
            'ccf': self.ccf,
            'pensionFund': self.pensionFund,
            'ibc': self.ibc,
            'description': self.description,
            'radicado': self.radicado,
            'solutionDescription': self.solutionDescription,
            'creationDate': self.creationDate,
            'updateDate': self.updateDate,
            'assignedTo': self.assignedTo,
            'history': self.history,
        }



# =============================================================================
# MÓDULO: SEGURIDAD
# =============================================================================

class CredencialPlataforma(db.Model):
    """
    Modelo ORM para la tabla 'credenciales_plataforma'
    Almacenamiento ENCRIPTADO de credenciales externas
    """
    __tablename__ = 'credenciales_plataforma'

    id = Column(Integer, primary_key=True, autoincrement=True)
    empresa_nit = Column(Text, ForeignKey('empresas.nit'), nullable=False)
    plataforma = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    usuario = Column(Text, nullable=False)
    contrasena = Column(Text, nullable=False)  # ⚠️ ENCRIPTADA con Fernet
    notas = Column(Text, nullable=True)
    created_at = Column(Text, nullable=True, default=datetime.utcnow)
    ruta_documento_txt = Column(Text, nullable=True)

    # Relaciones
    empresa = relationship('Empresa', back_populates='credenciales')

    # Índices
    __table_args__ = (
        Index('idx_credenciales_empresa_nit', 'empresa_nit'),
    )

    def __repr__(self):
        return f"<CredencialPlataforma {self.plataforma} - {self.empresa_nit}>"

    def to_dict(self, include_password=False):
        """Convierte el objeto a diccionario para JSON"""
        data = {
            'id': self.id,
            'empresa_nit': self.empresa_nit,
            'plataforma': self.plataforma,
            'url': self.url,
            'usuario': self.usuario,
            'notas': self.notas,
            'created_at': self.created_at,
            'ruta_documento_txt': self.ruta_documento_txt
        }
        if include_password:
            data['contrasena'] = self.contrasena
        return data


# =============================================================================
# MÓDULO: DOCUMENTOS
# =============================================================================

class FormularioImportado(db.Model):
    """
    Modelo ORM para la tabla 'formularios_importados'
    Registro de formularios PDF importados al sistema
    """
    __tablename__ = 'formularios_importados'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(Text, nullable=False)
    nombre_archivo = Column(Text, nullable=False)
    ruta_archivo = Column(Text, nullable=False)
    campos_mapeados = Column(Text, nullable=True)  # JSON
    created_at = Column(Text, nullable=True, default=datetime.utcnow)

    def __repr__(self):
        return f"<FormularioImportado {self.nombre}>"

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'nombre_archivo': self.nombre_archivo,
            'ruta_archivo': self.ruta_archivo,
            'campos_mapeados': self.campos_mapeados,
            'created_at': self.created_at
        }


# =============================================================================
# MÓDULO: CALIDAD DE DATOS
# =============================================================================

class DepuracionPendiente(db.Model):
    """
    Modelo ORM para la tabla 'depuraciones_pendientes'
    Control de calidad y depuración de datos
    """
    __tablename__ = 'depuraciones_pendientes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    entidad_tipo = Column(Text, nullable=False)
    entidad_id = Column(Text, nullable=False)
    entidad_nombre = Column(Text, nullable=True)
    causa = Column(Text, nullable=False)
    estado = Column(Text, nullable=True, default='Pendiente')
    fecha_sugerida = Column(Text, nullable=False)
    created_at = Column(Text, nullable=True, default=datetime.utcnow)

    # Índices
    __table_args__ = (
        Index('idx_depuraciones_entidad', 'entidad_tipo', 'entidad_id'),
    )

    def __repr__(self):
        return f"<DepuracionPendiente {self.entidad_tipo} - {self.entidad_nombre}>"

    def to_dict(self):
        return {
            'id': self.id,
            'entidad_tipo': self.entidad_tipo,
            'entidad_id': self.entidad_id,
            'entidad_nombre': self.entidad_nombre,
            'causa': self.causa,
            'estado': self.estado,
            'fecha_sugerida': self.fecha_sugerida,
            'created_at': self.created_at
        }


# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def init_db(app):
    """
    Inicializa la base de datos con la aplicación Flask

    Args:
        app: Instancia de Flask

    Returns:
        db: Instancia de SQLAlchemy configurada
    """
    db.init_app(app)
    return db


def create_all_tables(app):
    """
    Crea todas las tablas en la base de datos

    Args:
        app: Instancia de Flask con contexto de aplicación
    """
    with app.app_context():
        db.create_all()
        print("✅ Todas las tablas ORM han sido creadas exitosamente")
