-- ============================================================================
-- MIGRACION: Sistema de Tareas Personal (Fase 11.2)
-- Fecha: 30 de Noviembre de 2024
-- Descripción: Crea tabla tareas_usuario para To-Do List personal por usuario
-- ============================================================================

-- Crear tabla tareas_usuario
CREATE TABLE IF NOT EXISTS tareas_usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    descripcion TEXT NOT NULL,
    completada BOOLEAN NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key hacia usuarios_portal
    FOREIGN KEY (user_id) REFERENCES usuarios_portal(id) ON DELETE CASCADE
);

-- Crear índice para búsquedas rápidas por usuario
CREATE INDEX IF NOT EXISTS idx_tareas_user_id ON tareas_usuario(user_id);

-- Crear índice compuesto para filtrar por usuario y estado
CREATE INDEX IF NOT EXISTS idx_tareas_user_completada ON tareas_usuario(user_id, completada);

-- Insertar datos de prueba (3 tareas para usuario id=1)
INSERT INTO tareas_usuario (user_id, descripcion, completada, created_at) VALUES
    (1, 'Revisar planillas PILA de Enero 2025', 0, datetime('now')),
    (1, 'Generar reporte de nómina para auditoría', 0, datetime('now')),
    (1, 'Actualizar datos de nuevos afiliados', 1, datetime('now', '-1 day'));

-- Verificación
SELECT 
    COUNT(*) as total_tareas,
    SUM(CASE WHEN completada = 0 THEN 1 ELSE 0 END) as pendientes,
    SUM(CASE WHEN completada = 1 THEN 1 ELSE 0 END) as completadas
FROM tareas_usuario;

-- ============================================================================
-- ROLLBACK (por si necesitas revertir):
-- DROP TABLE IF EXISTS tareas_usuario;
-- DROP INDEX IF EXISTS idx_tareas_user_id;
-- DROP INDEX IF EXISTS idx_tareas_user_completada;
-- ============================================================================
