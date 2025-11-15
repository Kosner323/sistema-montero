# 🔄 GUÍA DE MIGRACIONES CON ALEMBIC - SISTEMA MONTERO

## 📋 Índice

1. [¿Qué son las Migraciones?](#qué-son-las-migraciones)
2. [Instalación](#instalación)
3. [Configuración Inicial](#configuración-inicial)
4. [Comandos Básicos](#comandos-básicos)
5. [Flujo de Trabajo](#flujo-de-trabajo)
6. [Ejemplos Prácticos](#ejemplos-prácticos)
7. [Resolución de Problemas](#resolución-de-problemas)
8. [Mejores Prácticas](#mejores-prácticas)

---

## ¿Qué son las Migraciones?

Las **migraciones de base de datos** son una forma de versionar y controlar los cambios en tu esquema de base de datos, similar a como Git versiona tu código.

### Ventajas:

- ✅ **Control de versiones** para tu base de datos
- ✅ **Reversibilidad**: Puedes revertir cambios si algo sale mal
- ✅ **Sincronización** entre desarrollo, pruebas y producción
- ✅ **Documentación** automática de cambios en el schema
- ✅ **Trabajo en equipo** más ordenado

### Sin Migraciones vs Con Migraciones

#### ❌ Sin Migraciones (Antiguo método):
```sql
-- Alguien ejecuta esto manualmente
ALTER TABLE usuarios ADD COLUMN fecha_nacimiento DATE;
-- ¿Quién lo ejecutó? ¿Cuándo? ¿En qué servidor?
-- ¿Cómo lo revertimos si hay un problema?
```

#### ✅ Con Migraciones (Alembic):
```python
# migrations/versions/002_agregar_fecha_nacimiento.py
def upgrade():
    op.add_column('usuarios', sa.Column('fecha_nacimiento', sa.Date()))

def downgrade():
    op.drop_column('usuarios', 'fecha_nacimiento')
```

---

## Instalación

### 1. Instalar Alembic

```bash
pip install alembic
```

### 2. Verificar instalación

```bash
alembic --version
```

---

## Configuración Inicial

Tu sistema ya viene con Alembic configurado. La estructura es:

```
mi-app-montero/
│
├── alembic.ini                    # Configuración de Alembic
├── manage_migrations.py           # Script helper (recomendado)
│
└── migrations/
    ├── env.py                     # Entorno de Alembic
    ├── script.py.mako             # Template para migraciones
    └── versions/                  # Aquí van las migraciones
        └── 001_initial_schema.py  # Migración inicial
```

### Archivos importantes:

- **alembic.ini**: Configuración general de Alembic
- **migrations/env.py**: Cómo Alembic se conecta a tu BD
- **manage_migrations.py**: Script helper que simplifica los comandos

---

## Comandos Básicos

### Opción 1: Usar el Script Helper (Recomendado)

```bash
# Ver ayuda
python manage_migrations.py help

# Ver estado actual
python manage_migrations.py status

# Ver historial
python manage_migrations.py history

# Aplicar migraciones
python manage_migrations.py upgrade

# Revertir última migración
python manage_migrations.py downgrade

# Crear nueva migración
python manage_migrations.py create "descripcion del cambio"

# Crear backup manual
python manage_migrations.py backup
```

### Opción 2: Usar Alembic Directamente

```bash
# Ver versión actual
alembic current

# Ver historial
alembic history

# Aplicar todas las migraciones
alembic upgrade head

# Revertir una migración
alembic downgrade -1

# Crear nueva migración
alembic revision -m "descripcion"
```

---

## Flujo de Trabajo

### Para una Base de Datos NUEVA (sin tablas):

```bash
# 1. Aplicar migración inicial (crea todas las tablas)
python manage_migrations.py upgrade

# Resultado: Base de datos creada con todas las tablas
```

### Para una Base de Datos EXISTENTE (ya tiene tablas):

```bash
# 1. Marcar la BD como "ya migrada"
python manage_migrations.py init

# Resultado: Alembic sabe que las tablas ya existen
# Ahora puedes crear nuevas migraciones para cambios futuros
```

### Para Agregar Nuevos Cambios:

```bash
# 1. Crear nueva migración
python manage_migrations.py create "agregar columna email_verificado"

# 2. Editar el archivo generado en migrations/versions/
# Agregar el código de upgrade() y downgrade()

# 3. Aplicar la migración
python manage_migrations.py upgrade
```

---

## Ejemplos Prácticos

### Ejemplo 1: Agregar una nueva columna

**Escenario**: Necesitas agregar una columna `email_verificado` a la tabla `usuarios`

```bash
# 1. Crear migración
python manage_migrations.py create "agregar email_verificado a usuarios"
```

Alembic creará un archivo como: `migrations/versions/002_agregar_email_verificado.py`

**2. Editar el archivo generado:**

```python
"""agregar email_verificado a usuarios

Revision ID: 002_agregar_email_verificado
Revises: 001_initial_schema
Create Date: 2025-11-01 10:30:00
"""
from alembic import op
import sqlalchemy as sa

revision = '002_agregar_email_verificado'
down_revision = '001_initial_schema'

def upgrade():
    # SQLite requiere batch mode para ALTER TABLE
    with op.batch_alter_table('usuarios') as batch_op:
        batch_op.add_column(
            sa.Column('email_verificado', sa.Boolean(), default=False)
        )

def downgrade():
    with op.batch_alter_table('usuarios') as batch_op:
        batch_op.drop_column('email_verificado')
```

**3. Aplicar la migración:**

```bash
python manage_migrations.py upgrade
```

### Ejemplo 2: Crear una nueva tabla

```bash
# 1. Crear migración
python manage_migrations.py create "crear tabla mensajes"
```

**2. Editar archivo:**

```python
def upgrade():
    op.create_table(
        'mensajes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.Column('contenido', sa.Text(), nullable=False),
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'])
    )
    
    # Crear índice
    op.create_index('idx_mensajes_usuario', 'mensajes', ['usuario_id'])

def downgrade():
    op.drop_index('idx_mensajes_usuario')
    op.drop_table('mensajes')
```

### Ejemplo 3: Modificar una columna existente

```bash
python manage_migrations.py create "ampliar longitud de telefono"
```

```python
def upgrade():
    # SQLite no soporta ALTER COLUMN directamente
    # Necesitamos recrear la tabla
    
    with op.batch_alter_table('usuarios') as batch_op:
        batch_op.alter_column(
            'telefono',
            type_=sa.String(20),  # Aumentar de 15 a 20
            existing_type=sa.String(15)
        )

def downgrade():
    with op.batch_alter_table('usuarios') as batch_op:
        batch_op.alter_column(
            'telefono',
            type_=sa.String(15),
            existing_type=sa.String(20)
        )
```

### Ejemplo 4: Agregar datos (data migration)

```bash
python manage_migrations.py create "agregar roles predeterminados"
```

```python
from alembic import op
from sqlalchemy import table, column, String

def upgrade():
    # Definir estructura temporal de la tabla
    roles = table('roles',
        column('nombre', String),
        column('descripcion', String)
    )
    
    # Insertar datos
    op.bulk_insert(roles, [
        {'nombre': 'admin', 'descripcion': 'Administrador del sistema'},
        {'nombre': 'usuario', 'descripcion': 'Usuario estándar'},
        {'nombre': 'supervisor', 'descripcion': 'Supervisor de operaciones'}
    ])

def downgrade():
    # Eliminar los roles agregados
    op.execute("DELETE FROM roles WHERE nombre IN ('admin', 'usuario', 'supervisor')")
```

---

## Resolución de Problemas

### Problema: "Table already exists"

**Causa**: Intentas aplicar la migración inicial pero las tablas ya existen.

**Solución**:
```bash
# Marcar la BD como "ya migrada"
python manage_migrations.py init
```

### Problema: "Can't locate revision identified by '...'"

**Causa**: La base de datos tiene una versión que no existe en tus archivos de migración.

**Solución**:
```bash
# Ver qué versión tiene la BD
alembic current

# Ver historial completo
alembic history

# Si necesitas "forzar" una versión
alembic stamp 001_initial_schema
```

### Problema: SQLite no permite modificar columnas

**Causa**: SQLite tiene limitaciones para ALTER TABLE.

**Solución**: Usar `batch_alter_table`:
```python
with op.batch_alter_table('tabla') as batch_op:
    batch_op.add_column(...)
    batch_op.alter_column(...)
```

### Problema: Error al revertir una migración

**Causa**: La función `downgrade()` no está bien implementada.

**Solución**:
1. Revisar y corregir el código en `downgrade()`
2. Si no es posible revertir automáticamente, puedes:
   ```bash
   # Restaurar desde backup
   cp backups/backup_*.db mi_sistema.db
   ```

---

## Mejores Prácticas

### 1. ✅ Siempre hacer backup antes de migrar

```bash
# Backup automático al usar manage_migrations.py
python manage_migrations.py upgrade

# Backup manual
python manage_migrations.py backup
```

### 2. ✅ Probar en desarrollo primero

```bash
# Nunca aplicar migraciones directamente en producción sin probar
# Flujo recomendado:
1. Desarrollo → Crear y probar migración
2. Testing → Aplicar en ambiente de pruebas
3. Producción → Aplicar con backup
```

### 3. ✅ Escribir migraciones descriptivas

```bash
# ❌ Mal
python manage_migrations.py create "cambios"

# ✅ Bien
python manage_migrations.py create "agregar columna fecha_nacimiento a usuarios"
```

### 4. ✅ Siempre implementar downgrade()

```python
# ❌ Mal
def downgrade():
    pass  # No hace nada

# ✅ Bien
def downgrade():
    with op.batch_alter_table('usuarios') as batch_op:
        batch_op.drop_column('fecha_nacimiento')
```

### 5. ✅ Una migración = Un cambio lógico

```bash
# ❌ Mal: Meter todo en una migración
python manage_migrations.py create "muchos cambios mezclados"

# ✅ Bien: Migraciones separadas y específicas
python manage_migrations.py create "agregar tabla mensajes"
python manage_migrations.py create "agregar indice email en usuarios"
```

### 6. ✅ Versionar las migraciones en Git

```bash
# Agregar a Git
git add migrations/versions/*.py
git commit -m "feat: agregar migración para email_verificado"
```

### 7. ⚠️ NUNCA editar migraciones ya aplicadas

Si una migración ya se aplicó en producción, NO la modifiques. En su lugar, crea una nueva migración para corregir.

### 8. ✅ Documentar cambios complejos

```python
def upgrade():
    """
    Esta migración realiza lo siguiente:
    1. Agrega columna email_verificado (boolean)
    2. Establece todos los valores existentes como False
    3. Agrega índice para búsquedas rápidas
    
    Nota: No afecta el rendimiento en tablas pequeñas (<10k registros)
    """
    # ... código ...
```

---

## Comandos de Referencia Rápida

```bash
# ===== CONFIGURACIÓN INICIAL =====
# Para BD nueva (sin tablas)
python manage_migrations.py upgrade

# Para BD existente (con tablas)
python manage_migrations.py init

# ===== OPERACIONES DIARIAS =====
# Ver estado
python manage_migrations.py status

# Crear migración nueva
python manage_migrations.py create "descripcion"

# Aplicar migraciones
python manage_migrations.py upgrade

# Revertir última migración
python manage_migrations.py downgrade

# Ver historial
python manage_migrations.py history

# ===== BACKUPS =====
# Crear backup
python manage_migrations.py backup

# ===== ALEMBIC DIRECTO =====
alembic current              # Versión actual
alembic history              # Historial
alembic upgrade head         # Aplicar todo
alembic downgrade -1         # Revertir una
alembic revision -m "msg"    # Nueva migración
alembic stamp head           # Marcar como migrada
```

---

## Integración con el Sistema Montero

### Actualizar requirements.txt

Agregar Alembic a las dependencias:

```txt
# En requirements.txt
alembic==1.13.0
SQLAlchemy==2.0.23
```

### Instalar dependencias:

```bash
pip install -r requirements.txt
```

---

## 📚 Recursos Adicionales

- **Documentación oficial de Alembic**: https://alembic.sqlalchemy.org/
- **Tutorial de Alembic**: https://alembic.sqlalchemy.org/en/latest/tutorial.html
- **SQLAlchemy Core (para operaciones)**: https://docs.sqlalchemy.org/en/20/core/

---

## ✅ Checklist de Implementación

Para implementar Alembic en tu sistema:

- [ ] Instalar Alembic: `pip install alembic`
- [ ] Copiar archivos de configuración (alembic.ini, migrations/)
- [ ] Decidir: ¿BD nueva o existente?
  - [ ] Si es nueva: `python manage_migrations.py upgrade`
  - [ ] Si es existente: `python manage_migrations.py init`
- [ ] Verificar que funciona: `python manage_migrations.py status`
- [ ] Crear backup antes de cambios: `python manage_migrations.py backup`
- [ ] Documentar el proceso al equipo
- [ ] Agregar migraciones a Git

---

## 🎯 Conclusión

Alembic es una herramienta poderosa que te permite:

1. **Versionar** tu base de datos como versionas tu código
2. **Revertir** cambios cuando algo sale mal
3. **Documentar** automáticamente los cambios en el schema
4. **Sincronizar** múltiples ambientes (dev, test, prod)
5. **Colaborar** mejor con tu equipo

Con esta guía y el script `manage_migrations.py`, tienes todo lo necesario para gestionar las migraciones de tu sistema Montero de forma profesional.

¡Éxito con las migraciones! 🚀

---

*Guía creada para Sistema Montero - Noviembre 2025*
