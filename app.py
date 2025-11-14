# -*- coding: utf-8 -*-
r"""
Sistema de GestiÃ³n Montero - AplicaciÃ³n Principal
VersiÃ³n: 1.2 - IntegraciÃ³n de Pydantic y Swagger (flask-restx)
Fecha: 1 de noviembre de 2025
"""

# --- INICIO DE CORRECCIÃ“N DE IMPORTACIÃ“N ---
import os
import sys

# AÃ±adir el directorio 'dashboard' (donde estÃ¡ app.py) al path
# para que las importaciones (ej. routes -> models) funcionen.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
# --- FIN DE CORRECCIÃ“N DE IMPORTACIÃ“N ---

from flask import (
    Flask,
    request,
    jsonify,
    send_file,
    send_from_directory,
    session,
    redirect,
)
from flask_cors import CORS
import sqlite3
from datetime import datetime
import io
import traceback
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from flask_restx import Api

# ==================== CARGAR VARIABLES DE ENTORNO ====================
load_dotenv()

# ==================== IMPORTAR UTILIDADES Y BLUEPRINTS ====================
from utils import get_db_connection, login_required

# Importamos el 'Namespace' (auth_ns) que creaste en routes/auth.py
from routes.auth import auth_ns

from routes.empresas import bp_empresas
from routes.usuarios import bp_usuarios
from routes.pagos import bp_pagos
from routes.formularios import bp_formularios
from routes.incapacidades import bp_incapacidades
from routes.tutelas import bp_tutelas
from routes.depuraciones import bp_depuraciones
from routes.cotizaciones import bp_cotizaciones
from routes.pago_impuestos import bp_impuestos
from routes.envio_planillas import bp_envio_planillas
from routes.credenciales import bp_credenciales
from routes.novedades import bp_novedades
from routes.unificacion import bp_unificacion
from routes.notificaciones_routes import bp_notificaciones
from logger import get_logger

logger = get_logger(__name__)

# ==================== CONFIGURACIÃ“N DE RUTAS ====================
# (BASE_DIR ya estÃ¡ definido arriba)

# ðŸŽ¨ ASSETS_DIR: Carpeta de archivos estÃ¡ticos (CSS, JS, imÃ¡genes, etc.)
ASSETS_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "assets"))

# Otras carpetas
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "formularios_pdf")
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.getenv("DATABASE_PATH", os.path.join(DATA_DIR, "mi_sistema.db"))

# Crear carpetas si no existen
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ==================== VERIFICACIÃ“N DE ASSETS_DIR ====================
logger.info("=" * 70)
logger.info("ðŸš€ INICIANDO SISTEMA DE GESTIÃ“N MONTERO")
logger.info("=" * 70)
logger.info(f"ðŸ“ BASE_DIR: {BASE_DIR}")
logger.info(f"ðŸŽ¨ ASSETS_DIR: {ASSETS_DIR}")

if not os.path.isdir(ASSETS_DIR):
    logger.warning(f"âš ï¸  ADVERTENCIA: Carpeta 'assets' NO encontrada en: {ASSETS_DIR}")
    potential_assets_dir_sibling = os.path.join(BASE_DIR, "assets")
    if os.path.isdir(potential_assets_dir_sibling):
        ASSETS_DIR = potential_assets_dir_sibling
        logger.info(f"âœ… Usando carpeta 'assets' encontrada en: {ASSETS_DIR}")
    else:
        logger.error(
            "âŒ ERROR: No se encontrÃ³ la carpeta 'assets' en ninguna ubicaciÃ³n"
        )
else:
    logger.info(f"âœ… Carpeta 'assets' encontrada correctamente")

logger.info(f"ðŸ“¤ UPLOAD_FOLDER: {UPLOAD_FOLDER}")
logger.info(f"ðŸ’¾ DATABASE: {DB_PATH}")
logger.info("=" * 70)

# ==================== INICIALIZACIÃ“N DE FLASK ====================

# --- INICIO DE CORRECCIÃ“N (Error 404 en /docs/) ---
# Restaurar el static_folder. Flask-RESTX lo necesita para servir la UI de Swagger.
app = Flask(__name__, static_folder="static")
# --- FIN DE CORRECCIÃ“N ---


# Inicializar la API de flask-restx (Swagger)
api = Api(
    app,
    version="1.0",
    title="API Sistema Montero",
    description="DocumentaciÃ³n interactiva de la API del Sistema Montero.",
    doc="/docs/",  # La documentaciÃ³n estarÃ¡ en http://127.0.0.1:5000/docs/
)

# ==================== CONFIGURACIÃ“N CORS ====================
cors_origins = os.getenv("CORS_ORIGINS", "http://127.0.0.1:5000,http://localhost:5000")
cors_origins_list = [origin.strip() for origin in cors_origins.split(",")]

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": cors_origins_list,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": [
                "Content-Type",
                "Accept",
                "Authorization",
                "X-Requested-With",
            ],
            "supports_credentials": True,
            "expose_headers": ["Content-Type"],
            "max_age": 3600,
        }
    },
    supports_credentials=True,
)

# ==================== CONFIGURACIÃ“N DE LA APLICACIÃ“N ====================
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError(
        "âŒ ERROR CRÃTICO: SECRET_KEY no definida en variables de entorno (.env)"
    )

app.config["SECRET_KEY"] = SECRET_KEY
app.config["SESSION_COOKIE_HTTPONLY"] = (
    os.getenv("SESSION_COOKIE_HTTPONLY", "True").lower() == "true"
)
app.config["SESSION_COOKIE_SAMESITE"] = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
app.config["SESSION_COOKIE_SECURE"] = (
    os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"
)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = int(
    os.getenv("MAX_CONTENT_LENGTH", 10 * 1024 * 1024)
)
app.config["ENV"] = os.getenv("FLASK_ENV", "production")
app.config["DEBUG"] = os.getenv("FLASK_DEBUG", "False").lower() == "true"


# ==================== INICIALIZACIÃ“N BASE DE DATOS ====================
def initialize_database():
    """Inicializa y configura la base de datos SQLite"""
    conn = get_db_connection()
    c = conn.cursor()

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS novedades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client TEXT,
            subject TEXT,
            priority TEXT,
            status TEXT,
            priorityText TEXT,
            idType TEXT,
            idNumber TEXT,
            firstName TEXT,
            lastName TEXT,
            nationality TEXT,
            gender TEXT,
            birthDate TEXT,
            phone TEXT,
            department TEXT,
            city TEXT,
            address TEXT,
            neighborhood TEXT,
            email TEXT,
            beneficiaries TEXT,
            eps TEXT,
            arl TEXT,
            arlClass TEXT,
            ccf TEXT,
            pensionFund TEXT,
            ibc REAL,
            description TEXT,
            radicado TEXT,
            solutionDescription TEXT,
            creationDate TEXT,
            updateDate TEXT,
            assignedTo TEXT,
            history TEXT
        );
    """
    )

    # Crear tabla de notificaciones
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            type TEXT DEFAULT 'info',
            link TEXT,
            metadata TEXT,
            is_read INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """
    )

    try:
        c.execute("SELECT ruta_documento_txt FROM credenciales_plataforma LIMIT 1")
    except sqlite3.OperationalError:
        logger.info(
            "âš ï¸  Columna 'ruta_documento_txt' no encontrada. Aplicando migraciÃ³n..."
        )
        c.execute(
            "ALTER TABLE credenciales_plataforma ADD COLUMN ruta_documento_txt TEXT;"
        )
        logger.info(
            "âœ… MigraciÃ³n aplicada: Columna 'ruta_documento_txt' aÃ±adida correctamente."
        )

    conn.commit()
    conn.close()
    logger.info("âœ… Base de datos inicializada correctamente.")


initialize_database()

# ==================== REGISTRO DE BLUEPRINTS ====================

# Registrar el Namespace de 'auth' en el objeto 'api' para que aparezca en Swagger
api.add_namespace(auth_ns, path="/api")

# --- INICIO DE CORRECCIÃ“N (Quitar /api de aquÃ­) ---
# Dejamos que los blueprints (ej. bp_empresas) definan su propia ruta completa.
app.register_blueprint(bp_empresas)
app.register_blueprint(bp_usuarios)
app.register_blueprint(bp_credenciales)
app.register_blueprint(bp_cotizaciones)
app.register_blueprint(bp_incapacidades)
app.register_blueprint(bp_tutelas)
app.register_blueprint(bp_formularios)
app.register_blueprint(bp_pagos)
app.register_blueprint(bp_impuestos)
app.register_blueprint(bp_envio_planillas)
app.register_blueprint(bp_depuraciones)
app.register_blueprint(bp_novedades)
app.register_blueprint(bp_unificacion)
app.register_blueprint(bp_notificaciones)
# --- FIN DE CORRECCIÃ“N ---


# ==================== RUTAS PRINCIPALES ====================


@app.route("/")
def serve_root():  # Renombrado de 'root' a 'serve_root' para evitar conflicto
    """Redirige a la pÃ¡gina de login"""
    return redirect("/ingresoportal.html")


@app.route("/<path:filename>.html")
def serve_html(filename):
    """
    Sirve archivos HTML del sistema
    """
    file_path = os.path.join(BASE_DIR, f"{filename}.html")

    # --- CORRECCIÃ“N DEL TYPO ---
    # Se cambiÃ³ "registropotal" a "registroportal"
    if filename in ["ingresoportal", "registroportal"]:
        if os.path.exists(file_path):
            return send_from_directory(BASE_DIR, f"{filename}.html")
        else:
            logger.error(f"âŒ Archivo HTML de autenticaciÃ³n no encontrado: {file_path}")
            return jsonify({"error": "PÃ¡gina de autenticaciÃ³n no encontrada"}), 404

    if "user_id" not in session:
        logger.warning(f"âš ï¸  Intento de acceso sin sesiÃ³n a: {filename}.html")
        return redirect("/ingresoportal.html")

    if os.path.exists(file_path):
        return send_from_directory(BASE_DIR, f"{filename}.html")
    else:
        logger.error(f"âŒ Archivo HTML no encontrado: {file_path}")
        return jsonify({"error": "PÃ¡gina no encontrada"}), 404


# ==================== RUTA PARA SERVIR ASSETS ====================
@app.route("/assets/<path:relative_path>")
def serve_assets(relative_path):
    """
    Sirve archivos estÃ¡ticos desde la carpeta assets/
    """
    safe_path = os.path.normpath(os.path.join(ASSETS_DIR, relative_path))

    try:
        common = os.path.commonpath([safe_path, ASSETS_DIR])
        if common != os.path.normpath(ASSETS_DIR):
            raise ValueError("Intento de acceso fuera del directorio de assets")
    except ValueError:
        logger.warning(f"ðŸš¨ Intento de directory traversal detectado: {relative_path}")
        return jsonify({"error": "Acceso denegado"}), 403

    if os.path.exists(safe_path) and os.path.isfile(safe_path):
        directory = os.path.dirname(safe_path)
        filename = os.path.basename(safe_path)

        try:
            return send_from_directory(directory, filename)
        except Exception as e:
            logger.error(f"âŒ Error sirviendo asset [{relative_path}]: {e}")
            return jsonify({"error": "Error al servir archivo estÃ¡tico"}), 500
    else:
        logger.warning(f"âš ï¸  Asset no encontrado: {relative_path}")
        logger.debug(f"   Ruta completa intentada: {safe_path}")
        return jsonify({"error": "Archivo no encontrado"}), 404


# ==================== RUTA PARA UPLOADS ====================
@app.route("/uploads/<path:filename>")
@login_required
def serve_uploaded_file(filename):
    """
    Sirve archivos subidos por usuarios (requiere autenticaciÃ³n)
    """
    upload_folder_abs = app.config.get("UPLOAD_FOLDER", UPLOAD_FOLDER)

    if not os.path.isabs(upload_folder_abs):
        upload_folder_abs = os.path.join(BASE_DIR, upload_folder_abs)

    safe_path = os.path.normpath(os.path.join(upload_folder_abs, filename))

    try:
        common = os.path.commonpath([safe_path, upload_folder_abs])
        if common != os.path.normpath(upload_folder_abs):
            raise ValueError("Intento de acceso fuera del directorio de uploads")
    except ValueError:
        logger.warning(f"ðŸš¨ Intento de directory traversal en uploads: {filename}")
        return jsonify({"error": "Acceso denegado"}), 403

    if os.path.exists(safe_path) and os.path.isfile(safe_path):
        directory = os.path.dirname(safe_path)
        base_filename = os.path.basename(safe_path)
        return send_from_directory(directory, base_filename)
    else:
        logger.warning(f"âš ï¸  Upload no encontrado: {filename}")
        return jsonify({"error": "Archivo no encontrado"}), 404


# ==================== MANEJO DE ERRORES ====================


@app.errorhandler(404)
def not_found(error):
    """Maneja errores 404 - Recurso no encontrado"""
    if request.path.startswith("/api/"):
        return jsonify({"error": "Recurso API no encontrado"}), 404
    return "Recurso no encontrado", 404


@app.errorhandler(401)
def unauthorized(error):
    """Maneja errores 401 - No autorizado"""
    if request.path.startswith("/api/"):
        return (
            jsonify({"error": "Acceso no autorizado. Se requiere inicio de sesiÃ³n"}),
            401,
        )
    return redirect("/ingresoportal.html")


@app.errorhandler(500)
def internal_error(error):
    """Maneja errores 500 - Error interno del servidor"""
    logger.error(f"ðŸ’¥ Error interno del servidor: {error}", exc_info=True)

    if request.path.startswith("/api/"):
        return jsonify({"error": "Error interno del servidor"}), 500
    return "Error interno del servidor", 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Maneja errores 413 - Archivo demasiado grande"""
    max_size = app.config["MAX_CONTENT_LENGTH"] / (1024 * 1024)
    return (
        jsonify(
            {
                "error": f"El archivo es demasiado grande. TamaÃ±o mÃ¡ximo: {max_size:.1f} MB"
            }
        ),
        413,
    )


# ==================== INICIO DEL SERVIDOR ====================
if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = app.config["DEBUG"]

    print("\n" + "=" * 70)
    logger.info(f"ðŸš€ Servidor Flask iniciando en http://{host}:{port}")
    logger.info(f"   Modo Debug: {'âœ… Activado' if debug else 'âš ï¸  Desactivado'}")
    logger.info(f"   Entorno: {app.config['ENV']}")
    print("=" * 70 + "\n")

    app.run(host=host, port=port, debug=debug)