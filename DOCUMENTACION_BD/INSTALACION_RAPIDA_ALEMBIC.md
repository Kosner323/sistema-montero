# 🚀 INSTALACIÓN RÁPIDA DE ALEMBIC - SISTEMA MONTERO

## 📋 Checklist de Instalación

### Paso 1: Instalar Dependencias (5 minutos)

```bash
# Instalar Alembic y SQLAlchemy
pip install alembic==1.13.0
pip install sqlalchemy==2.0.23

# O instalar desde requirements.txt actualizado
pip install -r requirements.txt
```

### Paso 2: Copiar Archivos de Configuración (2 minutos)

Copia estos archivos a tu proyecto:

```
tu-proyecto/
├── alembic.ini                    ← Copiar aquí
├── manage_migrations.py           ← Copiar aquí
├── validate_alembic_setup.py      ← Copiar aquí
├── GUIA_MIGRACIONES_ALEMBIC.md    ← Copiar aquí
│
└── migrations/                    ← Crear este directorio completo
    ├── env.py
    ├── script.py.mako
    ├── README.md
    └── versions/
        ├── 001_initial_schema.py
        └── 002_agregar_auditoria_EJEMPLO.py
```

### Paso 3: Validar Instalación (1 minuto)

```bash
# Ejecutar validador
python validate_alembic_setup.py

# Deberías ver: ✅ CONFIGURACIÓN CORRECTA
```

### Paso 4: Inicializar Según tu Caso

#### Caso A: Base de Datos NUEVA (sin tablas)

```bash
# Aplicar migración inicial (crea todas las tablas)
python manage_migrations.py upgrade

# Verificar
python manage_migrations.py status
```

#### Caso B: Base de Datos EXISTENTE (ya tiene tablas)

```bash
# Marcar como "ya migrada" (no crea nada, solo registra)
python manage_migrations.py init

# Verificar
python manage_migrations.py status
```

### Paso 5: Verificación Final (1 minuto)

```bash
# Ver estado actual
python manage_migrations.py status

# Ver historial
python manage_migrations.py history

# Si todo está OK, verás la versión actual
```

## 🎯 ¿Qué Archivos Hacen Qué?

| Archivo | Propósito | ¿Cuándo usarlo? |
|---------|-----------|-----------------|
| `alembic.ini` | Configuración general | Solo al instalar |
| `manage_migrations.py` | Script helper | TODO EL TIEMPO |
| `migrations/env.py` | Conexión a BD | No tocar |
| `migrations/versions/001_*.py` | Migración inicial | Solo una vez |
| `validate_alembic_setup.py` | Validar configuración | Cuando dudes |
| `GUIA_MIGRACIONES_ALEMBIC.md` | Documentación completa | Para referencia |

## 📝 Comandos del Día a Día

```bash
# Ver estado actual
python manage_migrations.py status

# Crear nueva migración
python manage_migrations.py create "descripción del cambio"

# Aplicar migraciones pendientes
python manage_migrations.py upgrade

# Ver historial
python manage_migrations.py history

# Crear backup
python manage_migrations.py backup
```

## ⚠️ Errores Comunes y Soluciones

### Error: "Table already exists"

**Causa**: Intentas crear tablas que ya existen.

**Solución**:
```bash
python manage_migrations.py init
```

### Error: "alembic: command not found"

**Causa**: Alembic no está instalado.

**Solución**:
```bash
pip install alembic
```

### Error: "Can't locate revision"

**Causa**: La BD tiene una versión que no existe en tus archivos.

**Solución**:
```bash
# Forzar a la versión inicial
alembic stamp 001_initial_schema
```

## 🔧 Actualizar requirements.txt

Agrega estas líneas a tu `requirements.txt`:

```txt
# Migraciones de base de datos
alembic==1.13.0
SQLAlchemy==2.0.23
```

## 📚 Siguiente Paso

Una vez instalado, lee la guía completa:

```bash
# Linux/Mac
cat GUIA_MIGRACIONES_ALEMBIC.md

# Windows
type GUIA_MIGRACIONES_ALEMBIC.md
```

O ábrela con tu editor de texto favorito.

## 🆘 Necesitas Ayuda?

1. **Validar configuración**:
   ```bash
   python validate_alembic_setup.py
   ```

2. **Ver estado actual**:
   ```bash
   python manage_migrations.py status
   ```

3. **Leer la guía completa**:
   - `GUIA_MIGRACIONES_ALEMBIC.md`

4. **Ver ejemplos de migraciones**:
   - `migrations/versions/001_initial_schema.py`
   - `migrations/versions/002_agregar_auditoria_EJEMPLO.py`

## ✅ ¡Listo!

Si la validación pasa al 100%, ya estás listo para usar Alembic.

**Próximo paso**: Crear tu primera migración personalizada.

```bash
python manage_migrations.py create "mi primer cambio"
```

---

*Instalación para Sistema Montero - Noviembre 2025*

## 🎓 Recursos de Aprendizaje

- [Documentación oficial](https://alembic.sqlalchemy.org/)
- [Tutorial interactivo](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- Guía completa: `GUIA_MIGRACIONES_ALEMBIC.md`

---

**Tiempo total de instalación**: ~10 minutos

**Nivel de dificultad**: ⭐⭐☆☆☆ (Fácil)

**Beneficios**: 
- ✅ Control de versiones de BD
- ✅ Cambios reversibles
- ✅ Trabajo en equipo más fácil
- ✅ Sincronización entre ambientes
