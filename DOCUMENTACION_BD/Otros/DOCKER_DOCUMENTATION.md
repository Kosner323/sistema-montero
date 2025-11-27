# Documentación Completa de Docker - Sistema Montero

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Arquitectura](#arquitectura)
3. [Archivos Docker](#archivos-docker)
4. [Configuración](#configuración)
5. [Uso Avanzado](#uso-avanzado)
6. [Producción](#producción)
7. [Troubleshooting](#troubleshooting)
8. [Optimizaciones](#optimizaciones)

---

## Introducción

### ¿Qué es Docker?

Docker es una plataforma de contenedorización que permite empaquetar aplicaciones y sus dependencias en contenedores portables.

### Beneficios para Sistema Montero

- **Portabilidad**: Funciona igual en desarrollo, staging y producción
- **Aislamiento**: Cada servicio corre en su propio contenedor
- **Reproducibilidad**: Mismo ambiente en todos los entornos
- **Escalabilidad**: Fácil de escalar horizontalmente
- **Versionado**: Control de versiones de infraestructura como código

---

## Arquitectura

### Diagrama de Servicios

```
┌─────────────────────────────────────────────┐
│             Internet/Cliente                │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │   Nginx (Opcional)   │
        │   Puerto: 80/443     │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │    Flask App         │
        │    Puerto: 5000      │
        │    Gunicorn (4w)     │
        └──────────┬───────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
         ▼                   ▼
    ┌────────┐          ┌────────┐
    │ Redis  │          │ SQLite │
    │  6379  │          │  File  │
    └────────┘          └────────┘
```

### Componentes

1. **App Container** (montero-backend)
   - Imagen: Custom (Python 3.11 slim)
   - Función: API Backend Flask
   - Servidor: Gunicorn
   - Workers: 4 (configurable)

2. **Redis Container** (montero-redis)
   - Imagen: redis:7-alpine
   - Función: Cache y Rate Limiting
   - Persistencia: AOF habilitada
   - Memoria máxima: 256MB

3. **Nginx Container** (montero-nginx) - Opcional
   - Imagen: nginx:alpine
   - Función: Proxy inverso, SSL termination
   - Solo en producción

---

## Archivos Docker

### 1. Dockerfile

Imagen multi-stage para optimizar tamaño y seguridad.

#### Stage 1: Builder
```dockerfile
FROM python:3.11-slim-buster as builder

# Instala dependencias de compilación
RUN apt-get update && apt-get install -y gcc g++ libffi-dev

# Instala paquetes Python en /root/.local
RUN pip install --user -r requirements.txt
```

**Propósito:**
- Compilar paquetes Python que requieren herramientas de build
- Mantener las dependencias de compilación separadas de runtime

#### Stage 2: Runtime
```dockerfile
FROM python:3.11-slim-buster

# Copia solo los paquetes instalados (no las herramientas de build)
COPY --from=builder /root/.local /root/.local

# Usuario no-root para seguridad
USER appuser
```

**Propósito:**
- Imagen final más pequeña (no incluye gcc, g++, etc.)
- Mayor seguridad (usuario no-root)
- Menos superficie de ataque

#### Características de Seguridad

1. **Usuario no-root:**
```dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

2. **Variables de entorno seguras:**
```dockerfile
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
```

3. **Healthcheck integrado:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s \
  CMD python -c "import urllib.request; ..."
```

### 2. docker-compose.yml

Orquestación de múltiples servicios.

#### Servicio App

```yaml
app:
  build:
    context: .
    dockerfile: Dockerfile
  restart: unless-stopped
  environment:
    - FLASK_ENV=${FLASK_ENV:-production}
    - SECRET_KEY=${SECRET_KEY}
  volumes:
    - ./data:/app/data
    - ./logs:/app/logs
  depends_on:
    - redis
```

**Explicación:**

- `restart: unless-stopped` - Reinicia automáticamente si falla
- `environment` - Variables con valores por defecto usando `${VAR:-default}`
- `volumes` - Persistencia de datos y logs
- `depends_on` - Espera a que Redis inicie primero

#### Servicio Redis

```yaml
redis:
  image: redis:7-alpine
  command: redis-server --appendonly yes --maxmemory 256mb
  volumes:
    - redis-data:/data
```

**Configuración:**

- `--appendonly yes` - Persistencia AOF (más segura)
- `--maxmemory 256mb` - Límite de memoria
- `--maxmemory-policy allkeys-lru` - Evicción LRU cuando se llena

#### Servicio Nginx (Producción)

```yaml
nginx:
  image: nginx:alpine
  profiles:
    - production
  volumes:
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
```

**Uso:**
```bash
# Solo se inicia con el perfil production
docker-compose --profile production up
```

### 3. .dockerignore

Excluye archivos innecesarios del contexto de build.

**Beneficios:**
- Build más rápido (menos archivos que copiar)
- Imagen más pequeña
- No incluye secretos accidentalmente

**Archivos excluidos:**
```
__pycache__/
*.pyc
.git/
.env
venv/
*.log
node_modules/
```

### 4. entrypoint.sh

Script de inicialización que se ejecuta al iniciar el contenedor.

**Tareas que realiza:**

1. **Verificación de directorios:**
```bash
mkdir -p /app/data /app/logs
```

2. **Espera a Redis:**
```bash
until nc -z redis 6379; do
  echo "Esperando Redis..."
  sleep 2
done
```

3. **Inicialización de BD:**
```bash
if [ ! -f "/app/data/mi_sistema.db" ]; then
  python -c "from models.database import init_db; init_db()"
fi
```

4. **Ejecución de migraciones:**
```bash
alembic upgrade head
```

5. **Validación de configuración:**
```bash
if [ -z "$SECRET_KEY" ]; then
  echo "[WARNING] SECRET_KEY no configurada"
fi
```

---

## Configuración

### Variables de Entorno

#### Obligatorias

```bash
SECRET_KEY=tu-clave-secreta-muy-segura-minimo-32-caracteres
MAIL_USERNAME=kevinlomasd@gmail.com
MAIL_PASSWORD=tu-app-password-de-gmail
```

#### Opcionales con valores por defecto

```bash
FLASK_ENV=production                    # development | production
MAIL_SERVER=smtp.gmail.com              # Servidor SMTP
MAIL_PORT=587                           # Puerto SMTP
MAIL_USE_TLS=True                       # Usar TLS
LOG_LEVEL=INFO                          # DEBUG | INFO | WARNING | ERROR
TZ=America/Bogota                       # Zona horaria
```

#### Para Rate Limiting

```bash
# Con Redis (recomendado en producción)
RATELIMIT_STORAGE_URL=redis://redis:6379/0

# Sin Redis (memoria local)
# No configurar RATELIMIT_STORAGE_URL
```

### Archivo .env

Crea un archivo `.env` en el directorio dashboard:

```bash
# .env
SECRET_KEY=genera-una-clave-secreta-aqui
FLASK_ENV=production

# Email
MAIL_USERNAME=kevinlomasd@gmail.com
MAIL_PASSWORD=lhxlprtwplxrsarj
MAIL_DEFAULT_SENDER=Sistema Montero <kevinlomasd@gmail.com>

# Logging
LOG_LEVEL=INFO
```

**Generar SECRET_KEY segura:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Uso Avanzado

### Comandos Docker Compose

#### Build y Ejecución

```bash
# Build y start
docker-compose up --build -d

# Build sin cache (fuerza reconstrucción)
docker-compose build --no-cache

# Start sin rebuild
docker-compose up -d

# Stop
docker-compose down

# Stop y eliminar volúmenes (CUIDADO)
docker-compose down -v
```

#### Logs

```bash
# Todos los servicios
docker-compose logs -f

# Solo app
docker-compose logs -f app

# Solo Redis
docker-compose logs -f redis

# Últimas 100 líneas
docker-compose logs --tail=100 app

# Desde hace 10 minutos
docker-compose logs --since 10m app
```

#### Escalado

```bash
# Escalar app a 3 instancias
docker-compose up -d --scale app=3

# Con load balancer (requiere configuración adicional)
docker-compose up -d --scale app=5
```

#### Shell en contenedor

```bash
# Shell interactivo
docker-compose exec app bash

# Ejecutar comando
docker-compose exec app python manage.py

# Como root (para instalar paquetes)
docker-compose exec --user root app bash
```

### Desarrollo con Hot-Reload

Edita `docker-compose.yml`:

```yaml
app:
  # ... configuración existente ...
  volumes:
    - ./data:/app/data
    - ./logs:/app/logs
    - .:/app  # <- Agregar esta línea
  command: flask run --host=0.0.0.0 --reload  # <- Cambiar CMD
  environment:
    - FLASK_ENV=development  # <- Cambiar a development
```

**Reiniciar:**
```bash
docker-compose down
docker-compose up
```

Ahora los cambios en código se reflejan automáticamente.

### Ejecución de Tests

```bash
# Dentro del contenedor
docker-compose exec app pytest

# Con coverage
docker-compose exec app pytest --cov=. --cov-report=html

# Tests específicos
docker-compose exec app pytest tests/test_auth.py -v
```

### Migraciones de Base de Datos

```bash
# Ver estado
docker-compose exec app alembic current

# Historial
docker-compose exec app alembic history

# Crear migración
docker-compose exec app alembic revision --autogenerate -m "Agregar campo"

# Aplicar migración
docker-compose exec app alembic upgrade head

# Revertir
docker-compose exec app alembic downgrade -1
```

### Gestión de Datos

#### Backup de SQLite

```bash
# Backup manual
docker-compose exec app sqlite3 /app/data/mi_sistema.db ".backup /app/data/backup.db"

# Copiar al host
docker cp montero-backend:/app/data/backup.db ./backups/
```

#### Backup de Redis

```bash
# Guardar snapshot
docker-compose exec redis redis-cli SAVE

# Copiar dump.rdb
docker cp montero-redis:/data/dump.rdb ./backups/
```

#### Restaurar desde backup

```bash
# Detener servicios
docker-compose down

# Restaurar archivo
cp ./backups/backup.db ./data/mi_sistema.db

# Reiniciar
docker-compose up -d
```

---

## Producción

### Checklist de Seguridad

- [ ] Cambiar SECRET_KEY de valor por defecto
- [ ] Usar contraseñas seguras
- [ ] Configurar firewall (solo puertos necesarios)
- [ ] Habilitar HTTPS con certificados SSL
- [ ] Configurar rate limiting con Redis
- [ ] Hacer backups automáticos
- [ ] Monitorear logs y métricas
- [ ] Actualizar imágenes regularmente

### Configuración con Nginx

Crea `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream flask_app {
        server app:5000;
    }

    server {
        listen 80;
        server_name tudominio.com;

        location / {
            proxy_pass http://flask_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /static {
            alias /app/static;
        }
    }
}
```

**Iniciar con Nginx:**
```bash
docker-compose --profile production up -d
```

### SSL/HTTPS con Let's Encrypt

```bash
# Instalar certbot
docker-compose exec nginx apk add certbot certbot-nginx

# Obtener certificado
docker-compose exec nginx certbot --nginx -d tudominio.com

# Auto-renovación (agregar a crontab)
0 0 * * * docker-compose exec nginx certbot renew --quiet
```

### Monitoreo

#### Healthchecks

```bash
# Verificar estado
docker inspect --format='{{.State.Health.Status}}' montero-backend

# Todos los servicios
docker-compose ps
```

#### Logs centralizados

Edita `docker-compose.yml`:

```yaml
app:
  logging:
    driver: "json-file"
    options:
      max-size: "10m"
      max-file: "3"
```

### Performance

#### Gunicorn Workers

Fórmula: `workers = (2 x CPU_CORES) + 1`

```yaml
# Para servidor con 2 CPUs
command: gunicorn --bind 0.0.0.0:5000 --workers 5 app:app
```

#### Redis Memory

```yaml
# Para tráfico alto
command: redis-server --appendonly yes --maxmemory 512mb
```

---

## Troubleshooting

### Problemas Comunes

#### 1. "Cannot connect to the Docker daemon"

```bash
# Iniciar Docker daemon
sudo systemctl start docker

# Verificar estado
sudo systemctl status docker
```

#### 2. "Port 5000 is already allocated"

```bash
# Ver qué proceso usa el puerto
sudo lsof -i :5000

# Cambiar puerto en docker-compose.yml
ports:
  - "8000:5000"
```

#### 3. "No space left on device"

```bash
# Limpiar imágenes no usadas
docker system prune -a

# Ver espacio usado
docker system df

# Eliminar volúmenes huérfanos
docker volume prune
```

#### 4. "Database is locked"

SQLite no soporta múltiples escrituras simultáneas.

**Soluciones:**
```bash
# 1. Reducir workers de Gunicorn
command: gunicorn --bind 0.0.0.0:5000 --workers 1 app:app

# 2. Migrar a PostgreSQL (recomendado)
```

#### 5. Contenedor se reinicia constantemente

```bash
# Ver logs del último crash
docker-compose logs --tail=50 app

# Verificar healthcheck
docker inspect montero-backend | grep -A 10 Health
```

### Debugging

#### Modo verbose

```bash
# Iniciar con logs detallados
docker-compose up --verbose
```

#### Inspeccionar contenedor

```bash
# Información completa
docker inspect montero-backend

# Ver configuración de red
docker inspect montero-backend --format='{{.NetworkSettings.Networks}}'

# Ver variables de entorno
docker inspect montero-backend --format='{{.Config.Env}}'
```

#### Ejecutar comandos de debug

```bash
# Python interactivo
docker-compose exec app python

# Ver procesos
docker-compose exec app ps aux

# Ver espacio en disco
docker-compose exec app df -h

# Test de conexión a Redis
docker-compose exec app nc -zv redis 6379
```

---

## Optimizaciones

### Reducir tamaño de imagen

1. **Usar alpine base:**
```dockerfile
FROM python:3.11-alpine
```

2. **Multi-stage build** (ya implementado)

3. **Eliminar archivos innecesarios:**
```dockerfile
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache
```

### Mejorar tiempo de build

1. **Ordenar COPY apropiadamente:**
```dockerfile
# Primero requirements (cambia menos)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Luego código (cambia más)
COPY . .
```

2. **Usar .dockerignore** (ya implementado)

3. **Build cache:**
```bash
# Habilitar BuildKit
export DOCKER_BUILDKIT=1
docker-compose build
```

### Seguridad adicional

1. **Escanear vulnerabilidades:**
```bash
# Con Trivy
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image montero-backend
```

2. **Read-only filesystem:**
```yaml
app:
  read_only: true
  tmpfs:
    - /tmp
```

3. **Limitar recursos:**
```yaml
app:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 1G
      reservations:
        cpus: '1'
        memory: 512M
```

---

## Referencias

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/configure.html)
- [Flask Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/)

---

**Implementado:** 2025-11-15
**Versión Docker:** 20.10+
**Versión Docker Compose:** 2.0+
