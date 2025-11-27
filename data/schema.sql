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

    -- Autenticación y autorización (AGREGADO)
    password_hash TEXT,
    estado TEXT DEFAULT 'activo',
    role TEXT DEFAULT 'empleado',
    username TEXT UNIQUE,

    -- Auditoría
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP,
    
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
-- TABLA: pago_impuestos
-- Propósito: Registros de formularios de impuestos subidos
-- ================================================================

CREATE TABLE IF NOT EXISTS pago_impuestos (
    -- Identificación
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_nit TEXT NOT NULL,
    empresa_nombre TEXT NOT NULL,

    -- Información del impuesto
    tipo_impuesto TEXT NOT NULL,
    periodo TEXT NOT NULL,
    fecha_limite TEXT NOT NULL,

    -- Estado y archivo
    estado TEXT DEFAULT 'Pendiente de Pago' CHECK(estado IN ('Pendiente de Pago', 'Pagado', 'Vencido')),
    ruta_archivo TEXT,

    -- Auditoría
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Key
    FOREIGN KEY (empresa_nit) REFERENCES empresas(nit) ON DELETE CASCADE
);

-- Índices para pago_impuestos
CREATE INDEX IF NOT EXISTS idx_impuestos_empresa
    ON pago_impuestos(empresa_nit);

CREATE INDEX IF NOT EXISTS idx_impuestos_tipo
    ON pago_impuestos(tipo_impuesto);

CREATE INDEX IF NOT EXISTS idx_impuestos_estado
    ON pago_impuestos(estado);

CREATE INDEX IF NOT EXISTS idx_impuestos_fecha_limite
    ON pago_impuestos(fecha_limite);

-- ================================================================
-- TABLA: tutelas
-- Propósito: Gestionar procesos de tutela de empleados
-- ================================================================

CREATE TABLE IF NOT EXISTS tutelas (
    -- Identificación
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    numero_tutela TEXT UNIQUE,
    juzgado TEXT,

    -- Fechas del proceso
    fecha_notificacion TEXT,
    fecha_inicio TEXT,
    fecha_fin TEXT,

    -- Información financiera
    valor_total REAL,
    valor_cuota REAL,
    numero_cuotas INTEGER,
    cuotas_pagadas INTEGER DEFAULT 0,
    saldo_pendiente REAL,

    -- Estado y documentación
    estado TEXT,
    documento_soporte TEXT,  -- Ruta del PDF/documento soporte
    observaciones TEXT,

    -- Auditoría
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Key
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Índices para tutelas
CREATE INDEX IF NOT EXISTS idx_tutelas_usuario
    ON tutelas(usuario_id);

CREATE INDEX IF NOT EXISTS idx_tutelas_estado
    ON tutelas(estado);

CREATE INDEX IF NOT EXISTS idx_tutelas_numero
    ON tutelas(numero_tutela);

-- ================================================================
-- TABLA: documentos_gestor
-- Propósito: Repositorio central de archivos del sistema
-- ================================================================

CREATE TABLE IF NOT EXISTS documentos_gestor (
    -- Identificación
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_archivo TEXT NOT NULL,
    nombre_interno TEXT NOT NULL UNIQUE,  -- Hash para evitar duplicados
    ruta TEXT NOT NULL,

    -- Clasificación
    categoria TEXT NOT NULL CHECK(categoria IN ('Legal', 'Contable', 'RRHH', 'Operativo', 'Otro')),
    tipo_mime TEXT,
    tamano_bytes INTEGER,

    -- Auditoría
    fecha_subida TEXT DEFAULT CURRENT_TIMESTAMP,
    subido_por INTEGER NOT NULL,  -- ID del usuario
    subido_por_nombre TEXT,  -- Redundancia útil

    -- Metadata
    descripcion TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Key
    FOREIGN KEY (subido_por) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Índices para documentos_gestor
CREATE INDEX IF NOT EXISTS idx_documentos_categoria
    ON documentos_gestor(categoria);

CREATE INDEX IF NOT EXISTS idx_documentos_subido_por
    ON documentos_gestor(subido_por);

CREATE INDEX IF NOT EXISTS idx_documentos_fecha
    ON documentos_gestor(fecha_subida);

-- ================================================================
-- TABLA: auditoria_logs
-- Propósito: Registro de actividad y seguridad del sistema
-- ================================================================

CREATE TABLE IF NOT EXISTS auditoria_logs (
    -- Identificación
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Usuario
    usuario_id INTEGER,
    usuario_nombre TEXT NOT NULL,  -- Redundancia útil para histórico

    -- Acción
    accion TEXT NOT NULL,  -- Ej: "Login", "Logout", "Crear Usuario", "Eliminar Archivo"
    detalle TEXT,  -- JSON o texto con información adicional
    resultado TEXT CHECK(resultado IN ('exito', 'error', 'advertencia')),  -- Estado de la acción

    -- Contexto técnico
    ip_address TEXT,
    user_agent TEXT,
    metodo_http TEXT,  -- GET, POST, PUT, DELETE
    ruta TEXT,  -- URL accedida

    -- Metadata
    fecha_hora TEXT DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Key (opcional, puede ser NULL si el usuario fue eliminado)
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
);

-- Índices para auditoria_logs
CREATE INDEX IF NOT EXISTS idx_auditoria_usuario
    ON auditoria_logs(usuario_id);

CREATE INDEX IF NOT EXISTS idx_auditoria_accion
    ON auditoria_logs(accion);

CREATE INDEX IF NOT EXISTS idx_auditoria_fecha
    ON auditoria_logs(fecha_hora DESC);

CREATE INDEX IF NOT EXISTS idx_auditoria_resultado
    ON auditoria_logs(resultado);

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

-- Trigger para pago_impuestos
CREATE TRIGGER IF NOT EXISTS trg_pago_impuestos_updated_at
AFTER UPDATE ON pago_impuestos
FOR EACH ROW
BEGIN
    UPDATE pago_impuestos
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

-- Trigger para documentos_gestor
CREATE TRIGGER IF NOT EXISTS trg_documentos_gestor_updated_at
AFTER UPDATE ON documentos_gestor
FOR EACH ROW
BEGIN
    UPDATE documentos_gestor
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
-- MÓDULO DE MARKETING (Growth)
-- ================================================================

-- ================================================================
-- TABLA: marketing_redes
-- Propósito: Gestionar enlaces y presencia en redes sociales
-- ================================================================

CREATE TABLE IF NOT EXISTS marketing_redes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plataforma TEXT NOT NULL,  -- Facebook, Instagram, LinkedIn, TikTok, Web, etc.
    url TEXT NOT NULL,
    seguidores INTEGER DEFAULT 0,
    estado TEXT DEFAULT 'Activo',  -- Activo, Inactivo
    descripcion TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Índice para búsquedas por plataforma
CREATE INDEX IF NOT EXISTS idx_marketing_redes_plataforma 
    ON marketing_redes(plataforma);

-- ================================================================
-- TABLA: marketing_campanas
-- Propósito: Gestionar campañas publicitarias y promocionales
-- ================================================================

CREATE TABLE IF NOT EXISTS marketing_campanas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_campana TEXT NOT NULL,
    descripcion TEXT,
    fecha_inicio TEXT NOT NULL,
    fecha_fin TEXT NOT NULL,
    presupuesto REAL DEFAULT 0.0,
    estado TEXT DEFAULT 'Activa',  -- Activa, Pausada, Finalizada
    objetivo TEXT,  -- Captación, Conversión, Engagement
    canal TEXT,  -- Redes Sociales, Email, WhatsApp, Mixto
    metricas_alcance INTEGER DEFAULT 0,
    metricas_conversiones INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Índice para búsquedas por estado
CREATE INDEX IF NOT EXISTS idx_marketing_campanas_estado 
    ON marketing_campanas(estado);

-- Índice para búsquedas por fechas
CREATE INDEX IF NOT EXISTS idx_marketing_campanas_fechas 
    ON marketing_campanas(fecha_inicio, fecha_fin);

-- ================================================================
-- TABLA: marketing_prospectos
-- Propósito: CRM de Leads B2B - Captura de empresas prospecto
-- ================================================================

CREATE TABLE IF NOT EXISTS marketing_prospectos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Información de la empresa prospecto
    nombre_empresa TEXT NOT NULL,

    -- Información del contacto principal
    nombre_contacto TEXT NOT NULL,
    telefono_contacto TEXT,
    correo_contacto TEXT,

    -- Clasificación del lead
    interes_servicio TEXT,  -- 'Nómina', 'Seguridad Social', 'Contabilidad', 'Asesoría Integral'
    origen TEXT DEFAULT 'Web',  -- 'Web', 'Referido', 'Llamada', 'Redes Sociales', 'WhatsApp'
    estado TEXT DEFAULT 'Nuevo',  -- 'Nuevo', 'Contactado', 'Calificado', 'Descartado', 'Convertido'

    -- Seguimiento
    notas TEXT,
    fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP,
    fecha_contacto TEXT,
    fecha_conversion TEXT,
    valor_estimado REAL DEFAULT 0.0,
    asignado_a TEXT,  -- Usuario responsable del seguimiento

    -- Auditoría
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Índices para marketing_prospectos
CREATE INDEX IF NOT EXISTS idx_marketing_prospectos_estado 
    ON marketing_prospectos(estado);

CREATE INDEX IF NOT EXISTS idx_marketing_prospectos_origen 
    ON marketing_prospectos(origen);

CREATE INDEX IF NOT EXISTS idx_marketing_prospectos_fecha 
    ON marketing_prospectos(fecha_registro);

-- ================================================================
-- DATOS INICIALES DE MARKETING (Ejemplos)
-- ================================================================

-- Redes sociales de ejemplo
INSERT OR IGNORE INTO marketing_redes (id, plataforma, url, seguidores, estado, descripcion) VALUES
(1, 'Facebook', 'https://facebook.com/monteronegocio', 1250, 'Activo', 'Página oficial de Facebook'),
(2, 'Instagram', 'https://instagram.com/monteronegocio', 890, 'Activo', 'Perfil empresarial de Instagram'),
(3, 'LinkedIn', 'https://linkedin.com/company/monteronegocio', 450, 'Activo', 'Perfil corporativo'),
(4, 'Web', 'https://monteronegocio.com', 0, 'Activo', 'Sitio web oficial');

-- Campañas de ejemplo
INSERT OR IGNORE INTO marketing_campanas (id, nombre_campana, descripcion, fecha_inicio, fecha_fin, presupuesto, estado, objetivo, canal) VALUES
(1, 'Black Friday 2025', 'Descuento 30% en afiliaciones nuevas', '2025-11-15', '2025-11-30', 500000, 'Activa', 'Captación', 'Redes Sociales'),
(2, 'Referidos Premium', 'Programa de incentivos por referidos', '2025-10-01', '2025-12-31', 300000, 'Activa', 'Conversión', 'WhatsApp');

-- Prospectos de ejemplo
INSERT OR IGNORE INTO marketing_prospectos (id, nombre_empresa, nombre_contacto, telefono_contacto, correo_contacto, origen, interes_servicio, estado) VALUES
(1, 'Distribuidora ABC S.A.S', 'María González', '3001234567', 'maria.gonzalez@distribuidoraabc.com', 'Redes Sociales', 'Seguridad Social', 'Nuevo'),
(2, 'Constructora El Sol Ltda', 'Carlos Ramírez', '3109876543', 'carlos.ramirez@elsol.com', 'Referido', 'Nómina', 'Contactado'),
(3, 'TechStart Colombia SAS', 'Ana Martínez', '3157894561', 'ana.martinez@techstart.co', 'Web', 'Asesoría Integral', 'Calificado');

-- ================================================================
-- MÓDULO DE CARTERA Y GESTIÓN FINANCIERA
-- ================================================================

-- ================================================================
-- TABLA: cartera_cobrar
-- Propósito: Gestionar cuentas por cobrar (lo que nos deben los clientes)
-- ================================================================

CREATE TABLE IF NOT EXISTS cartera_cobrar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_nit TEXT NOT NULL,
    concepto TEXT NOT NULL,  -- Ej: "Mensualidad Enero 2025", "Servicio Afiliación"
    monto REAL NOT NULL DEFAULT 0.0,
    fecha_emision TEXT DEFAULT CURRENT_TIMESTAMP,
    fecha_vencimiento TEXT NOT NULL,
    estado TEXT DEFAULT 'Pendiente',  -- Pendiente, Vencido, Pagado, Parcial
    monto_pagado REAL DEFAULT 0.0,
    fecha_pago TEXT,
    notas TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (empresa_nit) REFERENCES empresas(nit)
);

-- Índices para cartera_cobrar
CREATE INDEX IF NOT EXISTS idx_cartera_cobrar_empresa 
    ON cartera_cobrar(empresa_nit);

CREATE INDEX IF NOT EXISTS idx_cartera_cobrar_estado 
    ON cartera_cobrar(estado);

CREATE INDEX IF NOT EXISTS idx_cartera_cobrar_vencimiento 
    ON cartera_cobrar(fecha_vencimiento);

-- ================================================================
-- TABLA: cartera_pagar_ss
-- Propósito: Gestionar obligaciones de seguridad social (lo que debemos pagar)
-- ================================================================

CREATE TABLE IF NOT EXISTS cartera_pagar_ss (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_nit TEXT NOT NULL,  -- Empresa que debe pagar
    tipo_entidad TEXT NOT NULL,  -- EPS, ARL, Pensión, CCF, ICBF
    nombre_entidad TEXT NOT NULL,  -- Ej: Sura, Positiva, Porvenir, Compensar
    periodo TEXT NOT NULL,  -- Formato: "2025-02" (Año-Mes)
    monto REAL NOT NULL DEFAULT 0.0,
    fecha_limite TEXT NOT NULL,
    estado TEXT DEFAULT 'Pendiente',  -- Pendiente, Pagado, Atrasado
    fecha_pago TEXT,
    numero_planilla TEXT,  -- Número de planilla PILA generada
    notas TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (empresa_nit) REFERENCES empresas(nit)
);

-- Índices para cartera_pagar_ss
CREATE INDEX IF NOT EXISTS idx_cartera_pagar_empresa 
    ON cartera_pagar_ss(empresa_nit);

CREATE INDEX IF NOT EXISTS idx_cartera_pagar_tipo 
    ON cartera_pagar_ss(tipo_entidad);

CREATE INDEX IF NOT EXISTS idx_cartera_pagar_periodo 
    ON cartera_pagar_ss(periodo);

CREATE INDEX IF NOT EXISTS idx_cartera_pagar_estado 
    ON cartera_pagar_ss(estado);

-- ================================================================
-- TABLA: copiloto_jobs
-- Propósito: Registro de ejecuciones de automatización RPA (Copiloto ARL)
-- ================================================================

CREATE TABLE IF NOT EXISTS copiloto_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL UNIQUE,
    accion TEXT NOT NULL,  -- afiliar, certificado, incapacidad
    empresa_nit TEXT NOT NULL,
    empresa_nombre TEXT,
    empleado_id TEXT NOT NULL,
    empleado_nombre TEXT,
    estado TEXT DEFAULT 'iniciado',  -- iniciado, ejecutando, completado, error
    progreso INTEGER DEFAULT 0,  -- 0-100
    mensaje TEXT,
    usuario_id INTEGER,
    fecha_inicio TEXT DEFAULT CURRENT_TIMESTAMP,
    fecha_fin TEXT,
    resultado TEXT,  -- Detalles del resultado (JSON o texto)
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Índices para copiloto_jobs
CREATE INDEX IF NOT EXISTS idx_copiloto_jobs_job_id 
    ON copiloto_jobs(job_id);

CREATE INDEX IF NOT EXISTS idx_copiloto_jobs_estado 
    ON copiloto_jobs(estado);

CREATE INDEX IF NOT EXISTS idx_copiloto_jobs_empresa 
    ON copiloto_jobs(empresa_nit);

CREATE INDEX IF NOT EXISTS idx_copiloto_jobs_fecha 
    ON copiloto_jobs(fecha_inicio);

-- ================================================================
-- DATOS INICIALES DE CARTERA (Ejemplos)
-- ================================================================

-- Cuentas por cobrar de ejemplo
INSERT OR IGNORE INTO cartera_cobrar (id, empresa_nit, concepto, monto, fecha_vencimiento, estado) VALUES
(1, '900123456-7', 'Mensualidad Noviembre 2025', 850000, '2025-11-30', 'Pendiente'),
(2, '900123456-7', 'Servicio Afiliación ARL', 1200000, '2025-11-15', 'Vencido');

-- Obligaciones de seguridad social de ejemplo
INSERT OR IGNORE INTO cartera_pagar_ss (id, empresa_nit, tipo_entidad, nombre_entidad, periodo, monto, fecha_limite, estado) VALUES
(1, '900123456-7', 'EPS', 'Sura', '2025-11', 2500000, '2025-12-10', 'Pendiente'),
(2, '900123456-7', 'ARL', 'Positiva', '2025-11', 450000, '2025-12-10', 'Pendiente'),
(3, '900123456-7', 'Pensión', 'Porvenir', '2025-11', 3200000, '2025-12-10', 'Pendiente'),
(4, '900123456-7', 'CCF', 'Compensar', '2025-11', 800000, '2025-12-10', 'Pendiente');

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
