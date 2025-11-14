# -*- coding: utf-8 -*-
"""
notificaciones_routes.py - Rutas API para Notificaciones
=========================================================
Blueprint con endpoints para gestionar notificaciones in-app.
"""

from flask import Blueprint, request, jsonify, session
from logger import get_logger
from utils import login_required
from routes.notification_service import notification_service

logger = get_logger(__name__)

# Crear Blueprint
bp_notificaciones = Blueprint("notificaciones", __name__, url_prefix="/api/notificaciones")


@bp_notificaciones.route("/", methods=["GET"])
@login_required
def get_notifications():
    """
    Obtiene las notificaciones del usuario autenticado.

    Query Parameters:
        - unread_only (bool): Si es "true", solo devuelve notificaciones no leídas
        - limit (int): Número máximo de notificaciones a devolver (default: 50)

    Returns:
        JSON con lista de notificaciones
    """
    try:
        user_id = session.get("user_id")

        # Obtener parámetros de query
        unread_only = request.args.get("unread_only", "false").lower() == "true"
        limit = int(request.args.get("limit", 50))

        # Obtener notificaciones
        notifications = notification_service.get_user_notifications(
            user_id=user_id,
            unread_only=unread_only,
            limit=limit
        )

        logger.info(
            f"Usuario {user_id} obtuvo {len(notifications)} notificaciones "
            f"(unread_only={unread_only})"
        )

        return jsonify({
            "success": True,
            "notifications": notifications,
            "count": len(notifications)
        }), 200

    except ValueError as e:
        logger.error(f"Error de validación en get_notifications: {e}")
        return jsonify({
            "success": False,
            "error": "Parámetros inválidos"
        }), 400

    except Exception as e:
        logger.error(f"Error en get_notifications: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Error obteniendo notificaciones"
        }), 500


@bp_notificaciones.route("/unread-count", methods=["GET"])
@login_required
def get_unread_count():
    """
    Obtiene el número de notificaciones no leídas del usuario.

    Returns:
        JSON con el conteo de notificaciones no leídas
    """
    try:
        user_id = session.get("user_id")

        count = notification_service.get_unread_count(user_id)

        return jsonify({
            "success": True,
            "unread_count": count
        }), 200

    except Exception as e:
        logger.error(f"Error en get_unread_count: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Error obteniendo conteo de notificaciones"
        }), 500


@bp_notificaciones.route("/mark-read/<int:notification_id>", methods=["PUT", "PATCH"])
@login_required
def mark_notification_as_read(notification_id):
    """
    Marca una notificación como leída.

    Args:
        notification_id (int): ID de la notificación

    Returns:
        JSON confirmando la operación
    """
    try:
        user_id = session.get("user_id")

        success = notification_service.mark_as_read(
            notification_id=notification_id,
            user_id=user_id
        )

        if success:
            return jsonify({
                "success": True,
                "message": "Notificación marcada como leída"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "No se pudo marcar la notificación como leída"
            }), 404

    except Exception as e:
        logger.error(f"Error en mark_notification_as_read: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Error marcando notificación como leída"
        }), 500


@bp_notificaciones.route("/mark-all-read", methods=["PUT", "PATCH"])
@login_required
def mark_all_as_read():
    """
    Marca todas las notificaciones del usuario como leídas.

    Returns:
        JSON confirmando la operación
    """
    try:
        user_id = session.get("user_id")

        # Obtener todas las notificaciones no leídas
        unread_notifications = notification_service.get_user_notifications(
            user_id=user_id,
            unread_only=True,
            limit=1000  # Límite alto para obtener todas
        )

        # Marcar cada una como leída
        marked_count = 0
        for notification in unread_notifications:
            if notification_service.mark_as_read(notification["id"], user_id):
                marked_count += 1

        logger.info(
            f"Usuario {user_id} marcó {marked_count} notificaciones como leídas"
        )

        return jsonify({
            "success": True,
            "message": f"{marked_count} notificaciones marcadas como leídas",
            "marked_count": marked_count
        }), 200

    except Exception as e:
        logger.error(f"Error en mark_all_as_read: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Error marcando notificaciones como leídas"
        }), 500


@bp_notificaciones.route("/test", methods=["POST"])
@login_required
def test_notification():
    """
    Endpoint de prueba para crear una notificación de test.

    Body JSON:
        - title (str): Título de la notificación
        - message (str): Mensaje de la notificación
        - type (str): Tipo de notificación (info, warning, error, success)

    Returns:
        JSON confirmando la creación de la notificación
    """
    try:
        user_id = session.get("user_id")
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "Se requiere un body JSON"
            }), 400

        title = data.get("title", "Notificación de Prueba")
        message = data.get("message", "Esta es una notificación de prueba del sistema.")
        notification_type = data.get("type", "info")

        # Validar tipo
        valid_types = ["info", "warning", "error", "success"]
        if notification_type not in valid_types:
            return jsonify({
                "success": False,
                "error": f"Tipo inválido. Debe ser uno de: {', '.join(valid_types)}"
            }), 400

        # Crear notificación
        notification_id = notification_service.create_in_app_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type
        )

        if notification_id:
            return jsonify({
                "success": True,
                "message": "Notificación de prueba creada exitosamente",
                "notification_id": notification_id
            }), 201
        else:
            return jsonify({
                "success": False,
                "error": "No se pudo crear la notificación"
            }), 500

    except Exception as e:
        logger.error(f"Error en test_notification: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Error creando notificación de prueba"
        }), 500


@bp_notificaciones.route("/send-email-test", methods=["POST"])
@login_required
def test_email():
    """
    Endpoint de prueba para enviar un email de test (solo para desarrollo/debug).

    Body JSON:
        - email (str): Email destinatario
        - subject (str): Asunto del email
        - message (str): Mensaje del email

    Returns:
        JSON confirmando el envío del email
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "Se requiere un body JSON"
            }), 400

        email = data.get("email")
        subject = data.get("subject", "Email de Prueba - Sistema Montero")
        message = data.get("message", "Este es un email de prueba del sistema.")

        if not email:
            return jsonify({
                "success": False,
                "error": "Se requiere el campo 'email'"
            }), 400

        # Enviar email
        success = notification_service.send_email(
            to_email=email,
            subject=subject,
            body=f"<html><body><p>{message}</p></body></html>",
            html=True
        )

        if success:
            return jsonify({
                "success": True,
                "message": f"Email de prueba enviado a {email}"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "No se pudo enviar el email. Verifica la configuración SMTP."
            }), 500

    except Exception as e:
        logger.error(f"Error en test_email: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Error enviando email de prueba"
        }), 500


# Health check endpoint
@bp_notificaciones.route("/health", methods=["GET"])
def health_check():
    """
    Endpoint de health check para verificar que el servicio está funcionando.

    Returns:
        JSON con el estado del servicio
    """
    return jsonify({
        "success": True,
        "service": "notifications",
        "status": "healthy"
    }), 200
