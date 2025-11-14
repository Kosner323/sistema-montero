# -*- coding: utf-8 -*-
"""
celery_tasks.py - Tareas Asíncronas con Celery
===============================================
Define las tareas de Celery para el sistema de notificaciones.
"""

from celery import Celery
from celery_config import CeleryConfig
# IMPORTACIÓN CORREGIDA: Ahora importa desde routes.notification_service
from routes.notification_service import notification_service
from logger import get_logger

logger = get_logger(__name__)

# ==================== INICIALIZAR CELERY ====================

app = Celery("sistema_montero")
app.config_from_object(CeleryConfig)

# Autodescubrir tareas (opcional, si tienes tareas en otros módulos)
# app.autodiscover_tasks(['routes'])


# ==================== TAREAS DE NOTIFICACIONES ====================

@app.task(name="celery_tasks.send_email_async")
def send_email_async(to_email: str, subject: str, body: str, html: bool = True):
    """
    Tarea asíncrona para enviar emails.

    Args:
        to_email: Email destinatario
        subject: Asunto del email
        body: Contenido del email
        html: Si es True, envía como HTML

    Returns:
        bool: True si el email se envió exitosamente
    """
    try:
        logger.info(f"Iniciando tarea async de envío de email a {to_email}")

        success = notification_service.send_email(
            to_email=to_email,
            subject=subject,
            body=body,
            html=html
        )

        if success:
            logger.info(f"Email enviado exitosamente (async) a {to_email}")
        else:
            logger.warning(f"No se pudo enviar email (async) a {to_email}")

        return success

    except Exception as e:
        logger.error(f"Error en tarea send_email_async: {e}", exc_info=True)
        raise


@app.task(name="celery_tasks.create_notification_async")
def create_notification_async(
    user_id: int,
    title: str,
    message: str,
    notification_type: str = "info",
    link: str = None,
    metadata: dict = None
):
    """
    Tarea asíncrona para crear notificaciones in-app.

    Args:
        user_id: ID del usuario destinatario
        title: Título de la notificación
        message: Mensaje de la notificación
        notification_type: Tipo de notificación
        link: URL opcional
        metadata: Datos adicionales

    Returns:
        int: ID de la notificación creada
    """
    try:
        logger.info(
            f"Iniciando tarea async de creación de notificación "
            f"para usuario {user_id}"
        )

        notification_id = notification_service.create_in_app_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link,
            metadata=metadata
        )

        if notification_id:
            logger.info(
                f"Notificación {notification_id} creada exitosamente (async) "
                f"para usuario {user_id}"
            )
        else:
            logger.warning(
                f"No se pudo crear notificación (async) para usuario {user_id}"
            )

        return notification_id

    except Exception as e:
        logger.error(f"Error en tarea create_notification_async: {e}", exc_info=True)
        raise


@app.task(name="celery_tasks.notify_user_registered_async")
def notify_user_registered_async(user_id: int, email: str, username: str):
    """
    Tarea asíncrona para notificar registro de nuevo usuario.

    Args:
        user_id: ID del usuario
        email: Email del usuario
        username: Nombre del usuario

    Returns:
        bool: True si se enviaron las notificaciones exitosamente
    """
    try:
        logger.info(
            f"Iniciando notificación async de registro para usuario {user_id}"
        )

        success = notification_service.notify_user_registered(
            user_id=user_id,
            email=email,
            username=username
        )

        return success

    except Exception as e:
        logger.error(
            f"Error en tarea notify_user_registered_async: {e}",
            exc_info=True
        )
        raise


@app.task(name="celery_tasks.notify_payment_processed_async")
def notify_payment_processed_async(
    user_id: int,
    email: str,
    payment_id: int,
    amount: float,
    description: str
):
    """
    Tarea asíncrona para notificar procesamiento de pago.

    Args:
        user_id: ID del usuario
        email: Email del usuario
        payment_id: ID del pago
        amount: Monto del pago
        description: Descripción del pago

    Returns:
        bool: True si se enviaron las notificaciones exitosamente
    """
    try:
        logger.info(
            f"Iniciando notificación async de pago procesado para usuario {user_id}"
        )

        success = notification_service.notify_payment_processed(
            user_id=user_id,
            email=email,
            payment_id=payment_id,
            amount=amount,
            description=description
        )

        return success

    except Exception as e:
        logger.error(
            f"Error en tarea notify_payment_processed_async: {e}",
            exc_info=True
        )
        raise


@app.task(name="celery_tasks.notify_document_uploaded_async")
def notify_document_uploaded_async(
    user_id: int,
    email: str,
    document_type: str,
    document_name: str
):
    """
    Tarea asíncrona para notificar subida de documento.

    Args:
        user_id: ID del usuario
        email: Email del usuario
        document_type: Tipo de documento
        document_name: Nombre del documento

    Returns:
        bool: True si se enviaron las notificaciones exitosamente
    """
    try:
        logger.info(
            f"Iniciando notificación async de documento subido para usuario {user_id}"
        )

        success = notification_service.notify_document_uploaded(
            user_id=user_id,
            email=email,
            document_type=document_type,
            document_name=document_name
        )

        return success

    except Exception as e:
        logger.error(
            f"Error en tarea notify_document_uploaded_async: {e}",
            exc_info=True
        )
        raise


@app.task(name="celery_tasks.notify_system_alert_async")
def notify_system_alert_async(
    user_id: int,
    email: str,
    alert_title: str,
    alert_message: str,
    alert_type: str = "warning"
):
    """
    Tarea asíncrona para enviar alertas del sistema.

    Args:
        user_id: ID del usuario
        email: Email del usuario
        alert_title: Título de la alerta
        alert_message: Mensaje de la alerta
        alert_type: Tipo de alerta

    Returns:
        bool: True si se enviaron las notificaciones exitosamente
    """
    try:
        logger.info(
            f"Iniciando notificación async de alerta del sistema para usuario {user_id}"
        )

        success = notification_service.notify_system_alert(
            user_id=user_id,
            email=email,
            alert_title=alert_title,
            alert_message=alert_message,
            alert_type=alert_type
        )

        return success

    except Exception as e:
        logger.error(
            f"Error en tarea notify_system_alert_async: {e}",
            exc_info=True
        )
        raise


# ==================== TAREAS PROGRAMADAS (BEAT) ====================

@app.task(name="celery_tasks.send_daily_summary")
def send_daily_summary():
    """
    Tarea programada para enviar resumen diario.
    Esta es una tarea de ejemplo que se ejecutaría con Celery Beat.
    """
    try:
        logger.info("Iniciando tarea de resumen diario")

        # Aquí iría la lógica para enviar resumen diario
        # Por ejemplo, obtener métricas del día y enviar un email

        logger.info("Tarea de resumen diario completada")
        return True

    except Exception as e:
        logger.error(f"Error en tarea send_daily_summary: {e}", exc_info=True)
        raise


@app.task(name="celery_tasks.cleanup_old_notifications")
def cleanup_old_notifications(days: int = 30):
    """
    Tarea programada para limpiar notificaciones antiguas.

    Args:
        days: Número de días después de los cuales eliminar notificaciones leídas

    Returns:
        int: Número de notificaciones eliminadas
    """
    try:
        logger.info(f"Iniciando limpieza de notificaciones antiguas (>{days} días)")

        from utils import get_db_connection
        from datetime import datetime, timedelta

        conn = get_db_connection()
        cursor = conn.cursor()

        # Calcular fecha límite
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        # Eliminar notificaciones leídas antiguas
        cursor.execute(
            """
            DELETE FROM notifications
            WHERE is_read = 1 AND created_at < ?
            """,
            (cutoff_date,)
        )

        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()

        logger.info(f"Eliminadas {deleted_count} notificaciones antiguas")
        return deleted_count

    except Exception as e:
        logger.error(
            f"Error en tarea cleanup_old_notifications: {e}",
            exc_info=True
        )
        raise


# ==================== FUNCIONES DE UTILIDAD ====================

def queue_task(task_name: str, *args, **kwargs):
    """
    Función de utilidad para encolar tareas de forma genérica.

    Args:
        task_name: Nombre de la tarea a encolar
        *args: Argumentos posicionales para la tarea
        **kwargs: Argumentos con nombre para la tarea

    Returns:
        AsyncResult: Resultado asíncrono de la tarea
    """
    try:
        task = app.send_task(task_name, args=args, kwargs=kwargs)
        logger.info(f"Tarea '{task_name}' encolada con ID: {task.id}")
        return task

    except Exception as e:
        logger.error(f"Error encolando tarea '{task_name}': {e}", exc_info=True)
        raise
