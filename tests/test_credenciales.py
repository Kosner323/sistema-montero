# -*- coding: utf-8 -*-
"""
Tests para el Módulo de Credenciales - routes/credenciales.py
============================================================
Verifica el CRUD de credenciales y la encriptación/desencriptación.
"""

import pytest

# Pruebas de API para Credenciales
# (Se asume que el blueprint está en /api/credenciales)


@pytest.fixture
def test_credential_data():
    """Datos de prueba para la creación de credenciales."""
    return {
        "plataforma": "DIAN",
        "usuario": "usuario_prueba_dian",
        "contrasena": "SuperSecreta123!",
        "email": "dian@montero.com",
        "url": "https://dian.gov.co",
        "notas": "Credencial de acceso al portal.",
    }


def test_get_credenciales_requires_login(client):
    """
    Test 1: Verifica que no se pueda acceder a la lista de credenciales sin iniciar sesión.
    """
    response = client.get("/api/credenciales")
    assert response.status_code == 401
    assert "error" in response.get_json()


def test_create_credencial_requires_login(client, test_credential_data):
    """
    Test 2: Verifica que no se pueda crear una credencial sin iniciar sesión.
    """
    response = client.post("/api/credenciales", json=test_credential_data)
    assert response.status_code == 401


def test_full_credential_workflow(logged_in_client, test_db, test_credential_data):
    """
    Test 3: Flujo completo: Crear, Listar (encriptado), Desencriptar y Eliminar.
    """
    original_password = test_credential_data["contrasena"]

    # 1. CREAR CREDENCIAL
    response = logged_in_client.post("/api/credenciales", json=test_credential_data)
    assert response.status_code == 201

    # 2. LISTAR Y VERIFICAR ENCRIPTACIÓN
    response = logged_in_client.get("/api/credenciales")
    assert response.status_code == 200

    data = response.get_json()
    assert len(data) == 1
    cred_id = data[0]["id"]

    # El campo 'contrasena' no debe estar en la lista (o debe estar encriptado si se devuelve)
    # Asumimos que routes/credenciales.py NO devuelve la contraseña en la lista GET por seguridad.
    assert "contrasena" not in data[0]

    # 3. DESENCRIPTAR (Ruta sensible)
    # La ruta de desencriptación devuelve la contraseña real.
    response = logged_in_client.get(f"/api/credenciales/{cred_id}/decrypt")
    assert response.status_code == 200

    decrypted_data = response.get_json()
    assert "password" in decrypted_data
    assert decrypted_data["password"] == original_password  # La clave debe coincidir

    # 4. ELIMINAR CREDENCIAL
    response = logged_in_client.delete(f"/api/credenciales/{cred_id}")
    assert response.status_code == 200

    # 5. VERIFICAR ELIMINACIÓN
    response = logged_in_client.get("/api/credenciales")
    assert len(response.get_json()) == 0


def test_update_credential(logged_in_client, test_db, test_credential_data):
    """
    Test 4: Crea una credencial y luego la actualiza.
    """
    # Paso 1: Crear la credencial inicial
    logged_in_client.post("/api/credenciales", json=test_credential_data)

    # Obtener ID
    cred_id = logged_in_client.get("/api/credenciales").get_json()[0]["id"]

    # Paso 2: Actualizar el usuario y la contraseña
    new_data = {"usuario": "nuevo_usuario_cf", "contrasena": "NuevaContrasena321!"}
    response = logged_in_client.put(f"/api/credenciales/{cred_id}", json=new_data)
    assert response.status_code == 200

    # Paso 3: Verificar la nueva contraseña desencriptando
    decrypted_response = logged_in_client.get(f"/api/credenciales/{cred_id}/decrypt")
    assert decrypted_response.get_json()["password"] == "NuevaContrasena321!"

    # Paso 4: Verificar que el campo 'usuario' se actualizó
    list_response = logged_in_client.get("/api/credenciales")
    assert list_response.get_json()[0]["usuario"] == "nuevo_usuario_cf"


def test_delete_non_existent_credential(logged_in_client):
    """
    Test 5: Intenta eliminar una credencial que no existe (debe ser 404).
    """
    response = logged_in_client.delete("/api/credenciales/9999")
    assert response.status_code == 404
    assert "no encontrada" in response.get_json()["error"]
