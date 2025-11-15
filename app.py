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
from flask import Flask, current_app, g, jsonify, render_template, request, session
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect, generate_csrf

from logger import logger

# En la parte de imports:
# Asegúrate de que este import se añadió después de ejecutar el script:
from routes.notificaciones_routes import bp_notificaciones
from utils import login_required  # (CORREGIDO: Importa el decorador)

# ...


def create_app(test_config=None):
    # ... código de configuración de la app

    # === REGISTRO DE BLUEPRINTS ===
    # El archivo 'notificaciones_routes.py' debe estar importado arriba

    # 🔔 Nuevo: Notificaciones
    app.register_blueprint(bp_notificaciones)

    # ... código de manejo de errores
    return app


# --- Definición de Rutas Base ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.getenv("DATABASE_PATH", os.path.join(BASE_DIR, "data", "mi_sistema.db"))
ASSETS_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "assets"))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")  # <- AÑADIR ESTA LÍNEA

# ==============================================================================
# Gestión de la Base de Datos (Funciones Globales)
# ==============================================================================


def get_db_connection():
    """
    Función auxiliar para obtener una conexión a la base de datos.
    Esta función está a nivel de módulo para ser mockeable en tests.

    NOTA: En producción, se usa g.db en lugar de esta función.
    Esta función existe principalmente para compatibilidad con tests legacy.
    """
    db_path = DATABASE_PATH
    if current_app:
        db_path = current_app.config.get("DATABASE_PATH", DATABASE_PATH)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """
    Inicializa la base de datos creando las tablas si no existen.
    Esta función ahora es segura para ser llamada múltiples veces.
    """
    try:
        # Determinar la ruta de la BD (si estamos en testing, la app.config ya tiene la ruta temporal)
        db_path = current_app.config.get("DATABASE_PATH", DATABASE_PATH)

        # Asegura que el directorio 'data' exista (si no es en memoria)
        if db_path != ":memory:":
            os.makedirs(os.path.dirname(db_path), exist_ok=True)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        logger.info(f"Conectado a la base de datos ({db_path}) para inicialización.")

        # --- Creación de Tablas ---
        # Usar 'CREATE TABLE IF NOT EXISTS' para seguridad

        # Tabla de Usuarios del Portal
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS portal_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            telefono TEXT,
            fecha_nacimiento TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ultimo_acceso TIMESTAMP,
            rol TEXT DEFAULT 'usuario'
        );
        """
        )

        # Tabla de Empresas
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_empresa TEXT NOT NULL,
            tipo_identificacion_empresa TEXT,
            nit TEXT UNIQUE NOT NULL,
            direccion_empresa TEXT,
            telefono_empresa TEXT,
            correo_empresa TEXT,
            departamento_empresa TEXT,
            ciudad_empresa TEXT,
            ibc_empresa REAL,
            afp_empresa TEXT,
            arl_empresa TEXT,
            rep_legal_nombre TEXT,
            rep_legal_tipo_id TEXT,
            rep_legal_numero_id TEXT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        )

        # Tabla de Credenciales
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS credenciales_plataforma (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plataforma TEXT NOT NULL,
            usuario TEXT,
            contrasena TEXT,
            email TEXT,
            url TEXT,
            notas TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP,
            creado_por_id INTEGER,
            actualizado_por_id INTEGER,
            FOREIGN KEY (creado_por_id) REFERENCES portal_users(id),
            FOREIGN KEY (actualizado_por_id) REFERENCES portal_users(id)
        );
        """
        )

        # Tabla de Usuarios (empleados/afiliados)
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_completo TEXT,
            email TEXT,
            tipo_documento TEXT,
            numero_documento TEXT,
            telefono TEXT,
            cargo TEXT,
            empresa_nit TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            -- Campos adicionales para formularios
            tipoId TEXT,
            numeroId TEXT,
            primerNombre TEXT,
            segundoNombre TEXT,
            primerApellido TEXT,
            segundoApellido TEXT,
            sexoBiologico TEXT,
            sexoIdentificacion TEXT,
            nacionalidad TEXT,
            fechaNacimiento TEXT,
            paisNacimiento TEXT,
            departamentoNacimiento TEXT,
            municipioNacimiento TEXT,
            direccion TEXT,
            telefonoCelular TEXT,
            telefonoFijo TEXT,
            correoElectronico TEXT,
            comunaBarrio TEXT,
            afpNombre TEXT,
            afpCosto REAL,
            epsNombre TEXT,
            epsCosto REAL,
            arlNombre TEXT,
            arlCosto REAL,
            ccfNombre TEXT,
            ccfCosto REAL,
            administracion TEXT,
            ibc REAL,
            claseRiesgoARL TEXT,
            fechaIngreso TEXT,
            FOREIGN KEY (empresa_nit) REFERENCES empresas(nit),
            UNIQUE (tipoId, numeroId)
        );
        """
        )

        # Tabla de Formularios Importados
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS formularios_importados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            nombre_archivo TEXT NOT NULL,
            ruta_archivo TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        )

        # Tabla de Novedades
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS novedades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client TEXT,
            subject TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL,
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
            description TEXT NOT NULL,
            radicado TEXT,
            solutionDescription TEXT,
            creationDate TEXT DEFAULT (date('now')),
            updateDate TEXT DEFAULT (date('now')),
            assignedTo TEXT DEFAULT 'Sistema',
            history TEXT
        );
        """
        )

        # Tabla de Pagos
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS pagos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id TEXT NOT NULL,
            empresa_nit TEXT NOT NULL,
            monto REAL NOT NULL,
            tipo_pago TEXT NOT NULL,
            fecha_pago TEXT DEFAULT (date('now')),
            referencia TEXT,
            estado TEXT DEFAULT 'Pendiente',
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(numeroId),
            FOREIGN KEY (empresa_nit) REFERENCES empresas(nit)
        );
        """
        )

        # Tabla de Tutelas
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS tutelas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id TEXT NOT NULL,
            motivo TEXT NOT NULL,
            fecha_inicio TEXT NOT NULL,
            estado TEXT DEFAULT 'Registrada',
            descripcion TEXT,
            ruta_soporte_pdf TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(numeroId)
        );
        """
        )

        # Tabla de Incapacidades
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS incapacidades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id TEXT NOT NULL,
            tipo_incapacidad TEXT NOT NULL,
            fecha_inicio TEXT NOT NULL,
            fecha_fin TEXT,
            dias_incapacidad INTEGER,
            diagnostico TEXT,
            estado TEXT DEFAULT 'Registrada',
            ruta_soporte_pdf TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(numeroId)
        );
        """
        )

        # Tabla de Depuraciones Pendientes
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS depuraciones_pendientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entidad_tipo TEXT NOT NULL,
            entidad_id TEXT NOT NULL,
            entidad_nombre TEXT NOT NULL,
            causa TEXT,
            estado TEXT DEFAULT 'Pendiente',
            fecha_sugerida TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        )

        # (Añadir aquí otras tablas 'CREATE TABLE IF NOT EXISTS' según sea necesario)

        conn.commit()
        conn.close()
        logger.info("✅ Base de datos inicializada correctamente.")

    except Exception as e:
        # current_app puede no estar disponible si esto falla muy temprano
        logger.critical(f"Error fatal al inicializar la base de datos: {e}", exc_info=True)
        traceback.print_exc()


# ==============================================================================
# FÁBRICA DE LA APLICACIÓN (APP FACTORY)
# ==============================================================================


def create_app(config_override=None):
    """
    Fábrica de la aplicación Flask.
    """
    app = Flask(__name__, static_folder=None, template_folder=TEMPLATE_DIR)

    # --- Configuración de la App ---
    logger.info("======================================================================")
    logger.info("🚀 CREANDO INSTANCIA DE LA APP MONTERO (MODO TEST AISLADO)")
    logger.info("======================================================================")

    # Cargar variables de entorno
    env_path = os.path.join(BASE_DIR, "_env")
    if os.path.exists(env_path):
        load_dotenv(env_path)

    try:
        # Cargar configuración de seguridad
        app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
        if not app.config["SECRET_KEY"]:
            logger.critical("🚨 FATAL: SECRET_KEY no está definida.")
            raise ValueError("SECRET_KEY no definida en variables de entorno")

        app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=int(os.getenv("SESSION_LIFETIME_MINUTES", 60)))
        app.config["SESSION_COOKIE_SECURE"] = os.getenv("SESSION_COOKIE_SECURE", "True").lower() == "true"
        app.config["SESSION_COOKIE_HTTPONLY"] = os.getenv("SESSION_COOKIE_HTTPONLY", "True").lower() == "true"
        app.config["SESSION_COOKIE_SAMESITE"] = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
        app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER", "uploads")
        app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB
        app.config["DATABASE_PATH"] = os.getenv("DATABASE_PATH", os.path.join(BASE_DIR, "data", "mi_sistema.db"))

        # Aplicar configuraciones de testing (si se proveen)
        if config_override:
            app.config.update(config_override)
            logger.info(f"Configuración de testing aplicada. DATABASE_PATH: {app.config['DATABASE_PATH']}")

        logger.info("Configuración de la aplicación cargada.")

    except Exception as e:
        logger.critical(f"Error fatal durante la configuración de la app: {e}", exc_info=True)

    # --- Configuración de CORS y CSRF ---
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    CSRFProtect(app)
    logger.info("CORS y CSRFProtect inicializados.")

    # --- Importación y Registro de Blueprints (AISLADO PARA TESTING) ---
    from routes.auth import auth_bp
    from routes.credenciales import credenciales_bp
    from routes.depuraciones import bp_depuraciones as depuraciones_bp
    from routes.empresas import empresas_bp
    from routes.formularios import formularios as formularios_bp
    from routes.incapacidades import bp_incapacidades as incapacidades_bp
    from routes.novedades import bp_novedades as novedades_bp
    from routes.pagos import bp_pagos as pagos_bp
    from routes.tutelas import bp_tutelas as tutelas_bp
    from routes.usuarios import usuarios_bp

    # (Comentados temporalmente - Pendientes para días posteriores)
    # from routes.api_docs import api_docs_bp
    # from routes.cotizaciones import cotizaciones_bp
    # from routes.pago_impuestos import pago_impuestos_bp
    # from routes.envio_planillas import envio_planillas_bp

    logger.info("Blueprints (MODO AISLADO) han sido registrados exitosamente.")

    # --- Hooks de la Aplicación (Gestión de Peticiones) ---
    @app.before_request
    def before_request():
        if request.path.startswith("/assets/") or request.path.startswith("/docs/"):
            return
        try:
            if "db" not in g:
                db_path = current_app.config.get("DATABASE_PATH")
                g.db = sqlite3.connect(db_path)
                g.db.row_factory = sqlite3.Row
        except Exception as e:
            logger.error(f"Error al conectar a la BD en before_request: {e}", exc_info=True)
            g.db = None
            return jsonify({"error": "Error de conexión con la base de datos"}), 503
        if "user_id" in session:
            session.permanent = True
            session.modified = True
        if request.method == "GET" and not request.path.startswith("/api/"):
            g.csrf_token = generate_csrf()

    @app.after_request
    def after_request(response):
        if request.path.startswith("/assets/") or request.path.startswith("/docs/"):
            return response
        db = g.pop("db", None)
        if db is not None:
            db.close()
        if hasattr(g, "csrf_token"):
            response.set_cookie(
                "csrf_token",
                g.csrf_token,
                secure=app.config.get("SESSION_COOKIE_SECURE", True),
                httponly=False,
                samesite=app.config.get("SESSION_COOKIE_SAMESITE", "Lax"),
            )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

    # --- Registro de Blueprints (AISLADO PARA TESTING) ---
    try:
        app.register_blueprint(auth_bp)
        app.register_blueprint(usuarios_bp)
        app.register_blueprint(empresas_bp)
        app.register_blueprint(credenciales_bp)
        app.register_blueprint(formularios_bp)
        app.register_blueprint(novedades_bp)
        app.register_blueprint(pagos_bp)
        app.register_blueprint(tutelas_bp)
        app.register_blueprint(incapacidades_bp)
        app.register_blueprint(depuraciones_bp)

        # (Comentados temporalmente - Pendientes para días posteriores)
        # app.register_blueprint(api_docs_bp)
        # app.register_blueprint(cotizaciones_bp)
        # app.register_blueprint(pago_impuestos_bp)
        # app.register_blueprint(envio_planillas_bp)

        logger.info("Todos los blueprints (MODO AISLADO) han sido registrados exitosamente.")
    except Exception as e:
        logger.critical(f"Error al registrar blueprints: {e}", exc_info=True)

    # --- Rutas Principales y Manejadores de Errores ---
    @app.route("/")
    @login_required
    def index():
        return render_template("index.html")

    @app.route("/login")
    def login_page():
        return render_template("login.html")

    @app.route("/assets/<path:filename>")
    def serve_assets(filename):
        # (CORREGIDO: Ruta absoluta a la carpeta de assets)
        return app.send_static_file(os.path.join(ASSETS_DIR, filename))

    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Recurso no encontrado"}), 404
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.critical(f"Error interno del servidor (500): {error}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500

    @app.errorhandler(401)
    def unauthorized_error(error):
        return jsonify({"error": "No autorizado"}), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        return jsonify({"error": "Prohibido"}), 403

    return app


# ==============================================================================
# Punto de Entrada (si se ejecuta 'python app.py')
# ==============================================================================

if __name__ == "__main__":
    app = create_app()  # Crea la app usando la fábrica
    try:
        # Inicializar la base de datos al arrancar (usando el contexto de la app)
        with app.app_context():
            initialize_database()

        host = os.getenv("FLASK_HOST", "127.0.0.1")
        port = int(os.getenv("FLASK_PORT", 5000))
        debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"

        logger.info(f"Iniciando servidor en http://{host}:{port}/ (Debug: {debug_mode})")

        app.run(host=host, port=port, debug=debug_mode)

    except Exception as e:
        logger.critical(f"No se pudo iniciar el servidor: {e}", exc_info=True)
