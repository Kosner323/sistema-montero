# celery_config.py
import os

from celery import Celery
from kombu import Exchange, Queue

# Cargar variables de entorno (asumiendo que Redis está configurado en .env)
# CELERY_BROKER_URL y CELERY_RESULT_BACKEND deben estar en el .env
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Inicialización de la aplicación Celery
celery_app = Celery(
    "montero_notificaciones",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["celery_tasks"],  # Asegura que las tareas definidas en celery_tasks.py sean cargadas
)

# Configuración de Celery
celery_app.conf.update(
    # Timezone de Celery (Importante para tareas programadas)
    CELERY_TIMEZONE="America/Bogota",
    # Serializador
    CELERY_TASK_SERIALIZER="json",
    CELERY_RESULT_SERIALIZER="json",
    CELERY_ACCEPT_CONTENT=["json"],
    # Colas de Tareas (Opcional, pero recomendado para priorización)
    CELERY_QUEUES=(
        Queue("default", Exchange("default"), routing_key="default"),
        Queue("critical", Exchange("critical"), routing_key="critical"),
    ),
    CELERY_DEFAULT_QUEUE="default",
    # Tareas Programadas (Celery Beat)
    CELERY_BEAT_SCHEDULE={
        # Tarea 1: Verificar Tutelas Próximas a Vencer (Diaria a las 08:00 AM)
        "check-expiring-tutelas-daily": {
            "task": "celery_tasks.check_expiring_tutelas",
            "schedule": os.getenv("TUTELAS_SCHEDULE", "crontab(minute=0, hour=8)"),
        },
        # Tarea 2: Enviar Reporte Mensual (El primer día del mes a las 09:00 AM)
        "send-monthly-report": {
            "task": "celery_tasks.send_monthly_report",
            "schedule": os.getenv("REPORT_SCHEDULE", "crontab(day_of_month=1, hour=9, minute=0)"),
        },
        # Tarea 3: Limpieza de Notificaciones Antiguas (Semanal)
        "cleanup-old-notifications": {
            "task": "celery_tasks.cleanup_old_notifications",
            "schedule": os.getenv("CLEANUP_SCHEDULE", "crontab(day_of_week=0, hour=2, minute=0)"),  # Domingo a las 2 AM
        },
        # Tarea 4: Verificar Pagos Pendientes (Diaria a las 10:00 AM)
        "check-pending-payments-daily": {
            "task": "celery_tasks.check_pending_payments",
            "schedule": os.getenv("PENDING_PAYMENTS_SCHEDULE", "crontab(minute=0, hour=10)"),
        },
    },
)


# Configurar Celery para que se integre con la aplicación Flask si se usa fuera del contexto de una tarea
def get_celery_app():
    return celery_app
