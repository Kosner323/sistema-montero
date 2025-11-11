"""
📊 DOCUMENTACIÓN DEL ESQUEMA DE BASE DE DATOS - SISTEMA MONTERO (COMPLETO)
============================================================================

Archivo: database_schema_COMPLETO.py
Ubicación: config/database_schema_COMPLETO.py
Propósito: Documentar la estructura completa de la base de datos SQLite
Fecha de creación: 30 de octubre de 2025 (ACTUALIZADO)
Sistema: Sistema de Gestión Montero
Base de datos: mi_sistema.db (VERSIÓN PRODUCTIVA)

⚠️ ESTE ES EL ESQUEMA COMPLETO Y ACTUALIZADO DEL SISTEMA REAL
Incluye las 13 tablas del sistema en producción con datos reales.

Este archivo documenta todas las tablas, columnas, relaciones y restricciones
de la base de datos del sistema en producción.
"""

# ============================================================================
# INFORMACIÓN GENERAL DE LA BASE DE DATOS
# ============================================================================

DATABASE_INFO = {
    "nombre": "mi_sistema.db",
    "tipo": "SQLite",
    "version": "3.x",
    "ubicacion": "RUTA_BASE_DE_DATOS/mi_sistema.db (ver config_rutas.py)",
    "charset": "UTF-8",
    "tamaño": "132 KB",
    "total_tablas": 13,
    "tablas_principales": 12,
    "total_columnas": 163,
    "total_registros": 27,
    "foreign_keys": 6,
    "indices": 15,
    "descripcion": "Base de datos COMPLETA del sistema de gestión Montero que incluye: gestión de empresas, empleados, autenticación, formularios, tutelas, incapacidades, impuestos, credenciales, novedades, cotizaciones, y más.",
    "estado": "PRODUCCIÓN - Contiene datos reales",
}

# ============================================================================
# MÓDULOS DEL SISTEMA
# ============================================================================

SYSTEM_MODULES = {
    "gestion_empresas": {
        "tablas": ["empresas", "usuarios"],
        "descripcion": "Gestión de empresas cliente y sus empleados",
    },
    "autenticacion": {
        "tablas": ["portal_users"],
        "descripcion": "Sistema de autenticación web con hashing de contraseñas",
    },
    "documentos": {
        "tablas": ["formularios_importados"],
        "descripcion": "Gestión de formularios PDF de entidades",
    },
    "gestion_laboral": {
        "tablas": ["incapacidades", "tutelas"],
        "descripcion": "Gestión de incapacidades médicas y tutelas laborales",
    },
    "finanzas": {
        "tablas": ["pago_impuestos", "cotizaciones"],
        "descripcion": "Control de pagos de impuestos y cotizaciones comerciales",
    },
    "comunicaciones": {
        "tablas": ["envios_planillas", "novedades"],
        "descripcion": "Envío de planillas y sistema de tickets/novedades",
    },
    "seguridad": {
        "tablas": ["credenciales_plataforma"],
        "descripcion": "Almacenamiento encriptado de credenciales externas",
    },
    "calidad_datos": {
        "tablas": ["depuraciones_pendientes"],
        "descripcion": "Control de calidad y depuración de datos",
    },
}

# ============================================================================
# ESQUEMA DE TABLAS - SISTEMA COMPLETO
# ============================================================================

TABLES_SCHEMA = {
    # ========================================================================
    # MÓDULO: GESTIÓN DE EMPRESAS
    # ========================================================================
    # ------------------------------------------------------------------------
    # TABLA: empresas
    # Propósito: Almacena información de las empresas clientes
    # ------------------------------------------------------------------------
    "empresas": {
        "modulo": "gestion_empresas",
        "descripcion": "Registro de empresas cliente con información legal y de contacto",
        "tipo": "Tabla principal",
        "estado": "ACTIVA - 4 empresas registradas",
        "relaciones": [
            "Tiene relación 1:N con 'usuarios'",
            "Tiene relación 1:N con 'incapacidades'",
            "Tiene relación 1:N con 'tutelas'",
            "Tiene relación 1:N con 'pago_impuestos'",
            "Tiene relación 1:N con 'envios_planillas'",
            "Tiene relación 1:N con 'credenciales_plataforma'",
        ],
        "columnas": {
            "id": {
                "tipo": "INTEGER",
                "nullable": True,
                "default": None,
                "primary_key": True,
                "autoincrement": True,
                "descripcion": "Identificador único autoincremental de la empresa",
            },
            "nombre_empresa": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Razón social o nombre comercial de la empresa",
                "ejemplo": "Constructora El Futuro S.A.S.",
            },
            "tipo_identificacion_empresa": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Tipo de documento (NIT, RUT, etc.)",
                "valores_comunes": ["NIT"],
            },
            "nit": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "unique": True,  # ✅ YA IMPLEMENTADO
                "descripcion": "Número de Identificación Tributaria - CLAVE FORÁNEA para usuarios",
                "ejemplo": "900.123.456-7",
            },
            "direccion_empresa": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Dirección física de la empresa",
                "ejemplo": "Avenida Siempre Viva 742",
            },
            "telefono_empresa": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Número telefónico principal",
            },
            "correo_empresa": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Correo electrónico corporativo",
            },
            "departamento_empresa": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Departamento donde se ubica la empresa",
            },
            "ciudad_empresa": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Ciudad donde se ubica la empresa",
            },
            "ibc_empresa": {
                "tipo": "REAL",
                "nullable": True,
                "default": None,
                "descripcion": "Ingreso Base de Cotización de la empresa",
            },
            "afp_empresa": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Nombre del fondo de pensiones al que está afiliada la empresa",
            },
            "arl_empresa": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Nombre de la ARL (Administradora de Riesgos Laborales)",
            },
            "rep_legal_nombre": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Nombre completo del representante legal",
            },
            "rep_legal_tipo_id": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Tipo de identificación del representante legal",
            },
            "rep_legal_numero_id": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Número de documento del representante legal",
            },
            "created_at": {
                "tipo": "TEXT",
                "nullable": True,
                "default": "CURRENT_TIMESTAMP",
                "descripcion": "Fecha y hora de creación del registro (formato ISO 8601)",
            },
        },
        "indices": [
            {
                "nombre": "sqlite_autoindex_empresas_1",
                "columnas": ["nit"],
                "unique": True,
                "descripcion": "Índice automático UNIQUE en nit",
            }
        ],
        "constraints": ["PRIMARY KEY (id)", "UNIQUE (nit)"],  # ✅ YA IMPLEMENTADO
        "notas": [
            "✅ BIEN: Ya tiene constraint UNIQUE en 'nit'",
            "⚠️ MEJORA: Hacer campos críticos NOT NULL (nombre_empresa, nit)",
            "📊 DATOS: 4 empresas registradas actualmente",
        ],
        "datos_ejemplo": [
            "Constructora El Futuro S.A.S. (NIT: 900.123.456-7)",
            "Constructora El Futuro S.A. (NIT: 900.123.457-1)",
            "COMERCIALIZADORA AJK (NIT: 901429801)",
        ],
    },
    # ------------------------------------------------------------------------
    # TABLA: usuarios
    # Propósito: Almacena información de empleados/usuarios del sistema
    # ------------------------------------------------------------------------
    "usuarios": {
        "modulo": "gestion_empresas",
        "descripcion": "Registro de empleados con información personal, laboral y de seguridad social",
        "tipo": "Tabla principal",
        "estado": "ACTIVA - 4 empleados registrados",
        "relaciones": ["Tiene relación N:1 con 'empresas' a través de 'empresa_nit'"],
        "columnas": {
            "id": {
                "tipo": "INTEGER",
                "nullable": True,
                "default": None,
                "primary_key": True,
                "autoincrement": True,
                "descripcion": "Identificador único autoincremental del usuario/empleado",
            },
            "empresa_nit": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "foreign_key": "empresas.nit",
                "descripcion": "NIT de la empresa a la que pertenece el empleado (FK)",
                "nota": "⚠️ Algunos empleados tienen empresa_nit=NULL - necesita corrección",
            },
            "tipoId": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Tipo de identificación (CC, TI, CE, etc.)",
                "valores_comunes": ["Cédula de Ciudadanía", "CC", "TI", "CE"],
            },
            "numeroId": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "unique": True,  # ✅ YA IMPLEMENTADO (con tipoId)
                "descripcion": "Número de documento de identidad",
                "ejemplo": "1010123456",
            },
            "primerNombre": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Primer nombre del empleado",
                "ejemplo": "Carlos",
            },
            "segundoNombre": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Segundo nombre del empleado (opcional)",
            },
            "primerApellido": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Primer apellido del empleado",
            },
            "segundoApellido": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Segundo apellido del empleado (opcional)",
            },
            "sexoBiologico": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Sexo biológico (M/F)",
                "valores_permitidos": ["M", "F", "Masculino", "Femenino"],
            },
            "sexoIdentificacion": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Identidad de género declarada",
            },
            "nacionalidad": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Nacionalidad del empleado",
                "valores_comunes": ["Colombiana", "Venezolana"],
            },
            "fechaNacimiento": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Fecha de nacimiento (formato: YYYY-MM-DD)",
            },
            "paisNacimiento": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "País de nacimiento",
            },
            "departamentoNacimiento": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Departamento de nacimiento",
            },
            "municipioNacimiento": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Municipio de nacimiento",
            },
            "direccion": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Dirección de residencia actual",
            },
            "telefonoCelular": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Número de teléfono celular",
            },
            "telefonoFijo": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Número de teléfono fijo (opcional)",
            },
            "correoElectronico": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Correo electrónico personal",
            },
            "comunaBarrio": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Comuna o barrio de residencia",
            },
            "afpNombre": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Nombre del fondo de pensiones (AFP)",
            },
            "afpCosto": {
                "tipo": "REAL",
                "nullable": True,
                "default": None,
                "descripcion": "Costo de cotización a AFP",
            },
            "epsNombre": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Nombre de la EPS (Entidad Promotora de Salud)",
            },
            "epsCosto": {
                "tipo": "REAL",
                "nullable": True,
                "default": None,
                "descripcion": "Costo de cotización a EPS",
            },
            "arlNombre": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Nombre de la ARL (Riesgos Laborales)",
            },
            "arlCosto": {
                "tipo": "REAL",
                "nullable": True,
                "default": None,
                "descripcion": "Costo de cotización a ARL",
            },
            "ccfNombre": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Nombre de la Caja de Compensación Familiar",
            },
            "ccfCosto": {
                "tipo": "REAL",
                "nullable": True,
                "default": None,
                "descripcion": "Costo de cotización a CCF",
            },
            "administracion": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Información de administración (uso interno)",
            },
            "ibc": {
                "tipo": "REAL",
                "nullable": True,
                "default": None,
                "descripcion": "Ingreso Base de Cotización del empleado",
            },
            "claseRiesgoARL": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Clase de riesgo laboral (I, II, III, IV, V)",
                "valores_permitidos": ["I", "II", "III", "IV", "V"],
            },
            "fechaIngreso": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Fecha de ingreso a la empresa (formato: YYYY-MM-DD)",
            },
            "created_at": {
                "tipo": "TEXT",
                "nullable": True,
                "default": "CURRENT_TIMESTAMP",
                "descripcion": "Fecha y hora de creación del registro",
            },
        },
        "indices": [
            {
                "nombre": "sqlite_autoindex_usuarios_1",
                "columnas": ["tipoId", "numeroId"],
                "unique": True,
                "descripcion": "Índice automático UNIQUE en documento",
            }
        ],
        "constraints": [
            "PRIMARY KEY (id)",
            "FOREIGN KEY (empresa_nit) REFERENCES empresas(nit)",
            "UNIQUE (tipoId, numeroId)",  # ✅ YA IMPLEMENTADO
        ],
        "notas": [
            "✅ BIEN: Ya tiene constraint UNIQUE en (tipoId, numeroId)",
            "✅ BIEN: Ya tiene Foreign Key a empresas.nit",
            "⚠️ PROBLEMA: Algunos usuarios tienen empresa_nit = NULL",
            "⚠️ MEJORA: Hacer NOT NULL campos críticos",
            "📊 DATOS: 4 empleados registrados actualmente",
        ],
        "datos_ejemplo": [
            "Carlos (CC: 1010123456) - empresa_nit: NULL",
            "Carlos (CC: 1005878110) - empresa_nit: NULL",
        ],
    },
    # ========================================================================
    # MÓDULO: AUTENTICACIÓN
    # ========================================================================
    # ------------------------------------------------------------------------
    # TABLA: portal_users
    # Propósito: Usuarios que pueden acceder al portal web
    # ------------------------------------------------------------------------
    "portal_users": {
        "modulo": "autenticacion",
        "descripcion": "Usuarios del sistema con autenticación web (hashing de contraseñas)",
        "tipo": "Tabla de autenticación",
        "estado": "ACTIVA - 4 usuarios registrados",
        "seguridad": "✅ ALTA - Usa Werkzeug pbkdf2:sha256 para hashing",
        "relaciones": [],
        "columnas": {
            "id": {
                "tipo": "INTEGER",
                "nullable": True,
                "default": None,
                "primary_key": True,
                "autoincrement": True,
                "descripcion": "Identificador único del usuario del portal",
            },
            "nombre": {
                "tipo": "TEXT",
                "nullable": False,  # ✅ NOT NULL implementado
                "default": None,
                "descripcion": "Nombre completo del usuario",
                "ejemplo": "Kevin Montero",
            },
            "email": {
                "tipo": "TEXT",
                "nullable": False,  # ✅ NOT NULL implementado
                "default": None,
                "unique": True,  # ✅ UNIQUE implementado
                "descripcion": "Correo electrónico (usado para login)",
                "ejemplo": "kevinlomasd@gmail.com",
            },
            "password_hash": {
                "tipo": "TEXT",
                "nullable": False,  # ✅ NOT NULL implementado
                "default": None,
                "descripcion": "Hash de la contraseña con Werkzeug pbkdf2:sha256",
                "ejemplo": "pbkdf2:sha256:600000$w1KCARvfL48ov7b4$e291...",
                "seguridad": "✅ Hasheada con pbkdf2:sha256 y 600,000 iteraciones",
            },
            "created_at": {
                "tipo": "TEXT",
                "nullable": True,
                "default": "CURRENT_TIMESTAMP",
                "descripcion": "Fecha y hora de creación del usuario",
            },
        },
        "indices": [
            {
                "nombre": "sqlite_autoindex_portal_users_1",
                "columnas": ["email"],
                "unique": True,
                "descripcion": "Índice automático UNIQUE en email",
            }
        ],
        "constraints": ["PRIMARY KEY (id)", "UNIQUE (email)"],  # ✅ YA IMPLEMENTADO
        "notas": [
            "✅ EXCELENTE: Sistema de autenticación bien implementado",
            "✅ BIEN: Contraseñas hasheadas con Werkzeug",
            "✅ BIEN: 600,000 iteraciones de pbkdf2 (muy seguro)",
            "✅ BIEN: Email único para evitar duplicados",
            "✅ BIEN: Campos críticos con NOT NULL",
            "📊 DATOS: 4 usuarios activos en el sistema",
        ],
        "usuarios_registrados": [
            "Kevin Montero (kevinlomasd@gmail.com)",
            "Yeison David Montero (monterojk2014@hotmail.com)",
            "Alba Lucia Montero (comercializadoraajk@hotmail.com)",
        ],
    },
    # ========================================================================
    # MÓDULO: DOCUMENTOS
    # ========================================================================
    # ------------------------------------------------------------------------
    # TABLA: formularios_importados
    # Propósito: Registro de formularios PDF importados al sistema
    # ------------------------------------------------------------------------
    "formularios_importados": {
        "modulo": "documentos",
        "descripcion": "Registro de formularios PDF de entidades con configuración de mapeo",
        "tipo": "Tabla de control",
        "estado": "ACTIVA - 3 formularios PDF registrados",
        "relaciones": [],
        "columnas": {
            "id": {
                "tipo": "INTEGER",
                "nullable": True,
                "default": None,
                "primary_key": True,
                "autoincrement": True,
                "descripcion": "Identificador único del formulario",
            },
            "nombre": {
                "tipo": "TEXT",
                "nullable": False,  # ✅ NOT NULL implementado
                "default": None,
                "descripcion": "Nombre descriptivo del formulario",
                "ejemplo": "FORMULARIO EPS COOSALUD",
            },
            "nombre_archivo": {
                "tipo": "TEXT",
                "nullable": False,  # ✅ NOT NULL implementado
                "default": None,
                "descripcion": "Nombre del archivo PDF original",
                "ejemplo": "20251021003047_FORMULARIO_EPS_COOSALUD.pdf",
            },
            "ruta_archivo": {
                "tipo": "TEXT",
                "nullable": False,  # ✅ NOT NULL implementado
                "default": None,
                "descripcion": "Ruta completa donde se almacena el archivo",
                "ejemplo": "D:\\Mi-App-React\\src\\dashboard\\formularios_pdf\\...",
            },
            "campos_mapeados": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "JSON con la configuración de mapeo de campos del formulario",
                "formato": "JSON",
            },
            "created_at": {
                "tipo": "TEXT",
                "nullable": True,
                "default": "CURRENT_TIMESTAMP",
                "descripcion": "Fecha y hora de importación del formulario",
            },
        },
        "indices": [],
        "constraints": ["PRIMARY KEY (id)"],
        "notas": [
            "✅ BIEN: Campos críticos ya tienen NOT NULL",
            "⚠️ MEJORA: Agregar UNIQUE en nombre_archivo",
            "⚠️ MEJORA: Agregar índice en nombre_archivo",
            "💡 MEJORA: Validar que campos_mapeados sea JSON válido",
            "📊 DATOS: 3 formularios registrados",
        ],
        "formularios_registrados": [
            "FORMULARIO EPS COOSALUD",
            "FORMULARIO EPS COMFENALCO",
            "FORMULARIO EPS SANITAS",
        ],
    },
    # ========================================================================
    # MÓDULO: GESTIÓN LABORAL
    # ========================================================================
    # ------------------------------------------------------------------------
    # TABLA: incapacidades
    # Propósito: Gestión de incapacidades médicas de empleados
    # ------------------------------------------------------------------------
    "incapacidades": {
        "modulo": "gestion_laboral",
        "descripcion": "Registro y seguimiento de incapacidades médicas de empleados",
        "tipo": "Tabla transaccional",
        "estado": "ACTIVA - Sin registros actualmente",
        "relaciones": ["Tiene relación N:1 con 'empresas' a través de 'empresa_nit'"],
        "columnas": {
            "id": {
                "tipo": "INTEGER",
                "nullable": True,
                "default": None,
                "primary_key": True,
                "autoincrement": True,
                "descripcion": "Identificador único de la incapacidad",
            },
            "empresa_nit": {
                "tipo": "TEXT",
                "nullable": False,  # ✅ NOT NULL implementado
                "default": None,
                "foreign_key": "empresas.nit",
                "descripcion": "NIT de la empresa del empleado (FK)",
            },
            "usuario_id": {
                "tipo": "TEXT",
                "nullable": False,  # ✅ NOT NULL implementado
                "default": None,
                "descripcion": "ID del usuario/empleado incapacitado",
            },
            "diagnostico": {
                "tipo": "TEXT",
                "nullable": False,  # ✅ NOT NULL implementado
                "default": None,
                "descripcion": "Diagnóstico médico",
            },
            "fecha_inicio": {
                "tipo": "TEXT",
                "nullable": False,  # ✅ NOT NULL implementado
                "default": None,
                "descripcion": "Fecha de inicio de la incapacidad (formato: YYYY-MM-DD)",
            },
            "fecha_fin": {
                "tipo": "TEXT",
                "nullable": False,  # ✅ NOT NULL implementado
                "default": None,
                "descripcion": "Fecha de finalización de la incapacidad (formato: YYYY-MM-DD)",
            },
            "estado": {
                "tipo": "TEXT",
                "nullable": True,
                "default": "'En Proceso'",
                "descripcion": "Estado de la incapacidad",
                "valores_comunes": [
                    "En Proceso",
                    "Aprobada",
                    "Rechazada",
                    "Finalizada",
                ],
            },
            "archivos_info": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "JSON con información de archivos adjuntos",
                "formato": "JSON",
            },
            "created_at": {
                "tipo": "TEXT",
                "nullable": True,
                "default": "CURRENT_TIMESTAMP",
                "descripcion": "Fecha y hora de registro",
            },
        },
        "indices": [],
        "constraints": [
            "PRIMARY KEY (id)",
            "FOREIGN KEY (empresa_nit) REFERENCES empresas(nit)",
        ],
        "notas": [
            "✅ BIEN: Campos críticos con NOT NULL",
            "✅ BIEN: FK a empresas implementada",
            "⚠️ MEJORA: Agregar índice en empresa_nit",
            "⚠️ MEJORA: Agregar índice en estado",
            "💡 CONSIDERAR: Agregar índice en fechas para búsquedas por período",
            "📊 DATOS: Sin registros actualmente",
        ],
    },
    # ------------------------------------------------------------------------
    # TABLA: tutelas
    # Propósito: Gestión de tutelas laborales
    # ------------------------------------------------------------------------
    "tutelas": {
        "modulo": "gestion_laboral",
        "descripcion": "Registro y seguimiento de tutelas laborales",
        "tipo": "Tabla transaccional",
        "estado": "ACTIVA - 8 tutelas registradas",
        "relaciones": ["Tiene relación N:1 con 'empresas' a través de 'empresa_nit'"],
        "columnas": {
            "id": {
                "tipo": "INTEGER",
                "nullable": True,
                "default": None,
                "primary_key": True,
                "autoincrement": True,
                "descripcion": "Identificador único de la tutela",
            },
            "empresa_nit": {
                "tipo": "TEXT",
                "nullable": False,  # ✅ NOT NULL implementado
                "default": None,
                "foreign_key": "empresas.nit",
                "descripcion": "NIT de la empresa (FK)",
            },
            "empresa_nombre": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Nombre de la empresa (denormalizado para performance)",
            },
            "usuario_id": {
                "tipo": "TEXT",
                "nullable": False,  # ✅ NOT NULL implementado
                "default": None,
                "descripcion": "ID del usuario/empleado que interpone la tutela",
            },
            "usuario_nombre": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Nombre del usuario (denormalizado para performance)",
            },
            "motivo": {
                "tipo": "TEXT",
                "nullable": False,  # ✅ NOT NULL implementado
                "default": None,
                "descripcion": "Motivo de la tutela",
            },
            "fecha_radicacion": {
                "tipo": "TEXT",
                "nullable": False,  # ✅ NOT NULL implementado
                "default": None,
                "descripcion": "Fecha de radicación de la tutela (formato: YYYY-MM-DD)",
            },
            "estado": {
                "tipo": "TEXT",
                "nullable": True,
                "default": "'En Proceso'",
                "descripcion": "Estado de la tutela",
                "valores_comunes": [
                    "En Proceso",
                    "Resuelta",
                    "Rechazada",
                    "En Revisión",
                ],
            },
            "archivos_info": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "JSON con información de archivos adjuntos",
                "formato": "JSON",
            },
            "created_at": {
                "tipo": "TEXT",
                "nullable": True,
                "default": "CURRENT_TIMESTAMP",
                "descripcion": "Fecha y hora de registro",
            },
        },
        "indices": [
            {
                "nombre": "idx_tutelas_estado",
                "columnas": ["estado"],
                "unique": False,
                "descripcion": "Índice para búsquedas por estado",
            },
            {
                "nombre": "idx_tutelas_empresa_nit",
                "columnas": ["empresa_nit"],
                "unique": False,
                "descripcion": "Índice para búsquedas por empresa",
            },
            {
                "nombre": "idx_tutelas_usuario_id",
                "columnas": ["usuario_id"],
                "unique": False,
                "descripcion": "Índice para búsquedas por usuario",
            },
        ],
        "constraints": [
            "PRIMARY KEY (id)",
            "FOREIGN KEY (empresa_nit) REFERENCES empresas(nit)",
        ],
        "notas": [
            "✅ EXCELENTE: Tabla bien diseñada con 3 índices",
            "✅ BIEN: Campos críticos con NOT NULL",
            "✅ BIEN: FK a empresas implementada",
            "✅ BIEN: Índices en campos de búsqueda frecuente",
            "💡 BUENA PRÁCTICA: Denormalización de nombres para performance",
            "📊 DATOS: 8 tutelas registradas actualmente",
        ],
    },
    # ========================================================================
    # MÓDULO: FINANZAS
    # ========================================================================
    "pago_impuestos": {
        "modulo": "finanzas",
        "descripcion": "Control y seguimiento de pagos de impuestos por empresa",
        "tipo": "Tabla transaccional",
        "estado": "ACTIVA - 3 impuestos registrados",
        "relaciones": ["N:1 con empresas via empresa_nit"],
        "columnas": {
            "id": {"tipo": "INTEGER", "pk": True},
            "empresa_nit": {"tipo": "TEXT", "not_null": True, "fk": "empresas.nit"},
            "empresa_nombre": {"tipo": "TEXT", "not_null": True},
            "tipo_impuesto": {"tipo": "TEXT", "not_null": True},
            "periodo": {"tipo": "TEXT", "not_null": True},
            "fecha_limite": {"tipo": "TEXT", "not_null": True},
            "estado": {"tipo": "TEXT", "default": "Pendiente de Pago"},
            "ruta_archivo": {"tipo": "TEXT"},
            "ruta_soporte_pago": {"tipo": "TEXT"},
            "created_at": {"tipo": "TEXT", "default": "CURRENT_TIMESTAMP"},
        },
        "indices": ["idx_impuestos_estado", "idx_impuestos_empresa_nit"],
        "notas": [
            "✅ BIEN: 2 índices optimizados",
            "📊 3 impuestos para COMERCIALIZADORA AJK",
        ],
    },
    "cotizaciones": {
        "modulo": "finanzas",
        "descripcion": "Gestión de cotizaciones comerciales",
        "tipo": "Tabla transaccional",
        "estado": "ACTIVA - Sin registros",
        "columnas": {
            "id": {"tipo": "INTEGER", "pk": True},
            "id_cotizacion": {"tipo": "TEXT", "not_null": True, "unique": True},
            "cliente": {"tipo": "TEXT", "not_null": True},
            "email": {"tipo": "TEXT"},
            "servicio": {"tipo": "TEXT", "not_null": True},
            "monto": {"tipo": "REAL", "not_null": True},
            "notas": {"tipo": "TEXT"},
            "fecha_creacion": {"tipo": "TEXT", "not_null": True},
            "estado": {"tipo": "TEXT", "default": "Enviada"},
        },
        "indices": [
            "idx_cotizaciones_fecha",
            "idx_cotizaciones_cliente",
            "UNIQUE(id_cotizacion)",
        ],
        "notas": ["✅ EXCELENTE: 3 índices incluyendo UNIQUE"],
    },
    # ========================================================================
    # MÓDULO: COMUNICACIONES
    # ========================================================================
    "envios_planillas": {
        "modulo": "comunicaciones",
        "descripcion": "Control de envío de planillas a entidades",
        "tipo": "Tabla transaccional",
        "estado": "ACTIVA - Sin registros",
        "relaciones": ["N:1 con empresas via empresa_nit"],
        "columnas": {
            "id": {"tipo": "INTEGER", "pk": True},
            "empresa_nit": {"tipo": "TEXT", "not_null": True, "fk": "empresas.nit"},
            "empresa_nombre": {"tipo": "TEXT", "not_null": True},
            "periodo": {"tipo": "TEXT", "not_null": True},
            "tipo_id": {"tipo": "TEXT"},
            "numero_id": {"tipo": "TEXT"},
            "documento": {"tipo": "TEXT"},
            "contacto": {"tipo": "TEXT"},
            "telefono": {"tipo": "TEXT"},
            "correo": {"tipo": "TEXT"},
            "canal": {"tipo": "TEXT", "default": "Correo"},
            "mensaje": {"tipo": "TEXT"},
            "estado": {"tipo": "TEXT", "default": "Pendiente"},
            "fecha_envio": {"tipo": "TEXT"},
            "created_at": {"tipo": "TEXT", "default": "CURRENT_TIMESTAMP"},
        },
        "indices": ["idx_envios_estado", "idx_envios_empresa_periodo"],
        "notas": [
            "✅ EXCELENTE: 15 columnas completas",
            "✅ Índice compuesto empresa+período",
        ],
    },
    "novedades": {
        "modulo": "comunicaciones",
        "descripcion": "Sistema completo de tickets/novedades",
        "tipo": "Tabla transaccional",
        "estado": "ACTIVA - Sin registros",
        "columnas": 33,
        "campos_principales": [
            "id",
            "client",
            "subject",
            "priority",
            "status",
            "description",
            "eps",
            "arl",
            "ccf",
            "pensionFund",
            "ibc",
            "history (JSON)",
        ],
        "notas": [
            "⚠️ CRÍTICO: 33 columnas SIN ÍNDICES",
            "⚠️ URGENTE: Agregar índices",
            "✅ Sistema muy completo con datos personales y seguridad social",
        ],
    },
    # ========================================================================
    # MÓDULO: SEGURIDAD
    # ========================================================================
    "credenciales_plataforma": {
        "modulo": "seguridad",
        "descripcion": "Almacenamiento ENCRIPTADO de credenciales externas",
        "tipo": "Tabla de seguridad",
        "estado": "ACTIVA - 1 credencial",
        "seguridad": "✅ MUY ALTA - Fernet encryption",
        "relaciones": ["N:1 con empresas via empresa_nit"],
        "columnas": {
            "id": {"tipo": "INTEGER", "pk": True},
            "empresa_nit": {"tipo": "TEXT", "not_null": True, "fk": "empresas.nit"},
            "plataforma": {"tipo": "TEXT", "not_null": True},
            "url": {"tipo": "TEXT", "not_null": True},
            "usuario": {"tipo": "TEXT", "not_null": True},
            "contrasena": {"tipo": "TEXT", "not_null": True, "ENCRIPTADA": "Fernet"},
            "notas": {"tipo": "TEXT"},
            "created_at": {"tipo": "TEXT", "default": "CURRENT_TIMESTAMP"},
            "ruta_documento_txt": {"tipo": "TEXT"},
        },
        "indices": ["idx_credenciales_empresa_nit"],
        "notas": [
            "✅ EXCELENTE: Encriptación Fernet implementada",
            "✅ 1 credencial: EPS SURA (NIT 901429801)",
            "⚠️ IMPORTANTE: Verificar ENCRYPTION_KEY en .env",
        ],
    },
    # ========================================================================
    # MÓDULO: CALIDAD DE DATOS
    # ========================================================================
    "depuraciones_pendientes": {
        "modulo": "calidad_datos",
        "descripcion": "Control de calidad y depuración de datos",
        "tipo": "Tabla de control",
        "estado": "ACTIVA - Sin registros",
        "columnas": {
            "id": {"tipo": "INTEGER", "pk": True},
            "entidad_tipo": {"tipo": "TEXT", "not_null": True},
            "entidad_id": {"tipo": "TEXT", "not_null": True},
            "entidad_nombre": {"tipo": "TEXT"},
            "causa": {"tipo": "TEXT", "not_null": True},
            "estado": {"tipo": "TEXT", "default": "Pendiente"},
            "fecha_sugerida": {"tipo": "TEXT", "not_null": True},
            "created_at": {"tipo": "TEXT", "default": "CURRENT_TIMESTAMP"},
        },
        "indices": ["idx_depuraciones_entidad (entidad_tipo, entidad_id)"],
        "notas": [
            "✅ EXCELENTE: Sistema proactivo de mantenimiento",
            "✅ Índice compuesto en (tipo, id)",
        ],
    },
}

# ============================================================================
# ESTADÍSTICAS DEL SISTEMA COMPLETO
# ============================================================================

DATABASE_STATS = {
    "archivo": "mi_sistema.db",
    "tamaño_kb": 132,
    "total_tablas": 13,
    "total_columnas": 163,
    "total_registros": 27,
    "foreign_keys": 6,
    "indices_totales": 15,
    "por_tabla": {
        "empresas": {"columnas": 16, "registros": 4, "fks": 0, "indices": 1},
        "usuarios": {"columnas": 33, "registros": 4, "fks": 1, "indices": 1},
        "portal_users": {"columnas": 5, "registros": 4, "fks": 0, "indices": 1},
        "formularios_importados": {
            "columnas": 6,
            "registros": 3,
            "fks": 0,
            "indices": 0,
        },
        "incapacidades": {"columnas": 9, "registros": 0, "fks": 1, "indices": 0},
        "tutelas": {"columnas": 10, "registros": 8, "fks": 1, "indices": 3},
        "pago_impuestos": {"columnas": 10, "registros": 3, "fks": 1, "indices": 2},
        "cotizaciones": {"columnas": 9, "registros": 0, "fks": 0, "indices": 3},
        "envios_planillas": {"columnas": 15, "registros": 0, "fks": 1, "indices": 3},
        "novedades": {"columnas": 33, "registros": 0, "fks": 0, "indices": 0},
        "credenciales_plataforma": {
            "columnas": 9,
            "registros": 1,
            "fks": 1,
            "indices": 1,
        },
        "depuraciones_pendientes": {
            "columnas": 8,
            "registros": 0,
            "fks": 0,
            "indices": 1,
        },
    },
}

# ============================================================================
# DIAGRAMA DE RELACIONES COMPLETO
# ============================================================================

RELATIONSHIPS_DIAGRAM = """
                            ┌──────────────────┐
                            │    empresas      │
                            │  (16 cols, 4)    │
                            │  PK: id          │
                            │  UK: nit   ◄─────┼─── Referenciado por 6 tablas
                            └──────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────┬──────────────┬──────────────┬──────────────┐
        │                           │                       │              │              │              │
        ▼                           ▼                       ▼              ▼              ▼              ▼
┌───────────────┐     ┌───────────────────┐    ┌────────────────┐  ┌────────────┐  ┌──────────────┐  ┌──────────────────────┐
│   usuarios    │     │  incapacidades    │    │    tutelas     │  │pago_impuest│  │envios_planil│  │credenciales_platform│
│ (33 cols, 4)  │     │   (9 cols, 0)     │    │  (10 cols, 8)  │  │(10 cols, 3)│  │(15 cols, 0) │  │   (9 cols, 1)       │
│ FK: empresa_nit│     │  FK: empresa_nit  │    │FK: empresa_nit │  │FK: empr_nit│  │FK: empr_nit │  │  FK: empresa_nit    │
└───────────────┘     └───────────────────┘    └────────────────┘  └────────────┘  └──────────────┘  └──────────────────────┘
     │ UK: (tipoId, numeroId)                         │ 3 índices        │2 índices      │3 índices         │1 índice
     │ 1 índice                                       │ 8 tutelas        │3 impuestos    │                  │1 credencial
     │ 4 empleados                                    │                  │               │                  │(ENCRIPTADA)
     
     
┌──────────────────┐    ┌───────────────────────┐    ┌──────────────────┐    ┌───────────────────────┐
│  portal_users    │    │formularios_importados │    │  cotizaciones    │    │depuraciones_pendientes│
│   (5 cols, 4)    │    │     (6 cols, 3)       │    │   (9 cols, 0)    │    │     (8 cols, 0)       │
│   UK: email      │    │                       │    │UK: id_cotizacion │    │                       │
│   (Werkzeug hash)│    │   (PDFs EPS)          │    │   (3 índices)    │    │   (1 índice comp.)    │
│   1 índice       │    │   0 índices           │    │                  │    │                       │
│   4 usuarios     │    │   3 formularios       │    │                  │    │                       │
└──────────────────┘    └───────────────────────┘    └──────────────────┘    └───────────────────────┘


                              ┌────────────────────────┐
                              │      novedades         │
                              │    (33 cols, 0)        │
                              │  ⚠️ SIN ÍNDICES        │
                              │  (Sistema de tickets)  │
                              └────────────────────────┘

Leyenda:
  PK = Primary Key
  FK = Foreign Key
  UK = Unique Key
  cols = columnas
  números = cantidad de registros
"""

# ============================================================================
# QUERIES ÚTILES PARA EL SISTEMA COMPLETO
# ============================================================================

USEFUL_QUERIES = {
    "dashboard_empresas": """
        SELECT 
            e.id,
            e.nombre_empresa,
            e.nit,
            e.ciudad_empresa,
            COUNT(DISTINCT u.id) as total_empleados,
            COUNT(DISTINCT t.id) as tutelas_activas,
            COUNT(DISTINCT pi.id) as impuestos_pendientes,
            SUM(COALESCE(u.afpCosto, 0) + COALESCE(u.epsCosto, 0) + 
                COALESCE(u.arlCosto, 0) + COALESCE(u.ccfCosto, 0)) as costos_mensuales
        FROM empresas e
        LEFT JOIN usuarios u ON e.nit = u.empresa_nit
        LEFT JOIN tutelas t ON e.nit = t.empresa_nit AND t.estado = 'En Proceso'
        LEFT JOIN pago_impuestos pi ON e.nit = pi.empresa_nit AND pi.estado = 'Pendiente de Pago'
        GROUP BY e.id, e.nombre_empresa, e.nit, e.ciudad_empresa
        ORDER BY total_empleados DESC;
    """,
    "usuarios_portal_activos": """
        SELECT 
            id,
            nombre,
            email,
            date(created_at) as fecha_registro,
            'Activo' as estado
        FROM portal_users
        ORDER BY created_at DESC;
    """,
    "tutelas_pendientes": """
        SELECT 
            t.id,
            t.empresa_nombre,
            t.usuario_nombre,
            t.motivo,
            date(t.fecha_radicacion) as radicacion,
            t.estado,
            julianday('now') - julianday(t.fecha_radicacion) as dias_transcurridos
        FROM tutelas t
        WHERE t.estado = 'En Proceso'
        ORDER BY t.fecha_radicacion ASC;
    """,
    "impuestos_vencimientos_proximos": """
        SELECT 
            pi.empresa_nombre,
            pi.tipo_impuesto,
            pi.periodo,
            date(pi.fecha_limite) as vencimiento,
            julianday(pi.fecha_limite) - julianday('now') as dias_restantes,
            pi.estado
        FROM pago_impuestos pi
        WHERE pi.estado = 'Pendiente de Pago'
          AND date(pi.fecha_limite) >= date('now')
        ORDER BY pi.fecha_limite ASC;
    """,
    "credenciales_por_empresa": """
        SELECT 
            e.nombre_empresa,
            e.nit,
            cp.plataforma,
            cp.usuario,
            date(cp.created_at) as fecha_registro
        FROM credenciales_plataforma cp
        INNER JOIN empresas e ON cp.empresa_nit = e.nit
        ORDER BY e.nombre_empresa, cp.plataforma;
    """,
    "novedades_abiertas": """
        SELECT 
            id,
            client as cliente,
            subject as asunto,
            priorityText as prioridad,
            status as estado,
            assignedTo as asignado_a,
            date(creationDate) as fecha_creacion,
            julianday('now') - julianday(creationDate) as dias_abierta
        FROM novedades
        WHERE status IN ('Abierta', 'En Proceso')
        ORDER BY priority ASC, creationDate ASC;
    """,
    "formularios_disponibles": """
        SELECT 
            nombre,
            nombre_archivo,
            date(created_at) as fecha_importacion
        FROM formularios_importados
        ORDER BY nombre;
    """,
    "verificar_integridad_usuarios_sin_empresa": """
        -- Usuarios huérfanos (sin empresa asignada)
        SELECT 
            u.id,
            u.primerNombre,
            u.primerApellido,
            u.numeroId,
            u.empresa_nit as nit_invalido
        FROM usuarios u
        LEFT JOIN empresas e ON u.empresa_nit = e.nit
        WHERE e.nit IS NULL OR u.empresa_nit IS NULL;
    """,
    "resumen_sistema_completo": """
        SELECT 
            'Empresas' as entidad, COUNT(*) as cantidad FROM empresas
        UNION ALL
        SELECT 'Empleados', COUNT(*) FROM usuarios
        UNION ALL
        SELECT 'Usuarios Portal', COUNT(*) FROM portal_users
        UNION ALL
        SELECT 'Formularios', COUNT(*) FROM formularios_importados
        UNION ALL
        SELECT 'Tutelas', COUNT(*) FROM tutelas
        UNION ALL
        SELECT 'Incapacidades', COUNT(*) FROM incapacidades
        UNION ALL
        SELECT 'Impuestos', COUNT(*) FROM pago_impuestos
        UNION ALL
        SELECT 'Cotizaciones', COUNT(*) FROM cotizaciones
        UNION ALL
        SELECT 'Envíos Planillas', COUNT(*) FROM envios_planillas
        UNION ALL
        SELECT 'Novedades', COUNT(*) FROM novedades
        UNION ALL
        SELECT 'Credenciales', COUNT(*) FROM credenciales_plataforma
        UNION ALL
        SELECT 'Depuraciones', COUNT(*) FROM depuraciones_pendientes;
    """,
}

# ============================================================================
# MEJORAS RECOMENDADAS - SISTEMA COMPLETO
# ============================================================================

RECOMMENDED_IMPROVEMENTS = {
    "CRITICAS": [
        {
            "prioridad": "🔴 CRÍTICA",
            "tabla": "novedades",
            "mejora": "Agregar índices en campos de búsqueda frecuente",
            "razon": "Tabla con 33 columnas SIN índices afecta performance",
            "sql": """
                CREATE INDEX idx_novedades_status ON novedades(status);
                CREATE INDEX idx_novedades_priority ON novedades(priority);
                CREATE INDEX idx_novedades_client ON novedades(client);
                CREATE INDEX idx_novedades_creation_date ON novedades(creationDate);
            """,
        },
        {
            "prioridad": "🔴 CRÍTICA",
            "tabla": "usuarios",
            "mejora": "Corregir usuarios sin empresa asignada (empresa_nit = NULL)",
            "razon": "Viola integridad referencial, 4 usuarios afectados",
            "sql": "-- Requiere análisis manual y asignación de empresa correcta",
        },
    ],
    "IMPORTANTES": [
        {
            "prioridad": "🟠 ALTA",
            "tabla": "formularios_importados",
            "mejora": "Agregar UNIQUE en nombre_archivo e índice",
            "razon": "Evitar PDFs duplicados",
            "sql": """
                CREATE UNIQUE INDEX idx_formularios_archivo 
                ON formularios_importados(nombre_archivo);
            """,
        },
        {
            "prioridad": "🟠 ALTA",
            "tabla": "incapacidades",
            "mejora": "Agregar índices de búsqueda",
            "sql": """
                CREATE INDEX idx_incapacidades_empresa ON incapacidades(empresa_nit);
                CREATE INDEX idx_incapacidades_estado ON incapacidades(estado);
            """,
        },
        {
            "prioridad": "🟠 MEDIA",
            "tabla": "credenciales_plataforma",
            "mejora": "Agregar UNIQUE compuesto",
            "sql": """
                CREATE UNIQUE INDEX idx_credenciales_unique 
                ON credenciales_plataforma(empresa_nit, plataforma, usuario);
            """,
        },
    ],
    "RECOMENDADAS": [
        {
            "prioridad": "🟡 BAJA",
            "tabla": "todas",
            "mejora": "Implementar Alembic para migraciones",
            "razon": "Facilitar evolución del esquema",
        },
        {
            "prioridad": "🟡 BAJA",
            "tabla": "novedades",
            "mejora": "Considerar normalizar en varias tablas",
            "razon": "33 columnas es demasiado, dificulta mantenimiento",
        },
    ],
}

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================


def get_table_info(table_name: str) -> dict:
    """Obtiene información de una tabla específica"""
    return TABLES_SCHEMA.get(table_name, {})


def get_all_tables() -> list:
    """Obtiene lista de todas las tablas"""
    return [t for t in TABLES_SCHEMA.keys()]


def get_tables_by_module(module: str) -> list:
    """Obtiene tablas de un módulo específico"""
    return [
        name for name, info in TABLES_SCHEMA.items() if info.get("modulo") == module
    ]


def get_all_modules() -> dict:
    """Obtiene todos los módulos del sistema"""
    return SYSTEM_MODULES


def print_schema_summary():
    """Imprime resumen del esquema completo"""
    print("=" * 80)
    print("RESUMEN DEL ESQUEMA - SISTEMA MONTERO COMPLETO")
    print("=" * 80)
    print(f"\nBase de datos: {DATABASE_INFO['nombre']}")
    print(f"Tamaño: {DATABASE_INFO['tamaño']}")
    print(f"Total tablas: {DATABASE_INFO['total_tablas']}")
    print(f"Total columnas: {DATABASE_INFO['total_columnas']}")
    print(f"Total registros: {DATABASE_INFO['total_registros']}")
    print(f"Foreign Keys: {DATABASE_INFO['foreign_keys']}")
    print(f"Índices: {DATABASE_INFO['indices']}")

    print(f"\n📊 Módulos del Sistema:")
    for module, info in SYSTEM_MODULES.items():
        print(f"  • {module}: {len(info['tablas'])} tablas")

    print(f"\n🔗 Relaciones:")
    print(f"  • empresas es referenciada por 6 tablas")

    print("\n⚠️  Problemas Críticos:")
    for mejora in RECOMMENDED_IMPROVEMENTS["CRITICAS"]:
        print(f"  • {mejora['tabla']}: {mejora['mejora']}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    print_schema_summary()
    print("\n📋 Diagrama de relaciones:")
    print(RELATIONSHIPS_DIAGRAM)
    print("\n✅ Documentación del esquema COMPLETO generada exitosamente")
