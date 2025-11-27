# Alembic Quick Start - Sistema Montero

## ¿Qué se implementó?

✅ **Modelos SQLAlchemy completos** para todas las tablas
✅ **Configuración de Alembic** para migraciones automáticas
✅ **Migración inicial generada** que sincroniza el schema actual

## Archivos Creados

- ✅ `models/database.py` - Modelos SQLAlchemy (Empresa, Usuario, Pago, Tutela, etc.)
- ✅ `models/__init__.py` - Export de modelos
- ✅ `migrations/env.py` - Configuración actualizada para usar modelos
- ✅ `migrations/versions/a93ebf45de70_sincronizar_modelos_sqlalchemy_con_.py` - Nueva migración
- ✅ `ALEMBIC_MIGRATIONS_DOCUMENTATION.md` - Documentación completa

## Comandos Básicos

### Ver estado actual
```bash
cd D:\Mi-App-React\src\dashboard

# Ver la versión actual de la BD
alembic current

# Ver historial de migraciones
alembic history
```

### Crear una nueva migración

```bash
# 1. Modificar modelos en models/database.py
# 2. Generar migración automática
alembic revision --autogenerate -m "Descripción del cambio"

# 3. Revisar el archivo generado en migrations/versions/
# 4. Aplicar la migración
alembic upgrade head
```

### Aplicar migraciones

```bash
# Aplicar todas las migraciones pendientes
alembic upgrade head

# Aplicar solo la siguiente
alembic upgrade +1
```

### Revertir migraciones

```bash
# Revertir la última
alembic downgrade -1

# Revertir todas
alembic downgrade base
```

## Ejemplo Rápido: Agregar un campo

### 1. Modificar el modelo
```python
# En models/database.py
class Usuario(Base):
    # ... campos existentes ...
    numero_hijos = Column(Integer, default=0)  # ← NUEVO
```

### 2. Generar migración
```bash
alembic revision --autogenerate -m "Agregar numero_hijos a usuarios"
```

### 3. Aplicar migración
```bash
alembic upgrade head
```

### 4. Usar el campo
```python
from models import Usuario, get_session, get_engine

engine = get_engine()
session = get_session(engine)

usuario = session.query(Usuario).first()
usuario.numero_hijos = 2
session.commit()
```

## Usar SQLAlchemy ORM

### Antes (SQL raw)
```python
conn = get_db_connection()
user = conn.execute(
    "SELECT * FROM usuarios WHERE id = ?", (1,)
).fetchone()
print(user["primerNombre"])
```

### Ahora (ORM)
```python
from models import Usuario, get_session, get_engine

session = get_session(get_engine())
user = session.query(Usuario).filter_by(id=1).first()
print(user.primerNombre)
print(user.empresa.nombre_empresa)  # Relación automática!
```

## Modelos Disponibles

```python
from models import (
    Base,           # Base declarativa
    Empresa,        # Modelo de empresas
    Usuario,        # Modelo de usuarios/empleados
    Pago,           # Modelo de pagos
    Tutela,         # Modelo de tutelas
    Cotizacion,     # Modelo de cotizaciones
    Incapacidad,    # Modelo de incapacidades
    Notificacion,   # Modelo de notificaciones
    get_engine,     # Función para obtener engine
    get_session,    # Función para obtener sesión
    init_db,        # Función para inicializar BD
)
```

## Flujo de Trabajo

```
1. Editar models/database.py
2. alembic revision --autogenerate -m "mensaje"
3. Revisar migrations/versions/xxxxx_mensaje.py
4. alembic upgrade head
5. Usar los modelos en el código
```

## Solución Rápida de Problemas

### "Target database is not up to date"
```bash
alembic upgrade head
```

### "table already exists"
```bash
alembic stamp head
```

### "No module named 'models'"
Verifica que estás en el directorio correcto:
```bash
cd D:\Mi-App-React\src\dashboard
```

## Próximos Pasos

1. ✅ Revisar la migración generada en `migrations/versions/`
2. ✅ Aplicar la migración: `alembic upgrade head`
3. ✅ Leer la documentación completa: `ALEMBIC_MIGRATIONS_DOCUMENTATION.md`
4. ✅ Empezar a usar los modelos SQLAlchemy en tu código

## Ayuda

- 📚 Documentación completa: `ALEMBIC_MIGRATIONS_DOCUMENTATION.md`
- 🔧 Modelos: `models/database.py`
- 📝 Migraciones: `migrations/versions/`

---

¡Listo! Ahora tienes un sistema de migraciones profesional. 🎉
