-- ============================================================================
-- SCRIPT DE CORRECCIONES - SISTEMA MONTERO
-- ============================================================================
-- Fecha: 31 de octubre de 2025
-- Base: mi_sistema.db (132 KB)
-- Propósito: Corregir problemas detectados por verificar_esquema.py
-- 
-- ⚠️  IMPORTANTE: HACER BACKUP COMPLETO ANTES DE EJECUTAR
-- 
-- Comando de backup recomendado:
-- cp mi_sistema.db mi_sistema_backup_20251031.db
-- ============================================================================

BEGIN TRANSACTION;

-- ============================================================================
-- SECCIÓN 1: CORRECCIONES DE DATOS (CRÍTICO - REVISAR ANTES DE EJECUTAR)
-- ============================================================================

-- 🔴 CRÍTICO 1.1: Corregir empleados huérfanos
-- ⚠️  IMPORTANTE: Ajusta los NITs según las empresas reales en tu sistema
-- 
-- Primero, verifica qué empresas tienes disponibles:
-- SELECT nit, nombre_empresa FROM empresas;

-- Ejemplo: Asignar a la primera empresa disponible
-- Ajusta el NIT '900.123.456-7' según tu caso real

UPDATE usuarios 
SET empresa_nit = '900.123.456-7' 
WHERE id = 1 AND empresa_nit IS NULL;

UPDATE usuarios 
SET empresa_nit = '900.123.456-7' 
WHERE id = 2 AND empresa_nit IS NULL;

UPDATE usuarios 
SET empresa_nit = '900.123.456-7' 
WHERE id = 3 AND empresa_nit IS NULL;

UPDATE usuarios 
SET empresa_nit = '900.123.456-7' 
WHERE id = 4 AND empresa_nit IS NULL;

-- Verificar que no queden huérfanos
SELECT COUNT(*) as empleados_huerfanos_restantes 
FROM usuarios 
WHERE empresa_nit IS NULL;
-- Debe retornar 0


-- ⚠️  MEDIO 1.2: Corregir emails duplicados
-- Asignar emails únicos a cada empleado

UPDATE usuarios 
SET correoElectronico = 'carlos.perez1@ejemplo.com' 
WHERE id = 1;

UPDATE usuarios 
SET correoElectronico = 'carlos.perez2@ejemplo.com' 
WHERE id = 2;

UPDATE usuarios 
SET correoElectronico = 'carlos.perez3@ejemplo.com' 
WHERE id = 3;

UPDATE usuarios 
SET correoElectronico = 'carlos.perez4@ejemplo.com' 
WHERE id = 4;

-- Verificar emails únicos
SELECT correoElectronico, COUNT(*) as cantidad 
FROM usuarios 
GROUP BY correoElectronico 
HAVING COUNT(*) > 1;
-- No debe retornar nada


-- ============================================================================
-- SECCIÓN 2: CONSTRAINTS UNIQUE (IMPORTANTE)
-- ============================================================================

-- 🟠 IMPORTANTE 2.1: Agregar UNIQUE compuesto en usuarios
-- Actualmente solo numeroId es UNIQUE, debe ser (tipoId, numeroId)
-- 
-- Nota: En SQLite no se puede modificar constraints existentes fácilmente.
-- Creamos un índice UNIQUE compuesto adicional.
-- El índice en solo numeroId permanece (no causa conflicto).

CREATE UNIQUE INDEX IF NOT EXISTS idx_usuarios_documento_completo 
ON usuarios(tipoId, numeroId);


-- 🟠 IMPORTANTE 2.2: Agregar UNIQUE a formularios_importados
-- Evitar importar el mismo PDF múltiples veces

CREATE UNIQUE INDEX IF NOT EXISTS idx_formularios_archivo_unico 
ON formularios_importados(nombre_archivo);


-- ============================================================================
-- SECCIÓN 3: ÍNDICES CRÍTICOS (URGENTE - AFECTA PERFORMANCE)
-- ============================================================================

-- 🔴 CRÍTICO 3.1: Índices para tabla 'novedades' (33 columnas, 0 índices)
-- Esta tabla puede crecer rápidamente y necesita índices urgentemente

CREATE INDEX IF NOT EXISTS idx_novedades_status 
ON novedades(status);

CREATE INDEX IF NOT EXISTS idx_novedades_priority 
ON novedades(priority);

CREATE INDEX IF NOT EXISTS idx_novedades_client 
ON novedades(client);

CREATE INDEX IF NOT EXISTS idx_novedades_creation_date 
ON novedades(creationDate);

CREATE INDEX IF NOT EXISTS idx_novedades_assigned 
ON novedades(assignedTo);


-- 🔴 CRÍTICO 3.2: Índices para tabla 'incapacidades'
-- Tabla transaccional que necesita índices para búsquedas eficientes

CREATE INDEX IF NOT EXISTS idx_incapacidades_empresa 
ON incapacidades(empresa_nit);

CREATE INDEX IF NOT EXISTS idx_incapacidades_estado 
ON incapacidades(estado);

CREATE INDEX IF NOT EXISTS idx_incapacidades_usuario 
ON incapacidades(usuario_id);

CREATE INDEX IF NOT EXISTS idx_incapacidades_fechas 
ON incapacidades(fecha_inicio, fecha_fin);


-- ============================================================================
-- SECCIÓN 4: ÍNDICES RECOMENDADOS (MEJORA PERFORMANCE)
-- ============================================================================

-- 🟡 RECOMENDADO 4.1: Índices para búsquedas frecuentes en 'usuarios'

CREATE INDEX IF NOT EXISTS idx_usuarios_empresa 
ON usuarios(empresa_nit);

CREATE INDEX IF NOT EXISTS idx_usuarios_email 
ON usuarios(correoElectronico);


-- 🟡 RECOMENDADO 4.2: Índice para búsqueda de empresas por nombre

CREATE INDEX IF NOT EXISTS idx_empresas_nombre 
ON empresas(nombre_empresa);


-- 🟡 RECOMENDADO 4.3: Índice para búsqueda de formularios por nombre

CREATE INDEX IF NOT EXISTS idx_formularios_nombre 
ON formularios_importados(nombre);


-- ============================================================================
-- SECCIÓN 5: VERIFICACIONES POST-CORRECCIÓN
-- ============================================================================

-- Verificación 1: Empleados sin empresa
SELECT 'Verificación 1: Empleados huérfanos' as check_name;
SELECT COUNT(*) as cantidad, 
       CASE 
           WHEN COUNT(*) = 0 THEN '✅ CORRECTO'
           ELSE '❌ AÚN HAY PROBLEMAS'
       END as estado
FROM usuarios 
WHERE empresa_nit IS NULL;


-- Verificación 2: Emails duplicados
SELECT 'Verificación 2: Emails duplicados' as check_name;
SELECT correoElectronico, COUNT(*) as cantidad,
       CASE 
           WHEN COUNT(*) = 1 THEN '✅ CORRECTO'
           ELSE '⚠️ DUPLICADO'
       END as estado
FROM usuarios 
GROUP BY correoElectronico;


-- Verificación 3: Índices creados
SELECT 'Verificación 3: Nuevos índices' as check_name;
SELECT COUNT(*) as total_indices_nuevos,
       CASE 
           WHEN COUNT(*) >= 13 THEN '✅ CORRECTO (13+ índices agregados)'
           ELSE '⚠️ FALTAN ÍNDICES'
       END as estado
FROM sqlite_master 
WHERE type = 'index' 
  AND tbl_name IN ('novedades', 'incapacidades', 'usuarios', 'empresas', 'formularios_importados')
  AND name LIKE 'idx_%';


-- Verificación 4: Índices UNIQUE
SELECT 'Verificación 4: Constraints UNIQUE' as check_name;
SELECT tbl_name as tabla, 
       name as indice_unique,
       '✅ EXISTE' as estado
FROM sqlite_master 
WHERE type = 'index' 
  AND name IN (
      'sqlite_autoindex_empresas_1',
      'idx_usuarios_documento_completo',
      'idx_formularios_archivo_unico',
      'sqlite_autoindex_portal_users_1',
      'sqlite_autoindex_cotizaciones_1'
  )
ORDER BY tbl_name;


-- ============================================================================
-- SECCIÓN 6: ESTADÍSTICAS FINALES
-- ============================================================================

SELECT '=== ESTADÍSTICAS DEL SISTEMA DESPUÉS DE CORRECCIONES ===' as titulo;

SELECT 'Total de tablas' as metrica, COUNT(*) as valor
FROM sqlite_master 
WHERE type = 'table' AND name NOT LIKE 'sqlite_%'

UNION ALL

SELECT 'Total de índices', COUNT(*)
FROM sqlite_master 
WHERE type = 'index' AND name NOT LIKE 'sqlite_%'

UNION ALL

SELECT 'Empresas registradas', COUNT(*)
FROM empresas

UNION ALL

SELECT 'Empleados registrados', COUNT(*)
FROM usuarios

UNION ALL

SELECT 'Empleados con empresa asignada', COUNT(*)
FROM usuarios 
WHERE empresa_nit IS NOT NULL

UNION ALL

SELECT 'Usuarios portal', COUNT(*)
FROM portal_users

UNION ALL

SELECT 'Tutelas activas', COUNT(*)
FROM tutelas

UNION ALL

SELECT 'Impuestos pendientes', COUNT(*)
FROM pago_impuestos 
WHERE estado = 'Pendiente de Pago'

UNION ALL

SELECT 'Credenciales guardadas', COUNT(*)
FROM credenciales_plataforma;


-- ============================================================================
-- COMMIT O ROLLBACK
-- ============================================================================

-- Si todo se ve bien en las verificaciones, hacer COMMIT
-- Si algo salió mal, hacer ROLLBACK

-- COMMIT;

-- Descomentar la línea de arriba cuando estés seguro
-- Por seguridad, este script termina sin COMMIT automático


-- ============================================================================
-- FIN DEL SCRIPT DE CORRECCIONES
-- ============================================================================
-- 
-- 📋 RESUMEN DE CAMBIOS APLICADOS:
-- 
-- ✅ Corregidos 4 empleados huérfanos (empresa_nit asignado)
-- ✅ Corregidos 4 emails duplicados
-- ✅ Agregado UNIQUE compuesto en usuarios(tipoId, numeroId)
-- ✅ Agregado UNIQUE en formularios_importados(nombre_archivo)
-- ✅ Agregados 5 índices críticos a tabla 'novedades'
-- ✅ Agregados 4 índices críticos a tabla 'incapacidades'
-- ✅ Agregados 4 índices recomendados en otras tablas
-- 
-- Total de mejoras: 13 índices nuevos + 2 UNIQUE + corrección de datos
-- 
-- 🎯 PRÓXIMO PASO: Ejecutar 'python verificar_esquema.py mi_sistema.db' 
--    para confirmar que todos los problemas fueron resueltos.
-- 
-- ============================================================================
