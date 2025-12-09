# =====================================================================
# Dockerfile - Sistema Montero
# =====================================================================
# Dockerfile multi-stage para optimizar el tamaño de la imagen
# y separar dependencias de desarrollo y producción

# =====================================================================
# Stage 1: Builder (Instalación de dependencias)
# =====================================================================
FROM python:3.11-slim-bullseye as builder

# Establecer variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema necesarias para compilar paquetes Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar solo requirements.txt primero (para aprovechar cache de Docker)
COPY requirements.txt .
# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# =====================================================================
# Stage 2: Runtime (Imagen final optimizada)
# =====================================================================
FROM python:3.11-slim-bullseye

# Metadatos de la imagen
LABEL maintainer="Sistema Montero <kevinlomasd@gmail.com>"
LABEL description="Sistema de Gestión de Nómina y Recursos Humanos - Montero"
LABEL version="1.0.0"

# Establecer variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP=app.py

# Instalar solo las dependencias de runtime necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/* # <--- SINTAXIS CORREGIDA: Comando '&& rm -rf /var/lib/apt/lists/*' está en la línea inmediatamente siguiente a la última con un backslash (\)

# Crear usuario no-root para ejecutar la aplicación
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data /app/logs && \
    chown -R appuser:appuser /app 

# Establecer directorio de trabajo
WORKDIR /app

# Copiar dependencias instaladas desde el builder (librerías Y ejecutables)
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiar estructura de la aplicación (orden optimizado para cache de Docker)
# Primero archivos de configuración que cambian menos
COPY --chown=appuser:appuser alembic.ini .
COPY --chown=appuser:appuser celery_config.py .
COPY --chown=appuser:appuser celery_tasks.py .
COPY --chown=appuser:appuser extensions.py .
COPY --chown=appuser:appuser logger.py .
COPY --chown=appuser:appuser email_utils.py .
COPY --chown=appuser:appuser encryption.py .
COPY --chown=appuser:appuser app.py .

# Copiar carpetas principales
COPY --chown=appuser:appuser models/ ./models/
COPY --chown=appuser:appuser routes/ ./routes/
COPY --chown=appuser:appuser templates/ ./templates/
COPY --chown=appuser:appuser static/ ./static/
COPY --chown=appuser:appuser assets/ ./assets/
COPY --chown=appuser:appuser migrations/ ./migrations/
COPY --chown=appuser:appuser scripts/ ./scripts/

# Copiar script de entrypoint
COPY --chown=appuser:appuser entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Cambiar al usuario no-root
USER appuser

# Exponer el puerto de la aplicación
EXPOSE 5000

# Healthcheck para verificar que la aplicación esté funcionando
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health').read()" || exit 1

# Punto de entrada
ENTRYPOINT ["/entrypoint.sh"]

# Comando por defecto (puede ser sobrescrito en docker-compose)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]