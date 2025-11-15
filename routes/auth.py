# -*- coding: utf-8 -*-
"""
Blueprint para la autenticación de usuarios y gestión de sesión.
"""
import re
import sqlite3
import traceback
from datetime import datetime, timedelta

from flask import Blueprint, current_app, g, jsonify, make_response, request, session
from pydantic import ValidationError
from werkzeug.security import check_password_hash, generate_password_hash

from logger import logger
from models.validation_models import LoginRequest, RegisterRequest
from utils import login_required

# --- Configuración del Blueprint ---
auth_bp = Blueprint("auth", __name__, url_prefix="/api")

# --- Constantes de Seguridad ---
MIN_PASSWORD_LENGTH = 8
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = timedelta(minutes=15)

# --- Almacenamiento en memoria para Rate Limiting ---
LOGIN_ATTEMPTS = {}  # { 'email': [timestamp1, timestamp2, ...] }

# ==============================================================================
# Funciones de Ayuda (Helpers)
# ==============================================================================


def is_valid_email(email: str) -> bool:
    """Verifica si un email tiene un formato válido."""
    if not email or not isinstance(email, str):
        return False
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def register_failed_attempt(email: str):
    """Registra un intento fallido de login para un email."""
    now = datetime.now()
    if email not in LOGIN_ATTEMPTS:
        LOGIN_ATTEMPTS[email] = []

    LOGIN_ATTEMPTS[email].append(now)
    logger.warning(f"Intento fallido de login para: {email}. Total intentos: {len(LOGIN_ATTEMPTS[email])}")


def clear_login_attempts(email: str):
    """Limpia los intentos de login para un email (usado en login exitoso)."""
    if email in LOGIN_ATTEMPTS:
        try:
            del LOGIN_ATTEMPTS[email]
            logger.info(f"Intentos de login limpiados para: {email}")
        except KeyError:
            pass


def check_rate_limit(email: str) -> tuple[bool, str | None]:
    """
    Verifica si un email ha excedido el límite de intentos de login.
    Limpia intentos antiguos que ya expiraron.
    """
    now = datetime.now()

    if email not in LOGIN_ATTEMPTS:
        return True, None

    valid_attempts = [ts for ts in LOGIN_ATTEMPTS[email] if (now - ts) < LOCKOUT_TIME]

    LOGIN_ATTEMPTS[email] = valid_attempts

    if len(valid_attempts) >= MAX_LOGIN_ATTEMPTS:
        logger.critical(f"Bloqueo de cuenta por rate limit: {email}")

        oldest_attempt = min(valid_attempts)
        time_remaining = (oldest_attempt + LOCKOUT_TIME) - now
        minutes_remaining = max(1, (time_remaining.seconds // 60) + 1)

        error_msg = f"Demasiados intentos fallidos. Intente de nuevo en {minutes_remaining} minutos."
        return False, error_msg

    return True, None


# ==============================================================================
# Endpoints de Autenticación
# ==============================================================================


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Registra un nuevo usuario en el sistema.
    Valida los datos usando Pydantic.
    """
    try:
        data = RegisterRequest(**request.get_json())
    except ValidationError as e:
        logger.warning(f"Validación fallida en registro: {e.errors()}", extra={"data": request.get_json()})
        return jsonify({"error": e.errors()[0]["msg"]}), 422
    except Exception as e:
        logger.error(f"Error al parsear JSON de registro: {e}", extra={"raw_data": request.data})
        return jsonify({"error": "Formato de solicitud inválido."}), 400

    try:
        # Usar la conexión del contexto de la aplicación (g.db) que ya está configurada
        conn = g.db

        # El modelo Pydantic 'RegisterRequest' ya convierte el email a minúsculas
        user = conn.execute("SELECT id FROM portal_users WHERE email = ?", (data.email,)).fetchone()

        if user:
            logger.warning(f"Registro fallido: email ya existe - {data.email}")
            return jsonify({"error": "El email ya está registrado."}), 400

        password_hash = generate_password_hash(data.password)

        conn.execute(
            """
            INSERT INTO portal_users (nombre, email, password_hash, telefono, fecha_nacimiento)
            VALUES (?, ?, ?, ?, ?)
        """,
            (data.nombre, data.email, password_hash, data.telefono, data.fecha_nacimiento),
        )
        conn.commit()

        logger.info(f"Nuevo usuario registrado: {data.email}")
        return jsonify({"message": "Usuario registrado exitosamente."}), 201

    except sqlite3.IntegrityError:
        logger.error(f"Error de integridad al registrar: {data.email}", exc_info=True)
        return jsonify({"error": "Error al registrar el usuario (Email duplicado)."}), 400
    except Exception as e:
        logger.critical(f"Error inesperado en /register: {e}", exc_info=True)
        conn.rollback()
        return jsonify({"error": "Error interno del servidor."}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Autentica a un usuario y crea una sesión.
    Implementa rate limiting.
    """
    try:
        data = LoginRequest(**request.get_json())
        # (CORREGIDO: Normaliza el email a minúsculas)
        email = data.email.lower()
        password = data.password
    except ValidationError as e:
        logger.warning(f"Validación fallida en login: {e.errors()}", extra={"data": request.get_json()})
        return jsonify({"error": e.errors()[0]["msg"]}), 422
    except Exception as e:
        logger.error(f"Error al parsear JSON de login: {e}", extra={"raw_data": request.data})
        return jsonify({"error": "Formato de solicitud inválido."}), 400

    # 1. Verificar Rate Limiting (usando el email normalizado)
    allowed, error_msg = check_rate_limit(email)
    if not allowed:
        return jsonify({"error": error_msg}), 429

    try:
        # Usar la conexión del contexto de la aplicación (g.db) que ya está configurada
        conn = g.db

        # 2. Buscar usuario en la base de datos (usando el email normalizado)
        user = conn.execute("SELECT * FROM portal_users WHERE email = ?", (email,)).fetchone()

        # 3. Validar usuario y contraseña
        if user is None or not check_password_hash(user["password_hash"], password):
            register_failed_attempt(email)  # Registrar intento fallido
            logger.warning(f"Login fallido (credenciales incorrectas): {email}")
            return jsonify({"error": "Email o contraseña incorrectos."}), 401

        # 4. Login exitoso: Limpiar intentos y crear sesión
        clear_login_attempts(email)

        session.clear()
        session["user_id"] = user["id"]
        session["user_name"] = user["nombre"]
        session["login_time"] = datetime.now().isoformat()

        # Actualizar último acceso
        try:
            conn.execute("UPDATE portal_users SET ultimo_acceso = ? WHERE id = ?", (datetime.now(), user["id"]))
            conn.commit()
        except Exception as update_e:
            logger.error(f"Error al actualizar ultimo_acceso para {email}: {update_e}", exc_info=True)
            pass

        logger.info(f"Login exitoso: {email} (ID: {user['id']})")
        return jsonify({"message": "Inicio de sesión exitoso", "user_id": user["id"], "user_name": user["nombre"]}), 200

    except Exception as e:
        logger.critical(f"Error inesperado en /login: {e}", exc_info=True)
        return jsonify({"error": "Error interno del servidor."}), 500


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    Cierra la sesión del usuario.
    Esta ruta es pública y siempre devuelve JSON.
    """
    try:
        session.clear()
        logger.info(f"Sesión cerrada para el usuario (si existía).")
        return jsonify({"message": "Sesión cerrada exitosamente"}), 200
    except Exception as e:
        logger.error(f"Error durante logout: {e}", exc_info=True)
        return jsonify({"error": "Error al cerrar sesión"}), 500


@auth_bp.route("/check_auth", methods=["GET"])
def check_auth():
    """
    Verifica si el usuario tiene una sesión activa.
    """
    if "user_id" in session and "user_name" in session:
        return jsonify({"authenticated": True, "user_id": session["user_id"], "user_name": session["user_name"]}), 200
    else:
        return jsonify({"authenticated": False}), 200


# ==============================================================================
# Gestión de Errores Específicos del Blueprint
# ==============================================================================


@auth_bp.app_errorhandler(404)
def handle_404(error):
    """Maneja errores 404 para rutas de API."""
    if request.path.startswith("/api/"):
        return jsonify({"error": "Ruta no encontrada"}), 404
    return error


@auth_bp.app_errorhandler(405)
def handle_405(error):
    """Maneja errores 405 (Método no permitido) para rutas de API."""
    if request.path.startswith("/api/"):
        return jsonify({"error": "Método no permitido para esta ruta"}), 405
    return error
