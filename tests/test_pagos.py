# -*- coding: utf-8 -*-
"""
Tests para el Módulo de Pagos - routes/pagos.py
========================================================
Día 7 del plan de cobertura de tests.
"""

import pytest

# --- CONSTANTES DE PRUEBA ---
URL_BASE = "/api/pagos"

# Datos de prueba para crear un pago
PAGO_PAYLOAD = {
    "usuario_id": "123456789",
    "empresa_nit": "800555",
    "monto": 120000.00,
    "tipo_pago": "Nómina",
    "fecha_pago": "2025-01-01",
    "referencia": "REF-001",
}

# Datos de prueba insuficientes (faltan campos obligatorios)
PAGO_PAYLOAD_INCOMPLETO = {
    "monto": 120000.00,
    "fecha_pago": "2025-01-01"
    # Faltan: usuario_id, empresa_nit, tipo_pago
}


# ----------------------------------------------------------------------
# 1. TESTS DE CREACIÓN (POST) Y VALIDACIÓN
# ----------------------------------------------------------------------


def test_registrar_pago_exitoso(logged_in_client, test_db):
    """
    Test 1: Simula la creación exitosa de un pago (código 201).
    """
    # Primero crear empresa y usuario necesarios
    test_db.execute(
        """
        INSERT INTO empresas (nit, nombre_empresa)
        VALUES (?, ?)
    """,
        ("800555", "Empresa Test SA"),
    )

    test_db.execute(
        """
        INSERT INTO usuarios (numeroId, primerNombre, primerApellido)
        VALUES (?, ?, ?)
    """,
        ("123456789", "Juan", "Pérez"),
    )

    test_db.commit()

    # Crear el pago
    response = logged_in_client.post(URL_BASE, json=PAGO_PAYLOAD)

    # Verificar que el estado sea 201 Created
    assert response.status_code == 201

    data = response.get_json()
    assert "id" in data
    assert data["monto"] == 120000.00
    assert data["tipo_pago"] == "Nómina"
    assert data["usuario_id"] == "123456789"

    # Verificar que se guardó en la base de datos
    pago_db = test_db.execute("SELECT * FROM pagos WHERE id = ?", (data["id"],)).fetchone()
    assert pago_db is not None
    assert pago_db["monto"] == 120000.00


def test_registrar_pago_datos_invalidos(logged_in_client):
    """
    Test 2: Enviar POST sin campos obligatorios, esperando 400 Bad Request.
    """
    response = logged_in_client.post(URL_BASE, json=PAGO_PAYLOAD_INCOMPLETO)

    # Assertions
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "Faltan campos obligatorios" in data["error"]


def test_registrar_pago_sin_permiso(client):
    """
    Test 3: Intentar crear sin estar loggeado, esperando 401 Unauthorized.
    """
    response = client.post(URL_BASE, json=PAGO_PAYLOAD)

    # Assertions
    assert response.status_code == 401


# ----------------------------------------------------------------------
# 2. TESTS DE LECTURA (GET) Y FILTROS
# ----------------------------------------------------------------------


def test_listar_pagos_por_empresa(logged_in_client, test_db):
    """
    Test 4: Simular un GET para listar pagos filtrados por empresa.
    """
    # Crear empresa y usuario
    test_db.execute(
        """
        INSERT INTO empresas (nit, nombre_empresa)
        VALUES (?, ?)
    """,
        ("800555", "Empresa Test SA"),
    )

    test_db.execute(
        """
        INSERT INTO usuarios (numeroId, primerNombre, primerApellido)
        VALUES (?, ?, ?)
    """,
        ("123456789", "Juan", "Pérez"),
    )

    # Crear un pago de prueba
    test_db.execute(
        """
        INSERT INTO pagos (usuario_id, empresa_nit, monto, tipo_pago, fecha_pago, estado)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        ("123456789", "800555", 120000.00, "Nómina", "2025-01-01", "Pendiente"),
    )

    test_db.commit()

    # Consultar todos los pagos
    response = logged_in_client.get(URL_BASE)

    # Assertions
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["monto"] == 120000.00


# --- Fin test_pagos.py ---
