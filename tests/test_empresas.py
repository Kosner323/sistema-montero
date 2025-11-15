# -*- coding: utf-8 -*-
"""
Tests para el Módulo de Empresas - routes/empresas.py
"""

import pytest

# Pruebas de API para Empresas
# (Se asume que el blueprint está en /api/empresas)


def test_get_empresas_list_requires_login(client):
    """
    Test 1: Verifica que no se pueda acceder a la lista de empresas sin iniciar sesión.
    """
    response = client.get("/api/empresas")
    assert response.status_code == 401  # API debe devolver 401
    assert "error" in response.get_json()


def test_get_empresas_list_as_logged_in_user(logged_in_client):
    """
    Test 2: Verifica que un usuario logueado SÍ PUEDA acceder a la lista de empresas.
    """
    response = logged_in_client.get("/api/empresas")
    assert response.status_code == 200

    data = response.get_json()
    assert "items" in data
    assert "total_items" in data
    assert data["total_items"] == 0  # La BD de prueba está vacía


def test_create_empresa_requires_login(client):
    """
    Test 3: Verifica que no se pueda crear una empresa sin iniciar sesión.
    """
    response = client.post(
        "/api/empresas",
        json={
            "nit": "900123456-1",
            "nombre_empresa": "Empresa de Prueba SA",
            # ...otros campos
        },
    )
    assert response.status_code == 401


def test_create_empresa_success(logged_in_client, test_db):
    """
    Test 4: Verifica que se pueda crear una nueva empresa exitosamente.
    """
    # (El modelo Pydantic real se llama 'EmpresaCreate' en validation_models.py)
    test_data = {
        "nit": "900123456-1",
        "nombre_empresa": "Empresa de Prueba SA",
        "email": "contacto@empresa.com",
        "telefono": "3001234567",
        "direccion": "Calle Falsa 123",
        "ciudad": "Bogota",
    }

    response = logged_in_client.post("/api/empresas", json=test_data)

    assert response.status_code == 201  # 201 Created

    data = response.get_json()
    assert "message" in data
    assert "Empresa creada" in data["message"]

    # Verificar que se guardó en la base de datos
    # Nota: El validador limpia el NIT, removiendo guiones (900123456-1 → 9001234561)
    empresa = test_db.execute("SELECT * FROM empresas WHERE nit = ?", ("9001234561",)).fetchone()
    assert empresa is not None
    assert empresa["nombre_empresa"] == "Empresa de Prueba SA"  # El campo se llama 'nombre_empresa' en la BD


def test_create_empresa_missing_data(logged_in_client):
    """
    Test 5: Verifica que la API devuelva un error si faltan campos obligatorios.
    """
    response = logged_in_client.post("/api/empresas", json={"nit": "12345"})  # Razón social es obligatoria

    assert response.status_code == 422  # 422 Unprocessable Entity (Error de Pydantic)
    data = response.get_json()
    assert "error" in data
    assert "details" in data
