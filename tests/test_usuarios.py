# -*- coding: utf-8 -*-
"""
Tests para el Módulo de Usuarios - routes/usuarios.py
"""

import pytest

# Pruebas de API para Usuarios
# (Se asume que el blueprint está en /api/usuarios)


def test_get_usuarios_list_requires_login(client):
    """
    Test 1: Verifica que no se pueda acceder a la lista de usuarios sin iniciar sesión.
    """
    response = client.get("/api/usuarios")
    # Debería redirigir (302) a /login (porque es una API, pero nuestro
    # decorador login_required es inteligente)
    # Ah, no, /api/ devuelve 401. ¡Bien!
    assert response.status_code == 401
    assert "error" in response.get_json()


def test_get_usuarios_list_as_logged_in_user(logged_in_client):
    """
    Test 2: Verifica que un usuario logueado SÍ PUEDA acceder a la lista de usuarios.
    """
    response = logged_in_client.get("/api/usuarios")
    assert response.status_code == 200

    data = response.get_json()
    assert "items" in data
    assert "total_items" in data
    assert data["total_items"] == 0  # La BD de prueba está vacía


def test_create_usuario_requires_login(client):
    """
    Test 3: Verifica que no se pueda crear un usuario sin iniciar sesión.
    """
    response = client.post(
        "/api/usuarios",
        json={
            "nombre_completo": "Test User",
            "email": "test@example.com"
            # ...otros campos
        },
    )
    assert response.status_code == 401


def test_create_usuario_success(logged_in_client, test_db):
    """
    Test 4: Verifica que se pueda crear un nuevo usuario exitosamente.
    """
    response = logged_in_client.post(
        "/api/usuarios",
        json={
            "nombre_completo": "Usuario de Prueba",
            "email": "usuario1@prueba.com",
            "tipo_documento": "CC",
            "numero_documento": "123456",
            "telefono": "3001234567",
            "cargo": "Tester",
            "empresa_nit": "900123456-1",  # Asumimos que la validación de NIT no es estricta
        },
    )

    assert response.status_code == 201  # 201 Created

    data = response.get_json()
    assert "message" in data
    assert "Usuario creado" in data["message"]

    # Verificar que se guardó en la base de datos
    user = test_db.execute("SELECT * FROM usuarios WHERE email = ?", ("usuario1@prueba.com",)).fetchone()
    assert user is not None
    assert user["nombre_completo"] == "Usuario de Prueba"


def test_create_usuario_missing_data(logged_in_client):
    """
    Test 5: Verifica que la API devuelva un error si faltan campos obligatorios.
    """
    response = logged_in_client.post("/api/usuarios", json={"email": "sin_nombre@prueba.com"})

    assert response.status_code == 422  # 422 Unprocessable Entity (Error de Pydantic)
    data = response.get_json()
    assert "error" in data
    assert "details" in data
