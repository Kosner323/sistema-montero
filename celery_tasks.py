# celery_tasks.py
import os
import sqlite3
from datetime import datetime, timedelta

from celery_config import celery_app

# Importar notification_service desde routes/
from routes.notification_service import notification_service

# Helper para simular la conexión a la DB (ajusta la ruta real de tu BD)
DB_PATH = os.getenv("DATABASE_PATH", "./data/mi_sistema.db")


def get_db_connection():
    """Simula la conexión a la DB para las tareas Celery"""
    return sqlite3.connect(DB_PATH)


# ==============================================================================
# TAREAS PROGRAMADAS
# ==============================================================================


@celery_app.task
def check_expiring_tutelas():
    """Busca tutelas que vencen en 7 días y notifica al usuario."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fecha límite (hoy + 7 días)
        seven_days_from_now = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        # Simula la consulta de tutelas próximas a vencer
        cursor.execute(
            """
            SELECT id, empleado_id, fecha_vencimiento
            FROM tutelas
            WHERE estado = 'Radicada' AND fecha_vencimiento <= ?
        """,
            (seven_days_from_now,),
        )

        tutelas = cursor.fetchall()

        if tutelas:
            print(f"[INFO] Tareas: {len(tutelas)} tutelas próximas a vencer encontradas.")
            for tutela in tutelas:
                tutela_id, empleado_id, vencimiento = tutela

                # Simular el envío de notificación por email
                notification_service.send_email(
                    to_email=f"empleado_{empleado_id}@example.com",
                    subject=f"ALERTA: Tutela #{tutela_id} vence pronto",
                    template_name="tutela_expiring",
                    context={"tutela_id": tutela_id, "fecha_vencimiento": vencimiento},
                )

                # Simular la creación de notificación In-App
                notification_service.create_in_app_notification(
                    user_id=empleado_id,
                    message=f"La tutela #{tutela_id} vence el {vencimiento}.",
                    notification_type="warning",
                    priority="high",
                )
        else:
            print("[INFO] Tareas: No se encontraron tutelas próximas a vencer.")

        return {"status": "success", "count": len(tutelas)}
    except Exception as e:
        print(f"[ERROR] Tareas: Error en check_expiring_tutelas: {e}")
        return {"status": "failed", "error": str(e)}
    finally:
        conn.close()


@celery_app.task
def send_monthly_report():
    """Genera y envía el reporte mensual de actividad por email."""
    try:
        # Simular generación de métricas
        total_pagos = 1500
        total_empresas = 50

        # Simular consulta de usuarios (ejemplo: enviar a todos los administradores)
        admin_emails = ["admin@montero.com", "gerencia@montero.com"]

        for email in admin_emails:
            notification_service.send_email(
                to_email=email,
                subject=f'Reporte Mensual de Actividad - {datetime.now().strftime("%B")}',
                template_name="monthly_report",
                context={"total_pagos": total_pagos, "total_empresas": total_empresas},
            )
            print(f"[INFO] Tareas: Reporte enviado a {email}")

        return {"status": "success", "recipients": len(admin_emails)}
    except Exception as e:
        print(f"[ERROR] Tareas: Error en send_monthly_report: {e}")
        return {"status": "failed", "error": str(e)}


@celery_app.task
def cleanup_old_notifications():
    """Limpia notificaciones leídas con más de 30 días de antigüedad."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")

        # Simula la eliminación
        cursor.execute(
            """
            DELETE FROM notificaciones
            WHERE leida = 1 AND fecha_creacion < ?
        """,
            (thirty_days_ago,),
        )

        deleted_count = conn.total_changes
        conn.commit()

        print(f"[INFO] Tareas: Limpieza completada. {deleted_count} notificaciones eliminadas.")
        return {"status": "success", "deleted_count": deleted_count}
    except Exception as e:
        print(f"[ERROR] Tareas: Error en cleanup_old_notifications: {e}")
        return {"status": "failed", "error": str(e)}
    finally:
        conn.close()


@celery_app.task
def check_pending_payments():
    """Verifica si hay pagos pendientes con más de 3 días y genera alerta."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        three_days_ago = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")

        # Simula la consulta de pagos pendientes
        cursor.execute(
            """
            SELECT id, empresa_nit
            FROM pagos
            WHERE estado = 'Pendiente' AND fecha_pago < ?
        """,
            (three_days_ago,),
        )

        pending_payments = cursor.fetchall()

        for payment in pending_payments:
            payment_id, empresa_nit = payment
            # Simular la creación de notificación In-App (para administradores)
            notification_service.create_in_app_notification(
                user_id=1,  # Asumiendo ID 1 es el admin
                message=f"ALERTA: Pago #{payment_id} de {empresa_nit} está pendiente hace 3+ días.",
                notification_type="error",
                priority="urgent",
            )

        print(f"[INFO] Tareas: {len(pending_payments)} pagos pendientes críticos encontrados.")
        return {"status": "success", "count": len(pending_payments)}
    except Exception as e:
        print(f"[ERROR] Tareas: Error en check_pending_payments: {e}")
        return {"status": "failed", "error": str(e)}
    finally:
        conn.close()


# ==============================================================================
# HELPER PARA EJECUTAR TAREAS MANUALMENTE (Para testing y diagnóstico)
# ==============================================================================


def run_task_manually(task_name, *args, **kwargs):
    """
    Función helper para ejecutar una tarea Celery síncrona
    Útil para testing en desarrollo.
    """
    if task_name not in celery_app.tasks:
        return {"status": "error", "message": f"Tarea '{task_name}' no encontrada."}

    # Obtener la tarea por nombre y ejecutarla inmediatamente
    result = celery_app.tasks[task_name].apply(args=args, kwargs=kwargs, throw=True)
    return {"status": "executed", "result": result.get()}
