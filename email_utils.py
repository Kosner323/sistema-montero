# -*- coding: utf-8 -*-
"""
Utilidades para envío de correos electrónicos con Flask-Mail.
"""
from flask import render_template_string
from flask_mail import Message
from extensions import mail
from logger import logger


# =============================================================================
# Plantillas de Correo HTML
# =============================================================================

WELCOME_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bienvenido a Sistema Montero</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }
        .container {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .header {
            background-color: #007bff;
            color: white;
            padding: 20px;
            border-radius: 8px 8px 0 0;
            text-align: center;
            margin: -30px -30px 20px -30px;
        }
        .header h1 {
            margin: 0;
            font-size: 24px;
        }
        .content {
            margin: 20px 0;
        }
        .button {
            display: inline-block;
            padding: 12px 24px;
            background-color: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            margin: 20px 0;
        }
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            font-size: 12px;
            color: #666;
            text-align: center;
        }
        .highlight {
            background-color: #e9f5ff;
            padding: 15px;
            border-left: 4px solid #007bff;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>¡Bienvenido a Sistema Montero!</h1>
        </div>
        <div class="content">
            <p>Hola <strong>{{ nombre }}</strong>,</p>

            <p>¡Gracias por registrarte en Sistema Montero! Tu cuenta ha sido creada exitosamente.</p>

            <div class="highlight">
                <strong>Detalles de tu cuenta:</strong><br>
                📧 Email: {{ email }}<br>
                📅 Fecha de registro: {{ fecha_registro }}
            </div>

            <p>Ya puedes acceder a todas las funcionalidades del sistema.</p>

            <p style="text-align: center;">
                <a href="{{ url_login }}" class="button">Iniciar Sesión</a>
            </p>

            <p>Si tienes alguna pregunta o necesitas ayuda, no dudes en contactarnos.</p>

            <p>¡Bienvenido a bordo!</p>

            <p>Saludos,<br>
            <strong>El equipo de Sistema Montero</strong></p>
        </div>
        <div class="footer">
            <p>Este es un correo automático, por favor no respondas a este mensaje.</p>
            <p>&copy; 2025 Sistema Montero. Todos los derechos reservados.</p>
        </div>
    </div>
</body>
</html>
"""


# =============================================================================
# Funciones de Envío de Correo
# =============================================================================

def send_notification_email(recipient, subject, body_html):
    """
    Función genérica para enviar un correo electrónico con contenido HTML.

    Args:
        recipient (str): Dirección de correo del destinatario
        subject (str): Asunto del correo
        body_html (str): Contenido HTML del correo

    Returns:
        bool: True si el envío fue exitoso, False en caso contrario
    """
    try:
        msg = Message(
            subject=subject,
            recipients=[recipient],
            html=body_html
        )
        mail.send(msg)
        logger.info(f"Correo enviado exitosamente a {recipient}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Error al enviar correo a {recipient}: {e}", exc_info=True)
        return False


def send_welcome_email(recipient, nombre, fecha_registro="Hoy", url_login="http://localhost:5000/login"):
    """
    Envía un correo de bienvenida a un nuevo usuario registrado.

    Args:
        recipient (str): Dirección de correo del destinatario
        nombre (str): Nombre del usuario
        fecha_registro (str, optional): Fecha de registro. Por defecto "Hoy"
        url_login (str, optional): URL de inicio de sesión

    Returns:
        bool: True si el envío fue exitoso, False en caso contrario
    """
    try:
        # Renderizar la plantilla con los datos del usuario
        html_content = render_template_string(
            WELCOME_EMAIL_TEMPLATE,
            nombre=nombre,
            email=recipient,
            fecha_registro=fecha_registro,
            url_login=url_login
        )

        subject = "¡Bienvenido a Sistema Montero!"

        return send_notification_email(recipient, subject, html_content)

    except Exception as e:
        logger.error(f"Error al enviar correo de bienvenida a {recipient}: {e}", exc_info=True)
        return False


def send_password_reset_email(recipient, nombre, reset_token, reset_url="http://localhost:5000/reset-password"):
    """
    Envía un correo para restablecer la contraseña.

    Args:
        recipient (str): Dirección de correo del destinatario
        nombre (str): Nombre del usuario
        reset_token (str): Token de restablecimiento
        reset_url (str): URL base para restablecer contraseña

    Returns:
        bool: True si el envío fue exitoso, False en caso contrario
    """
    try:
        html_content = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #dc3545; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #dc3545;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    margin: 20px 0;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Restablecer Contraseña</h1>
                </div>
                <div class="content">
                    <p>Hola <strong>{nombre}</strong>,</p>

                    <p>Recibimos una solicitud para restablecer la contraseña de tu cuenta en Sistema Montero.</p>

                    <p style="text-align: center;">
                        <a href="{reset_url}?token={reset_token}" class="button">Restablecer Contraseña</a>
                    </p>

                    <div class="warning">
                        <strong>⚠️ Importante:</strong><br>
                        Este enlace expirará en 1 hora por seguridad.<br>
                        Si no solicitaste este cambio, ignora este correo.
                    </div>

                    <p>Saludos,<br>
                    <strong>El equipo de Sistema Montero</strong></p>
                </div>
            </div>
        </body>
        </html>
        """

        subject = "Restablecer Contraseña - Sistema Montero"

        return send_notification_email(recipient, subject, html_content)

    except Exception as e:
        logger.error(f"Error al enviar correo de restablecimiento a {recipient}: {e}", exc_info=True)
        return False


def send_test_email(recipient):
    """
    Envía un correo de prueba simple para verificar la configuración SMTP.

    Args:
        recipient (str): Dirección de correo del destinatario

    Returns:
        bool: True si el envío fue exitoso, False en caso contrario
    """
    try:
        html_content = """
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #28a745;">✅ Prueba de Configuración SMTP</h2>
            <p>¡Felicidades! La configuración de Flask-Mail está funcionando correctamente.</p>
            <p>Este es un correo de prueba enviado desde el Sistema Montero.</p>
            <hr>
            <p style="color: #666; font-size: 12px;">
                Si recibiste este correo, significa que tu servidor SMTP está configurado correctamente.
            </p>
        </body>
        </html>
        """

        subject = "Prueba de Configuración SMTP - Sistema Montero"

        return send_notification_email(recipient, subject, html_content)

    except Exception as e:
        logger.error(f"Error al enviar correo de prueba a {recipient}: {e}", exc_info=True)
        return False
