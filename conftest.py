# -*- coding: utf-8 -*-
"""
conftest.py
====================================================
Configuración global de pytest para el Sistema Montero
====================================================
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))


# ==============================================================================
# FIXTURES GLOBALES
# ==============================================================================


@pytest.fixture(scope="session")
def test_env_file():
    """
    Crea un archivo .env temporal para tests.
    Se ejecuta una vez por sesión de testing.
    """
    env_content = """
# Test Environment Variables
SECRET_KEY=test_secret_key_for_testing_12345678901234567890123456789012
ENCRYPTION_KEY=test_encryption_key_base64_encoded_here
FLASK_ENV=testing
FLASK_DEBUG=False
DATABASE_PATH=:memory:
LOG_LEVEL=ERROR
"""

    # Crear archivo temporal
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write(env_content)
        temp_env_file = f.name

    # Establecer variable de entorno para que el sistema use este archivo
    original_env = os.environ.get("ENV_FILE")
    os.environ["ENV_FILE"] = temp_env_file

    yield temp_env_file

    # Cleanup
    os.environ["ENV_FILE"] = original_env if original_env else ""
    try:
        os.unlink(temp_env_file)
    except:
        pass


@pytest.fixture(scope="session")
def test_db_path():
    """
    Crea una base de datos temporal SQLite para tests.
    Se ejecuta una vez por sesión de testing.
    """
    # Crear directorio temporal para la BD
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_database.db")

    yield db_path

    # Cleanup
    try:
        shutil.rmtree(temp_dir)
    except:
        pass


@pytest.fixture
def test_encryption_key():
    """
    Proporciona una clave de encriptación válida para tests.
    """
    # Esta es una clave Fernet válida generada para testing
    return "L9Zr7K3xW5qN8vB4mP2jY6fH1cT0gS9aU7oI4eR6wD8="


@pytest.fixture
def sample_user_data():
    """
    Proporciona datos de usuario de ejemplo para tests.
    """
    return {
        "nombre": "Juan",
        "apellido": "Pérez",
        "email": "juan.perez@ejemplo.com",
        "password": "Password123!",
        "cargo": "Contador",
        "tipo_usuario": "admin",
    }


@pytest.fixture
def sample_credential_data():
    """
    Proporciona datos de credencial de ejemplo para tests.
    """
    return {
        "entidad": "DIAN",
        "usuario": "admin@empresa.com",
        "contrasena": "SecurePass123!",
        "url": "https://muisca.dian.gov.co",
        "notas": "Credenciales de prueba",
    }


@pytest.fixture
def mock_login_attempts():
    """
    Mock del diccionario de intentos de login para tests de rate limiting.
    """
    from auth import LOGIN_ATTEMPTS

    original_attempts = LOGIN_ATTEMPTS.copy()
    LOGIN_ATTEMPTS.clear()

    yield LOGIN_ATTEMPTS

    # Restaurar estado original
    LOGIN_ATTEMPTS.clear()
    LOGIN_ATTEMPTS.update(original_attempts)


# ==============================================================================
# CONFIGURACIÓN DE PYTEST
# ==============================================================================


def pytest_configure(config):
    """
    Configuración que se ejecuta antes de los tests.
    """
    # Agregar markers personalizados
    config.addinivalue_line("markers", "unit: marca tests unitarios")
    config.addinivalue_line("markers", "integration: marca tests de integración")
    config.addinivalue_line("markers", "slow: marca tests lentos")
    config.addinivalue_line("markers", "security: marca tests de seguridad")


def pytest_collection_modifyitems(config, items):
    """
    Modifica la colección de tests antes de ejecutarlos.
    """
    # Agregar marker 'unit' a todos los tests que no tienen marker
    for item in items:
        if not any(item.iter_markers()):
            item.add_marker(pytest.mark.unit)


# ==============================================================================
# HELPERS PARA TESTS
# ==============================================================================


class TestHelper:
    """
    Clase con métodos helper para facilitar los tests.
    """

    @staticmethod
    def create_test_user(db_connection, user_data):
        """
        Crea un usuario de prueba en la base de datos.
        """
        from werkzeug.security import generate_password_hash

        cursor = db_connection.cursor()
        cursor.execute(
            """
            INSERT INTO usuarios (nombre, apellido, email, password, cargo, tipo_usuario)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                user_data["nombre"],
                user_data["apellido"],
                user_data["email"],
                generate_password_hash(user_data["password"]),
                user_data["cargo"],
                user_data["tipo_usuario"],
            ),
        )
        db_connection.commit()
        return cursor.lastrowid

    @staticmethod
    def assert_valid_response(response, expected_status=200):
        """
        Verifica que una respuesta sea válida.
        """
        assert response.status_code == expected_status
        assert response.content_type == "application/json"
        return response.get_json()


@pytest.fixture
def test_helper():
    """
    Proporciona la clase TestHelper para usar en tests.
    """
    return TestHelper()


# ==============================================================================
# CONFIGURACIÓN DE LOGGING PARA TESTS
# ==============================================================================


@pytest.fixture(autouse=True)
def configure_test_logging():
    """
    Configura el logging para tests (se ejecuta automáticamente).
    """
    import logging

    # Silenciar logs durante tests (excepto errores críticos)
    logging.basicConfig(level=logging.ERROR)

    # Silenciar logger específicos
    for logger_name in ["werkzeug", "flask", "app"]:
        logging.getLogger(logger_name).setLevel(logging.ERROR)


# ==============================================================================
# FIXTURES PARA FLASK APP
# ==============================================================================


@pytest.fixture
def app():
    """
    Crea una instancia de la aplicación Flask para tests.
    """
    # Import debe ser aquí para evitar circular imports
    from app import app as flask_app

    # Configurar app para testing
    flask_app.config["TESTING"] = True
    flask_app.config["SECRET_KEY"] = "test-secret-key"
    flask_app.config["WTF_CSRF_ENABLED"] = False

    yield flask_app


@pytest.fixture
def client(app):
    """
    Crea un cliente de prueba para la aplicación Flask.
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    Crea un runner CLI para tests.
    """
    return app.test_cli_runner()


# ==============================================================================
# FIXTURES PARA MANEJO DE SESIONES
# ==============================================================================


@pytest.fixture
def logged_in_client(client, sample_user_data):
    """
    Proporciona un cliente con sesión iniciada.
    """
    # Primero registrar el usuario
    client.post("/auth/register", json=sample_user_data)

    # Luego hacer login
    response = client.post(
        "/auth/login",
        json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"],
        },
    )

    assert response.status_code == 200

    return client
