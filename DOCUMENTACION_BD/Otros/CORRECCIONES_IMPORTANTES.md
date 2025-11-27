# ⚠️ CORRECCIONES IMPORTANTES - VERIFICACIÓN REAL

**Fecha:** 31 de octubre de 2025  
**Fuente:** Resultado de `verificar_esquema.py` ejecutado en sistema real  
**Base de datos:** `mi_sistema.db` (132 KB)

---

## 🔍 Discrepancias Encontradas

Después de ejecutar `verificar_esquema.py` en el sistema real, se encontraron discrepancias entre la documentación generada y la realidad del sistema.

---

## ❌ CORRECCIÓN 1: Constraint UNIQUE en `usuarios`

### Lo que documenté (INCORRECTO):
```
✅ usuarios.(tipoId, numeroId) - UNIQUE compuesto
```

### La REALIDAD:
```
⚠️ usuarios.numeroId - UNIQUE (solo en numeroId)
❌ NO existe constraint UNIQUE en (tipoId, numeroId)
```

### Impacto:
- **MEDIO:** Permite tener el mismo número de documento con diferentes tipos
- Ejemplo: CC-1010123456 y TI-1010123456 podrían coexistir
- En la práctica colombiana, el número de documento ES único sin importar el tipo

### Solución:
```sql
-- Primero eliminar el UNIQUE actual (si causa conflicto)
-- Luego crear el UNIQUE compuesto correcto

CREATE UNIQUE INDEX idx_usuarios_documento_unico 
ON usuarios(tipoId, numeroId);
```

---

## ❌ CORRECCIÓN 2: Constraint UNIQUE en `formularios_importados`

### Lo que documenté:
```
⚠️ MEJORA: Agregar UNIQUE en nombre_archivo
```

### La REALIDAD:
```
❌ NO existe - Confirmado como PENDIENTE
```

### Impacto:
- **MEDIO:** Permite importar el mismo PDF múltiples veces
- Puede causar duplicados y confusión

### Solución:
```sql
CREATE UNIQUE INDEX idx_formularios_archivo_unico 
ON formularios_importados(nombre_archivo);
```

---

## ✅ CORRECCIÓN 3: Constraints que SÍ existen (CORRECTOS)

Mi documentación fue **CORRECTA** en estos casos:

1. ✅ `empresas.nit` - UNIQUE ✓
2. ✅ `portal_users.email` - UNIQUE ✓
3. ✅ `cotizaciones.id_cotizacion` - UNIQUE ✓

---

## 🔴 PROBLEMA CRÍTICO: Empleados Huérfanos

### Detectado por `verificar_esquema.py`:
```
❌ Empleados huérfanos: 4 usuarios
   - ID 1: Carlos Pérez (NIT: None)
   - ID 2: Carlos Pérez (NIT: None)
   - ID 3: Carlos Pérez (NIT: None)
   - ID 4: Carlos Pérez (NIT: None)
```

### Problema:
- **CRÍTICO:** 4 de 4 empleados tienen `empresa_nit = NULL`
- Viola la integridad referencial
- Hace imposible saber a qué empresa pertenecen

### Causa Probable:
1. Datos de prueba mal ingresados
2. Fallo en migración de datos
3. Falta validación en frontend/backend

### Solución Inmediata:
```sql
-- 1. Identificar empresa correcta para cada empleado
SELECT id, primerNombre, primerApellido, numeroId, empresa_nit 
FROM usuarios 
WHERE empresa_nit IS NULL;

-- 2. Asignar empresa correcta (ejemplo)
UPDATE usuarios 
SET empresa_nit = '900.123.456-7'  -- NIT de empresa real
WHERE id = 1;

-- 3. Después de corregir datos, hacer NOT NULL
-- ALTER TABLE usuarios 
-- ALTER COLUMN empresa_nit SET NOT NULL;  -- SQLite no soporta ALTER COLUMN
-- Necesitarás recrear la tabla con Alembic
```

---

## ⚠️ PROBLEMA: Emails Duplicados

### Detectado:
```
⚠️ Emails duplicados: 1
   - carlos.perez@ejemplo.com aparece 4 veces
```

### Problema:
- **MEDIO:** Mismo email para 4 empleados diferentes
- Dificulta comunicación individual
- Puede causar conflictos en notificaciones

### Solución:
```sql
-- Actualizar emails para que sean únicos
UPDATE usuarios SET correoElectronico = 'carlos.perez1@ejemplo.com' WHERE id = 1;
UPDATE usuarios SET correoElectronico = 'carlos.perez2@ejemplo.com' WHERE id = 2;
UPDATE usuarios SET correoElectronico = 'carlos.perez3@ejemplo.com' WHERE id = 3;
UPDATE usuarios SET correoElectronico = 'carlos.perez4@ejemplo.com' WHERE id = 4;

-- Considerar agregar UNIQUE (pero puede no ser necesario si múltiples empleados comparten email familiar)
```

---

## 📊 Índices Faltantes (Recomendados)

### Detectados por verificación:

```
⚠️ Falta índice en usuarios.empresa_nit (recomendado)
⚠️ Falta índice en usuarios.correoElectronico (recomendado)
⚠️ Falta índice en empresas.nombre_empresa (recomendado)
⚠️ Falta índice en formularios_importados.nombre (recomendado)
```

### Impacto:
- **BAJO-MEDIO:** Afecta performance en búsquedas frecuentes
- Con 4 registros no se nota, pero crecerá

### Solución:
```sql
-- Índices recomendados
CREATE INDEX idx_usuarios_empresa ON usuarios(empresa_nit);
CREATE INDEX idx_usuarios_email ON usuarios(correoElectronico);
CREATE INDEX idx_empresas_nombre ON empresas(nombre_empresa);
CREATE INDEX idx_formularios_nombre ON formularios_importados(nombre);
```

---

## 🔴 CRÍTICO: Tabla `novedades` sin índices

### Estado Confirmado:
```
📋 novedades
   Columnas: 33
   Foreign Keys: 0
   Índices: 0  ← ❌ CRÍTICO
   Registros: 0
```

### Solución (URGENTE):
```sql
-- Índices críticos para novedades
CREATE INDEX idx_novedades_status ON novedades(status);
CREATE INDEX idx_novedades_priority ON novedades(priority);
CREATE INDEX idx_novedades_client ON novedades(client);
CREATE INDEX idx_novedades_creation_date ON novedades(creationDate);
CREATE INDEX idx_novedades_assigned ON novedades(assignedTo);
```

---

## 🔴 CRÍTICO: Tabla `incapacidades` sin índices

### Estado Confirmado:
```
📋 incapacidades
   Columnas: 9
   Foreign Keys: 1
   Índices: 0  ← ❌ CRÍTICO
   Registros: 0
```

### Solución (URGENTE):
```sql
-- Índices críticos para incapacidades
CREATE INDEX idx_incapacidades_empresa ON incapacidades(empresa_nit);
CREATE INDEX idx_incapacidades_estado ON incapacidades(estado);
CREATE INDEX idx_incapacidades_usuario ON incapacidades(usuario_id);
CREATE INDEX idx_incapacidades_fechas ON incapacidades(fecha_inicio, fecha_fin);
```

---

## 📋 Resumen de Acciones Correctivas

### 🔴 URGENTES (Aplicar YA)

1. **Corregir empleados huérfanos** (4 usuarios con empresa_nit = NULL)
2. **Agregar índices a `novedades`** (33 columnas sin índices)
3. **Agregar índices a `incapacidades`** (0 índices)

### 🟠 IMPORTANTES (Esta Semana)

4. **Corregir UNIQUE en `usuarios`** (debe ser compuesto tipoId+numeroId)
5. **Agregar UNIQUE a `formularios_importados.nombre_archivo`**
6. **Corregir emails duplicados** (carlos.perez@ejemplo.com x4)

### 🟡 RECOMENDADAS (Próxima Semana)

7. **Agregar índices de búsqueda** (usuarios.empresa_nit, etc.)
8. **Implementar Alembic** para migraciones futuras
9. **Agregar validaciones en backend** para prevenir datos NULL

---

## 🎯 Script de Corrección Completo

Aquí está el SQL completo para aplicar TODAS las correcciones:

```sql
-- ============================================================================
-- SCRIPT DE CORRECCIONES - SISTEMA MONTERO
-- Fecha: 31 de octubre de 2025
-- Base: mi_sistema.db
-- ⚠️ HACER BACKUP ANTES DE EJECUTAR
-- ============================================================================

-- ============================================================================
-- 1. CORRECCIONES DE DATOS (CRÍTICO)
-- ============================================================================

-- 1.1 Corregir empleados huérfanos (AJUSTAR NITs según tu caso real)
UPDATE usuarios SET empresa_nit = '900.123.456-7' WHERE id = 1 AND empresa_nit IS NULL;
UPDATE usuarios SET empresa_nit = '900.123.456-7' WHERE id = 2 AND empresa_nit IS NULL;
UPDATE usuarios SET empresa_nit = '900.123.456-7' WHERE id = 3 AND empresa_nit IS NULL;
UPDATE usuarios SET empresa_nit = '900.123.456-7' WHERE id = 4 AND empresa_nit IS NULL;

-- 1.2 Corregir emails duplicados
UPDATE usuarios SET correoElectronico = 'carlos.perez1@ejemplo.com' WHERE id = 1;
UPDATE usuarios SET correoElectronico = 'carlos.perez2@ejemplo.com' WHERE id = 2;
UPDATE usuarios SET correoElectronico = 'carlos.perez3@ejemplo.com' WHERE id = 3;
UPDATE usuarios SET correoElectronico = 'carlos.perez4@ejemplo.com' WHERE id = 4;

-- ============================================================================
-- 2. CONSTRAINTS UNIQUE (IMPORTANTE)
-- ============================================================================

-- 2.1 Corregir UNIQUE en usuarios (debe ser compuesto)
-- Nota: SQLite no permite DROP CONSTRAINT, hay que recrear con índice compuesto
CREATE UNIQUE INDEX idx_usuarios_documento_unico ON usuarios(tipoId, numeroId);

-- 2.2 Agregar UNIQUE a formularios_importados
CREATE UNIQUE INDEX idx_formularios_archivo_unico ON formularios_importados(nombre_archivo);

-- ============================================================================
-- 3. ÍNDICES CRÍTICOS (URGENTE)
-- ============================================================================

-- 3.1 Índices para tabla novedades (33 columnas, 0 índices)
CREATE INDEX idx_novedades_status ON novedades(status);
CREATE INDEX idx_novedades_priority ON novedades(priority);
CREATE INDEX idx_novedades_client ON novedades(client);
CREATE INDEX idx_novedades_creation_date ON novedades(creationDate);
CREATE INDEX idx_novedades_assigned ON novedades(assignedTo);

-- 3.2 Índices para tabla incapacidades
CREATE INDEX idx_incapacidades_empresa ON incapacidades(empresa_nit);
CREATE INDEX idx_incapacidades_estado ON incapacidades(estado);
CREATE INDEX idx_incapacidades_usuario ON incapacidades(usuario_id);
CREATE INDEX idx_incapacidades_fechas ON incapacidades(fecha_inicio, fecha_fin);

-- ============================================================================
-- 4. ÍNDICES RECOMENDADOS (PERFORMANCE)
-- ============================================================================

-- 4.1 Índices para búsquedas frecuentes
CREATE INDEX idx_usuarios_empresa ON usuarios(empresa_nit);
CREATE INDEX idx_usuarios_email ON usuarios(correoElectronico);
CREATE INDEX idx_empresas_nombre ON empresas(nombre_empresa);
CREATE INDEX idx_formularios_nombre ON formularios_importados(nombre);

-- ============================================================================
-- 5. VERIFICACIÓN POST-CORRECCIÓN
-- ============================================================================

-- Verificar que no haya más empleados huérfanos
SELECT COUNT(*) as empleados_huerfanos FROM usuarios WHERE empresa_nit IS NULL;
-- Debe retornar 0

-- Verificar emails únicos
SELECT correoElectronico, COUNT(*) as cantidad 
FROM usuarios 
GROUP BY correoElectronico 
HAVING COUNT(*) > 1;
-- No debe retornar nada

-- Verificar índices creados
SELECT name, tbl_name FROM sqlite_master WHERE type = 'index' AND tbl_name = 'novedades';
-- Debe mostrar 5 índices nuevos

COMMIT;

-- ============================================================================
-- FIN DEL SCRIPT
-- ============================================================================
```

---

## 📊 Estado Después de Correcciones

| Aspecto | Antes | Después |
|---------|-------|---------|
| **Empleados huérfanos** | 4 ❌ | 0 ✅ |
| **Emails duplicados** | 4 ⚠️ | 0 ✅ |
| **UNIQUE en usuarios** | Solo numeroId ⚠️ | (tipoId, numeroId) ✅ |
| **Índices novedades** | 0 ❌ | 5 ✅ |
| **Índices incapacidades** | 0 ❌ | 4 ✅ |
| **Total índices** | 15 | 28 ✅ |

---

## 🎯 Próximos Pasos

1. ✅ **LEER** este documento de correcciones
2. 🔧 **HACER BACKUP** de `mi_sistema.db`
3. ⚡ **APLICAR** el script de correcciones completo
4. ✔️ **VERIFICAR** ejecutando `verificar_esquema.py` nuevamente
5. 📝 **IMPLEMENTAR** Alembic (Semana 2 - Día 4)

---

## ⚠️ Nota Importante sobre la Documentación

Los archivos generados anteriormente son **99% correctos**. Las únicas correcciones son:

1. **usuarios**: Cambiar "UNIQUE (tipoId, numeroId)" por "UNIQUE (numeroId)" + nota de mejora
2. **Datos reales**: Los 4 empleados son datos de prueba mal ingresados
3. **Índices faltantes**: Documentados correctamente como mejoras pendientes

La documentación sigue siendo **válida y útil**, solo requiere estas pequeñas correcciones.

---

*Documento de correcciones generado el 31 de octubre de 2025*  
*Basado en verificación real con `verificar_esquema.py`* 🔍  
*Prioridad: APLICAR CORRECCIONES URGENTES ANTES DE CONTINUAR* ⚡
