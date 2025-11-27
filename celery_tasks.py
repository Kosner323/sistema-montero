# celery_tasks.py
# -*- coding: utf-8 -*-
"""
Tareas programadas Celery - REFACTORIZADO CON ORM
==================================================
Todas las tareas ahora usan SQLAlchemy ORM en lugar de SQL manual.
Requiere Flask app context para acceder a la base de datos.

Cambios principales:
- Eliminado sqlite3.connect() completamente
- Integrado app.app_context() en cada tarea
- Uso de modelos ORM (Tutela, Pago, Empresa, Usuario)
- Datos reales de la base de datos (no simulados)
"""
from datetime import datetime, timedelta

from celery_config import celery_app

# Importar Flask app factory y extensiones
from app import create_app
from extensions import db

# Importar modelos ORM
from models.orm_models import (
    Tutela,
    Pago,
    Empresa,
    Usuario,
    PortalUser
)

# Importar notification_service desde routes/
from routes.notification_service import notification_service


# ==============================================================================
# TAREAS PROGRAMADAS
# ==============================================================================


@celery_app.task
def check_expiring_tutelas():
    """
    Busca tutelas que vencen en 7 días y notifica al usuario.
    REFACTORIZADO: Usa ORM y datos reales de la base de datos.
    """
    try:
        # Crear app context para acceder a la base de datos
        app = create_app()
        with app.app_context():
            # Fecha límite (hoy + 7 días)
            seven_days_from_now = datetime.now() + timedelta(days=7)
            fecha_limite = seven_days_from_now.strftime("%Y-%m-%d")

            # Consulta usando ORM: tutelas próximas a vencer
            tutelas = Tutela.query.filter_by(estado='Radicada').filter(
                Tutela.fecha_fin <= fecha_limite
            ).all()

            if tutelas:
                print(f"[INFO] Tareas: {len(tutelas)} tutelas proximas a vencer encontradas.")
                notificaciones_enviadas = 0
                notificaciones_fallidas = 0

                for tutela in tutelas:
                    try:
                        # Obtener información del empleado usando relación ORM
                        empleado = Usuario.query.filter_by(numeroId=str(tutela.usuario_id)).first()

                        if not empleado:
                            print(f"[WARN] Tareas: Usuario {tutela.usuario_id} no encontrado para tutela #{tutela.numero_tutela or tutela.id}")
                            notificaciones_fallidas += 1
                            continue

                        # Verificar que el empleado tenga correo electrónico
                        correo = getattr(empleado, 'correoElectronico', None)
                        if not correo or correo.strip() == '':
                            print(f"[WARN] Tareas: Usuario {tutela.usuario_id} ({empleado.primerNombre} {empleado.primerApellido}) sin correo electrónico")
                            notificaciones_fallidas += 1
                            continue

                        # Envío de notificación por email con datos reales
                        try:
                            notification_service.send_email(
                                to_email=correo,
                                subject=f"ALERTA: Tutela #{tutela.numero_tutela or tutela.id} vence pronto",
                                template_name="tutela_expiring",
                                context={
                                    "tutela_id": tutela.id,
                                    "numero_tutela": tutela.numero_tutela,
                                    "fecha_vencimiento": tutela.fecha_fin,
                                    "empleado_nombre": f"{empleado.primerNombre} {empleado.primerApellido}",
                                    "juzgado": tutela.juzgado
                                },
                            )
                            print(f"[SUCCESS] Email enviado a {correo} para tutela #{tutela.numero_tutela or tutela.id}")
                        except Exception as email_error:
                            print(f"[ERROR] Tareas: Fallo al enviar email a {correo}: {email_error}")
                            notificaciones_fallidas += 1
                            # Continuar con la notificación in-app aunque falle el email

                        # Creación de notificación In-App con datos reales
                        try:
                            notification_service.create_in_app_notification(
                                user_id=tutela.usuario_id,
                                message=f"La tutela #{tutela.numero_tutela or tutela.id} del juzgado {tutela.juzgado} vence el {tutela.fecha_fin}.",
                                notification_type="warning",
                                priority="high",
                            )
                            notificaciones_enviadas += 1
                        except Exception as notif_error:
                            print(f"[ERROR] Tareas: Fallo al crear notificación in-app para usuario {tutela.usuario_id}: {notif_error}")
                            notificaciones_fallidas += 1

                    except Exception as tutela_error:
                        print(f"[ERROR] Tareas: Error procesando tutela #{tutela.numero_tutela or tutela.id}: {tutela_error}")
                        notificaciones_fallidas += 1
                        continue  # Continuar con la siguiente tutela

                print(f"[INFO] Tareas: Procesamiento completado. Enviadas: {notificaciones_enviadas}, Fallidas: {notificaciones_fallidas}")
            else:
                print("[INFO] Tareas: No se encontraron tutelas proximas a vencer.")

            return {"status": "success", "count": len(tutelas)}

    except Exception as e:
        print(f"[ERROR] Tareas: Error en check_expiring_tutelas: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "failed", "error": str(e)}


@celery_app.task
def send_monthly_report():
    """
    Genera y envía el reporte mensual de actividad por email.
    REFACTORIZADO: Usa datos reales de la base de datos en lugar de valores simulados.
    """
    try:
        # Crear app context para acceder a la base de datos
        app = create_app()
        with app.app_context():
            # Calcular métricas reales del mes actual
            primer_dia_mes = datetime.now().replace(day=1)

            # Total de pagos del mes usando ORM
            total_pagos = Pago.query.filter(
                Pago.created_at >= primer_dia_mes.strftime("%Y-%m-%d")
            ).count()

            # Monto total de pagos del mes
            monto_total = db.session.query(
                db.func.sum(Pago.monto)
            ).filter(
                Pago.created_at >= primer_dia_mes.strftime("%Y-%m-%d")
            ).scalar() or 0.0

            # Total de empresas activas
            total_empresas = Empresa.query.count()

            # Total de usuarios activos
            total_usuarios = Usuario.query.count()

            # Obtener emails de administradores (usuarios con rol de admin)
            # Nota: Ajustar según tu lógica de roles
            admin_emails = db.session.query(Usuario.correoElectronico).filter(
                Usuario.correoElectronico.isnot(None),
                Usuario.correoElectronico != ''
            ).limit(10).all()  # Limitar a primeros 10 para no saturar

            admin_emails = [email[0] for email in admin_emails if email[0] and '@' in email[0]]

            if not admin_emails:
                admin_emails = ["admin@montero.com"]  # Fallback

            # Enviar reporte a cada administrador
            for email in admin_emails:
                notification_service.send_email(
                    to_email=email,
                    subject=f'Reporte Mensual de Actividad - {datetime.now().strftime("%B %Y")}',
                    template_name="monthly_report",
                    context={
                        "total_pagos": total_pagos,
                        "monto_total": monto_total,
                        "total_empresas": total_empresas,
                        "total_usuarios": total_usuarios,
                        "mes": datetime.now().strftime("%B %Y")
                    },
                )
                print(f"[INFO] Tareas: Reporte mensual enviado a {email}")

            return {
                "status": "success",
                "recipients": len(admin_emails),
                "total_pagos": total_pagos,
                "monto_total": monto_total
            }

    except Exception as e:
        print(f"[ERROR] Tareas: Error en send_monthly_report: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "failed", "error": str(e)}


@celery_app.task
def cleanup_old_notifications():
    """
    Limpia notificaciones leídas con más de 30 días de antigüedad.
    NOTA: Deshabilitado temporalmente - tabla 'notificaciones' no existe en ORM.
    TODO: Crear modelo Notificacion en orm_models.py cuando se defina la estructura.
    """
    try:
        print("[INFO] Tareas: cleanup_old_notifications deshabilitado temporalmente (modelo Notificacion no existe)")
        return {"status": "skipped", "message": "Modelo Notificacion no implementado en ORM"}
    except Exception as e:
        print(f"[ERROR] Tareas: Error en cleanup_old_notifications: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "failed", "error": str(e)}


@celery_app.task
def check_pending_payments():
    """
    Verifica si hay pagos pendientes con más de 3 días y genera alerta.
    REFACTORIZADO: Usa ORM para consultar pagos pendientes reales.
    """
    try:
        # Crear app context para acceder a la base de datos
        app = create_app()
        with app.app_context():
            # Fecha límite (hace 3 días)
            three_days_ago = datetime.now() - timedelta(days=3)
            fecha_limite = three_days_ago.strftime("%Y-%m-%d")

            # Consulta usando ORM: pagos pendientes antiguos
            pending_payments = Pago.query.filter(
                Pago.estado == 'Pendiente',
                Pago.fecha_pago < fecha_limite
            ).all()

            for pago in pending_payments:
                # Obtener información de la empresa usando relación ORM
                empresa = Empresa.query.filter_by(nit=pago.empresa_nit).first()
                nombre_empresa = empresa.nombre_empresa if empresa else pago.empresa_nit

                # Crear notificación In-App para administradores con datos reales
                notification_service.create_in_app_notification(
                    user_id=1,  # ID del administrador principal
                    message=f"ALERTA: Pago #{pago.id} de {nombre_empresa} (${pago.monto:,.2f}) esta pendiente hace 3+ dias.",
                    notification_type="error",
                    priority="urgent",
                )

                print(f"[INFO] Tareas: Alerta creada para pago #{pago.id} de {nombre_empresa}")

            print(f"[INFO] Tareas: {len(pending_payments)} pagos pendientes criticos encontrados.")
            return {"status": "success", "count": len(pending_payments)}

    except Exception as e:
        print(f"[ERROR] Tareas: Error en check_pending_payments: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "failed", "error": str(e)}


# ==============================================================================
# HELPER PARA EJECUTAR TAREAS MANUALMENTE (Para testing y diagnóstico)
# ==============================================================================


def run_task_manually(task_name, *args, **kwargs):
    """
    Función helper para ejecutar una tarea Celery síncrona.
    Útil para testing en desarrollo.

    Ejemplo:
        result = run_task_manually('celery_tasks.check_expiring_tutelas')
    """
    if task_name not in celery_app.tasks:
        return {"status": "error", "message": f"Tarea '{task_name}' no encontrada."}

    # Obtener la tarea por nombre y ejecutarla inmediatamente
    try:
        result = celery_app.tasks[task_name].apply(args=args, kwargs=kwargs, throw=True)
        return {"status": "executed", "result": result.get()}
    except Exception as e:
        return {"status": "error", "message": str(e)}
