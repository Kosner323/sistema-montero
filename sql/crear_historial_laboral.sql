-- ==============================================================================
-- SISTEMA MONTERO - MÓDULO DE UNIFICACIÓN
-- Script de creación de tabla de auditoría para Historial Laboral
-- ==============================================================================
-- Autor: Sistema Montero
-- Fecha: 2025-11-23
-- Propósito: Registrar cada cambio de empresa de los usuarios para trazabilidad
-- ==============================================================================

-- Crear tabla de historial laboral si no existe
CREATE TABLE IF NOT EXISTS historial_laboral (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    empresa_anterior_nit TEXT,
    empresa_nueva_nit TEXT,
    fecha_cambio DATETIME DEFAULT CURRENT_TIMESTAMP,
    motivo TEXT,
    responsable_id INTEGER,
    -- Campos adicionales para auditoría completa
    responsable_nombre TEXT,
    tipo_operacion TEXT DEFAULT 'VINCULACION', -- VINCULACION, DESVINCULACION, CAMBIO
    ibc_anterior REAL,
    ibc_nuevo REAL,
    fecha_ingreso_anterior DATE,
    fecha_ingreso_nueva DATE,
    observaciones TEXT,
    -- Restricciones
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (responsable_id) REFERENCES usuarios(id) ON DELETE SET NULL,
    FOREIGN KEY (empresa_anterior_nit) REFERENCES empresas(nit) ON DELETE SET NULL,
    FOREIGN KEY (empresa_nueva_nit) REFERENCES empresas(nit) ON DELETE SET NULL
);

-- Crear índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_historial_usuario 
    ON historial_laboral(usuario_id);

CREATE INDEX IF NOT EXISTS idx_historial_fecha 
    ON historial_laboral(fecha_cambio DESC);

CREATE INDEX IF NOT EXISTS idx_historial_empresa_nueva 
    ON historial_laboral(empresa_nueva_nit);

CREATE INDEX IF NOT EXISTS idx_historial_empresa_anterior 
    ON historial_laboral(empresa_anterior_nit);

CREATE INDEX IF NOT EXISTS idx_historial_responsable 
    ON historial_laboral(responsable_id);

-- Crear vista para consultas optimizadas
CREATE VIEW IF NOT EXISTS vista_historial_laboral_completo AS
SELECT 
    h.id,
    h.usuario_id,
    u.tipoId || ' - ' || u.numeroId AS identificacion_usuario,
    u.primerNombre || ' ' || COALESCE(u.segundoNombre, '') || ' ' || 
    u.primerApellido || ' ' || COALESCE(u.segundoApellido, '') AS nombre_completo_usuario,
    h.empresa_anterior_nit,
    ea.nombre_empresa AS empresa_anterior_nombre,
    h.empresa_nueva_nit,
    en.nombre_empresa AS empresa_nueva_nombre,
    h.fecha_cambio,
    h.motivo,
    h.responsable_id,
    h.responsable_nombre,
    h.tipo_operacion,
    h.ibc_anterior,
    h.ibc_nuevo,
    h.fecha_ingreso_anterior,
    h.fecha_ingreso_nueva,
    h.observaciones
FROM historial_laboral h
LEFT JOIN usuarios u ON h.usuario_id = u.id
LEFT JOIN empresas ea ON h.empresa_anterior_nit = ea.nit
LEFT JOIN empresas en ON h.empresa_nueva_nit = en.nit
ORDER BY h.fecha_cambio DESC;

-- ==============================================================================
-- FIN DEL SCRIPT
-- ==============================================================================
