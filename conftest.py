# -*- coding: utf-8 -*-
"""
Configuración de fixtures para pytest - Sistema Montero
=====================================================
Define fixtures compartidas para todas las pruebas.
"""

import os
import sqlite3
import tempfile
from datetime import datetime, timedelta

import pytest

# Configurar ENCRYPTION_KEY para tests ANTES de importar encryption
os.environ.setdefault("ENCRYPTION_KEY", "tZNEUELUZ7lMMN8g4WW1nxpu67mALsZOCBdV5bniow4=")

# (CORREGIDO) Importa la FÁBRICA de la app y el inicializador
from app import create_app, initialize_database
from utils import get_db_connection as original_get_db_connection

# --- Fixtures Principales de la App ---


@pytest.fixture(scope="function")
def app():
    """
    Crea una instancia de app FRESCA y AISLADA para CADA test.
    Usa una base de datos temporal única.
    """

    # 1. Crea un archivo de base de datos temporal y único
    db_fd, db_path = tempfile.mkstemp(suffix=".db")

    # 2. Llama a la fábrica para crear la app
    app = create_app(
        {
            "TESTING": True,
            "DATABASE_PATH": db_path,  # Sobrescribe la BD con la temporal
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "test-secret-key",
        }
    )

    # 3. Inicializa el schema en esa base de datos temporal
    with app.app_context():
        initialize_database()

    # 4. Entrega la app configurada al test
    yield app

    # 5. Limpieza: Cierra todas las conexiones y elimina el archivo de la BD después del test
    # Cerrar cualquier conexión en g.db que pueda estar abierta
    with app.app_context():
        from flask import g

        db = g.pop("db", None)
        if db is not None:
            try:
                db.close()
            except:
                pass

    # Pequeña pausa para asegurar que Windows libere el archivo
    import time

    time.sleep(0.1)

    os.close(db_fd)
    try:
        os.unlink(db_path)
    except PermissionError:
        # En Windows, a veces el archivo sigue bloqueado brevemente
        time.sleep(0.2)
        try:
            os.unlink(db_path)
        except:
            pass  # Si aún falla, el archivo temporal se limpiará eventualmente


@pytest.fixture(scope="function")
def client(app):
    """
    Un cliente de prueba para la app.
    Configura g.db automáticamente para cada request en el contexto de testing.
    """
    client = app.test_client()

    # Hook para configurar g.db antes de cada request en testing
    @app.before_request
    def setup_test_db():
        from flask import g

        if not hasattr(g, "db") or g.db is None:
            g.db = sqlite3.connect(app.config["DATABASE_PATH"])
            g.db.row_factory = sqlite3.Row

    return client


@pytest.fixture(scope="function")
def test_db(app):
    """
    Provee una conexión a la base de datos de PRUEBA TEMPORAL.
    """
    # Se conecta a la MISMA base de datos temporal que usa la app
    conn = sqlite3.connect(app.config["DATABASE_PATH"])
    conn.row_factory = sqlite3.Row

    yield conn  # Provee la conexión al test

    conn.close()  # Cierra la conexión al finalizar


@pytest.fixture
def runner(app):
    """Un runner para ejecutar comandos CLI de Flask."""
    return app.test_cli_runner()


# --- Fixtures de Mocking (Simulación) ---


@pytest.fixture
def mock_login_attempts(mocker):
    """Mockea el diccionario LOGIN_ATTEMPTS en routes.auth"""
    # Importa aquí para evitar importación circular en el nivel superior
    from routes.auth import LOGIN_ATTEMPTS

    # Usa patch.object si LOGIN_ATTEMPTS es un atributo de módulo
    # O patch si es un objeto importado
    mocker.patch.dict(LOGIN_ATTEMPTS, {}, clear=True)
    yield LOGIN_ATTEMPTS


@pytest.fixture
def logged_in_client(client, app):
    """Crea un cliente que ya ha iniciado sesión"""
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Test User"
        sess["login_time"] = datetime.now().isoformat()
    return client


# --- Fixtures de Datos de Prueba ---


@pytest.fixture
def sample_user_data():
    """Datos de muestra para un nuevo usuario"""
    return {
        "nombre": "Test User",
        "email": "test@example.com",
        "password": "Password123!",
        "password_confirm": "Password123!",
        "telefono": "3001234567",
        "fecha_nacimiento": "1990-01-01",
    }


@pytest.fixture
def sample_credential_data():
    """Datos de muestra para una nueva credencial"""
    return {
        "plataforma": "Test Platform",
        "usuario": "test_user",
        "contrasena": "TestPassword123!",
        "email": "test_user@platform.com",
        "url": "https://platform.com",
        "notas": "Some test notes",
    }


# --- Fixtures de Ayuda (Helpers) ---


@pytest.fixture
def test_helper():
    """Una clase de ayuda con métodos útiles para tests"""

    class Helper:
        @staticmethod
        def get_user_by_email(email, db):
            """Obtiene un usuario de la BD por su email"""
            user = db.execute("SELECT * FROM portal_users WHERE email = ?", (email,)).fetchone()
            return user

        @staticmethod
        def get_all_users(db):
            """Obtiene todos los usuarios de la BD"""
            users = db.execute("SELECT * FROM portal_users").fetchall()
            return users

        @staticmethod
        def create_test_user(db, email="test@example.com", password="password123"):
            """Inserta un usuario de prueba directamente en la BD"""
            from werkzeug.security import generate_password_hash

            hashed_password = generate_password_hash(password)
            cursor = db.execute(
                "INSERT INTO portal_users (nombre, email, password_hash) VALUES (?, ?, ?)",
                ("Test User", email, hashed_password),
            )
            db.commit()
            return cursor.lastrowid

    return Helper()
