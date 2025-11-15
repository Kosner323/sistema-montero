# -*- coding: utf-8 -*-
"""
Servicio de Notificaciones - Sistema Montero
=============================================
Maneja el envío de notificaciones por email y notificaciones in-app.
"""

import logging
import os
import smtplib
import sqlite3
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Importar get_db_connection desde app para compatibilidad con mocking
from utils import get_db_connection

# Configuración de logging
logger = logging.getLogger(__name__)

# Configuración de Email (desde variables de entorno)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "noreply@montero.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "Sistema Montero <noreply@montero.com>")


class NotificationService:
    """
    Clase de servicio para manejar notificaciones por email e in-app.
    """

    def __init__(self):
        """Inicializa el servicio de notificaciones."""
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.smtp_user = SMTP_USER
        self.smtp_password = SMTP_PASSWORD
        self.email_from = EMAIL_FROM

    # ========================================================================
    # MÉTODOS DE ENVÍO DE EMAIL
    # ========================================================================

    def send_email(self, to_email, subject, template_name=None, context=None, html_body=None):
        """
        Envía un email usando SMTP.

        Args:
            to_email (str): Dirección de email del destinatario
            subject (str): Asunto del email
            template_name (str, optional): Nombre de la plantilla a usar
            context (dict, optional): Contexto para renderizar la plantilla
            html_body (str, optional): Cuerpo HTML directo (si no se usa template)

        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            # Crear mensaje
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.email_from
            msg["To"] = to_email

            # Generar cuerpo del email
            if html_body:
                body_html = html_body
            elif template_name and context:
                body_html = self._render_template(template_name, context)
            else:
                body_html = "<p>Notificación del Sistema Montero</p>"

            # Adjuntar HTML
            msg.attach(MIMEText(body_html, "html"))

            # Enviar email
            if self.smtp_password:  # Solo intentar enviar si hay credenciales configuradas
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)

                logger.info(f"Email enviado exitosamente a {to_email}")
                return {"success": True, "message": f"Email enviado a {to_email}"}
            else:
                # Modo desarrollo: simular envío
                logger.warning(f"[MODO DEV] Email simulado a {to_email}: {subject}")
                return {"success": True, "message": f"Email simulado (dev) a {to_email}"}

        except Exception as e:
            logger.error(f"Error al enviar email a {to_email}: {str(e)}")
            return {"success": False, "message": f"Error al enviar email: {str(e)}"}

    def _render_template(self, template_name, context):
        """
        Renderiza una plantilla de email HTML.

        Args:
            template_name (str): Nombre de la plantilla
            context (dict): Contexto para la plantilla

        Returns:
            str: HTML renderizado
        """
        # Plantillas básicas embebidas
        templates = {
            "tutela_expiring": """
                <html>
                <body>
                    <h2>Alerta: Tutela Próxima a Vencer</h2>
                    <p>La tutela <strong>#{tutela_id}</strong> vence el <strong>{fecha_vencimiento}</strong>.</p>
                    <p>Por favor, tome las acciones necesarias.</p>
                    <hr>
                    <p><small>Sistema Montero - Notificaciones Automáticas</small></p>
                </body>
                </html>
            """,
            "monthly_report": """
                <html>
                <body>
                    <h2>Reporte Mensual de Actividad</h2>
                    <ul>
                        <li>Total de Pagos: <strong>{total_pagos}</strong></li>
                        <li>Total de Empresas: <strong>{total_empresas}</strong></li>
                    </ul>
                    <hr>
                    <p><small>Sistema Montero - Reporte Automático</small></p>
                </body>
                </html>
            """,
            "user_registered": """
                <html>
                <body>
                    <h2>Bienvenido al Sistema Montero</h2>
                    <p>Hola <strong>{user_name}</strong>,</p>
                    <p>Tu cuenta ha sido creada exitosamente. Ya puedes acceder al sistema.</p>
                    <hr>
                    <p><small>Sistema Montero</small></p>
                </body>
                </html>
            """,
        }

        template = templates.get(template_name, "<p>Notificación del sistema</p>")
        return template.format(**context) if context else template

    # ========================================================================
    # MÉTODOS DE NOTIFICACIONES IN-APP
    # ========================================================================

    def create_in_app_notification(self, user_id, message, notification_type="info", priority="normal"):
        """
        Crea una notificación in-app en la base de datos.

        Args:
            user_id (int/str): ID del usuario destinatario
            message (str): Mensaje de la notificación
            notification_type (str): Tipo de notificación (info, warning, error, success)
            priority (str): Prioridad (low, normal, high, urgent)

        Returns:
            dict: {'success': bool, 'notification_id': int}
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insertar notificación
            cursor.execute(
                """
                INSERT INTO notificaciones (user_id, mensaje, tipo, prioridad, leida, fecha_creacion)
                VALUES (?, ?, ?, ?, 0, ?)
            """,
                (user_id, message, notification_type, priority, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            )

            notification_id = cursor.lastrowid
            conn.commit()
            conn.close()

            logger.info(f"Notificación in-app creada para usuario {user_id}")
            return {"success": True, "notification_id": notification_id}

        except Exception as e:
            logger.error(f"Error al crear notificación in-app: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}"}

    def mark_notification_as_read(self, notification_id):
        """
        Marca una notificación como leída.

        Args:
            notification_id (int): ID de la notificación

        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE notificaciones
                SET leida = 1, fecha_lectura = ?
                WHERE id = ?
            """,
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), notification_id),
            )

            conn.commit()
            conn.close()

            return {"success": True, "message": "Notificación marcada como leída"}

        except Exception as e:
            logger.error(f"Error al marcar notificación como leída: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}"}

    def get_user_notifications(self, user_id, unread_only=False):
        """
        Obtiene las notificaciones de un usuario.

        Args:
            user_id (int/str): ID del usuario
            unread_only (bool): Si True, solo devuelve notificaciones no leídas

        Returns:
            list: Lista de notificaciones
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            if unread_only:
                cursor.execute(
                    """
                    SELECT id, mensaje, tipo, prioridad, leida, fecha_creacion
                    FROM notificaciones
                    WHERE user_id = ? AND leida = 0
                    ORDER BY fecha_creacion DESC
                """,
                    (user_id,),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, mensaje, tipo, prioridad, leida, fecha_creacion
                    FROM notificaciones
                    WHERE user_id = ?
                    ORDER BY fecha_creacion DESC
                """,
                    (user_id,),
                )

            notifications = [dict(row) for row in cursor.fetchall()]
            conn.close()

            return notifications

        except Exception as e:
            logger.error(f"Error al obtener notificaciones: {str(e)}")
            return []

    def get_unread_count(self, user_id):
        """
        Obtiene el conteo de notificaciones no leídas de un usuario.

        Args:
            user_id (int/str): ID del usuario

        Returns:
            int: Cantidad de notificaciones no leídas
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT COUNT(*) as count
                FROM notificaciones
                WHERE user_id = ? AND leida = 0
            """,
                (user_id,),
            )

            count = cursor.fetchone()["count"]
            conn.close()

            return count

        except Exception as e:
            logger.error(f"Error al obtener conteo de notificaciones: {str(e)}")
            return 0

    # ========================================================================
    # MÉTODOS DE CONVENIENCIA
    # ========================================================================

    def notify_user_registered(self, user_email, user_name):
        """
        Envía notificación de bienvenida a un usuario recién registrado.

        Args:
            user_email (str): Email del usuario
            user_name (str): Nombre del usuario

        Returns:
            dict: Resultado del envío
        """
        return self.send_email(
            to_email=user_email,
            subject="Bienvenido al Sistema Montero",
            template_name="user_registered",
            context={"user_name": user_name},
        )

    def notify_payment_created(self, user_id, payment_amount, payment_date):
        """
        Notifica al usuario sobre un nuevo pago registrado.

        Args:
            user_id (int/str): ID del usuario
            payment_amount (float): Monto del pago
            payment_date (str): Fecha del pago

        Returns:
            dict: Resultado de la notificación
        """
        message = f"Se ha registrado un nuevo pago de ${payment_amount:,.2f} con fecha {payment_date}."
        return self.create_in_app_notification(
            user_id=user_id, message=message, notification_type="success", priority="normal"
        )

    def notify_tutela_created(self, user_id, tutela_id):
        """
        Notifica al usuario sobre una nueva tutela creada.

        Args:
            user_id (int/str): ID del usuario
            tutela_id (int): ID de la tutela

        Returns:
            dict: Resultado de la notificación
        """
        message = f"Se ha registrado una nueva tutela (#{tutela_id}) a tu nombre."
        return self.create_in_app_notification(user_id=user_id, message=message, notification_type="info", priority="high")


# Instancia global del servicio de notificaciones
notification_service = NotificationService()
