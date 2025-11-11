-- ================================================================
-- SCRIPT DE CREACIÓN DE BASE DE DATOS - SISTEMA MONTERO
-- ================================================================
-- Archivo: create_database.sql
-- Propósito: Script completo para crear la estructura de la BD
-- Fecha: 30 de octubre de 2025
-- Base de datos: SQLite
-- ================================================================

-- Activar foreign keys (importante en SQLite)
PRAGMA foreign_keys = ON;
PRAGMA encoding = "UTF-8";

-- ================================================================
-- TABLA: empresas
-- Propósito: Almacena información de empresas cliente
-- ================================================================

CREATE TABLE IF NOT EXISTS empresas (
    -- Identificación
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_empresa TEXT NOT NULL,
    tipo_identificacion_empresa TEXT,
    nit TEXT NOT NULL UNIQUE,  -- ✅ AGREGADO UNIQUE
    
    -- Información de contacto
    direccion_empresa TEXT,
    telefono_empresa TEXT,
    correo_empresa TEXT,
    departamento_empresa TEXT,
    ciudad_empresa TEXT,
    
    -- Información financiera/laboral
    ibc_empresa REAL,
    afp_empresa TEXT,
    arl_empresa TEXT,
    
    -- Representante legal
    rep_legal_nombre TEXT,
    rep_legal_tipo_id TEXT,
    rep_legal_numero_id TEXT,
    
    -- Auditoría
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Índices para empresas
CREATE INDEX IF NOT EXISTS idx_empresas_nombre 
    ON empresas(nombre_empresa);

-- ================================================================
-- TABLA: usuarios (empleados)
-- Propósito: Almacena información de empleados
-- ================================================================

CREATE TABLE IF NOT EXISTS usuarios (
    -- Identificación
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_nit TEXT NOT NULL,  -- ✅ AGREGADO NOT NULL
    tipoId TEXT NOT NULL,  -- ✅ AGREGADO NOT NULL
    numeroId TEXT NOT NULL,  -- ✅ AGREGADO NOT NULL
    
    -- Información personal
    primerNombre TEXT NOT NULL,  -- ✅ AGREGADO NOT NULL
    segundoNombre TEXT,
    primerApellido TEXT NOT NULL,  -- ✅ AGREGADO NOT NULL
    segundoApellido TEXT,
    sexoBiologico TEXT,
    sexoIdentificacion TEXT,
    nacionalidad TEXT,
    
    -- Información de nacimiento
    fechaNacimiento TEXT,
    paisNacimiento TEXT,
    departamentoNacimiento TEXT,
    municipioNacimiento TEXT,
    
    -- Información de contacto
    direccion TEXT,
    telefonoCelular TEXT,
    telefonoFijo TEXT,
    correoElectronico TEXT,
    comunaBarrio TEXT,
    
    -- Información de seguridad social
    afpNombre TEXT,
    afpCosto REAL DEFAULT 0,
    epsNombre TEXT,
    epsCosto REAL DEFAULT 0,
    arlNombre TEXT,
    arlCosto REAL DEFAULT 0,
    ccfNombre TEXT,
    ccfCosto REAL DEFAULT 0,
    
    -- Información laboral
    administracion TEXT,
    ibc REAL,
    claseRiesgoARL TEXT,
    fechaIngreso TEXT,
    
    -- Auditoría
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    
    -- Restricciones
    FOREIGN KEY (empresa_nit) REFERENCES empresas(nit) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE,
    
    -- ✅ CONSTRAINT ÚNICO para evitar duplicados
    UNIQUE(tipoId, numeroId)
);

-- Índices para usuarios
CREATE INDEX IF NOT EXISTS idx_usuarios_empresa 
    ON usuarios(empresa_nit);

CREATE INDEX IF NOT EXISTS idx_usuarios_nombre 
    ON usuarios(primerNombre, primerApellido);

CREATE INDEX IF NOT EXISTS idx_usuarios_email 
    ON usuarios(correoElectronico);

-- ================================================================
-- TABLA: formularios_importados
-- Propósito: Registro de formularios PDF importados
-- ================================================================

CREATE TABLE IF NOT EXISTS formularios_importados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    nombre_archivo TEXT NOT NULL UNIQUE,  -- ✅ AGREGADO UNIQUE
    ruta_archivo TEXT NOT NULL,
    campos_mapeados TEXT,  -- JSON
    
    -- Auditoría
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Índices para formularios_importados
CREATE INDEX IF NOT EXISTS idx_formularios_nombre 
    ON formularios_importados(nombre);

-- ================================================================
-- TABLA: audit_log (NUEVA - para auditoría)
-- Propósito: Registro de cambios en la base de datos
-- ================================================================

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tabla TEXT NOT NULL,
    registro_id INTEGER NOT NULL,
    accion TEXT NOT NULL CHECK(accion IN ('INSERT', 'UPDATE', 'DELETE')),
    usuario TEXT,
    fecha_hora TEXT DEFAULT CURRENT_TIMESTAMP,
    datos_anteriores TEXT,  -- JSON
    datos_nuevos TEXT  -- JSON
);

-- Índices para audit_log
CREATE INDEX IF NOT EXISTS idx_audit_tabla_fecha 
    ON audit_log(tabla, fecha_hora);

CREATE INDEX IF NOT EXISTS idx_audit_registro 
    ON audit_log(tabla, registro_id);

-- ================================================================
-- VISTAS ÚTILES
-- ================================================================

-- Vista: Listado completo de empleados con su empresa
CREATE VIEW IF NOT EXISTS v_empleados_completo AS
SELECT 
    u.id,
    u.tipoId,
    u.numeroId,
    u.primerNombre || ' ' || 
    COALESCE(u.segundoNombre || ' ', '') || 
    u.primerApellido || ' ' || 
    COALESCE(u.segundoApellido, '') as nombre_completo,
    u.correoElectronico,
    u.telefonoCelular,
    u.fechaIngreso,
    u.ibc,
    e.nombre_empresa,
    e.nit as empresa_nit,
    e.ciudad_empresa,
    (COALESCE(u.afpCosto, 0) + 
     COALESCE(u.epsCosto, 0) + 
     COALESCE(u.arlCosto, 0) + 
     COALESCE(u.ccfCosto, 0)) as costo_total_seguridad_social
FROM usuarios u
INNER JOIN empresas e ON u.empresa_nit = e.nit;

-- Vista: Resumen de empresas con conteo de empleados
CREATE VIEW IF NOT EXISTS v_empresas_resumen AS
SELECT 
    e.id,
    e.nombre_empresa,
    e.nit,
    e.ciudad_empresa,
    e.correo_empresa,
    e.telefono_empresa,
    COUNT(u.id) as total_empleados,
    SUM(COALESCE(u.afpCosto, 0)) as total_afp,
    SUM(COALESCE(u.epsCosto, 0)) as total_eps,
    SUM(COALESCE(u.arlCosto, 0)) as total_arl,
    SUM(COALESCE(u.ccfCosto, 0)) as total_ccf,
    SUM(
        COALESCE(u.afpCosto, 0) + 
        COALESCE(u.epsCosto, 0) + 
        COALESCE(u.arlCosto, 0) + 
        COALESCE(u.ccfCosto, 0)
    ) as costo_total_mensual
FROM empresas e
LEFT JOIN usuarios u ON e.nit = u.empresa_nit
GROUP BY e.id, e.nombre_empresa, e.nit, e.ciudad_empresa, e.correo_empresa, e.telefono_empresa;

-- ================================================================
-- TRIGGERS (para mantener updated_at actualizado)
-- ================================================================

-- Trigger para empresas
CREATE TRIGGER IF NOT EXISTS trg_empresas_updated_at
AFTER UPDATE ON empresas
FOR EACH ROW
BEGIN
    UPDATE empresas 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;

-- Trigger para usuarios
CREATE TRIGGER IF NOT EXISTS trg_usuarios_updated_at
AFTER UPDATE ON usuarios
FOR EACH ROW
BEGIN
    UPDATE usuarios 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;

-- Trigger para formularios
CREATE TRIGGER IF NOT EXISTS trg_formularios_updated_at
AFTER UPDATE ON formularios_importados
FOR EACH ROW
BEGIN
    UPDATE formularios_importados 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;

-- ================================================================
-- DATOS DE EJEMPLO (OPCIONAL - comentar en producción)
-- ================================================================

/*
-- Empresa de ejemplo
INSERT INTO empresas (
    nombre_empresa, 
    tipo_identificacion_empresa, 
    nit, 
    direccion_empresa, 
    ciudad_empresa,
    departamento_empresa,
    correo_empresa,
    telefono_empresa
) VALUES (
    'Empresa Demo S.A.S',
    'NIT',
    '900123456-7',
    'Calle 123 #45-67',
    'Cali',
    'Valle del Cauca',
    'contacto@demo.com',
    '3001234567'
);

-- Usuario de ejemplo
INSERT INTO usuarios (
    empresa_nit,
    tipoId,
    numeroId,
    primerNombre,
    primerApellido,
    correoElectronico,
    telefonoCelular,
    fechaIngreso
) VALUES (
    '900123456-7',
    'CC',
    '1234567890',
    'Juan',
    'Pérez',
    'juan.perez@demo.com',
    '3109876543',
    '2025-01-15'
);
*/

-- ================================================================
-- VERIFICACIÓN FINAL
-- ================================================================

-- Verificar que las tablas se crearon correctamente
SELECT 'Tablas creadas:' as mensaje;
SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;

-- Verificar índices
SELECT 'Índices creados:' as mensaje;
SELECT name, tbl_name FROM sqlite_master WHERE type='index' ORDER BY tbl_name, name;

-- Verificar vistas
SELECT 'Vistas creadas:' as mensaje;
SELECT name FROM sqlite_master WHERE type='view' ORDER BY name;

-- Verificar triggers
SELECT 'Triggers creados:' as mensaje;
SELECT name FROM sqlite_master WHERE type='trigger' ORDER BY name;

SELECT '✅ Base de datos creada exitosamente' as mensaje;
