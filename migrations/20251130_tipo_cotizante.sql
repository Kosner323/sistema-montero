-- ========================================
-- MIGRACIÓN: Agregar tipo_cotizante a tabla usuarios
-- Fecha: 2025-11-30
-- Autor: Senior Backend Developer
-- Objetivo: Diferenciar Dependientes vs Independientes en PILA
-- ========================================

-- 1. Agregar columna tipo_cotizante
ALTER TABLE usuarios 
ADD COLUMN tipo_cotizante TEXT DEFAULT 'Dependiente' NOT NULL;

-- 2. Validación: Solo permite 'Dependiente' o 'Independiente'
-- Nota: SQLite no soporta CHECK CONSTRAINT en ALTER TABLE,
-- por lo que se debe aplicar en la definición del modelo ORM

-- 3. Actualizar empresa_nit a nullable (ya lo es en orm_models.py)
-- Si hay registros sin empresa_nit, se mantienen NULL para Independientes

-- 4. Crear índice para optimizar queries por tipo
CREATE INDEX IF NOT EXISTS idx_usuarios_tipo_cotizante 
ON usuarios(tipo_cotizante);

-- 5. Datos de prueba: Marcar algunos usuarios como Independientes
-- (Opcional - descomentar si se desea poblar datos)
/*
UPDATE usuarios 
SET tipo_cotizante = 'Independiente'
WHERE empresa_nit IS NULL OR empresa_nit = '';
*/

-- ========================================
-- ROLLBACK (Si se requiere deshacer)
-- ========================================
/*
DROP INDEX IF EXISTS idx_usuarios_tipo_cotizante;
-- SQLite no permite DROP COLUMN directamente
-- Se requeriría recrear la tabla sin la columna
*/

-- ========================================
-- VERIFICACIÓN
-- ========================================
-- SELECT tipo_cotizante, COUNT(*) as total
-- FROM usuarios
-- GROUP BY tipo_cotizante;
