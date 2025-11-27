# -*- coding: utf-8 -*-
"""
user_settings.py - Configuración de Usuario
====================================================
Maneja la lógica de configuración del usuario:
- Vista de configuración del perfil
- Cambio de contraseña
"""
import sqlite3
import traceback

from flask import Blueprint, jsonify, render_template, request, session, redirect, current_app
from werkzeug.security import check_password_hash, generate_password_hash

from logger import logger

# --- IMPORTACIÓN CENTRALIZADA ---
# Intentamos importar desde nivel superior o local, SIN crear fallbacks locales
try:
    from ..extensions import db
    from ..models.orm_models import PortalUser
    from ..utils import login_required
except (ImportError, ValueError):
    from extensions import db
    from models.orm_models import PortalUser
    from utils import login_required
# -------------------------------


# ==================== DEFINICIÓN DEL BLUEPRINT ====================
user_settings_bp = Blueprint("user_settings", __name__)


# ==================== RUTAS DE VISTAS ====================

@user_settings_bp.route("/configuracion")
@login_required
def configuracion():
    """
    Página de configuración del usuario.
    Renderiza: main/configuracion.html
    """
    logger.debug(f"Usuario {session.get('user_id')} accediendo a configuración")
    return render_template("main/configuracion.html", user=session.get('user'))


# ==================== RUTAS DE API ====================

@user_settings_bp.route("/api/user/change_password", methods=["POST"])
@login_required
def change_password():
    """
    Cambia la contraseña del usuario autenticado.

    Request JSON:
        {
            "current_password": str,
            "new_password": str
        }

    Response JSON:
        {
            "message": str,
            "success": bool
        }
    """
    conn = None
    user_id = session.get("user_id")

    try:
        data = request.get_json()

        if not data:
            logger.warning(f"Intento de cambio de contraseña sin datos JSON. User: {user_id}")
            return jsonify({"error": "No se recibieron datos."}), 400

        current_password = data.get("current_password")
        new_password = data.get("new_password")

        # Validaciones básicas
        if not current_password or not new_password:
            logger.warning(f"Cambio de contraseña: campos faltantes. User: {user_id}")
            return jsonify({"error": "La contraseña actual y la nueva son requeridas."}), 400

        if len(new_password) < 6:
            return jsonify({"error": "La nueva contraseña debe tener al menos 6 caracteres."}), 400

        if current_password == new_password:
            return jsonify({"error": "La nueva contraseña debe ser diferente a la actual."}), 400

        conn = get_db_connection()

        # 1. Obtener el hash de la contraseña actual del usuario
        user = conn.execute(
            "SELECT id, password_hash, primerNombre, primerApellido FROM usuarios WHERE id = ?",
            (user_id,)
        ).fetchone()

        if not user:
            logger.error(f"Usuario no encontrado en BD durante cambio de contraseña: {user_id}")
            return jsonify({"error": "Usuario no encontrado."}), 404

        # 2. Verificar que la contraseña actual sea correcta
        if not user["password_hash"]:
            logger.warning(f"Usuario {user_id} no tiene password_hash en BD")
            return jsonify({"error": "No se puede cambiar la contraseña. Contacte al administrador."}), 500

        if not check_password_hash(user["password_hash"], current_password):
            logger.warning(f"Intento fallido de cambio de contraseña (contraseña actual incorrecta). User: {user_id}")
            return jsonify({"error": "La contraseña actual es incorrecta."}), 401

        # 3. Generar hash de la nueva contraseña
        new_password_hash = generate_password_hash(new_password)

        # 4. Actualizar la contraseña en la base de datos
        conn.execute(
            "UPDATE usuarios SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_password_hash, user_id)
        )
        conn.commit()

        logger.info(f"Contraseña actualizada exitosamente para usuario: {user_id} ({user['primerNombre']} {user['primerApellido']})")

        return jsonify({
            "message": "Contraseña actualizada exitosamente.",
            "success": True
        }), 200

    except sqlite3.Error as db_err:
        if conn:
            conn.rollback()
        logger.error(f"Error de BD al cambiar contraseña para usuario {user_id}: {db_err}", exc_info=True)
        return jsonify({"error": "Error de base de datos al actualizar la contraseña."}), 500

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error inesperado al cambiar contraseña para usuario {user_id}: {e}", exc_info=True)
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500

    finally:
        if conn:
            conn.close()


@user_settings_bp.route("/api/user/verify_password", methods=["POST"])
@login_required
def verify_password():
    """
    Verifica la contraseña del usuario autenticado (usado para lock screen).

    Request JSON:
        {
            "password": str
        }

    Response JSON:
        {
            "valid": bool,
            "message": str
        }
    """
    conn = None
    user_id = session.get("user_id")

    try:
        data = request.get_json()

        if not data:
            logger.warning(f"Intento de verificación de contraseña sin datos JSON. User: {user_id}")
            return jsonify({"error": "No se recibieron datos.", "valid": False}), 400

        password = data.get("password")

        # Validación básica
        if not password:
            logger.warning(f"Verificación de contraseña: campo faltante. User: {user_id}")
            return jsonify({"error": "La contraseña es requerida.", "valid": False}), 400

        conn = get_db_connection()

        # Obtener el hash de la contraseña del usuario
        user = conn.execute(
            "SELECT id, password_hash, primerNombre, primerApellido FROM usuarios WHERE id = ?",
            (user_id,)
        ).fetchone()

        if not user:
            logger.error(f"Usuario no encontrado en BD durante verificación de contraseña: {user_id}")
            return jsonify({"error": "Usuario no encontrado.", "valid": False}), 404

        # Verificar que el usuario tenga contraseña configurada
        if not user["password_hash"]:
            logger.warning(f"Usuario {user_id} no tiene password_hash en BD")
            return jsonify({"error": "No se puede verificar la contraseña. Contacte al administrador.", "valid": False}), 500

        # Verificar la contraseña
        if not check_password_hash(user["password_hash"], password):
            logger.warning(f"Intento fallido de verificación de contraseña (lockscreen). User: {user_id}")
            return jsonify({"error": "Contraseña incorrecta.", "valid": False}), 401

        # Contraseña válida
        logger.info(f"Contraseña verificada exitosamente (lockscreen). User: {user_id} ({user['primerNombre']} {user['primerApellido']})")

        return jsonify({
            "valid": True,
            "message": "Contraseña verificada exitosamente."
        }), 200

    except sqlite3.Error as db_err:
        logger.error(f"Error de BD al verificar contraseña para usuario {user_id}: {db_err}", exc_info=True)
        return jsonify({"error": "Error de base de datos.", "valid": False}), 500

    except Exception as e:
        logger.error(f"Error inesperado al verificar contraseña para usuario {user_id}: {e}", exc_info=True)
        return jsonify({"error": f"Error interno del servidor: {str(e)}", "valid": False}), 500

    finally:
        if conn:
            conn.close()


@user_settings_bp.route("/api/user/profile", methods=["GET"])
@login_required
def get_user_profile():
    """
    Obtiene la información del perfil del usuario autenticado.

    Response JSON:
        {
            "id": int,
            "primerNombre": str,
            "primerApellido": str,
            "correoElectronico": str,
            "tipoId": str,
            "numeroId": str,
            "empresa_nit": str,
            "role": str
        }
    """
    conn = None
    user_id = session.get("user_id")

    try:
        conn = get_db_connection()

        user = conn.execute(
            """
            SELECT
                u.id,
                u.primerNombre,
                u.segundoNombre,
                u.primerApellido,
                u.segundoApellido,
                u.correoElectronico,
                u.tipoId,
                u.numeroId,
                u.empresa_nit,
                u.role,
                u.telefonoCelular,
                e.nombre_empresa
            FROM usuarios u
            LEFT JOIN empresas e ON u.empresa_nit = e.nit
            WHERE u.id = ?
            """,
            (user_id,)
        ).fetchone()

        if not user:
            return jsonify({"error": "Usuario no encontrado."}), 404

        logger.debug(f"Perfil cargado para usuario: {user_id}")
        return jsonify(dict(user)), 200

    except Exception as e:
        logger.error(f"Error obteniendo perfil para usuario {user_id}: {e}", exc_info=True)
        return jsonify({"error": "Error al obtener el perfil del usuario."}), 500

    finally:
        if conn:
            conn.close()
