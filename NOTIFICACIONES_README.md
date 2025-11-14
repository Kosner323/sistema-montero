# Sistema de Notificaciones - Documentación

## Descripción

Sistema completo de notificaciones para el Sistema Montero, que incluye:
- **Notificaciones in-app**: Notificaciones dentro de la aplicación almacenadas en base de datos
- **Notificaciones por email**: Envío de emails usando SMTP
- **Tareas asíncronas**: Procesamiento de notificaciones en background usando Celery

## Archivos Creados

### 1. `routes/notification_service.py`
Servicio centralizado para el manejo de notificaciones.

**Clase Principal**: `NotificationService`

**Métodos Principales**:
- `send_email(to_email, subject, body, html=True)`: Envía emails
- `create_in_app_notification(user_id, title, message, ...)`: Crea notificaciones in-app
- `get_user_notifications(user_id, unread_only=False, limit=50)`: Obtiene notificaciones de un usuario
- `mark_as_read(notification_id, user_id)`: Marca una notificación como leída
- `get_unread_count(user_id)`: Obtiene el número de notificaciones no leídas

**Funciones de Conveniencia**:
- `notify_user_registered(user_id, email, username)`: Notifica registro de nuevo usuario
- `notify_payment_processed(user_id, email, payment_id, amount, description)`: Notifica pago procesado
- `notify_document_uploaded(user_id, email, document_type, document_name)`: Notifica documento subido
- `notify_system_alert(user_id, email, alert_title, alert_message, alert_type)`: Notifica alertas del sistema

### 2. `routes/notificaciones_routes.py`
Blueprint con las rutas API para gestionar notificaciones.

**Endpoints**:
- `GET /api/notificaciones/`: Obtiene notificaciones del usuario
- `GET /api/notificaciones/unread-count`: Obtiene el conteo de notificaciones no leídas
- `PUT /api/notificaciones/mark-read/<notification_id>`: Marca una notificación como leída
- `PUT /api/notificaciones/mark-all-read`: Marca todas las notificaciones como leídas
- `POST /api/notificaciones/test`: Crea una notificación de prueba
- `POST /api/notificaciones/send-email-test`: Envía un email de prueba
- `GET /api/notificaciones/health`: Health check del servicio

### 3. `celery_config.py`
Configuración de Celery para tareas asíncronas.

**Configuraciones Principales**:
- Broker: Redis (por defecto)
- Backend de resultados: Redis
- Timezone: America/Bogota
- Límite de tiempo de tareas: 30 minutos

### 4. `celery_tasks.py`
Tareas asíncronas de Celery para el sistema de notificaciones.

**Tareas Principales**:
- `send_email_async`: Envía emails de forma asíncrona
- `create_notification_async`: Crea notificaciones in-app de forma asíncrona
- `notify_user_registered_async`: Notifica registro de usuario (async)
- `notify_payment_processed_async`: Notifica pago procesado (async)
- `notify_document_uploaded_async`: Notifica documento subido (async)
- `notify_system_alert_async`: Notifica alertas del sistema (async)

**Tareas Programadas** (Celery Beat):
- `send_daily_summary`: Envía resumen diario
- `cleanup_old_notifications`: Limpia notificaciones antiguas

## Configuración

### Variables de Entorno

Agrega las siguientes variables a tu archivo `.env`:

```bash
# ==================== CELERY CONFIGURATION ====================
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# ==================== EMAIL CONFIGURATION ====================
EMAIL_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_email@gmail.com
SMTP_PASSWORD=tu_contraseña_de_aplicación
FROM_EMAIL=tu_email@gmail.com
```

### Requisitos

Instala las dependencias necesarias:

```bash
pip install celery redis python-dotenv
```

Si usas Gmail, necesitas crear una "Contraseña de Aplicación":
1. Ve a tu cuenta de Google
2. Seguridad > Verificación en 2 pasos
3. Contraseñas de aplicaciones
4. Genera una nueva contraseña para "Correo"

### Base de Datos

La tabla `notifications` se crea automáticamente al iniciar la aplicación. Estructura:

```sql
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT DEFAULT 'info',
    link TEXT,
    metadata TEXT,
    is_read INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## Uso

### 1. Usar el Servicio Directamente (Síncrono)

```python
from routes.notification_service import notification_service

# Enviar email
notification_service.send_email(
    to_email="usuario@example.com",
    subject="Bienvenido",
    body="<h1>Hola!</h1>",
    html=True
)

# Crear notificación in-app
notification_service.create_in_app_notification(
    user_id=1,
    title="Nueva Notificación",
    message="Este es un mensaje de prueba",
    notification_type="info",
    link="/dashboard"
)

# Obtener notificaciones de un usuario
notifications = notification_service.get_user_notifications(
    user_id=1,
    unread_only=True,
    limit=10
)

# Marcar como leída
notification_service.mark_as_read(notification_id=5, user_id=1)

# Obtener conteo de no leídas
count = notification_service.get_unread_count(user_id=1)
```

### 2. Usar Tareas de Celery (Asíncrono)

Primero, inicia el worker de Celery:

```bash
# En un terminal separado
celery -A celery_tasks worker --loglevel=info
```

Luego, desde tu código Python:

```python
from celery_tasks import (
    send_email_async,
    create_notification_async,
    notify_user_registered_async
)

# Enviar email asíncrono
task = send_email_async.delay(
    to_email="usuario@example.com",
    subject="Email Asíncrono",
    body="<p>Este email se envía en background</p>",
    html=True
)

# Crear notificación asíncrona
task = create_notification_async.delay(
    user_id=1,
    title="Notificación Async",
    message="Esta notificación se crea en background",
    notification_type="success"
)

# Notificar registro de usuario
task = notify_user_registered_async.delay(
    user_id=1,
    email="nuevo_usuario@example.com",
    username="Juan Pérez"
)

# Verificar estado de la tarea
print(task.status)  # PENDING, SUCCESS, FAILURE, etc.
print(task.result)  # Resultado de la tarea
```

### 3. Usar los Endpoints API

#### Obtener notificaciones del usuario

```bash
GET /api/notificaciones/?unread_only=true&limit=20
```

Respuesta:
```json
{
  "success": true,
  "notifications": [
    {
      "id": 1,
      "title": "Bienvenido",
      "message": "Tu cuenta ha sido creada",
      "type": "success",
      "link": "/dashboard",
      "is_read": false,
      "created_at": "2025-11-14T10:30:00"
    }
  ],
  "count": 1
}
```

#### Obtener conteo de no leídas

```bash
GET /api/notificaciones/unread-count
```

Respuesta:
```json
{
  "success": true,
  "unread_count": 5
}
```

#### Marcar como leída

```bash
PUT /api/notificaciones/mark-read/1
```

Respuesta:
```json
{
  "success": true,
  "message": "Notificación marcada como leída"
}
```

#### Marcar todas como leídas

```bash
PUT /api/notificaciones/mark-all-read
```

Respuesta:
```json
{
  "success": true,
  "message": "5 notificaciones marcadas como leídas",
  "marked_count": 5
}
```

#### Crear notificación de prueba

```bash
POST /api/notificaciones/test
Content-Type: application/json

{
  "title": "Test",
  "message": "Esto es una prueba",
  "type": "info"
}
```

## Integración en el Sistema

### En routes/usuarios.py (Ejemplo)

```python
from routes.notification_service import notification_service

@bp_usuarios.route("/register", methods=["POST"])
def register_user():
    # ... crear usuario ...

    # Notificar al usuario
    notification_service.notify_user_registered(
        user_id=new_user_id,
        email=user_email,
        username=username
    )

    return jsonify({"success": True})
```

### En routes/pagos.py (Ejemplo)

```python
from celery_tasks import notify_payment_processed_async

@bp_pagos.route("/process", methods=["POST"])
def process_payment():
    # ... procesar pago ...

    # Notificar asíncronamente
    notify_payment_processed_async.delay(
        user_id=user_id,
        email=user_email,
        payment_id=payment_id,
        amount=amount,
        description=description
    )

    return jsonify({"success": True})
```

## Celery Beat (Tareas Programadas)

Para ejecutar tareas programadas, inicia Celery Beat:

```bash
celery -A celery_tasks beat --loglevel=info
```

Configura tareas programadas en `celery_config.py`:

```python
from celery.schedules import crontab

beat_schedule = {
    "cleanup-old-notifications": {
        "task": "celery_tasks.cleanup_old_notifications",
        "schedule": crontab(hour=2, minute=0),  # Todos los días a las 2:00 AM
        "args": (30,)  # Eliminar notificaciones de más de 30 días
    },
}
```

## Testing

### Test de Notificación In-App

```bash
curl -X POST http://localhost:5000/api/notificaciones/test \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test",
    "message": "Esto es una notificación de prueba",
    "type": "success"
  }'
```

### Test de Email

```bash
curl -X POST http://localhost:5000/api/notificaciones/send-email-test \
  -H "Content-Type: application/json" \
  -d '{
    "email": "tu_email@example.com",
    "subject": "Test Email",
    "message": "Este es un email de prueba"
  }'
```

## Troubleshooting

### Error: "No module named 'notification_service'"

**Solución**: Asegúrate de que la importación sea:
```python
from routes.notification_service import notification_service
```

### Error: "Celery worker no se conecta a Redis"

**Solución**:
1. Verifica que Redis esté corriendo: `redis-cli ping` (debe responder "PONG")
2. Verifica la URL en `.env`: `CELERY_BROKER_URL=redis://localhost:6379/0`

### Emails no se envían

**Solución**:
1. Verifica que `EMAIL_ENABLED=true` en `.env`
2. Verifica las credenciales SMTP
3. Para Gmail, usa una "Contraseña de Aplicación" en lugar de tu contraseña normal
4. Verifica los logs: `logger.error` mostrará el error específico

### Notificaciones no aparecen en la BD

**Solución**:
1. Verifica que la tabla `notifications` existe en la base de datos
2. Reinicia la aplicación para que se cree la tabla automáticamente
3. Verifica los logs para ver errores de base de datos

## Monitoreo

### Ver estado de Celery

```bash
celery -A celery_tasks inspect active
celery -A celery_tasks inspect scheduled
celery -A celery_tasks inspect stats
```

### Ver tareas en Redis

```bash
redis-cli
> KEYS celery*
> GET celery-task-meta-<task_id>
```

## Mejoras Futuras

- [ ] Implementar notificaciones push (web push)
- [ ] Agregar plantillas HTML para emails
- [ ] Implementar preferencias de notificación por usuario
- [ ] Agregar soporte para notificaciones SMS
- [ ] Crear dashboard de administración de notificaciones
- [ ] Implementar rate limiting para evitar spam
- [ ] Agregar métricas y analytics de notificaciones

## Soporte

Para reportar problemas o sugerencias, contacta al equipo de desarrollo.
