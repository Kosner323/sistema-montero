# -*- coding: utf-8 -*-
"""
notification_service.py - Servicio de Notificaciones
====================================================
Gestiona el envío de notificaciones por email y notificaciones in-app.
"""

import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, Dict, List
import os
from dotenv import load_dotenv

# Importar logger y utilidades
from logger import get_logger
from utils import get_db_connection

logger = get_logger(__name__)

# Cargar variables de entorno
load_dotenv()


class NotificationService:
    """
    Servicio centralizado para el manejo de notificaciones.
    Soporta notificaciones por email y notificaciones in-app.
    """

    def __init__(self):
        """Inicializa el servicio de notificaciones."""
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        self.email_enabled = os.getenv("EMAIL_ENABLED", "false").lower() == "true"

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: bool = True
    ) -> bool:
        """
        Envía un email.

        Args:
            to_email: Dirección de email del destinatario
            subject: Asunto del email
            body: Contenido del email
            html: Si es True, envía como HTML; si no, como texto plano

        Returns:
            bool: True si el email se envió exitosamente, False en caso contrario
        """
        if not self.email_enabled:
            logger.info(f"Email deshabilitado. Email no enviado a {to_email}: {subject}")
            return False

        if not self.smtp_user or not self.smtp_password:
            logger.warning("Credenciales SMTP no configuradas. Email no enviado.")
            return False

        try:
            # Crear mensaje
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email

            # Adjuntar contenido
            if html:
                part = MIMEText(body, "html", "utf-8")
            else:
                part = MIMEText(body, "plain", "utf-8")

            msg.attach(part)

            # Enviar email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email enviado exitosamente a {to_email}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Error enviando email a {to_email}: {e}", exc_info=True)
            return False

    def create_in_app_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        notification_type: str = "info",
        link: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[int]:
        """
        Crea una notificación in-app en la base de datos.

        Args:
            user_id: ID del usuario destinatario
            title: Título de la notificación
            message: Mensaje de la notificación
            notification_type: Tipo de notificación (info, warning, error, success)
            link: URL opcional para redirección
            metadata: Datos adicionales en formato JSON

        Returns:
            int: ID de la notificación creada, o None si hubo error
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO notifications (
                    user_id, title, message, type, link, metadata,
                    is_read, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    title,
                    message,
                    notification_type,
                    link,
                    str(metadata) if metadata else None,
                    False,
                    datetime.now().isoformat()
                )
            )

            notification_id = cursor.lastrowid
            conn.commit()
            conn.close()

            logger.info(
                f"Notificación in-app creada (ID: {notification_id}) "
                f"para usuario {user_id}: {title}"
            )
            return notification_id

        except Exception as e:
            logger.error(
                f"Error creando notificación in-app para usuario {user_id}: {e}",
                exc_info=True
            )
            return None

    def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Dict]:
        """
        Obtiene las notificaciones de un usuario.

        Args:
            user_id: ID del usuario
            unread_only: Si es True, solo devuelve notificaciones no leídas
            limit: Número máximo de notificaciones a devolver

        Returns:
            List[Dict]: Lista de notificaciones
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            query = """
                SELECT id, title, message, type, link, metadata,
                       is_read, created_at
                FROM notifications
                WHERE user_id = ?
            """
            params = [user_id]

            if unread_only:
                query += " AND is_read = 0"

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            notifications = [
                {
                    "id": row[0],
                    "title": row[1],
                    "message": row[2],
                    "type": row[3],
                    "link": row[4],
                    "metadata": row[5],
                    "is_read": bool(row[6]),
                    "created_at": row[7]
                }
                for row in cursor.fetchall()
            ]

            conn.close()
            return notifications

        except Exception as e:
            logger.error(
                f"Error obteniendo notificaciones para usuario {user_id}: {e}",
                exc_info=True
            )
            return []

    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """
        Marca una notificación como leída.

        Args:
            notification_id: ID de la notificación
            user_id: ID del usuario (para validación)

        Returns:
            bool: True si se marcó exitosamente, False en caso contrario
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE notifications
                SET is_read = 1
                WHERE id = ? AND user_id = ?
                """,
                (notification_id, user_id)
            )

            conn.commit()
            affected_rows = cursor.rowcount
            conn.close()

            if affected_rows > 0:
                logger.info(
                    f"Notificación {notification_id} marcada como leída "
                    f"para usuario {user_id}"
                )
                return True
            else:
                logger.warning(
                    f"No se pudo marcar notificación {notification_id} "
                    f"como leída para usuario {user_id}"
                )
                return False

        except Exception as e:
            logger.error(
                f"Error marcando notificación {notification_id} como leída: {e}",
                exc_info=True
            )
            return False

    def get_unread_count(self, user_id: int) -> int:
        """
        Obtiene el número de notificaciones no leídas de un usuario.

        Args:
            user_id: ID del usuario

        Returns:
            int: Número de notificaciones no leídas
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM notifications
                WHERE user_id = ? AND is_read = 0
                """,
                (user_id,)
            )

            count = cursor.fetchone()[0]
            conn.close()

            return count

        except Exception as e:
            logger.error(
                f"Error obteniendo conteo de notificaciones no leídas "
                f"para usuario {user_id}: {e}",
                exc_info=True
            )
            return 0

    # ==================== FUNCIONES DE CONVENIENCIA ====================

    def notify_user_registered(self, user_id: int, email: str, username: str) -> bool:
        """
        Notifica cuando un nuevo usuario se registra.

        Args:
            user_id: ID del usuario
            email: Email del usuario
            username: Nombre del usuario

        Returns:
            bool: True si se enviaron las notificaciones exitosamente
        """
        try:
            # Notificación in-app
            self.create_in_app_notification(
                user_id=user_id,
                title="¡Bienvenido!",
                message=f"Tu cuenta ha sido creada exitosamente. Bienvenido al Sistema Montero, {username}.",
                notification_type="success",
                link="/dashboard"
            )

            # Email de bienvenida
            if self.email_enabled:
                subject = "Bienvenido al Sistema Montero"
                body = f"""
                <html>
                    <body>
                        <h2>¡Bienvenido al Sistema Montero!</h2>
                        <p>Hola {username},</p>
                        <p>Tu cuenta ha sido creada exitosamente.</p>
                        <p>Ya puedes acceder al sistema con tus credenciales.</p>
                        <br>
                        <p>Saludos,<br>El equipo de Sistema Montero</p>
                    </body>
                </html>
                """
                self.send_email(email, subject, body, html=True)

            return True

        except Exception as e:
            logger.error(f"Error en notify_user_registered: {e}", exc_info=True)
            return False

    def notify_payment_processed(
        self,
        user_id: int,
        email: str,
        payment_id: int,
        amount: float,
        description: str
    ) -> bool:
        """
        Notifica cuando un pago ha sido procesado.

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
            # Notificación in-app
            self.create_in_app_notification(
                user_id=user_id,
                title="Pago Procesado",
                message=f"Tu pago de ${amount:,.2f} ha sido procesado exitosamente. Referencia: {description}",
                notification_type="success",
                link=f"/pagos/{payment_id}",
                metadata={"payment_id": payment_id, "amount": amount}
            )

            # Email de confirmación
            if self.email_enabled:
                subject = f"Confirmación de Pago - ${amount:,.2f}"
                body = f"""
                <html>
                    <body>
                        <h2>Pago Procesado Exitosamente</h2>
                        <p><strong>Monto:</strong> ${amount:,.2f}</p>
                        <p><strong>Descripción:</strong> {description}</p>
                        <p><strong>Referencia:</strong> {payment_id}</p>
                        <br>
                        <p>Gracias por usar el Sistema Montero.</p>
                    </body>
                </html>
                """
                self.send_email(email, subject, body, html=True)

            return True

        except Exception as e:
            logger.error(f"Error en notify_payment_processed: {e}", exc_info=True)
            return False

    def notify_document_uploaded(
        self,
        user_id: int,
        email: str,
        document_type: str,
        document_name: str
    ) -> bool:
        """
        Notifica cuando un documento ha sido subido.

        Args:
            user_id: ID del usuario
            email: Email del usuario
            document_type: Tipo de documento
            document_name: Nombre del documento

        Returns:
            bool: True si se enviaron las notificaciones exitosamente
        """
        try:
            # Notificación in-app
            self.create_in_app_notification(
                user_id=user_id,
                title="Documento Subido",
                message=f"Tu documento '{document_name}' ({document_type}) ha sido subido exitosamente.",
                notification_type="info",
                link="/documentos"
            )

            return True

        except Exception as e:
            logger.error(f"Error en notify_document_uploaded: {e}", exc_info=True)
            return False

    def notify_system_alert(
        self,
        user_id: int,
        email: str,
        alert_title: str,
        alert_message: str,
        alert_type: str = "warning"
    ) -> bool:
        """
        Notifica alertas del sistema.

        Args:
            user_id: ID del usuario
            email: Email del usuario
            alert_title: Título de la alerta
            alert_message: Mensaje de la alerta
            alert_type: Tipo de alerta (info, warning, error)

        Returns:
            bool: True si se enviaron las notificaciones exitosamente
        """
        try:
            # Notificación in-app
            self.create_in_app_notification(
                user_id=user_id,
                title=alert_title,
                message=alert_message,
                notification_type=alert_type,
                link="/dashboard"
            )

            # Email solo para alertas críticas
            if self.email_enabled and alert_type == "error":
                subject = f"Alerta del Sistema: {alert_title}"
                body = f"""
                <html>
                    <body>
                        <h2 style="color: #d32f2f;">Alerta del Sistema</h2>
                        <h3>{alert_title}</h3>
                        <p>{alert_message}</p>
                        <br>
                        <p>Por favor, accede al sistema para más información.</p>
                    </body>
                </html>
                """
                self.send_email(email, subject, body, html=True)

            return True

        except Exception as e:
            logger.error(f"Error en notify_system_alert: {e}", exc_info=True)
            return False


# Instancia global del servicio de notificaciones
notification_service = NotificationService()
