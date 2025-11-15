# -*- coding: utf-8 -*-
"""
Tests para Módulo de Autenticación - Sistema Montero
=====================================================
Versión: 1.0 - Cobertura completa de auth.py
Coverage Objetivo: 85%+
"""

import sqlite3
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from werkzeug.security import generate_password_hash

# Importaciones del sistema
from routes import auth
from routes.auth import (
    LOCKOUT_TIME,
    LOGIN_ATTEMPTS,
    MAX_LOGIN_ATTEMPTS,
    MIN_PASSWORD_LENGTH,
    check_rate_limit,
    clear_login_attempts,
    is_valid_email,
    register_failed_attempt,
)

# ==============================================================================
# FIXTURES
# ==============================================================================


@pytest.fixture
def clean_login_attempts():
    """Limpia el diccionario de intentos de login antes y después de cada test"""
    LOGIN_ATTEMPTS.clear()
    yield
    LOGIN_ATTEMPTS.clear()


@pytest.fixture
def test_user(test_db):
    """Crea un usuario de prueba en la base de datos"""
    conn = test_db
    password_hash = generate_password_hash("test123456")

    conn.execute(
        """
        INSERT INTO portal_users (nombre, email, password_hash, telefono, fecha_nacimiento)
        VALUES (?, ?, ?, ?, ?)
    """,
        ("Test User", "test@example.com", password_hash, "+573001234567", "1990-01-01"),
    )
    conn.commit()

    return {"email": "test@example.com", "password": "test123456", "nombre": "Test User"}


@pytest.fixture
def auth_client(client, test_db):
    """Cliente de prueba con autenticación"""
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Test User"
    yield client


# ==============================================================================
# TESTS DE VALIDACIÓN DE EMAIL
# ==============================================================================


class TestEmailValidation:
    """Tests para validación de formato de email"""

    def test_email_valido_basico(self):
        """Test: Email válido con formato básico"""
        assert is_valid_email("usuario@example.com") is True

    def test_email_valido_con_puntos(self):
        """Test: Email válido con puntos en nombre de usuario"""
        assert is_valid_email("usuario.nombre@example.com") is True

    def test_email_valido_con_numeros(self):
        """Test: Email válido con números"""
        assert is_valid_email("usuario123@example.com") is True

    def test_email_valido_con_guiones(self):
        """Test: Email válido con guiones"""
        assert is_valid_email("usuario-nombre@example.com") is True

    def test_email_invalido_sin_arroba(self):
        """Test: Email inválido sin @"""
        assert is_valid_email("usuarioexample.com") is False

    def test_email_invalido_sin_dominio(self):
        """Test: Email inválido sin dominio"""
        assert is_valid_email("usuario@") is False

    def test_email_invalido_sin_extension(self):
        """Test: Email inválido sin extensión"""
        assert is_valid_email("usuario@example") is False

    def test_email_vacio(self):
        """Test: Email vacío"""
        assert is_valid_email("") is False

    def test_email_none(self):
        """Test: Email None"""
        assert is_valid_email(None) is False

    def test_email_no_string(self):
        """Test: Email que no es string"""
        assert is_valid_email(12345) is False


# ==============================================================================
# TESTS DE RATE LIMITING
# ==============================================================================


class TestRateLimiting:
    """Tests para el sistema de rate limiting"""

    def test_primer_intento_permitido(self, clean_login_attempts):
        """Test: Primer intento de login siempre es permitido"""
        allowed, error_msg = check_rate_limit("test@example.com")
        assert allowed is True
        assert error_msg is None

    def test_intentos_bajo_limite(self, clean_login_attempts):
        """Test: Intentos bajo el límite máximo son permitidos"""
        email = "test@example.com"

        for i in range(MAX_LOGIN_ATTEMPTS - 1):
            register_failed_attempt(email)

        allowed, error_msg = check_rate_limit(email)
        assert allowed is True
        assert error_msg is None

    def test_bloqueado_al_alcanzar_limite(self, clean_login_attempts):
        """Test: Usuario bloqueado al alcanzar el límite de intentos"""
        email = "test@example.com"

        for i in range(MAX_LOGIN_ATTEMPTS):
            register_failed_attempt(email)

        allowed, error_msg = check_rate_limit(email)
        assert allowed is False
        assert error_msg is not None
        assert "Demasiados intentos" in error_msg

    def test_mensaje_error_incluye_tiempo(self, clean_login_attempts):
        """Test: Mensaje de error incluye tiempo de espera"""
        email = "test@example.com"

        for i in range(MAX_LOGIN_ATTEMPTS):
            register_failed_attempt(email)

        allowed, error_msg = check_rate_limit(email)
        assert "minutos" in error_msg.lower()

    def test_intentos_antiguos_ignorados(self, clean_login_attempts):
        """Test: Intentos antiguos son ignorados después del LOCKOUT_TIME"""
        email = "test@example.com"

        # Simular intentos antiguos
        old_time = datetime.now() - LOCKOUT_TIME - timedelta(minutes=1)
        LOGIN_ATTEMPTS[email] = [old_time] * MAX_LOGIN_ATTEMPTS

        # Verificar que ahora está permitido
        allowed, error_msg = check_rate_limit(email)
        assert allowed is True
        assert error_msg is None

    def test_registro_intento_fallido(self, clean_login_attempts):
        """Test: Registro de intento fallido incrementa contador"""
        email = "test@example.com"

        register_failed_attempt(email)
        assert email in LOGIN_ATTEMPTS
        assert len(LOGIN_ATTEMPTS[email]) == 1

    def test_registro_multiples_intentos(self, clean_login_attempts):
        """Test: Registro de múltiples intentos fallidos"""
        email = "test@example.com"

        for i in range(3):
            register_failed_attempt(email)

        assert len(LOGIN_ATTEMPTS[email]) == 3

    def test_limpiar_intentos(self, clean_login_attempts):
        """Test: Limpiar intentos de login exitoso"""
        email = "test@example.com"

        register_failed_attempt(email)
        register_failed_attempt(email)
        assert email in LOGIN_ATTEMPTS

        clear_login_attempts(email)
        assert email not in LOGIN_ATTEMPTS

    def test_limpiar_intentos_email_inexistente(self, clean_login_attempts):
        """Test: Limpiar intentos de email que no existe"""
        # No debe lanzar error
        clear_login_attempts("noexiste@example.com")


# ==============================================================================
# TESTS DE LOGIN
# ==============================================================================


class TestLogin:
    """Tests para el endpoint de login"""

    def test_login_exitoso(self, client, test_user):
        """Test: Login exitoso con credenciales correctas"""
        response = client.post("/api/login", json={"email": test_user["email"], "password": test_user["password"]})

        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Inicio de sesión exitoso"
        assert "user_name" in data

    def test_login_limpia_intentos_fallidos(self, client, test_user, clean_login_attempts):
        """Test: Login exitoso limpia intentos fallidos previos"""
        email = test_user["email"]

        # Registrar intentos fallidos
        register_failed_attempt(email)
        register_failed_attempt(email)

        # Login exitoso
        response = client.post("/api/login", json={"email": email, "password": test_user["password"]})

        assert response.status_code == 200
        assert email not in LOGIN_ATTEMPTS

    def test_login_usuario_inexistente(self, client, clean_login_attempts):
        """Test: Login falla con usuario inexistente"""
        response = client.post("/api/login", json={"email": "noexiste@example.com", "password": "cualquierpassword"})

        assert response.status_code == 401
        data = response.get_json()
        assert "error" in data
        assert "incorrectos" in data["error"].lower()

    def test_login_password_incorrecta(self, client, test_user, clean_login_attempts):
        """Test: Login falla con contraseña incorrecta"""
        response = client.post("/api/login", json={"email": test_user["email"], "password": "password_incorrecta"})

        assert response.status_code == 401
        data = response.get_json()
        assert "error" in data

    def test_login_registra_intento_fallido(self, client, test_user, clean_login_attempts):
        """Test: Login fallido registra intento"""
        email = test_user["email"]

        response = client.post("/api/login", json={"email": email, "password": "password_incorrecta"})

        assert response.status_code == 401
        assert email in LOGIN_ATTEMPTS
        assert len(LOGIN_ATTEMPTS[email]) == 1

    def test_login_bloqueado_por_rate_limit(self, client, test_user, clean_login_attempts):
        """Test: Login bloqueado después de muchos intentos fallidos"""
        email = test_user["email"]

        # Registrar múltiples intentos fallidos
        for i in range(MAX_LOGIN_ATTEMPTS):
            register_failed_attempt(email)

        # Intentar login
        response = client.post("/api/login", json={"email": email, "password": test_user["password"]})

        assert response.status_code == 429
        data = response.get_json()
        assert "error" in data
        assert "Demasiados intentos" in data["error"]

    def test_login_email_case_insensitive(self, client, test_user):
        """Test: Login funciona con email en mayúsculas"""
        response = client.post("/api/login", json={"email": test_user["email"].upper(), "password": test_user["password"]})

        assert response.status_code == 200

    def test_login_sin_email(self, client):
        """Test: Login falla sin email"""
        response = client.post("/api/login", json={"password": "somepassword"})

        assert response.status_code in [400, 422]

    def test_login_sin_password(self, client, test_user):
        """Test: Login falla sin contraseña"""
        response = client.post("/api/login", json={"email": test_user["email"]})

        assert response.status_code in [400, 422]

    def test_login_email_invalido(self, client):
        """Test: Login falla con email inválido"""
        response = client.post("/api/login", json={"email": "emailinvalido", "password": "somepassword"})

        assert response.status_code in [400, 422]

    def test_login_establece_sesion(self, client, test_user):
        """Test: Login establece variables de sesión correctamente"""
        response = client.post("/api/login", json={"email": test_user["email"], "password": test_user["password"]})

        assert response.status_code == 200

        with client.session_transaction() as sess:
            assert "user_id" in sess
            assert "user_name" in sess
            assert "login_time" in sess


# ==============================================================================
# TESTS DE REGISTRO
# ==============================================================================


class TestRegister:
    """Tests para el endpoint de registro"""

    def test_registro_exitoso(self, client, test_db):
        """Test: Registro exitoso con datos válidos"""
        response = client.post(
            "/api/register",
            json={
                "nombre": "Nuevo Usuario",
                "email": "nuevo@example.com",
                "password": "password123",
                "password_confirm": "password123",
                "telefono": "+573001234567",
                "fecha_nacimiento": "1995-05-15",
            },
        )

        assert response.status_code == 201
        data = response.get_json()
        assert "message" in data
        assert "registrado exitosamente" in data["message"].lower()

    def test_registro_sin_campos_opcionales(self, client, test_db):
        """Test: Registro exitoso sin campos opcionales"""
        response = client.post(
            "/api/register",
            json={
                "nombre": "Usuario Simple",
                "email": "simple@example.com",
                "password": "password123",
                "password_confirm": "password123",
            },
        )

        assert response.status_code == 201

    def test_registro_email_duplicado(self, client, test_user):
        """Test: Registro falla con email duplicado"""
        response = client.post(
            "/api/register",
            json={
                "nombre": "Otro Usuario",
                "email": test_user["email"],  # Email ya existente
                "password": "password123",
                "password_confirm": "password123",
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        # Normalizar la búsqueda para manejar problemas de codificación
        error_msg = data["error"].lower()
        assert "ya" in error_msg and "registrado" in error_msg

    def test_registro_passwords_no_coinciden(self, client):
        """Test: Registro falla si las contraseñas no coinciden"""
        response = client.post(
            "/api/register",
            json={
                "nombre": "Test User",
                "email": "test@example.com",
                "password": "password123",
                "password_confirm": "password456",
            },
        )

        assert response.status_code in [400, 422]
        data = response.get_json()
        assert "error" in data

    def test_registro_password_corta(self, client):
        """Test: Registro falla con contraseña muy corta"""
        response = client.post(
            "/api/register",
            json={"nombre": "Test User", "email": "test@example.com", "password": "123", "password_confirm": "123"},
        )

        assert response.status_code in [400, 422]

    def test_registro_email_invalido(self, client):
        """Test: Registro falla con email inválido"""
        response = client.post(
            "/api/register",
            json={
                "nombre": "Test User",
                "email": "emailinvalido",
                "password": "password123",
                "password_confirm": "password123",
            },
        )

        assert response.status_code in [400, 422]

    def test_registro_sin_nombre(self, client):
        """Test: Registro falla sin nombre"""
        response = client.post(
            "/api/register", json={"email": "test@example.com", "password": "password123", "password_confirm": "password123"}
        )

        assert response.status_code in [400, 422]

    def test_registro_hashea_password(self, client, test_db):
        """Test: Registro hashea la contraseña correctamente"""
        plain_password = "mypassword123"

        response = client.post(
            "/api/register",
            json={
                "nombre": "Test User",
                "email": "hashtest@example.com",
                "password": plain_password,
                "password_confirm": plain_password,
            },
        )

        assert response.status_code == 201

        # Verificar que la contraseña está hasheada en BD
        conn = test_db
        user = conn.execute("SELECT password_hash FROM portal_users WHERE email = ?", ("hashtest@example.com",)).fetchone()

        assert user is not None
        assert user["password_hash"] != plain_password
        assert user["password_hash"].startswith(("pbkdf2:", "scrypt:"))

    def test_registro_email_convertido_a_minusculas(self, client, test_db):
        """Test: Email se convierte a minúsculas al registrar"""
        email_mixto = "TeSt@ExAmPlE.cOm"

        response = client.post(
            "/api/register",
            json={"nombre": "Test User", "email": email_mixto, "password": "password123", "password_confirm": "password123"},
        )

        assert response.status_code == 201

        # Verificar que se guardó en minúsculas
        conn = test_db
        user = conn.execute("SELECT email FROM portal_users WHERE email = ?", (email_mixto.lower(),)).fetchone()

        assert user is not None
        assert user["email"] == email_mixto.lower()


# ==============================================================================
# TESTS DE CHECK_AUTH
# ==============================================================================


class TestCheckAuth:
    """Tests para el endpoint de verificación de autenticación"""

    def test_check_auth_autenticado(self, auth_client):
        """Test: Check auth retorna True para usuario autenticado"""
        response = auth_client.get("/api/check_auth")

        assert response.status_code == 200
        data = response.get_json()
        assert data["authenticated"] is True
        assert "user_name" in data

    def test_check_auth_no_autenticado(self, client):
        """Test: Check auth retorna False para usuario no autenticado"""
        response = client.get("/api/check_auth")

        assert response.status_code == 200
        data = response.get_json()
        assert data["authenticated"] is False


# ==============================================================================
# TESTS DE LOGOUT
# ==============================================================================


class TestLogout:
    """Tests para el endpoint de logout"""

    def test_logout_exitoso(self, auth_client):
        """Test: Logout exitoso limpia la sesión"""
        response = auth_client.post("/api/logout")

        assert response.status_code == 200
        data = response.get_json()
        assert "message" in data

        # Verificar que la sesión se limpió
        with auth_client.session_transaction() as sess:
            assert "user_id" not in sess
            assert "user_name" not in sess

    def test_logout_sin_autenticar(self, client):
        """Test: Logout sin estar autenticado"""
        response = client.post("/api/logout")

        # Debe retornar éxito de todas formas
        assert response.status_code == 200


# ==============================================================================
# TESTS DE SEGURIDAD
# ==============================================================================


class TestSecurity:
    """Tests de seguridad general"""

    def test_password_no_se_retorna_en_login(self, client, test_user):
        """Test: Password no se retorna en la respuesta de login"""
        response = client.post("/api/login", json={"email": test_user["email"], "password": test_user["password"]})

        data = response.get_json()
        assert "password" not in str(data).lower()
        assert "password_hash" not in str(data).lower()

    def test_sanitizacion_sql_injection_login(self, client):
        """Test: Prevención de SQL injection en login"""
        response = client.post("/api/login", json={"email": "'; DROP TABLE portal_users; --", "password": "anypassword"})

        # No debe causar error 500
        assert response.status_code in [400, 401, 422]

    def test_session_permanent_false(self, client, test_user):
        """Test: Sesión no es permanente por defecto"""
        response = client.post("/api/login", json={"email": test_user["email"], "password": test_user["password"]})

        assert response.status_code == 200

        with client.session_transaction() as sess:
            # Verificar que la sesión expira con el navegador
            assert sess.permanent is False or not sess.permanent


# ==============================================================================
# TESTS DE INTEGRACIÓN
# ==============================================================================


class TestIntegration:
    """Tests de integración de flujos completos"""

    def test_flujo_completo_registro_login_logout(self, client, test_db):
        """Test: Flujo completo de registro, login y logout"""
        email = "flujo@example.com"
        password = "password123"

        # 1. Registro
        response = client.post(
            "/api/register",
            json={"nombre": "Usuario Flujo", "email": email, "password": password, "password_confirm": password},
        )
        assert response.status_code == 201

        # 2. Login
        response = client.post("/api/login", json={"email": email, "password": password})
        assert response.status_code == 200

        # 3. Check auth
        response = client.get("/api/check_auth")
        assert response.status_code == 200
        assert response.get_json()["authenticated"] is True

        # 4. Logout
        response = client.post("/api/logout")
        assert response.status_code == 200

        # 5. Verificar que ya no está autenticado
        response = client.get("/api/check_auth")
        assert response.get_json()["authenticated"] is False

    def test_multiples_intentos_fallidos_y_recuperacion(self, client, test_user, clean_login_attempts):
        """Test: Múltiples intentos fallidos y recuperación después de tiempo"""
        email = test_user["email"]

        # Intentos fallidos hasta bloquearse
        for i in range(MAX_LOGIN_ATTEMPTS):
            response = client.post("/api/login", json={"email": email, "password": "wrongpassword"})

        # Verificar que está bloqueado
        response = client.post("/api/login", json={"email": email, "password": test_user["password"]})
        assert response.status_code == 429

        # Simular que pasó el tiempo de bloqueo
        clear_login_attempts(email)

        # Ahora debería poder loguearse
        response = client.post("/api/login", json={"email": email, "password": test_user["password"]})
        assert response.status_code == 200


# ==============================================================================
# EJECUTAR TESTS
# ==============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=auth", "--cov-report=term-missing"])
