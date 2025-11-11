# -*- coding: utf-8 -*-
"""
Módulo de Autenticación - Sistema Montero
=========================================
Versión: 2.6 - CORREGIDO (Imports absolutos desde la raíz del proyecto)
"""

from flask_restx import Namespace, Resource, fields
from flask import session, request

from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import re
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, Any

# --- IMPORTACIONES CORREGIDAS (SIN '..') ---
# Python buscará estos archivos en la carpeta raíz (dashboard/)
# donde 'app.py' está corriendo.
from utils import get_db_connection, login_required
from logger import get_logger
from validators import validate_json

try:
    # Buscará la carpeta 'models' en la raíz (dashboard/models)
    from models.validation_models import LoginRequest, RegisterRequest
except ImportError as e:
    print(f"ERROR CRÍTICO: No se pudieron importar los modelos de validación: {e}")
    print("Por favor, asegúrate de crear 'models/__init__.py' y 'models/validation_models.py'")

    # Clases de respaldo
    class LoginRequest:
        pass

    class RegisterRequest:
        pass


# Configurar logger para este módulo
logger = get_logger(__name__)


# ==============================================================================
# CONFIGURACIÓN DE SEGURIDAD
# (El resto del código no cambia)
# ==============================================================================

LOGIN_ATTEMPTS: Dict[str, list] = {}
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = timedelta(minutes=15)
MIN_PASSWORD_LENGTH = 6
EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


# ==============================================================================
# FUNCIONES DE VALIDACIÓN
# ==============================================================================


def is_valid_email(email: str) -> bool:
    if not email or not isinstance(email, str):
        return False
    return re.match(EMAIL_PATTERN, email) is not None


def check_rate_limit(email: str) -> Tuple[bool, Optional[str]]:
    now = datetime.now()

    if email in LOGIN_ATTEMPTS:
        LOGIN_ATTEMPTS[email] = [
            timestamp
            for timestamp in LOGIN_ATTEMPTS[email]
            if now - timestamp < LOCKOUT_TIME
        ]

        if len(LOGIN_ATTEMPTS[email]) >= MAX_LOGIN_ATTEMPTS:
            remaining_time = LOCKOUT_TIME - (now - LOGIN_ATTEMPTS[email][0])
            minutes = max(1, int(remaining_time.total_seconds() / 60))

            error_msg = (
                f"Demasiados intentos fallidos. "
                f"Por favor intenta nuevamente en {minutes} minutos."
            )
            logger.warning(
                f"Rate limit alcanzado para email: {email} "
                f"({len(LOGIN_ATTEMPTS[email])} intentos)"
            )
            return False, error_msg

    return True, None


def register_failed_attempt(email: str) -> None:
    if email not in LOGIN_ATTEMPTS:
        LOGIN_ATTEMPTS[email] = []

    LOGIN_ATTEMPTS[email].append(datetime.now())

    logger.info(
        f"Intento de login fallido registrado para: {email} "
        f"(Total: {len(LOGIN_ATTEMPTS[email])} intentos)"
    )


def clear_login_attempts(email: str) -> None:
    if email in LOGIN_ATTEMPTS:
        del LOGIN_ATTEMPTS[email]
        logger.debug(f"Intentos de login limpiados para: {email}")


# ==============================================================================
# DEFINICIÓN DEL NAMESPACE
# ==============================================================================

auth_ns = Namespace(
    "auth", description="Operaciones de Autenticación y Usuarios", path="/api"
)

# Modelo para la DOCUMENTACIÓN de Login (lo que ve Swagger)
login_request_doc = auth_ns.model(
    "LoginRequestDoc",
    {
        "email": fields.String(
            required=True,
            description="Correo electrónico del usuario",
            example="usuario@ejemplo.com",
        ),
        "password": fields.String(
            required=True,
            description="Contraseña del usuario",
            example="password123",
            min_length=6,
        ),
    },
)

# --- MODELO DE DOCUMENTACIÓN DE REGISTRO ACTUALIZADO (SIN SNAPCHAT) ---
register_request_doc = auth_ns.model(
    "RegisterRequestDoc",
    {
        "nombre": fields.String(
            required=True, description="Nombre del usuario", example="Juan Pérez"
        ),
        "email": fields.String(
            required=True,
            description="Correo electrónico del usuario",
            example="juan@ejemplo.com",
        ),
        "password": fields.String(
            required=True,
            description="Contraseña (mínimo 6 caracteres)",
            example="password123",
            min_length=6,
        ),
        "password_confirm": fields.String(
            required=True,
            description="Confirmación de la contraseña",
            example="password123",
        ),
        # --- CAMPOS OPCIONALES ACTUALIZADOS ---
        "telefono": fields.String(
            required=False,
            description="Teléfono opcional (ej. +573001234567)",
            example="+573001234567"
        ),
        "fecha_nacimiento": fields.String(
            required=False,
            description="Fecha de nacimiento opcional (YYYY-MM-DD)",
            example="1995-10-20"
        ),
    },
)


# ==============================================================================
# ENDPOINTS DE AUTENTICACIÓN
# ==============================================================================


@auth_ns.route("/check_auth")
class CheckAuth(Resource):
    def get(self):
        """
        Verifica el estado de autenticación del usuario actual.
        """
        user_id = session.get("user_id")

        logger.debug(f"Check auth - User ID: {user_id}, Session data: {dict(session)}")

        if user_id:
            user_name = session.get("user_name", "Usuario")
            logger.info(f"Usuario autenticado verificado: {user_name} (ID: {user_id})")
            return {"authenticated": True, "user_name": user_name}, 200
        else:
            logger.debug("Verificación de auth: usuario no autenticado")
            return {"authenticated": False}, 200


@auth_ns.route("/login")
class LoginUser(Resource):

    @auth_ns.expect(login_request_doc)
    @validate_json(LoginRequest)
    def post(self, body: LoginRequest):
        """
        Autentica un usuario con email y contraseña.
        Validado automáticamente por Pydantic.
        """
        conn = None
        try:
            email = body.email.lower()
            password = body.password

            logger.debug(f"Intento de login para email: {email}")

            allowed, error_msg = check_rate_limit(email)
            if not allowed:
                return {"error": error_msg}, 429

            conn = get_db_connection()
            user = conn.execute(
                "SELECT id, nombre, password_hash FROM portal_users WHERE email = ?",
                (email,),
            ).fetchone()

            if user is None:
                register_failed_attempt(email)
                logger.warning(f"Login fallido: usuario no encontrado - {email}")
                return {"error": "Email o contraseña incorrectos"}, 401

            if not check_password_hash(user["password_hash"], password):
                register_failed_attempt(email)
                logger.warning(
                    f"Login fallido: contraseña incorrecta - {email} (ID: {user['id']})"
                )
                return {"error": "Email o contraseña incorrectos"}, 401

            clear_login_attempts(email)

            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["nombre"]
            session["login_time"] = datetime.now().isoformat()
            session.permanent = False

            logger.info(
                f"✅ Login exitoso - Usuario: {user['nombre']} ({email}), ID: {user['id']}"
            )
            
            return {"message": "Inicio de sesión exitoso", "user_name": user["nombre"]}, 200

        except sqlite3.Error as db_error:
            logger.error(
                f"❌ Error de base de datos en /api/login: {db_error}", exc_info=True
            )
            return {"error": "Error al acceder a la base de datos"}, 500

        except Exception as error:
            logger.error(f"❌ Error inesperado en /api/login: {error}", exc_info=True)
            return {"error": "Error interno del servidor"}, 500

        finally:
            if conn:
                conn.close()


@auth_ns.route("/logout")
class LogoutUser(Resource):

    @login_required
    def post(self):
        """
        Cierra la sesión del usuario actual.
        """
        user_id = session.get("user_id")
        user_name = session.get("user_name", "Usuario")

        session.clear()

        logger.info(f"🔓 Logout exitoso - Usuario: {user_name} (ID: {user_id})")

        return {"message": "Sesión cerrada exitosamente"}, 200


# --- ENDPOINT DE REGISTRO ACTUALIZADO ---
@auth_ns.route("/register")
class RegisterUser(Resource):

    @auth_ns.expect(register_request_doc)
    @validate_json(RegisterRequest)
    def post(self, body: RegisterRequest):
        """
        Registra un nuevo usuario en el sistema.
        Validado automáticamente por Pydantic.
        Acepta campos opcionales: telefono, fecha_nacimiento
        """
        conn = None
        try:
            # Campos obligatorios
            nombre = body.nombre.strip()
            email = body.email.lower()
            password = body.password

            # --- Campos opcionales (leídos desde el body) ---
            telefono = getattr(body, 'telefono', None)
            fecha_nacimiento = getattr(body, 'fecha_nacimiento', None)
            
            if fecha_nacimiento:
                fecha_nacimiento = str(fecha_nacimiento)

            logger.debug(f"Intento de registro para: {nombre} ({email})")

            conn = get_db_connection()

            user_exists = conn.execute(
                "SELECT id FROM portal_users WHERE email = ?", (email,)
            ).fetchone()

            if user_exists:
                logger.warning(f"Registro fallido: email ya existe - {email}")
                return {"error": "El correo electrónico ya está registrado"}, 409

            password_hash = generate_password_hash(password, method="pbkdf2:sha256")

            # --- CONSULTA SQL ACTUALIZADA (SIN SNAPCHAT) ---
            sql_query = """
                INSERT INTO portal_users 
                (nombre, email, password_hash, telefono, fecha_nacimiento) 
                VALUES (?, ?, ?, ?, ?)
            """
            sql_params = (nombre, email, password_hash, telefono, fecha_nacimiento)
            
            cursor = conn.execute(sql_query, sql_params)
            conn.commit()
            new_user_id = cursor.lastrowid

            log_opcionales = []
            if telefono: log_opcionales.append(f"Tel: {telefono}")
            if fecha_nacimiento: log_opcionales.append(f"Nac: {fecha_nacimiento}")
            
            info_opcional = ", ".join(log_opcionales) if log_opcionales else "sin datos opcionales"

            logger.info(
                f"✅ Usuario registrado exitosamente - "
                f"Nombre: {nombre}, Email: {email}, ID: {new_user_id} ({info_opcional})"
            )

            return {"message": "Usuario registrado exitosamente"}, 201

        except sqlite3.IntegrityError as integrity_error:
            if conn:
                conn.rollback()
            logger.error(
                f"❌ Error de integridad en /api/register: {integrity_error}",
                exc_info=True,
            )
            return {"error": "El correo electrónico ya está registrado"}, 409

        except sqlite3.Error as db_error:
            if conn:
                conn.rollback()
            logger.error(
                f"❌ Error de base de datos en /api/register: {db_error}", exc_info=True
            )
            return {"error": "Error al acceder a la base de datos"}, 500

        except Exception as error:
            if conn:
                conn.rollback()
            logger.error(
                f"❌ Error inesperado en /api/register: {error}", exc_info=True
            )
            return {"error": "Error interno del servidor"}, 500

        finally:
            if conn:
                conn.close()


# ==============================================================================
# FIN DEL MÓDULO
# ==============================================================================