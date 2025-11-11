"""
📊 DOCUMENTACIÓN DEL ESQUEMA DE BASE DE DATOS - SISTEMA MONTERO
================================================================

Archivo: database_schema.py
Ubicación: config/database_schema.py
Propósito: Documentar la estructura completa de la base de datos SQLite
Fecha de creación: 30 de octubre de 2025
Sistema: Sistema de Gestión Montero
Base de datos: SQLite (database.db)

Este archivo documenta todas las tablas, columnas, relaciones y restricciones
de la base de datos del sistema.
"""

# ============================================================================
# INFORMACIÓN GENERAL DE LA BASE DE DATOS
# ============================================================================

DATABASE_INFO = {
    "nombre": "database.db",
    "tipo": "SQLite",
    "version": "3.x",
    "ubicacion": "RUTA_BASE_DE_DATOS/database.db (ver config_rutas.py)",
    "charset": "UTF-8",
    "total_tablas": 4,
    "descripcion": "Base de datos principal del sistema de gestión Montero que almacena información de empresas, empleados, formularios y relaciones laborales",
}

# ============================================================================
# ESQUEMA DE TABLAS
# ============================================================================

TABLES_SCHEMA = {
    # ------------------------------------------------------------------------
    # TABLA: empresas
    # Propósito: Almacena información de las empresas clientes
    # ------------------------------------------------------------------------
    "empresas": {
        "descripcion": "Registro de empresas cliente con información legal y de contacto",
        "tipo": "Tabla principal",
        "relaciones": [
            "Tiene relación 1:N con 'usuarios' (una empresa puede tener múltiples empleados)"
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
            },
            "tipo_identificacion_empresa": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Tipo de documento (NIT, RUT, etc.)",
            },
            "nit": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "unique": False,  # ⚠️ NOTA: Debería ser UNIQUE
                "descripcion": "Número de Identificación Tributaria - CLAVE FORÁNEA para usuarios",
            },
            "direccion_empresa": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Dirección física de la empresa",
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
        "indices": [],  # ⚠️ RECOMENDACIÓN: Crear índice en 'nit'
        "constraints": ["PRIMARY KEY (id)"],
        "notas": [
            "⚠️ MEJORA RECOMENDADA: Agregar restricción UNIQUE en campo 'nit'",
            "⚠️ MEJORA RECOMENDADA: Hacer campos críticos NOT NULL (nombre_empresa, nit)",
            "⚠️ MEJORA RECOMENDADA: Agregar validación de formato de email en 'correo_empresa'",
            "⚠️ MEJORA RECOMENDADA: Cambiar 'created_at' por tipo DATETIME real o INTEGER (timestamp)",
        ],
    },
    # ------------------------------------------------------------------------
    # TABLA: usuarios
    # Propósito: Almacena información de empleados/usuarios del sistema
    # ------------------------------------------------------------------------
    "usuarios": {
        "descripcion": "Registro de empleados con información personal, laboral y de seguridad social",
        "tipo": "Tabla principal",
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
            },
            "tipoId": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Tipo de identificación (CC, TI, CE, etc.)",
            },
            "numeroId": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Número de documento de identidad",
            },
            "primerNombre": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Primer nombre del empleado",
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
        "indices": [],  # ⚠️ RECOMENDACIÓN: Crear índices en numeroId, empresa_nit, correoElectronico
        "constraints": [
            "PRIMARY KEY (id)",
            "FOREIGN KEY (empresa_nit) REFERENCES empresas(nit)",
        ],
        "notas": [
            "⚠️ MEJORA RECOMENDADA: Hacer NOT NULL campos críticos (tipoId, numeroId, primerNombre, primerApellido, empresa_nit)",
            "⚠️ MEJORA RECOMENDADA: Agregar UNIQUE en (tipoId, numeroId) para evitar duplicados",
            "⚠️ MEJORA RECOMENDADA: Validar formato de email en 'correoElectronico'",
            "⚠️ MEJORA RECOMENDADA: Usar INTEGER para fechas (timestamp Unix) en lugar de TEXT",
            "⚠️ MEJORA RECOMENDADA: Agregar campo 'estado' (activo/inactivo)",
            "⚠️ MEJORA RECOMENDADA: Normalizar datos de seguridad social en tablas separadas",
        ],
    },
    # ------------------------------------------------------------------------
    # TABLA: formularios_importados
    # Propósito: Registro de formularios PDF importados al sistema
    # ------------------------------------------------------------------------
    "formularios_importados": {
        "descripcion": "Registro de formularios PDF importados con su configuración de mapeo",
        "tipo": "Tabla de control",
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
                "nullable": False,
                "default": None,
                "descripcion": "Nombre descriptivo del formulario",
            },
            "nombre_archivo": {
                "tipo": "TEXT",
                "nullable": False,
                "default": None,
                "descripcion": "Nombre del archivo PDF original",
            },
            "ruta_archivo": {
                "tipo": "TEXT",
                "nullable": False,
                "default": None,
                "descripcion": "Ruta completa donde se almacena el archivo",
            },
            "campos_mapeados": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "JSON con la configuración de mapeo de campos del formulario",
            },
            "created_at": {
                "tipo": "TEXT",
                "nullable": True,
                "default": "CURRENT_TIMESTAMP",
                "descripcion": "Fecha y hora de importación del formulario",
            },
        },
        "indices": [],  # ⚠️ RECOMENDACIÓN: Crear índice en nombre_archivo
        "constraints": ["PRIMARY KEY (id)"],
        "notas": [
            "✅ BIEN: Campos críticos ya tienen NOT NULL",
            "⚠️ MEJORA RECOMENDADA: Agregar UNIQUE en nombre_archivo",
            "⚠️ MEJORA RECOMENDADA: Validar que campos_mapeados sea JSON válido",
            "⚠️ MEJORA RECOMENDADA: Agregar campo 'estado' (activo/archivado)",
            "💡 CONSIDERAR: Agregar campo 'version' para control de cambios",
        ],
    },
    # ------------------------------------------------------------------------
    # TABLA: sqlite_sequence
    # Propósito: Tabla interna de SQLite (NO MODIFICAR)
    # ------------------------------------------------------------------------
    "sqlite_sequence": {
        "descripcion": "Tabla interna de SQLite para controlar secuencias AUTOINCREMENT",
        "tipo": "Sistema (SQLite interno)",
        "relaciones": [],
        "columnas": {
            "name": {
                "tipo": "TEXT",
                "nullable": True,
                "default": None,
                "descripcion": "Nombre de la tabla con AUTOINCREMENT",
            },
            "seq": {
                "tipo": "INTEGER",
                "nullable": True,
                "default": None,
                "descripcion": "Último valor de secuencia usado",
            },
        },
        "indices": [],
        "constraints": [],
        "notas": [
            "⚠️ NO MODIFICAR: Esta tabla es gestionada automáticamente por SQLite",
            "📖 INFORMACIÓN: Almacena el último ID generado para cada tabla con AUTOINCREMENT",
        ],
    },
}

# ============================================================================
# DIAGRAMA DE RELACIONES
# ============================================================================

RELATIONSHIPS_DIAGRAM = """
┌─────────────────────────────┐
│        empresas             │
│─────────────────────────────│
│ 🔑 id (PK)                  │
│ 📌 nit (FK referenciado)    │◄─────┐
│    nombre_empresa           │      │
│    tipo_identificacion      │      │
│    direccion_empresa        │      │ 1:N
│    telefono_empresa         │      │
│    correo_empresa           │      │
│    ...                      │      │
└─────────────────────────────┘      │
                                      │
                                      │
┌─────────────────────────────┐      │
│         usuarios            │      │
│─────────────────────────────│      │
│ 🔑 id (PK)                  │      │
│ 🔗 empresa_nit (FK) ────────┼──────┘
│    tipoId                   │
│    numeroId                 │
│    primerNombre             │
│    segundoNombre            │
│    primerApellido           │
│    segundoApellido          │
│    ...                      │
│    (32+ campos)             │
└─────────────────────────────┘

┌─────────────────────────────┐
│  formularios_importados     │
│─────────────────────────────│
│ 🔑 id (PK)                  │
│    nombre                   │
│    nombre_archivo           │
│    ruta_archivo             │
│    campos_mapeados (JSON)   │
│    created_at               │
└─────────────────────────────┘
     (Sin relaciones FK)

Leyenda:
🔑 = Primary Key
🔗 = Foreign Key
📌 = Campo referenciado por FK
"""

# ============================================================================
# ESTADÍSTICAS DE LA BASE DE DATOS
# ============================================================================

DATABASE_STATS = {
    "total_tablas": 4,
    "tablas_principales": 3,
    "tablas_sistema": 1,
    "total_columnas": {
        "empresas": 16,
        "usuarios": 33,
        "formularios_importados": 6,
        "sqlite_sequence": 2,
    },
    "relaciones_foreign_key": 1,
    "indices_definidos": 0,  # ⚠️ Ningún índice adicional creado
    "registros_actuales": {"empresas": 0, "usuarios": 0, "formularios_importados": 0},
}

# ============================================================================
# MEJORAS RECOMENDADAS DE ALTO IMPACTO
# ============================================================================

RECOMMENDED_IMPROVEMENTS = {
    "CRITICAS": [
        {
            "prioridad": "🔴 ALTA",
            "tabla": "empresas",
            "mejora": "Agregar constraint UNIQUE en campo 'nit'",
            "razon": "El NIT es único por empresa y se usa como FK en usuarios",
            "sql": "CREATE UNIQUE INDEX idx_empresas_nit ON empresas(nit);",
        },
        {
            "prioridad": "🔴 ALTA",
            "tabla": "usuarios",
            "mejora": "Agregar constraint UNIQUE en (tipoId, numeroId)",
            "razon": "Evitar registros duplicados del mismo empleado",
            "sql": "CREATE UNIQUE INDEX idx_usuarios_documento ON usuarios(tipoId, numeroId);",
        },
        {
            "prioridad": "🔴 ALTA",
            "tabla": "empresas",
            "mejora": "Hacer NOT NULL campos críticos",
            "razon": "Garantizar integridad de datos esenciales",
            "sql": "ALTER TABLE requiere recrear tabla - ver script de migración",
        },
    ],
    "IMPORTANTES": [
        {
            "prioridad": "🟠 MEDIA",
            "tabla": "usuarios",
            "mejora": "Crear índice en empresa_nit",
            "razon": "Mejorar performance en consultas por empresa",
            "sql": "CREATE INDEX idx_usuarios_empresa ON usuarios(empresa_nit);",
        },
        {
            "prioridad": "🟠 MEDIA",
            "tabla": "usuarios",
            "mejora": "Crear índice en correoElectronico",
            "razon": "Búsquedas frecuentes por email",
            "sql": "CREATE INDEX idx_usuarios_email ON usuarios(correoElectronico);",
        },
        {
            "prioridad": "🟠 MEDIA",
            "tabla": "formularios_importados",
            "mejora": "Agregar UNIQUE en nombre_archivo",
            "razon": "Evitar importar el mismo formulario dos veces",
            "sql": "CREATE UNIQUE INDEX idx_formularios_archivo ON formularios_importados(nombre_archivo);",
        },
    ],
    "RECOMENDADAS": [
        {
            "prioridad": "🟡 BAJA",
            "tabla": "todas",
            "mejora": "Cambiar campos de fecha TEXT a INTEGER (timestamp)",
            "razon": "Mejor performance y facilidad para ordenar/filtrar fechas",
            "sql": "Ver script de migración",
        },
        {
            "prioridad": "🟡 BAJA",
            "tabla": "usuarios",
            "mejora": "Normalizar datos de seguridad social en tablas separadas",
            "razon": "Evitar redundancia (AFP, EPS, ARL se repiten)",
            "sql": "Crear tablas: afp_catalogo, eps_catalogo, arl_catalogo",
        },
    ],
}

# ============================================================================
# QUERIES ÚTILES PARA ADMINISTRACIÓN
# ============================================================================

USEFUL_QUERIES = {
    "listar_empresas_con_empleados": """
        SELECT 
            e.id,
            e.nombre_empresa,
            e.nit,
            COUNT(u.id) as total_empleados
        FROM empresas e
        LEFT JOIN usuarios u ON e.nit = u.empresa_nit
        GROUP BY e.id, e.nombre_empresa, e.nit
        ORDER BY total_empleados DESC;
    """,
    "empleados_por_empresa": """
        SELECT 
            u.id,
            u.tipoId,
            u.numeroId,
            u.primerNombre || ' ' || u.primerApellido as nombre_completo,
            u.correoElectronico,
            u.fechaIngreso,
            e.nombre_empresa
        FROM usuarios u
        INNER JOIN empresas e ON u.empresa_nit = e.nit
        WHERE e.nit = ?
        ORDER BY u.fechaIngreso DESC;
    """,
    "total_costos_seguridad_social_por_empresa": """
        SELECT 
            e.nombre_empresa,
            e.nit,
            COUNT(u.id) as total_empleados,
            SUM(u.afpCosto) as total_afp,
            SUM(u.epsCosto) as total_eps,
            SUM(u.arlCosto) as total_arl,
            SUM(u.ccfCosto) as total_ccf,
            SUM(u.afpCosto + u.epsCosto + u.arlCosto + u.ccfCosto) as total_costos
        FROM empresas e
        INNER JOIN usuarios u ON e.nit = u.empresa_nit
        GROUP BY e.nombre_empresa, e.nit
        ORDER BY total_costos DESC;
    """,
    "formularios_recientes": """
        SELECT 
            id,
            nombre,
            nombre_archivo,
            created_at
        FROM formularios_importados
        ORDER BY created_at DESC
        LIMIT 10;
    """,
    "verificar_integridad_foreign_keys": """
        -- Buscar usuarios huérfanos (sin empresa)
        SELECT 
            u.id,
            u.primerNombre,
            u.primerApellido,
            u.empresa_nit as nit_invalido
        FROM usuarios u
        LEFT JOIN empresas e ON u.empresa_nit = e.nit
        WHERE e.nit IS NULL;
    """,
}

# ============================================================================
# SCRIPT DE MIGRACIÓN PARA MEJORAS
# ============================================================================

MIGRATION_SCRIPT = """
-- ================================================================
-- SCRIPT DE MIGRACIÓN: Mejoras de esquema database.db
-- Fecha: 30 de octubre de 2025
-- IMPORTANTE: Hacer backup antes de ejecutar
-- ================================================================

-- 1. Crear índices recomendados
-- ----------------------------------------------------------------
CREATE UNIQUE INDEX IF NOT EXISTS idx_empresas_nit 
    ON empresas(nit);

CREATE UNIQUE INDEX IF NOT EXISTS idx_usuarios_documento 
    ON usuarios(tipoId, numeroId);

CREATE INDEX IF NOT EXISTS idx_usuarios_empresa 
    ON usuarios(empresa_nit);

CREATE INDEX IF NOT EXISTS idx_usuarios_email 
    ON usuarios(correoElectronico);

CREATE UNIQUE INDEX IF NOT EXISTS idx_formularios_archivo 
    ON formularios_importados(nombre_archivo);

-- 2. Verificar integridad referencial
-- ----------------------------------------------------------------
PRAGMA foreign_keys = ON;

-- 3. Crear tabla de auditoría (opcional pero recomendada)
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tabla TEXT NOT NULL,
    registro_id INTEGER NOT NULL,
    accion TEXT NOT NULL CHECK(accion IN ('INSERT', 'UPDATE', 'DELETE')),
    usuario TEXT,
    fecha_hora TEXT DEFAULT CURRENT_TIMESTAMP,
    datos_anteriores TEXT,
    datos_nuevos TEXT
);

-- 4. Agregar columnas de auditoría a tablas principales (opcional)
-- ----------------------------------------------------------------
-- Nota: SQLite no soporta ALTER COLUMN, se debe recrear la tabla
-- Este es un ejemplo conceptual - requiere migración completa

-- ALTER TABLE empresas ADD COLUMN updated_at TEXT;
-- ALTER TABLE empresas ADD COLUMN updated_by TEXT;
-- ALTER TABLE usuarios ADD COLUMN updated_at TEXT;
-- ALTER TABLE usuarios ADD COLUMN updated_by TEXT;

-- 5. Verificar resultados
-- ----------------------------------------------------------------
SELECT 'Índices creados exitosamente' as mensaje;

-- Listar todos los índices
SELECT name, tbl_name, sql 
FROM sqlite_master 
WHERE type = 'index' 
  AND tbl_name IN ('empresas', 'usuarios', 'formularios_importados');
"""

# ============================================================================
# FUNCIONES AUXILIARES PARA TRABAJAR CON EL ESQUEMA
# ============================================================================


def get_table_info(table_name: str) -> dict:
    """
    Obtiene información detallada de una tabla específica.

    Args:
        table_name: Nombre de la tabla

    Returns:
        dict: Información completa de la tabla
    """
    return TABLES_SCHEMA.get(table_name, {})


def get_all_tables() -> list:
    """
    Obtiene lista de todas las tablas.

    Returns:
        list: Lista de nombres de tablas
    """
    return [table for table in TABLES_SCHEMA.keys() if table != "sqlite_sequence"]


def get_foreign_keys() -> dict:
    """
    Obtiene todas las relaciones de foreign keys del esquema.

    Returns:
        dict: Diccionario con las relaciones FK
    """
    fk_relations = {}
    for table_name, table_info in TABLES_SCHEMA.items():
        for col_name, col_info in table_info.get("columnas", {}).items():
            if "foreign_key" in col_info:
                if table_name not in fk_relations:
                    fk_relations[table_name] = []
                fk_relations[table_name].append(
                    {"columna": col_name, "referencia": col_info["foreign_key"]}
                )
    return fk_relations


def print_schema_summary():
    """
    Imprime un resumen del esquema de la base de datos.
    """
    print("=" * 70)
    print("RESUMEN DEL ESQUEMA DE BASE DE DATOS - SISTEMA MONTERO")
    print("=" * 70)
    print(f"\nBase de datos: {DATABASE_INFO['nombre']}")
    print(f"Tipo: {DATABASE_INFO['tipo']}")
    print(f"Total de tablas: {DATABASE_STATS['total_tablas']}")
    print(f"\nTablas principales:")
    for table in get_all_tables():
        info = get_table_info(table)
        cols = len(info.get("columnas", {}))
        print(f"  • {table:<30} ({cols} columnas)")

    print(f"\n🔗 Relaciones Foreign Key: {DATABASE_STATS['relaciones_foreign_key']}")
    fks = get_foreign_keys()
    for table, relations in fks.items():
        for rel in relations:
            print(f"  • {table}.{rel['columna']} → {rel['referencia']}")

    print("\n⚠️  Mejoras críticas recomendadas:")
    for mejora in RECOMMENDED_IMPROVEMENTS["CRITICAS"]:
        print(f"  • {mejora['prioridad']} {mejora['tabla']}: {mejora['mejora']}")

    print("\n" + "=" * 70)


# ============================================================================
# EJECUCIÓN DE EJEMPLO
# ============================================================================

if __name__ == "__main__":
    print_schema_summary()
    print("\n📋 Diagrama de relaciones:")
    print(RELATIONSHIPS_DIAGRAM)
    print("\n✅ Documentación del esquema generada exitosamente")
    print("📁 Guardar este archivo en: config/database_schema.py")
