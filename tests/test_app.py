# -*- coding: utf-8 -*-
"""
Tests para el Módulo Principal - app.py
=======================================
Verifica la creación de la app, la configuración
y los manejadores de errores básicos.
"""

import pytest


def test_app_creation(app):
    """
    Test 1: Verifica que la 'app' fixture (de conftest.py)
    se crea correctamente y está en modo TESTING.
    """
    assert app is not None
    assert app.config["TESTING"] is True
    assert "test-secret-key" in app.config["SECRET_KEY"]


def test_login_page_loads(client):
    """
    Test 2: Verifica que la PÁGINA de login (ruta /login)
    cargue correctamente.
    """
    response = client.get("/login")
    assert response.status_code == 200
    assert b"login.html" in response.data  # Asumiendo que 'login.html' está en el template


def test_index_redirects_when_not_logged_in(client):
    """
    Test 3: Verifica que la ruta raíz ('/')
    redirija al login si el usuario no está autenticado.
    (El decorador @login_required debe hacer esto).
    """
    response = client.get("/")
    # 302 es el código para "Redirección"
    assert response.status_code == 302
    # Verifica que redirige a la página de login
    assert "/login" in response.location


def test_404_error_handler(client):
    """
    Test 4: Verifica que el manejador de error 404
    funcione para rutas de API.
    """
    response = client.get("/api/ruta-que-no-existe-999")
    assert response.status_code == 404

    data = response.get_json()
    assert "error" in data
    assert "Recurso no encontrado" in data["error"]
