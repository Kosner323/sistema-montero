# -*- coding: utf-8 -*-
"""
Tests para el Módulo de Novedades - routes/novedades.py
========================================================
Día 7 del plan de cobertura de tests.
"""

import json

import pytest

# --- CONSTANTES DE PRUEBA ---
URL_BASE = "/api/novedades"

# Datos de prueba para crear novedad
NOVEDAD_PAYLOAD = {
    "client": "Empresa Test SA",
    "subject": "Incapacidad General",
    "priority": "Alta",
    "status": "Nuevo",
    "priorityText": "Alta",
    "idType": "CC",
    "idNumber": "123456789",
    "firstName": "Juan",
    "lastName": "Pérez",
    "nationality": "Colombiana",
    "gender": "Masculino",
    "birthDate": "1990-01-01",
    "phone": "3001234567",
    "department": "Bogotá",
    "city": "Bogotá",
    "address": "Calle 123",
    "neighborhood": "Centro",
    "email": "juan.perez@test.com",
    "beneficiaries": [],
    "eps": "Sanitas",
    "arl": "Sura",
    "arlClass": "I",
    "ccf": "Compensar",
    "pensionFund": "Protección",
    "ibc": 1000000.0,
    "description": "Descripción detallada de la novedad de prueba",
    "radicado": "RAD-2025-001",
}

# Datos de prueba insuficientes (faltan campos obligatorios)
NOVEDAD_PAYLOAD_INCOMPLETA = {
    "client": "Empresa Test SA",
    "subject": "Incapacidad General",
    # Faltan: priority, status, description
}


# ----------------------------------------------------------------------
# 1. TESTS DE CREACIÓN (POST) Y VALIDACIÓN
# ----------------------------------------------------------------------


def test_crear_novedad_exitosa(logged_in_client, test_db):
    """
    Test 1: Simula la creación exitosa de una novedad (código 201).
    """
    response = logged_in_client.post(URL_BASE, json=NOVEDAD_PAYLOAD)

    # Verificar que el estado sea 201 Created
    assert response.status_code == 201

    data = response.get_json()
    assert "id" in data
    assert data["client"] == "Empresa Test SA"
    assert data["subject"] == "Incapacidad General"
    assert data["status"] == "Nuevo"

    # Verificar que se guardó en la base de datos
    novedad_db = test_db.execute("SELECT * FROM novedades WHERE id = ?", (data["id"],)).fetchone()
    assert novedad_db is not None
    assert novedad_db["client"] == "Empresa Test SA"


def test_crear_novedad_datos_faltantes(logged_in_client):
    """
    Test 2: Enviar POST sin campos obligatorios, esperando 400 Bad Request.
    """
    response = logged_in_client.post(URL_BASE, json=NOVEDAD_PAYLOAD_INCOMPLETA)

    # Assertions
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "Faltan campos obligatorios" in data["error"]


def test_crear_novedad_sin_permiso(client):
    """
    Test 3: Intentar crear sin estar loggeado, esperando 401 Unauthorized.
    """
    response = client.post(URL_BASE, json=NOVEDAD_PAYLOAD)

    # Assertions
    assert response.status_code == 401


# ----------------------------------------------------------------------
# 2. TESTS DE LECTURA (GET) Y FILTROS
# ----------------------------------------------------------------------


def test_listar_novedades_exitoso(logged_in_client, test_db):
    """
    Test 4: Listar todas las novedades después de crear una.
    """
    # Crear una novedad primero
    test_db.execute(
        """
        INSERT INTO novedades (
            client, subject, priority, status, description, creationDate, updateDate, history
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        ("Empresa Test", "Asunto Test", "Alta", "Nuevo", "Descripción", "2025-01-01", "2025-01-01", "[]"),
    )
    test_db.commit()

    response = logged_in_client.get(URL_BASE)

    # Assertions
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["client"] == "Empresa Test"


def test_obtener_novedad_por_id_no_existe(logged_in_client):
    """
    Test 5: Intentar obtener una novedad que no existe.
    Nota: La API actual no tiene endpoint GET /<id>, solo lista todas.
    Este test verifica que el endpoint base funciona correctamente.
    """
    response = logged_in_client.get(URL_BASE)

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_listar_novedades_vacia(logged_in_client):
    """
    Test 6: Listar novedades cuando la tabla está vacía.
    """
    response = logged_in_client.get(URL_BASE)

    # Assertions
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0  # La BD de prueba está vacía


# ----------------------------------------------------------------------
# 3. TESTS DE MODIFICACIÓN (PUT) Y ELIMINACIÓN
# ----------------------------------------------------------------------


def test_actualizar_novedad_exitoso(logged_in_client, test_db):
    """
    Test 7: Actualizar una novedad existente (PUT).
    """
    # 1. Crear una novedad primero
    test_db.execute(
        """
        INSERT INTO novedades (
            client, subject, priority, status, description,
            creationDate, updateDate, history
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        ("Empresa Test", "Asunto Original", "Media", "Nuevo", "Descripción original", "2025-01-01", "2025-01-01", "[]"),
    )
    test_db.commit()

    novedad_id = test_db.execute("SELECT id FROM novedades ORDER BY id DESC LIMIT 1").fetchone()["id"]

    # 2. Actualizar el estado y prioridad
    datos_actualizados = {
        "status": "En Proceso",
        "priority": "Alta",
        "priorityText": "Alta",
        "newComment": "Se está procesando el caso",
    }
    response = logged_in_client.put(f"{URL_BASE}/{novedad_id}", json=datos_actualizados)

    # 3. Assertions
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "En Proceso"
    assert data["priority"] == "Alta"

    # Verificar que el historial se actualizó
    assert len(data["history"]) > 0


def test_eliminar_novedad_no_encontrada(logged_in_client):
    """
    Test 8: Intentar eliminar una novedad que no existe, esperando 404 Not Found.
    """
    # ID que no existe
    novedad_id_inexistente = 99999

    response = logged_in_client.delete(f"{URL_BASE}/{novedad_id_inexistente}")

    # Assertions
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data
    assert "no encontrada" in data["error"]
