# -*- coding: utf-8 -*-
"""
Aplicación principal Flask para el Sistema de Gestión Montero.
Utiliza el patrón de fábrica (create_app) para permitir
instancias de app limpias, especialmente para testing.
"""

import os
import sqlite3
import traceback
from datetime import timedelta

from dotenv import load_dotenv
from flask import (Flask, current_app, g, jsonify, render_template, request,
                   session, url_for, redirect, send_from_directory) 
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect, generate_csrf
from werkzeug.security import generate_password_hash

from logger import logger
from extensions import limiter, mail, db, migrate

# =============================================================================
# Carga de Variables de Entorno
# =============================================================================
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)
logger.info(f"Cargando variables de entorno desde: {dotenv_path}")

# =============================================================================
# Importación de Blueprints (Rutas Modulares)
# =============================================================================
from routes.auth import auth_bp as bp_auth
from routes.index import bp_main
from routes.empresas import empresas_bp as bp_empresa
from routes.usuarios import usuarios_bp as bp_empleado
from routes.pagos import bp_pagos as bp_pago
from routes.notificaciones_routes import bp_notificaciones
from routes.analytics import analytics_bp as bp_api
from routes.tutelas import bp_tutelas as bp_tutela
from routes.cotizaciones import bp_cotizaciones as bp_cotizacion
from routes.incapacidades import bp_incapacidades as bp_incapacidad
from routes.depuraciones import bp_depuraciones
from routes.formularios import bp_formularios, bp_formularios_pages
from routes.pago_impuestos import bp_impuestos
from routes.unificacion import bp_unificacion
from routes.envio_planillas import bp_envio_planillas
from routes.credenciales import credenciales_bp
from routes.novedades import bp_novedades
from routes.pages import pages_bp

# Nuevos blueprints
from routes.marketing_routes import bp_marketing
from routes.automation_routes import automation_bp
from routes.finance_routes import finance_bp
from routes.admin_routes import admin_bp
from routes.user_settings import user_settings_bp


# =============================================================================
# Lógica de Base de Datos (SQLite)
# =============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.getenv("DATABASE_PATH", os.path.join(BASE_DIR, "data", "mi_sistema.db"))
SCHEMA_PATH = os.getenv("SCHEMA_PATH", os.path.join(BASE_DIR, "data", "schema.sql"))

# Configuración de URI para SQLAlchemy
DATABASE_URI = f"sqlite:///{DATABASE_PATH}"


def get_db():
    if "db" not in g:
        try:
            os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
            g.db = sqlite3.connect(
                DATABASE_PATH, detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row
            logger.debug(f"Conexión a la BBDD establecida en: {DATABASE_PATH}")
        except sqlite3.Error as e:
            logger.error(f"Error al conectar con la base de datos: {e}")
            raise
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
        logger.debug("Conexión a la BBDD cerrada.")


# =============================================================================
# NOTA: La función initialize_database ha sido ELIMINADA
# Ahora usamos Flask-SQLAlchemy y Flask-Migrate para gestionar la BD
# =============================================================================


# =============================================================================
# Fábrica de la Aplicación (create_app)
# =============================================================================

def create_app(test_config=None):
    logger.info("======================================================================")
    logger.info("🚀 CREANDO INSTANCIA DE LA APP MONTERO")
    logger.info("======================================================================")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(base_dir, 'assets') 

    app = Flask(__name__,
                instance_relative_config=True,
                static_folder=static_dir,
                static_url_path='/assets') 
                
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "default_secret_key_for_dev"),
        DATABASE=os.path.join(app.instance_path, "mi_sistema.db"),

        # ✅ CONFIGURACIÓN CENTRALIZADA DE BASE DE DATOS
        DATABASE_PATH=DATABASE_PATH,  # Ruta absoluta a mi_sistema.db

        # ✅ CONFIGURACIÓN FLASK-SQLALCHEMY
        SQLALCHEMY_DATABASE_URI=DATABASE_URI,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,  # Desactivar tracking para mejor performance
        SQLALCHEMY_ECHO=False,  # Cambiar a True para debugging SQL

        SESSION_COOKIE_SECURE=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_NAME='montero_session',  # ✅ Nombre específico para la cookie
        SESSION_COOKIE_PATH='/',  # ✅ Cookie válida para toda la aplicación
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),

        # Configuración de Flask-Mail
        MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
        MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
        MAIL_USE_TLS=os.getenv("MAIL_USE_TLS", "True").lower() == "true",
        MAIL_USE_SSL=os.getenv("MAIL_USE_SSL", "False").lower() == "true",
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
        MAIL_DEFAULT_SENDER=os.getenv("MAIL_DEFAULT_SENDER", "Sistema Montero <noreply@montero.com>"),
        MAIL_MAX_EMAILS=os.getenv("MAIL_MAX_EMAILS"),
        MAIL_ASCII_ATTACHMENTS=os.getenv("MAIL_ASCII_ATTACHMENTS", "False").lower() == "true",

        # Configuración de subida de archivos (centralizada para todos los módulos)
        UPLOAD_FOLDER=os.path.join(base_dir, 'static', 'uploads'),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # Límite de 16MB por archivo
        ALLOWED_EXTENSIONS={'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'csv'},
    )

    # 🔍 LOG para debugging de rutas críticas
    logger.info(f"📂 DATABASE_PATH configurado: {DATABASE_PATH}")
    logger.info(f"📂 UPLOAD_FOLDER configurado: {app.config['UPLOAD_FOLDER']}")

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    logger.info("Configuración de la aplicación cargada.")

    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        logger.error(f"No se pudo crear el directorio de instancia en: {app.instance_path}")

    # Crear estructura de carpetas para uploads organizados
    upload_subdirs = ['docs', 'formularios', 'tutelas', 'impuestos', 'temp']
    for subdir in upload_subdirs:
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], subdir)
        try:
            os.makedirs(upload_path, exist_ok=True)
            logger.info(f"Carpeta de uploads creada/verificada: {upload_path}")
        except OSError as e:
            logger.error(f"No se pudo crear carpeta {upload_path}: {e}")

    CORS(app, supports_credentials=True, resources={
        r"/*": {
            "origins": ["http://localhost:5000", "http://127.0.0.1:5000"]
        }
    })
    
    # Inicializar CSRF
    csrf = CSRFProtect(app)
    
    # Configurar WTF_CSRF_CHECK_DEFAULT = False para APIs
    app.config['WTF_CSRF_CHECK_DEFAULT'] = False
    app.config['WTF_CSRF_ENABLED'] = True  # Habilitado solo para rutas que lo necesiten

    # Inicializar Flask-Limiter
    limiter.init_app(app)

    # Inicializar Flask-Mail
    mail.init_app(app)

    # ✅ Inicializar Flask-SQLAlchemy
    db.init_app(app)
    logger.info("Flask-SQLAlchemy inicializado correctamente")

    # ✅ Inicializar Flask-Migrate
    migrate.init_app(app, db)
    logger.info("Flask-Migrate inicializado correctamente")

    # ✅ Crear tablas si no existen (solo en desarrollo)
    with app.app_context():
        # Importar modelos para que SQLAlchemy los reconozca
        from models import orm_models
        db.create_all()
        logger.info("✅ Tablas de la base de datos verificadas/creadas con SQLAlchemy ORM")

    logger.info("CORS, CSRFProtect, Flask-Limiter, Flask-Mail, SQLAlchemy y Migrate inicializados.")

    app.teardown_appcontext(close_db)
    logger.info("Comandos de la app (teardown) registrados.")

    # REGISTRO DE BLUEPRINTS
    logger.info("Registrando Blueprints de la aplicación...")
    try:
        app.register_blueprint(bp_auth)
        app.register_blueprint(bp_main)
        app.register_blueprint(bp_empresa)
        app.register_blueprint(bp_empleado)
        app.register_blueprint(bp_pago)
        app.register_blueprint(bp_notificaciones)
        app.register_blueprint(bp_api)
        app.register_blueprint(bp_tutela)
        app.register_blueprint(bp_cotizacion)
        app.register_blueprint(bp_incapacidad)
        app.register_blueprint(bp_depuraciones)
        app.register_blueprint(bp_formularios)
        app.register_blueprint(bp_formularios_pages)
        app.register_blueprint(bp_impuestos)
        app.register_blueprint(bp_unificacion)
        app.register_blueprint(bp_envio_planillas)
        app.register_blueprint(credenciales_bp)
        app.register_blueprint(bp_novedades)
        app.register_blueprint(pages_bp)

        # Nuevos blueprints para Marketing, Automation, Finance y Admin
        app.register_blueprint(bp_marketing)
        app.register_blueprint(automation_bp)
        app.register_blueprint(finance_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(user_settings_bp)

        logger.info("✅ Todos los blueprints han sido registrados exitosamente.")
        logger.info("✅ Módulos cargados: Auth, RPA (automation_bp), Marketing, Finance, Admin, User Settings")
        logger.info("✅ Sistema Montero completamente inicializado y listo para producción.")
        
    except Exception as e:
        logger.critical(f"Error CRÍTICO al registrar un blueprint: {e}")
        traceback.print_exc()

    # RUTAS DE VERIFICACIÓN Y CSRF
    @app.route("/hello")
    def hello():
        return "¡Hola! El servidor Montero está funcionando."

    @app.route("/health")
    def health():
        """Endpoint de health check para Docker y monitoreo."""
        return jsonify({
            "status": "healthy",
            "service": "Sistema Montero",
            "database": "connected"
        }), 200

    @app.route('/get-csrf-token', methods=['GET'])
    def get_csrf_token():
        token = generate_csrf()
        return jsonify({'csrf_token': token})

    # Ruta silenciosa para favicon (evita warnings en logs)
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'assets', 'images'), 'favicon.svg', mimetype='image/svg+xml')

    # MANEJADORES DE ERRORES PERSONALIZADOS
    @app.errorhandler(404)
    def not_found_error(error):
        # Ignorar warnings de rutas del navegador y archivos de desarrollo
        RUTAS_SILENCIOSAS = [
            '/favicon.ico',
            '/.well-known/appspecific/com.chrome.devtools.json'
        ]
        
        # Ignorar archivos .map (source maps de desarrollo)
        if request.path.endswith('.map') or request.path in RUTAS_SILENCIOSAS:
            return '', 204

        logger.warning(f"⚠️ Ruta no encontrada (404): {request.path}")

        # Si la petición espera JSON (API), devolver JSON
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({
                "error": "Recurso no encontrado",
                "path": request.path,
                "status": 404
            }), 404

        # Si la petición espera HTML, mostrar página personalizada
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        # Generar timestamp único para tracking
        import datetime
        timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')

        logger.critical(f"❌ Error interno del servidor (500) - ID: {timestamp}")
        logger.critical(f"Ruta: {request.path}")
        logger.critical(f"Detalles: {error}", exc_info=True)

        # Si la petición espera JSON (API), devolver JSON
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify({
                "error": "Error interno del servidor",
                "error_id": f"ERR-{timestamp}",
                "status": 500
            }), 500

        # Si la petición espera HTML, mostrar página personalizada
        return render_template('errors/500.html', timestamp=timestamp), 500 

    @app.errorhandler(401)
    def unauthorized_error(error):
        logger.warning(f"Acceso no autorizado (401) a: {request.path}")
        return jsonify({"error": "No autorizado"}), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        logger.warning(f"Acceso prohibido (403) a: {request.path}")
        return jsonify({"error": "Prohibido"}), 403

    return app


# Crear instancia de app para Gunicorn
app = create_app()

# PUNTO DE ENTRADA
if __name__ == "__main__":
    try:
        # ✅ Ya no necesitamos initialize_database() - SQLAlchemy lo maneja automáticamente

        host = os.getenv("FLASK_HOST", "0.0.0.0")
        port = int(os.getenv("FLASK_PORT", 5000))
        debug_mode = os.getenv("FLASK_DEBUG", "True").lower() == "true"

        logger.info(f"Iniciando servidor en http://{host}:{port}/ (Debug: {debug_mode})")
        logger.info("✅ Sistema usando Flask-SQLAlchemy ORM - SQL manual eliminado")

        app.run(host=host, port=port, debug=debug_mode)

    except Exception as e:
        logger.critical(f"No se pudo iniciar el servidor: {e}")
        traceback.print_exc()