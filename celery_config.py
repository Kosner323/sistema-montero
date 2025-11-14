# -*- coding: utf-8 -*-
"""
celery_config.py - Configuración de Celery
==========================================
Configuración centralizada para Celery y tareas asíncronas.
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ==================== CONFIGURACIÓN DE CELERY ====================

class CeleryConfig:
    """Configuración de Celery."""

    # Broker URL (Redis por defecto, puede ser RabbitMQ u otros)
    broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

    # Backend de resultados
    result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    # Serialización
    task_serializer = "json"
    result_serializer = "json"
    accept_content = ["json"]

    # Timezone
    timezone = "America/Bogota"  # Ajustar según la ubicación
    enable_utc = True

    # Configuración de tareas
    task_track_started = True
    task_time_limit = 30 * 60  # 30 minutos
    task_soft_time_limit = 25 * 60  # 25 minutos

    # Configuración de workers
    worker_prefetch_multiplier = 1
    worker_max_tasks_per_child = 1000

    # Configuración de beat (scheduler)
    beat_schedule = {
        # Ejemplo de tarea programada (descomentarla si se necesita)
        # "send-daily-summary": {
        #     "task": "celery_tasks.send_daily_summary",
        #     "schedule": crontab(hour=8, minute=0),  # Todos los días a las 8:00 AM
        # },
    }

    # Configuración de logs
    worker_hijack_root_logger = False
    worker_log_format = "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s"
    worker_task_log_format = (
        "[%(asctime)s: %(levelname)s/%(processName)s] "
        "[%(task_name)s(%(task_id)s)] %(message)s"
    )

    # Configuración de retry
    task_acks_late = True
    task_reject_on_worker_lost = True

    # Configuración de resultados
    result_expires = 3600  # Los resultados expiran después de 1 hora

    # Configuración de eventos
    worker_send_task_events = True
    task_send_sent_event = True


# ==================== CONFIGURACIÓN ADICIONAL ====================

# Variables de entorno para el sistema de notificaciones
NOTIFICATION_CONFIG = {
    "email_enabled": os.getenv("EMAIL_ENABLED", "false").lower() == "true",
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "smtp_user": os.getenv("SMTP_USER", ""),
    "smtp_password": os.getenv("SMTP_PASSWORD", ""),
    "from_email": os.getenv("FROM_EMAIL", os.getenv("SMTP_USER", "")),
}

# Variables de entorno para la base de datos
DATABASE_CONFIG = {
    "db_path": os.getenv("DATABASE_PATH", "data/mi_sistema.db"),
}
