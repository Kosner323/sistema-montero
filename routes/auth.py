# -*- coding: utf-8 -*-
"""
Blueprint para la autenticación de usuarios y gestión de sesión.
"""
import re
import sqlite3
import traceback
from datetime import datetime, timedelta

from flask import Blueprint, current_app, jsonify, redirect, render_template, request, session
from pydantic import ValidationError
from werkzeug.security import check_password_hash, generate_password_hash

from logger import logger
from models.validation_models import LoginRequest, RegisterRequest
from utils import login_required, get_db_connection
from extensions import limiter
from email_utils import send_welcome_email

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
@limiter.limit("10 per hour")
def register():
    """
    Registra un nuevo usuario en el sistema.
    Implementa rate limiting mediante Flask-Limiter (10 intentos por hora).
    Valida los datos usando Pydantic.
    Siempre devuelve JSON (robustez ante errores inesperados).
    """
    try:
        try:
            json_data = request.get_json()
            if not json_data:
                logger.error("No se recibió JSON en /register")
                return jsonify({"error": "No se recibieron datos JSON"}), 400

            logger.info(f"Datos recibidos para registro: {json_data.keys()}")
            data = RegisterRequest(**json_data)

        except ValidationError as e:
            logger.warning(f"Validación fallida en registro: {e.errors()}", extra={"data": request.get_json()})
            first_error = e.errors()[0]
            error_msg = f"{first_error['loc'][0]}: {first_error['msg']}"
            return jsonify({"error": error_msg, "details": e.errors()}), 422
        except Exception as e:
            logger.error(f"Error al parsear JSON de registro: {e}", extra={"raw_data": request.data})
            return jsonify({"error": f"Formato de solicitud inválido: {str(e)}"}), 400

        try:
            conn = get_db_connection()
            user = conn.execute("SELECT id FROM usuarios WHERE correoElectronico = ?", (data.email,)).fetchone()

            if user:
                logger.warning(f"Registro fallido: email ya existe - {data.email}")
                return jsonify({"error": "El email ya está registrado."}), 409

            password_hash = generate_password_hash(data.password)

            conn.execute(
                """
                INSERT INTO usuarios (
                    primerNombre, correoElectronico, password_hash,
                    telefonoCelular, fechaNacimiento,
                    empresa_nit, tipoId, numeroId, primerApellido,
                    estado, role
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    data.nombre, data.email, password_hash,
                    data.telefono, data.fecha_nacimiento,
                    '999999999',
                    'CC', '0000000',
                    'Usuario',
                    'activo', 'empleado'
                ),
            )
            conn.commit()
            conn.close()

            logger.info(f"Nuevo usuario registrado: {data.email}")

            # Enviar correo de bienvenida
            try:
                email_sent = send_welcome_email(
                    recipient=data.email,
                    nombre=data.nombre,
                    fecha_registro=datetime.now().strftime("%d/%m/%Y"),
                    url_login=request.host_url + "login" if request.host_url else "http://localhost:5000/login"
                )
                if email_sent:
                    logger.info(f"Correo de bienvenida enviado a {data.email}")
                else:
                    logger.warning(f"No se pudo enviar correo de bienvenida a {data.email}")
            except Exception as email_error:
                # No fallamos el registro si falla el email
                logger.error(f"Error al enviar correo de bienvenida a {data.email}: {email_error}")

            return jsonify({"message": "Usuario registrado exitosamente."}), 201

        except sqlite3.IntegrityError as e:
            logger.error(f"Error de integridad al registrar: {data.email} - {e}", exc_info=True)
            return jsonify({"error": "Violación de integridad (posible email o username duplicado)."}), 409
        except Exception as e:
            logger.critical(f"Error inesperado en /register (DB): {e}", exc_info=True)
            try:
                conn.rollback()
            except Exception:
                pass
            return jsonify({"error": "Error interno del servidor."}), 500

    except Exception as e:
        logger.critical(f"Error CRÍTICO no manejado en /register: {e}", exc_info=True)
        return jsonify({"error": f"Fallo interno del servidor (API): {str(e)}"}), 500


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    """
    Autentica a un usuario y crea una sesión.
    Implementa rate limiting mediante Flask-Limiter (5 intentos por minuto).
    Siempre devuelve JSON (robustez ante errores inesperados).
    """
    try:
        try:
            json_data = request.get_json()
            if not json_data:
                logger.error("No se recibió JSON en /login")
                return jsonify({"error": "No se recibieron datos JSON"}), 400

            logger.info(f"Intento de login con datos: {json_data.keys()}")
            data = LoginRequest(**json_data)
            email = data.email.lower()
            password = data.password
        except ValidationError as e:
            logger.warning(f"Validación fallida en login: {e.errors()}", extra={"data": request.get_json()})
            first_error = e.errors()[0]
            error_msg = f"{first_error['loc'][0]}: {first_error['msg']}"
            return jsonify({"error": error_msg, "details": e.errors()}), 422
        except Exception as e:
            logger.error(f"Error al parsear JSON de login: {e}", extra={"raw_data": request.data})
            return jsonify({"error": f"Formato de solicitud inválido: {str(e)}"}), 400

        # Rate limiting
        allowed, error_msg = check_rate_limit(email)
        if not allowed:
            return jsonify({"error": error_msg}), 429

        try:
            conn = get_db_connection()
            user = conn.execute(
                "SELECT id, primerNombre, correoElectronico, password_hash, role FROM usuarios WHERE correoElectronico = ?",
                (email,)
            ).fetchone()

            if user is None or not user["password_hash"] or not check_password_hash(user["password_hash"], password):
                register_failed_attempt(email)
                logger.warning(f"Login fallido (credenciales incorrectas): {email}")
                conn.close()
                return jsonify({"error": "Email o contraseña incorrectos."}), 401

            clear_login_attempts(email)
            session.clear()
            session.permanent = True  # ✅ Marcar la sesión como permanente
            session["user_id"] = user["id"]
            session["user_name"] = user["primerNombre"]
            session["user_email"] = user["correoElectronico"]
            session["user_role"] = user["role"]
            session["login_time"] = datetime.now().isoformat()

            try:
                conn.execute("UPDATE usuarios SET updated_at = ? WHERE id = ?", (datetime.now(), user["id"]))
                conn.commit()
            except Exception as update_e:
                logger.error(f"Error al actualizar updated_at para {email}: {update_e}", exc_info=True)
                pass

            conn.close()

            logger.info(f"Login exitoso: {email} (ID: {user['id']})")
            return jsonify({
                "message": "Inicio de sesión exitoso",
                "user_id": user["id"],
                "user_name": user["primerNombre"],
                "user_role": user["role"]
            }), 200

        except sqlite3.Error as e:
            logger.critical(f"Error de base de datos en /login: {e}", exc_info=True)
            return jsonify({"error": "Error de base de datos. Intente nuevamente."}), 500
        except Exception as e:
            logger.critical(f"Error inesperado en /login (DB): {e}", exc_info=True)
            return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500

    except Exception as e:
        logger.critical(f"Error CRÍTICO no manejado en /login: {e}", exc_info=True)
        return jsonify({"error": f"Fallo interno del servidor (API): {str(e)}"}), 500


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


@auth_bp.route("/verify-password", methods=["POST"])
@login_required
def verify_password():
    """
    Verifica la contraseña del usuario actual para desbloquear la pantalla.
    Endpoint de seguridad para Lock Screen.

    Request JSON:
        {
            "password": str  # Contraseña en texto plano a verificar
        }

    Response JSON (Success):
        {
            "success": true,
            "message": "Desbloqueo exitoso"
        }

    Response JSON (Error):
        {
            "success": false,
            "message": "Contraseña incorrecta"
        }
    """
    conn = None
    try:
        data = request.get_json()

        if not data:
            logger.warning("Intento de verificación de contraseña sin datos JSON")
            return jsonify({"success": False, "message": "No se recibieron datos"}), 400

        password_input = data.get("password")

        # Validación básica
        if not password_input:
            logger.warning("Verificación de contraseña: campo 'password' faltante")
            return jsonify({"success": False, "message": "Contraseña requerida"}), 400

        user_id = session.get("user_id")

        if not user_id:
            logger.error("Intento de verificación sin user_id en sesión")
            return jsonify({"success": False, "message": "Sesión no válida"}), 401

        # Buscar el hash real del usuario en la BD
        conn = get_db_connection()
        user = conn.execute(
            "SELECT id, password_hash, primerNombre, primerApellido FROM usuarios WHERE id = ?",
            (user_id,)
        ).fetchone()

        if not user:
            logger.error(f"Usuario no encontrado en BD durante verificación lockscreen: {user_id}")
            return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

        # Verificar que el usuario tenga contraseña configurada
        if not user["password_hash"]:
            logger.warning(f"Usuario {user_id} no tiene password_hash en BD (lockscreen)")
            return jsonify({"success": False, "message": "Contraseña no configurada. Contacte al administrador"}), 500

        # Verificar la contraseña con bcrypt
        if check_password_hash(user["password_hash"], password_input):
            # Contraseña correcta: refrescar sesión
            session.modified = True
            logger.info(f"✅ Desbloqueo exitoso - User: {user_id} ({user['primerNombre']} {user['primerApellido']})")
            return jsonify({"success": True, "message": "Desbloqueo exitoso"}), 200
        else:
            # Contraseña incorrecta
            logger.warning(f"❌ Intento fallido de desbloqueo - User: {user_id}")
            return jsonify({"success": False, "message": "Contraseña incorrecta"}), 401

    except sqlite3.Error as db_err:
        logger.error(f"Error de BD en verificación lockscreen: {db_err}", exc_info=True)
        return jsonify({"success": False, "message": "Error de base de datos"}), 500

    except Exception as e:
        logger.error(f"Error inesperado en verificación lockscreen: {e}", exc_info=True)
        return jsonify({"success": False, "message": f"Error de servidor: {str(e)}"}), 500

    finally:
        if conn:
            conn.close()


# --- RUTA DE PANTALLA DE BLOQUEO ---
@auth_bp.route('/lockscreen')
def lockscreen():
    """Muestra la pantalla de bloqueo de sesión."""
    # Si no hay usuario en sesión, mandar al login normal
    if 'user_id' not in session:
        return redirect('/login')

    return render_template('auth/lockscreen.html')


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
