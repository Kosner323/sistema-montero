# 📊 DOCUMENTACIÓN DE BASE DE DATOS - SISTEMA MONTERO

**Fecha:** 30 de octubre de 2025  
**Tarea:** Semana 2 - Día 3 del Plan de Acción (Dictamen Técnico)  
**Sistema:** Sistema de Gestión Montero  
**Base de datos:** SQLite (database.db)

---

## 📁 Archivos Generados

Esta documentación incluye los siguientes archivos:

```
config/
├── database_schema.py          # Documentación completa del esquema (Python)
├── create_database.sql         # Script SQL para crear la BD desde cero
└── README_DATABASE.md          # Este archivo (guía de uso)
```

---

## 🎯 Propósito

Cumplir con el punto **"Documentar base de datos"** de la Semana 2 del plan de mejoras del dictamen técnico. Esta documentación proporciona:

1. ✅ **Esquema completo** de todas las tablas
2. ✅ **Descripción detallada** de cada columna
3. ✅ **Relaciones entre tablas** (Foreign Keys)
4. ✅ **Mejoras recomendadas** con prioridades
5. ✅ **Scripts SQL** listos para usar
6. ✅ **Queries útiles** para administración

---

## 📋 Estructura de la Base de Datos

### Tablas Principales

#### 1. **empresas** (16 columnas)
- **Propósito:** Almacenar información de empresas cliente
- **Columnas clave:**
  - `id` (PK): Identificador único
  - `nit` (UNIQUE): NIT de la empresa - usado como FK
  - `nombre_empresa`: Razón social
  - `rep_legal_*`: Datos del representante legal
- **Relaciones:** 1:N con `usuarios`

#### 2. **usuarios** (33 columnas)
- **Propósito:** Almacenar información de empleados
- **Columnas clave:**
  - `id` (PK): Identificador único
  - `empresa_nit` (FK): Referencia a empresas.nit
  - `tipoId`, `numeroId`: Documento de identidad
  - `afp*`, `eps*`, `arl*`, `ccf*`: Seguridad social
- **Relaciones:** N:1 con `empresas`

#### 3. **formularios_importados** (6 columnas)
- **Propósito:** Registro de formularios PDF importados
- **Columnas clave:**
  - `id` (PK): Identificador único
  - `nombre_archivo`: Nombre del PDF
  - `campos_mapeados`: JSON con configuración de mapeo
- **Relaciones:** Ninguna

#### 4. **sqlite_sequence** (tabla del sistema)
- **Propósito:** Control interno de SQLite para AUTOINCREMENT
- **⚠️ NO MODIFICAR** - Gestionada automáticamente

---

## 🔗 Diagrama de Relaciones

```
┌─────────────────┐
│    empresas     │
│─────────────────│
│ 🔑 id (PK)      │
│ 📌 nit (FK ref) │◄─────┐
│ nombre_empresa  │      │
│ ...             │      │ 1:N
└─────────────────┘      │
                          │
┌─────────────────┐      │
│    usuarios     │      │
│─────────────────│      │
│ 🔑 id (PK)      │      │
│ 🔗 empresa_nit ─┼──────┘
│ (FK)            │
│ numeroId        │
│ primerNombre    │
│ ...             │
└─────────────────┘

┌─────────────────────────┐
│ formularios_importados  │
│─────────────────────────│
│ 🔑 id (PK)              │
│ nombre_archivo          │
│ campos_mapeados (JSON)  │
└─────────────────────────┘
```

**Leyenda:**
- 🔑 = Primary Key
- 🔗 = Foreign Key
- 📌 = Campo referenciado

---

## ⚠️ Problemas Identificados

### 🔴 Críticos

1. **Campo `nit` sin UNIQUE**
   - **Problema:** Permite NITs duplicados
   - **Impacto:** Integridad referencial comprometida
   - **Solución:** `CREATE UNIQUE INDEX idx_empresas_nit ON empresas(nit);`

2. **Sin constraint UNIQUE en usuarios**
   - **Problema:** Permite empleados duplicados
   - **Impacto:** Datos inconsistentes
   - **Solución:** `CREATE UNIQUE INDEX idx_usuarios_documento ON usuarios(tipoId, numeroId);`

3. **Campos críticos permiten NULL**
   - **Problema:** Registros incompletos
   - **Impacto:** Errores en operaciones
   - **Solución:** Migración para hacer NOT NULL campos esenciales

### 🟠 Importantes

4. **Sin índices de búsqueda**
   - **Problema:** Consultas lentas
   - **Impacto:** Performance degradada
   - **Solución:** Crear índices en `empresa_nit`, `correoElectronico`

5. **Fechas almacenadas como TEXT**
   - **Problema:** Dificulta ordenamiento y comparación
   - **Impacto:** Complejidad en queries
   - **Solución:** Migrar a INTEGER (timestamp Unix)

---

## 🔧 Cómo Aplicar las Mejoras

### Opción 1: Mejoras Incrementales (Recomendado)

```bash
# 1. Hacer backup
cp database.db database.db.backup_$(date +%Y%m%d)

# 2. Abrir SQLite
sqlite3 database.db

# 3. Aplicar mejoras críticas
sqlite> .read create_database.sql
```

### Opción 2: Migración Completa con Alembic

```bash
# 1. Instalar Alembic
pip install alembic --break-system-packages

# 2. Inicializar Alembic
alembic init migrations

# 3. Crear migración
alembic revision -m "agregar_constraints_e_indices"

# 4. Aplicar migración
alembic upgrade head
```

---

## 📖 Uso de la Documentación

### En Python

```python
# Importar la documentación del esquema
from config.database_schema import (
    TABLES_SCHEMA,
    get_table_info,
    get_all_tables,
    get_foreign_keys,
    print_schema_summary
)

# Obtener información de una tabla
tabla_usuarios = get_table_info('usuarios')
print(f"Columnas: {len(tabla_usuarios['columnas'])}")

# Listar todas las tablas
tablas = get_all_tables()
print(f"Tablas principales: {tablas}")

# Ver relaciones
fks = get_foreign_keys()
print(f"Foreign Keys: {fks}")

# Imprimir resumen completo
print_schema_summary()
```

### Queries Útiles Incluidas

El archivo `database_schema.py` incluye queries pre-escritas en `USEFUL_QUERIES`:

```python
from config.database_schema import USEFUL_QUERIES

# Obtener query
query = USEFUL_QUERIES['empleados_por_empresa']

# Ejecutar con parámetros
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
empleados = cursor.execute(query, ('900123456-7',)).fetchall()
```

Queries disponibles:
- `listar_empresas_con_empleados`
- `empleados_por_empresa`
- `total_costos_seguridad_social_por_empresa`
- `formularios_recientes`
- `verificar_integridad_foreign_keys`

---

## 🚀 Mejoras Implementadas en create_database.sql

El script SQL incluye mejoras sobre el esquema actual:

### ✅ Constraints Agregados
```sql
-- En empresas
nit TEXT NOT NULL UNIQUE  -- Antes: TEXT (sin constraints)

-- En usuarios
tipoId TEXT NOT NULL      -- Antes: TEXT (nullable)
numeroId TEXT NOT NULL    -- Antes: TEXT (nullable)
UNIQUE(tipoId, numeroId)  -- Antes: sin constraint

-- En formularios_importados
nombre_archivo TEXT NOT NULL UNIQUE  -- Antes: sin UNIQUE
```

### ✅ Índices Creados
```sql
-- Para búsquedas frecuentes
CREATE INDEX idx_empresas_nombre ON empresas(nombre_empresa);
CREATE INDEX idx_usuarios_empresa ON usuarios(empresa_nit);
CREATE INDEX idx_usuarios_email ON usuarios(correoElectronico);
CREATE INDEX idx_formularios_nombre ON formularios_importados(nombre);
```

### ✅ Nuevas Funcionalidades

**1. Tabla de Auditoría**
```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY,
    tabla TEXT NOT NULL,
    accion TEXT CHECK(accion IN ('INSERT', 'UPDATE', 'DELETE')),
    usuario TEXT,
    fecha_hora TEXT,
    datos_anteriores TEXT,  -- JSON
    datos_nuevos TEXT        -- JSON
);
```

**2. Vistas Útiles**
```sql
-- Vista con empleados y su empresa
CREATE VIEW v_empleados_completo AS ...

-- Vista con resumen de empresas
CREATE VIEW v_empresas_resumen AS ...
```

**3. Triggers Automáticos**
```sql
-- Actualiza updated_at automáticamente
CREATE TRIGGER trg_usuarios_updated_at
AFTER UPDATE ON usuarios ...
```

---

## 📊 Estadísticas Actuales

```python
DATABASE_STATS = {
    "total_tablas": 4,
    "tablas_principales": 3,
    "total_columnas": {
        "empresas": 16,
        "usuarios": 33,
        "formularios_importados": 6
    },
    "relaciones_foreign_key": 1,
    "indices_definidos": 0,  # ⚠️ Ninguno - MEJORAR
    "registros_actuales": {
        "empresas": 0,
        "usuarios": 0,
        "formularios_importados": 0
    }
}
```

---

## 🎯 Próximos Pasos Recomendados

### Semana 2 - Día 4: Implementar Alembic
```bash
# 1. Instalar Alembic
pip install alembic

# 2. Configurar migraciones
alembic init migrations

# 3. Crear primera migración basada en este esquema
alembic revision -m "initial_schema_documented"
```

### Semana 2 - Día 5: Corregir rutas de assets
- Ver archivo `config_rutas.py` (ya recibido)
- Verificar que las rutas sean coherentes con la estructura

### Semana 3: Testing y Validación
```bash
# Instalar pytest
pip install pytest pytest-cov

# Crear tests para la BD
# tests/test_database_schema.py
```

---

## 📞 Soporte y Contacto

Si encuentras problemas al aplicar esta documentación:

1. **Verifica el backup:** Siempre haz backup antes de modificar la BD
2. **Revisa logs:** Ejecuta queries en modo verbose
3. **Consulta queries útiles:** Usa `USEFUL_QUERIES` para debugging
4. **Foreign Keys:** Asegúrate de activar `PRAGMA foreign_keys = ON`

---

## ✅ Checklist de Implementación

- [ ] Revisar `database_schema.py` completo
- [ ] Hacer backup de `database.db`
- [ ] Ejecutar verificación de integridad actual
- [ ] Aplicar índices críticos (nit, documento)
- [ ] Crear tabla de auditoría (opcional)
- [ ] Implementar vistas útiles
- [ ] Configurar Alembic para futuras migraciones
- [ ] Crear tests unitarios para el esquema
- [ ] Actualizar `config_rutas.py` si es necesario
- [ ] Documentar cambios en CHANGELOG

---

## 📚 Referencias

- **Dictamen Técnico:** Ver `DICTAMEN_SISTEMA_MONTERO.md`
- **SQLite Docs:** https://www.sqlite.org/docs.html
- **Alembic Docs:** https://alembic.sqlalchemy.org/
- **Ubicación de archivos:** Ver `config_rutas.py`

---

## 🎉 Conclusión

Esta documentación cumple con el requisito de **Semana 2 - Día 3** del plan de mejoras. Proporciona:

✅ Esquema completo y detallado  
✅ Identificación de problemas  
✅ Soluciones implementables  
✅ Scripts listos para usar  
✅ Guías de migración  
✅ Queries útiles pre-escritas  

**Próximo paso:** Implementar Alembic (Semana 2 - Día 4)

---

*Documentación generada el 30 de octubre de 2025*  
*Tarea: Semana 2 - Día 3 - Documentar base de datos* ✅
