# -*- coding: utf-8 -*-
"""
Blueprint de Notificaciones - Sistema Montero
=============================================
Rutas API para gestionar notificaciones in-app.
"""

import logging
from functools import wraps

from flask import Blueprint, g, jsonify, request

# Importar el servicio de notificaciones
from routes.notification_service import notification_service
from utils import get_db_connection

# Configuración de logging
logger = logging.getLogger(__name__)

# Crear Blueprint
bp_notificaciones = Blueprint("notificaciones", __name__, url_prefix="/api/notificaciones")


# ========================================================================
# DECORADOR DE AUTENTICACIÓN
# ========================================================================


def login_required(f):
    """Decorador para verificar que el usuario esté autenticado."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session

        if "user_id" not in session:
            return jsonify({"error": "No autorizado"}), 401
        return f(*args, **kwargs)

    return decorated_function


# ========================================================================
# RUTAS API - NOTIFICACIONES
# ========================================================================


@bp_notificaciones.route("/", methods=["GET"])
@login_required
def get_notifications():
    """
    Obtiene las notificaciones del usuario autenticado.

    Query Parameters:
        - unread_only (bool): Si True, solo devuelve notificaciones no leídas

    Returns:
        JSON: Lista de notificaciones
    """
    try:
        from flask import session

        user_id = session.get("user_id")

        # Obtener parámetro de consulta
        unread_only = request.args.get("unread_only", "false").lower() == "true"

        # Obtener notificaciones del servicio
        notifications = notification_service.get_user_notifications(user_id=user_id, unread_only=unread_only)

        return jsonify(notifications), 200

    except Exception as e:
        logger.error(f"Error al obtener notificaciones: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error al obtener notificaciones: {str(e)}"}), 500


@bp_notificaciones.route("/unread-count", methods=["GET"])
@login_required
def get_unread_count():
    """
    Obtiene el conteo de notificaciones no leídas del usuario autenticado.

    Returns:
        JSON: {'count': int}
    """
    try:
        from flask import session

        user_id = session.get("user_id")

        # Obtener conteo del servicio
        count = notification_service.get_unread_count(user_id=user_id)

        return jsonify({"count": count}), 200

    except Exception as e:
        logger.error(f"Error al obtener conteo de notificaciones: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error al obtener conteo: {str(e)}"}), 500


@bp_notificaciones.route("/mark-read", methods=["POST"])
@login_required
def mark_notification_read():
    """
    Marca una notificación como leída.

    Request Body:
        {
            "notification_id": int
        }

    Returns:
        JSON: {'success': bool, 'message': str}
    """
    try:
        data = request.get_json()

        # Validar datos
        if not data or "notification_id" not in data:
            return jsonify({"error": "Falta el ID de la notificación"}), 400

        notification_id = data["notification_id"]

        # Marcar como leída usando el servicio
        result = notification_service.mark_notification_as_read(notification_id)

        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 500

    except Exception as e:
        logger.error(f"Error al marcar notificación como leída: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error al marcar notificación: {str(e)}"}), 500


@bp_notificaciones.route("/mark-all-read", methods=["POST"])
@login_required
def mark_all_notifications_read():
    """
    Marca todas las notificaciones del usuario como leídas.

    Returns:
        JSON: {'success': bool, 'message': str, 'count': int}
    """
    try:
        from flask import session

        user_id = session.get("user_id")

        # Obtener todas las notificaciones no leídas
        unread_notifications = notification_service.get_user_notifications(user_id=user_id, unread_only=True)

        # Marcar cada una como leída
        count = 0
        for notification in unread_notifications:
            result = notification_service.mark_notification_as_read(notification["id"])
            if result["success"]:
                count += 1

        return jsonify({"success": True, "message": f"{count} notificaciones marcadas como leídas", "count": count}), 200

    except Exception as e:
        logger.error(f"Error al marcar todas las notificaciones: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error al marcar notificaciones: {str(e)}"}), 500


@bp_notificaciones.route("/create", methods=["POST"])
@login_required
def create_notification():
    """
    Crea una nueva notificación in-app (solo para administradores).

    Request Body:
        {
            "user_id": int/str,
            "message": str,
            "notification_type": str (optional, default: 'info'),
            "priority": str (optional, default: 'normal')
        }

    Returns:
        JSON: {'success': bool, 'notification_id': int}
    """
    try:
        data = request.get_json()

        # Validar datos requeridos
        if not data or "user_id" not in data or "message" not in data:
            return jsonify({"error": "Faltan datos requeridos (user_id, message)"}), 400

        user_id = data["user_id"]
        message = data["message"]
        notification_type = data.get("notification_type", "info")
        priority = data.get("priority", "normal")

        # Crear notificación usando el servicio
        result = notification_service.create_in_app_notification(
            user_id=user_id, message=message, notification_type=notification_type, priority=priority
        )

        if result["success"]:
            return jsonify(result), 201
        else:
            return jsonify(result), 500

    except Exception as e:
        logger.error(f"Error al crear notificación: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error al crear notificación: {str(e)}"}), 500


@bp_notificaciones.route("/<int:notification_id>", methods=["DELETE"])
@login_required
def delete_notification(notification_id):
    """
    Elimina una notificación específica.

    Args:
        notification_id (int): ID de la notificación a eliminar

    Returns:
        JSON: {'success': bool, 'message': str}
    """
    try:
        from flask import session

        user_id = session.get("user_id")

        # Usar g.db para consistencia con otros blueprints
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar que la notificación pertenece al usuario
        cursor.execute(
            """
            SELECT user_id FROM notificaciones WHERE id = ?
        """,
            (notification_id,),
        )

        notification = cursor.fetchone()

        if not notification:
            return jsonify({"error": "Notificación no encontrada"}), 404

        if notification["user_id"] != user_id:
            return jsonify({"error": "No tienes permiso para eliminar esta notificación"}), 403

        # Eliminar notificación
        cursor.execute("DELETE FROM notificaciones WHERE id = ?", (notification_id,))
        conn.commit()

        return jsonify({"success": True, "message": "Notificación eliminada exitosamente"}), 200

    except Exception as e:
        logger.error(f"Error al eliminar notificación: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error al eliminar notificación: {str(e)}"}), 500
    # g.db se cierra automáticamente por app.after_request


# ========================================================================
# RUTAS DE UTILIDAD
# ========================================================================


@bp_notificaciones.route("/test", methods=["POST"])
@login_required
def test_notification():
    """
    Endpoint de prueba para enviar una notificación de test al usuario autenticado.

    Returns:
        JSON: {'success': bool, 'message': str}
    """
    try:
        from flask import session

        user_id = session.get("user_id")

        # Crear notificación de prueba
        result = notification_service.create_in_app_notification(
            user_id=user_id,
            message="Esta es una notificación de prueba del Sistema Montero",
            notification_type="info",
            priority="normal",
        )

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error en test de notificación: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error en test: {str(e)}"}), 500
