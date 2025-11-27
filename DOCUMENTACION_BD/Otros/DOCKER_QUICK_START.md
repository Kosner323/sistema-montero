# Docker Quick Start - Sistema Montero

## Resumen

Sistema Montero ha sido completamente dockerizado para facilitar el despliegue y desarrollo.

## Archivos Creados

- **Dockerfile** - Imagen multi-stage optimizada con Python 3.11
- **docker-compose.yml** - Orquestación de servicios (App + Redis + Nginx)
- **.dockerignore** - Exclusión de archivos innecesarios
- **entrypoint.sh** - Script de inicialización automática
- **requirements.txt** - Actualizado con gunicorn

## Inicio Rápido (3 pasos)

### 1. Configurar variables de entorno

Crea un archivo `.env` en el directorio `dashboard/`:

```bash
# Copia el archivo de ejemplo
cp .env.example .env

# Edita las variables importantes
SECRET_KEY=tu-clave-secreta-super-segura
MAIL_USERNAME=kevinlomasd@gmail.com
MAIL_PASSWORD=tu-password-de-aplicacion
```

### 2. Construir y levantar los contenedores

```bash
# Construir la imagen y levantar los servicios
docker-compose up --build -d

# Ver los logs
docker-compose logs -f
```

### 3. Verificar que todo funciona

```bash
# Verificar estado de contenedores
docker-compose ps

# Probar el endpoint de health
curl http://localhost:5000/health
```

¡Listo! La aplicación está corriendo en `http://localhost:5000`

## Comandos Básicos

### Gestión de contenedores

```bash
# Iniciar servicios
docker-compose up -d

# Detener servicios
docker-compose down

# Ver logs en tiempo real
docker-compose logs -f app

# Reiniciar un servicio específico
docker-compose restart app

# Ver estado de contenedores
docker-compose ps
```

### Desarrollo

```bash
# Modo desarrollo con hot-reload
docker-compose up --build

# Entrar al contenedor
docker-compose exec app bash

# Ejecutar comandos dentro del contenedor
docker-compose exec app python -c "print('Hello')"

# Ver logs de un servicio específico
docker-compose logs -f redis
```

### Base de datos y migraciones

```bash
# Ejecutar migraciones
docker-compose exec app alembic upgrade head

# Crear nueva migración
docker-compose exec app alembic revision --autogenerate -m "Descripción"

# Ver estado de migraciones
docker-compose exec app alembic current

# Revertir última migración
docker-compose exec app alembic downgrade -1
```

### Limpieza

```bash
# Detener y eliminar contenedores
docker-compose down

# Eliminar también los volúmenes (CUIDADO: borra la BD)
docker-compose down -v

# Eliminar imágenes no usadas
docker system prune -a

# Ver espacio usado por Docker
docker system df
```

## Estructura de Servicios

### App (Flask Backend)
- **Puerto:** 5000
- **Imagen:** Construida desde Dockerfile
- **Servidor:** Gunicorn con 4 workers
- **Usuario:** appuser (no-root)

### Redis (Cache & Rate Limiting)
- **Puerto:** 6379
- **Imagen:** redis:7-alpine
- **Configuración:** Persistencia habilitada, 256MB max memory

### Nginx (Proxy - Opcional)
- **Puerto:** 80, 443
- **Perfil:** production
- **Uso:** `docker-compose --profile production up`

## Variables de Entorno Importantes

```bash
# Flask
FLASK_ENV=production
SECRET_KEY=clave-secreta

# Email
MAIL_USERNAME=kevinlomasd@gmail.com
MAIL_PASSWORD=app-password

# Logging
LOG_LEVEL=INFO

# Timezone
TZ=America/Bogota
```

## Troubleshooting

### "Cannot connect to Redis"
```bash
# Verificar que Redis esté corriendo
docker-compose ps redis

# Ver logs de Redis
docker-compose logs redis

# Reiniciar Redis
docker-compose restart redis
```

### "Database locked"
```bash
# SQLite no soporta múltiples escrituras simultáneas
# Solución: Reducir workers de Gunicorn o usar PostgreSQL
```

### "Port 5000 already in use"
```bash
# Cambiar puerto en docker-compose.yml
ports:
  - "8000:5000"  # Usar 8000 en lugar de 5000
```

### Reconstruir imagen desde cero
```bash
# Forzar reconstrucción sin cache
docker-compose build --no-cache

# Reiniciar todo
docker-compose down -v
docker-compose up --build -d
```

## Modos de Ejecución

### Desarrollo (con hot-reload)
```yaml
# En docker-compose.yml, descomentar:
volumes:
  - .:/app  # Monta el código en el contenedor

# Cambiar CMD a:
command: flask run --host=0.0.0.0 --reload
```

### Producción (optimizado)
```bash
# Usar configuración por defecto
docker-compose up -d

# O con Nginx
docker-compose --profile production up -d
```

## Healthchecks

La aplicación incluye healthchecks automáticos:

```bash
# Ver estado de salud
docker inspect --format='{{.State.Health.Status}}' montero-backend

# Endpoint de health
curl http://localhost:5000/health
```

## Backup de Datos

```bash
# Backup de base de datos
docker-compose exec app sqlite3 /app/data/mi_sistema.db ".backup /app/data/backup_$(date +%Y%m%d).db"

# Copiar backup al host
docker cp montero-backend:/app/data/backup_*.db ./backups/

# Backup de volumen de Redis
docker run --rm -v montero_redis-data:/data -v $(pwd):/backup alpine tar czf /backup/redis_backup.tar.gz -C /data .
```

## Próximos Pasos

1. Configurar `.env` con tus credenciales
2. Ejecutar `docker-compose up -d`
3. Verificar logs: `docker-compose logs -f`
4. Acceder a `http://localhost:5000`
5. Leer documentación completa: `DOCKER_DOCUMENTATION.md`

---

**¡Todo listo para usar Docker!**
Para más información, consulta [DOCKER_DOCUMENTATION.md](DOCKER_DOCUMENTATION.md)
