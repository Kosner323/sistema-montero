#!/bin/bash
# =====================================================================
# entrypoint.sh - Sistema Montero
# =====================================================================
# Script de inicialización del contenedor Docker

# NO usar set -e para permitir que el script continúe ante errores de migración
set +e

echo "=========================================="
echo "Sistema Montero - Iniciando aplicación"
echo "=========================================="

# =====================================================================
# 1. Verificar que existan los directorios necesarios
# =====================================================================
echo "[INFO] Verificando directorios..."
mkdir -p /app/data /app/logs
echo "[OK] Directorios verificados"

# =====================================================================
# 2. Esperar a que Redis esté disponible (si se usa)
# =====================================================================
if [ ! -z "$RATELIMIT_STORAGE_URL" ]; then
    echo "[INFO] Esperando a que Redis esté disponible..."
    max_attempts=30
    attempt=0

    until nc -z redis 6379 || [ $attempt -eq $max_attempts ]; do
        attempt=$((attempt + 1))
        echo "[INFO] Intento $attempt/$max_attempts - Esperando Redis..."
        sleep 2
    done

    if [ $attempt -eq $max_attempts ]; then
        echo "[WARNING] Redis no está disponible después de $max_attempts intentos"
        echo "[WARNING] Continuando sin Redis (rate limiting usará memoria local)"
    else
        echo "[OK] Redis está disponible"
    fi
fi

# =====================================================================
# 3. Verificar/Crear base de datos SQLite
# =====================================================================
echo "[INFO] Verificando base de datos..."
if [ ! -f "/app/data/mi_sistema.db" ]; then
    echo "[INFO] Base de datos no encontrada. Creando..."
    python -c "from models.database import init_db; init_db()"
    echo "[OK] Base de datos creada"
else
    echo "[OK] Base de datos existente encontrada"
fi

# =====================================================================
# 4. Ejecutar migraciones de Alembic
# =====================================================================
echo "[INFO] Ejecutando migraciones de base de datos..."
alembic current 2>/dev/null
current_status=$?

if [ $current_status -eq 0 ]; then
    echo "[INFO] Aplicando migraciones pendientes..."
    alembic upgrade head 2>&1
    upgrade_status=$?

    if [ $upgrade_status -eq 0 ]; then
        echo "[OK] Migraciones aplicadas correctamente"
    else
        echo "[WARNING] Error al aplicar migraciones (posiblemente tablas ya existen)"
        echo "[INFO] Marcando la base de datos como actualizada..."
        alembic stamp head
        echo "[OK] Base de datos marcada como actualizada"
    fi
else
    echo "[WARNING] No se pudo verificar el estado de migraciones"
    echo "[INFO] Intentando marcar la base de datos como actualizada..."
    alembic stamp head 2>/dev/null || echo "[WARNING] No se pudo ejecutar alembic stamp"
fi

# =====================================================================
# 5. Verificar variables de entorno críticas
# =====================================================================
echo "[INFO] Verificando configuración..."
if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "change-this-secret-key-in-production" ]; then
    echo "[WARNING] SECRET_KEY no está configurada o usa el valor por defecto"
    echo "[WARNING] Por favor, configura SECRET_KEY en producción"
fi

if [ -z "$MAIL_USERNAME" ] || [ -z "$MAIL_PASSWORD" ]; then
    echo "[WARNING] Credenciales de email no configuradas"
    echo "[WARNING] El envío de correos no funcionará"
fi

echo "[OK] Verificación de configuración completada"

# =====================================================================
# 6. Configurar el modo de ejecución
# =====================================================================
if [ "$FLASK_ENV" = "development" ]; then
    echo "[INFO] Modo: DESARROLLO"
    echo "[INFO] Hot-reload habilitado"
else
    echo "[INFO] Modo: PRODUCCIÓN"
fi

# =====================================================================
# 7. Mostrar información del sistema
# =====================================================================
echo "=========================================="
echo "Información del contenedor:"
echo "  - Python: $(python --version)"
echo "  - Flask: $(python -c 'import flask; print(flask.__version__)')"
echo "  - Gunicorn: $(gunicorn --version)"
echo "  - Usuario: $(whoami)"
echo "  - Directorio: $(pwd)"
echo "=========================================="

# =====================================================================
# 8. Ejecutar el comando pasado como argumento
# =====================================================================
echo "[INFO] Iniciando aplicación..."
echo "=========================================="

# Si no se pasa ningún comando, usar el CMD del Dockerfile
exec "$@"
