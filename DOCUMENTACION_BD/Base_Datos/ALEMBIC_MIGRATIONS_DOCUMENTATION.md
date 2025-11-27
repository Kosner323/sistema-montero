# Documentación de Migraciones con Alembic - Sistema Montero

## Resumen
Se ha implementado **Alembic** para gestionar las migraciones de base de datos del Sistema Montero, permitiendo aplicar cambios al esquema de forma incremental, reversible y controlada.

## Archivos Creados/Modificados

### Modelos SQLAlchemy
1. **`models/database.py`** (NUEVO) - Modelos completos de SQLAlchemy
   - `Empresa`
   - `Usuario`
   - `Pago`
   - `Tutela`
   - `Cotizacion`
   - `Incapacidad`
   - `Notificacion`

2. **`models/__init__.py`** (MODIFICADO) - Export de modelos SQLAlchemy

### Configuración de Alembic
3. **`migrations/env.py`** (MODIFICADO) - Configurado para usar modelos SQLAlchemy
4. **`alembic.ini`** (EXISTENTE) - Configuración de Alembic

### Migraciones Generadas
5. **`migrations/versions/a93ebf45de70_sincronizar_modelos_sqlalchemy_con_.py`** (NUEVO)
   - Sincroniza modelos SQLAlchemy con la estructura actual

## ¿Qué es Alembic?

Alembic es una herramienta de migración de bases de datos para SQLAlchemy que permite:
- ✅ Versionar cambios en el esquema de la base de datos
- ✅ Aplicar migraciones de forma incremental
- ✅ Revertir migraciones si es necesario
- ✅ Generar migraciones automáticamente comparando modelos con el esquema actual
- ✅ Trabajar en equipo sincronizando cambios de schema

## Estructura de Archivos

```
src/dashboard/
├── alembic.ini                    # Configuración principal de Alembic
├── migrations/                    # Directorio de migraciones
│   ├── env.py                     # Script de entorno
│   ├── script.py.mako             # Template para nuevas migraciones
│   ├── README.md                  # Documentación del directorio
│   └── versions/                  # Archivos de migración
│       ├── 001_initial_schema.py
│       ├── 002_agregar_auditoria_EJEMPLO.py
│       ├── cf6695b8bf8f_agregar_fecha_inicio_a_tutelas.py
│       └── a93ebf45de70_sincronizar_modelos_sqlalchemy_con_.py  ← NUEVA
└── models/
    ├── __init__.py
    ├── database.py                # Modelos SQLAlchemy ← NUEVO
    └── validation_models.py       # Modelos Pydantic
```

## Modelos SQLAlchemy Implementados

### 1. Modelo Empresa
```python
class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True)
    nombre_empresa = Column(String, nullable=False)
    nit = Column(String, nullable=False, unique=True)
    # ... más campos
```

### 2. Modelo Usuario
```python
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    empresa_nit = Column(String, ForeignKey("empresas.nit"))
    primerNombre = Column(String, nullable=False)
    # ... más campos

    # Relaciones
    empresa = relationship("Empresa", back_populates="usuarios")
    pagos = relationship("Pago", back_populates="usuario")
```

### 3. Modelo Pago
```python
class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    periodo = Column(String, nullable=False)
    # ... más campos
```

### 4. Modelo Tutela
```python
class Tutela(Base):
    __tablename__ = "tutelas"

    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    numero_tutela = Column(String, unique=True)
    # ... más campos
```

## Comandos Principales de Alembic

### Ver el estado actual
```bash
cd D:\Mi-App-React\src\dashboard

# Ver la versión actual de la base de datos
alembic current

# Ver el historial de migraciones
alembic history

# Ver migraciones pendientes
alembic history --verbose
```

### Generar una nueva migración

#### Opción 1: Autogenerate (Recomendado)
```bash
# Detecta automáticamente los cambios comparando modelos con la BD
alembic revision --autogenerate -m "Descripción del cambio"
```

#### Opción 2: Manual
```bash
# Crea un archivo de migración vacío para editar manualmente
alembic revision -m "Descripción del cambio"
```

### Aplicar migraciones

```bash
# Aplicar todas las migraciones pendientes
alembic upgrade head

# Aplicar solo la siguiente migración
alembic upgrade +1

# Aplicar hasta una revisión específica
alembic upgrade a93ebf45de70
```

### Revertir migraciones

```bash
# Revertir la última migración
alembic downgrade -1

# Revertir todas las migraciones
alembic downgrade base

# Revertir hasta una revisión específica
alembic downgrade cf6695b8bf8f
```

### Otros comandos útiles

```bash
# Ver el SQL que se ejecutará (sin aplicarlo)
alembic upgrade head --sql

# Marcar la BD como actualizada sin ejecutar migraciones
alembic stamp head

# Ver información de una revisión
alembic show a93ebf45de70
```

## Flujo de Trabajo Típico

### 1. Modificar Modelos
Edita `models/database.py` para agregar, modificar o eliminar campos/tablas:

```python
# Ejemplo: Agregar campo a Usuario
class Usuario(Base):
    __tablename__ = "usuarios"
    # ... campos existentes ...
    nuevo_campo = Column(String)  # ← NUEVO
```

### 2. Generar Migración
```bash
alembic revision --autogenerate -m "Agregar campo nuevo_campo a usuarios"
```

### 3. Revisar Migración Generada
Abre el archivo en `migrations/versions/` y verifica que los cambios sean correctos:

```python
def upgrade():
    op.add_column('usuarios',
        sa.Column('nuevo_campo', sa.String(), nullable=True)
    )

def downgrade():
    op.drop_column('usuarios', 'nuevo_campo')
```

### 4. Aplicar Migración
```bash
alembic upgrade head
```

### 5. Verificar en la BD
```python
# En Python:
from models import Usuario, get_session, get_engine

engine = get_engine()
session = get_session(engine)

usuarios = session.query(Usuario).all()
print(usuarios[0].nuevo_campo)  # None o el valor por defecto
```

## Ejemplos Prácticos

### Ejemplo 1: Agregar una nueva columna

**1. Modificar el modelo:**
```python
# En models/database.py
class Usuario(Base):
    # ... código existente ...
    numero_hijos = Column(Integer, default=0)  # ← NUEVO
```

**2. Generar migración:**
```bash
alembic revision --autogenerate -m "Agregar numero_hijos a usuarios"
```

**3. Aplicar migración:**
```bash
alembic upgrade head
```

### Ejemplo 2: Crear una nueva tabla

**1. Crear el modelo:**
```python
# En models/database.py
class Departamento(Base):
    __tablename__ = "departamentos"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    codigo = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

**2. Exportar el modelo:**
```python
# En models/__init__.py
from .database import (
    # ... otros modelos ...
    Departamento,  # ← NUEVO
)
```

**3. Generar y aplicar migración:**
```bash
alembic revision --autogenerate -m "Crear tabla departamentos"
alembic upgrade head
```

### Ejemplo 3: Modificar un campo existente

**1. Modificar el modelo:**
```python
# Cambiar tipo de datos
class Usuario(Base):
    # Antes: ibc = Column(Float)
    ibc = Column(Float, nullable=False, default=0)  # ← Ahora not null
```

**2. Generar migración:**
```bash
alembic revision --autogenerate -m "Hacer ibc NOT NULL con default 0"
```

**3. Revisar y editar migración:**
```python
def upgrade():
    # Primero actualizar valores nulos
    op.execute("UPDATE usuarios SET ibc = 0 WHERE ibc IS NULL")
    # Luego cambiar a NOT NULL
    op.alter_column('usuarios', 'ibc',
        existing_type=sa.Float(),
        nullable=False,
        server_default='0')

def downgrade():
    op.alter_column('usuarios', 'ibc',
        existing_type=sa.Float(),
        nullable=True,
        server_default=None)
```

**4. Aplicar:**
```bash
alembic upgrade head
```

## Integración con Flask

### Usar modelos SQLAlchemy en lugar de SQL raw

**Antes (SQL raw):**
```python
conn = get_db_connection()
user = conn.execute(
    "SELECT * FROM usuarios WHERE id = ?", (user_id,)
).fetchone()
```

**Ahora (SQLAlchemy ORM):**
```python
from models import Usuario, get_session, get_engine

engine = get_engine()
session = get_session(engine)

user = session.query(Usuario).filter_by(id=user_id).first()
print(user.primerNombre, user.primerApellido)
```

### Ventajas de usar ORM:
- ✅ Autocompletado en el IDE
- ✅ Type hints y validación
- ✅ Relaciones automáticas
- ✅ Menos propenso a errores
- ✅ Más fácil de refactorizar

## Configuración

### alembic.ini
```ini
[alembic]
script_location = migrations
file_template = %%(rev)s_%%(slug)s
sqlalchemy.url = sqlite:///data/mi_sistema.db  # ← URL de la BD
```

### migrations/env.py
```python
import sys
import os

# Agregar path para importar modelos
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Importar Base con todos los modelos
from models.database import Base

# Configurar metadata
target_metadata = Base.metadata  # ← Esto permite autogenerate
```

## Troubleshooting

### Error: "Target database is not up to date"
**Causa:** La BD no tiene aplicadas todas las migraciones
**Solución:**
```bash
alembic upgrade head
```

### Error: "table already exists"
**Causa:** La tabla ya existe pero Alembic intenta crearla
**Solución:**
```bash
# Marcar la BD como actualizada
alembic stamp head
```

### Error: "No module named 'models'"
**Causa:** El path no está configurado en env.py
**Solución:** Verifica que env.py tenga:
```python
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
```

### La migración no detecta cambios
**Posibles causas:**
1. Los modelos no están importados en `models/__init__.py`
2. El modelo no hereda de `Base`
3. `target_metadata` no está configurado en `env.py`

**Solución:** Verificar los 3 puntos anteriores

## Buenas Prácticas

### 1. Siempre revisa las migraciones autogeneradas
```bash
# Después de generar
alembic revision --autogenerate -m "..."

# Abre y revisa el archivo en migrations/versions/
# Verifica que upgrade() y downgrade() sean correctos
```

### 2. Agrega datos de prueba en la migración si es necesario
```python
def upgrade():
    op.create_table('departamentos', ...)

    # Agregar datos iniciales
    op.execute("""
        INSERT INTO departamentos (nombre, codigo) VALUES
        ('Recursos Humanos', 'RH'),
        ('Contabilidad', 'CONT')
    """)
```

### 3. Prueba downgrade antes de hacer commit
```bash
alembic upgrade head
alembic downgrade -1  # Probar revertir
alembic upgrade head  # Volver a aplicar
```

### 4. Usa mensajes descriptivos
```bash
# Mal
alembic revision --autogenerate -m "cambios"

# Bien
alembic revision --autogenerate -m "Agregar tabla departamentos y campo usuario.numero_hijos"
```

### 5. Haz backups antes de migraciones importantes
```bash
# Backup de SQLite
cp data/mi_sistema.db data/mi_sistema_backup_$(date +%Y%m%d).db

# Aplicar migración
alembic upgrade head
```

## Referencias

- [Documentación oficial de Alembic](https://alembic.sqlalchemy.org/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/14/orm/tutorial.html)
- [Alembic Autogenerate](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)

---

**Implementado el:** 2025-11-15
**Versión de Alembic:** Instalada desde requirements.txt
**Base de datos:** SQLite
