# ⚡ INICIO RÁPIDO - ALEMBIC EN 5 MINUTOS

> **Para los que no tienen tiempo de leer documentación completa**

## 🚀 Instalación Express (3 minutos)

```bash
# 1. Instalar (30 seg)
pip install alembic sqlalchemy

# 2. Copiar archivos a tu proyecto (1 min)
# Copia todo el contenido de esta carpeta a tu proyecto

# 3. Validar (30 seg)
python validate_alembic_setup.py
# Espera ver: ✅ CONFIGURACIÓN CORRECTA

# 4. Inicializar (1 min)
# Si tu BD es NUEVA (sin tablas):
python manage_migrations.py upgrade

# Si tu BD YA EXISTE (con tablas):
python manage_migrations.py init
```

## 📋 Comandos del Día a Día

```bash
# Ver estado actual
python manage_migrations.py status

# Crear nueva migración
python manage_migrations.py create "descripción del cambio"

# Aplicar migraciones pendientes
python manage_migrations.py upgrade

# Ver historial de cambios
python manage_migrations.py history
```

## 🎯 Ejemplo Práctico: Agregar una Columna

### Paso 1: Crear migración

```bash
python manage_migrations.py create "agregar email_verificado a usuarios"
```

### Paso 2: Editar archivo generado

Alembic crea: `migrations/versions/003_agregar_email_verificado.py`

Edítalo así:

```python
def upgrade():
    with op.batch_alter_table('usuarios') as batch_op:
        batch_op.add_column(
            sa.Column('email_verificado', sa.Boolean(), default=False)
        )

def downgrade():
    with op.batch_alter_table('usuarios') as batch_op:
        batch_op.drop_column('email_verificado')
```

### Paso 3: Aplicar

```bash
python manage_migrations.py upgrade
```

¡Listo! La columna está agregada.

## 🆘 Solución de Problemas Rápida

| Error | Solución |
|-------|----------|
| "Table already exists" | `python manage_migrations.py init` |
| "alembic: command not found" | `pip install alembic` |
| "Can't locate revision" | `alembic stamp 001_initial_schema` |

## 📚 ¿Necesitas más detalles?

- **Instalación completa**: `INSTALACION_RAPIDA_ALEMBIC.md` (10 min)
- **Guía completa**: `GUIA_MIGRACIONES_ALEMBIC.md` (1 hora)
- **Documentación oficial**: https://alembic.sqlalchemy.org/

## ✅ Checklist Express

- [ ] Alembic instalado
- [ ] Archivos copiados al proyecto
- [ ] Validación pasada (verde)
- [ ] BD inicializada (upgrade o init)
- [ ] Primera migración creada y aplicada

## 💡 Recuerda

1. **Siempre** haz backup antes de migrar (automático con manage_migrations.py)
2. **Prueba** en desarrollo antes de producción
3. **Una migración** = Un cambio lógico
4. **Nunca modifiques** migraciones ya aplicadas en producción

---

**Tiempo total**: 5-10 minutos  
**Dificultad**: ⭐⭐☆☆☆ Fácil  
**Nivel requerido**: Básico en Python y SQL

¡Listo para usar! 🎉
