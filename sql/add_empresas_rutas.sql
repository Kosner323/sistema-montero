-- ================================================================
-- ACTUALIZACIÓN TABLA EMPRESAS: AGREGAR CAMPOS DE RUTAS FÍSICAS
-- ================================================================
-- Fecha: 2025-11-24
-- Propósito: Agregar columnas para gestión de expedientes digitales
--            de empresas (carpetas físicas, archivos PDF, imágenes)
-- ================================================================

-- 1. Ruta de la carpeta física principal de la empresa
ALTER TABLE empresas ADD COLUMN ruta_carpeta TEXT;

-- 2. Rutas de imágenes (Base64 convertidas a PNG)
ALTER TABLE empresas ADD COLUMN ruta_firma TEXT;
ALTER TABLE empresas ADD COLUMN ruta_logo TEXT;

-- 3. Rutas de archivos PDF adjuntos
ALTER TABLE empresas ADD COLUMN ruta_rut TEXT;
ALTER TABLE empresas ADD COLUMN ruta_camara_comercio TEXT;
ALTER TABLE empresas ADD COLUMN ruta_cedula_representante TEXT;
ALTER TABLE empresas ADD COLUMN ruta_arl TEXT;
ALTER TABLE empresas ADD COLUMN ruta_cuenta_bancaria TEXT;
ALTER TABLE empresas ADD COLUMN ruta_carta_autorizacion TEXT;

-- 4. Crear índice para búsqueda rápida por carpeta
CREATE INDEX IF NOT EXISTS idx_empresas_ruta_carpeta 
    ON empresas(ruta_carpeta);

-- ================================================================
-- VERIFICACIÓN: Consultar estructura actualizada
-- ================================================================
-- Descomentar para verificar:
-- PRAGMA table_info(empresas);

-- ================================================================
-- EJEMPLO DE USO:
-- ================================================================
-- SELECT 
--     nit,
--     nombre_empresa,
--     ruta_carpeta,
--     ruta_firma,
--     ruta_logo,
--     ruta_rut,
--     ruta_camara_comercio
-- FROM empresas
-- WHERE nit = '900123456';
-- ================================================================
