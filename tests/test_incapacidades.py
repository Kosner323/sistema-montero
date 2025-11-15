# -*- coding: utf-8 -*-
"""
Tests para el Módulo de Incapacidades - routes/incapacidades.py
========================================================
Día 8 del plan de cobertura de tests.
"""

import pytest

# --- CONSTANTES DE PRUEBA ---
URL_BASE = "/api/incapacidades"

# Datos de prueba para crear incapacidad (usando form-data)
INCAPACIDAD_FORM_DATA = {
    "usuario_id": "123456789",
    "tipo_incapacidad": "Enfermedad General",
    "fecha_inicio": "2025-01-01",
    "dias_incapacidad": "5",
    "diagnostico": "Gripe común",
}


# ----------------------------------------------------------------------
# 1. TESTS DE CREACIÓN (POST) Y VALIDACIÓN
# ----------------------------------------------------------------------


def test_crear_incapacidad_sin_soporte_pdf(logged_in_client, test_db):
    """
    Test 1: Intentar crear incapacidad sin archivo PDF (debe devolver 400).
    """
    # Crear usuario necesario
    test_db.execute(
        """
        INSERT INTO usuarios (numeroId, primerNombre, primerApellido)
        VALUES (?, ?, ?)
    """,
        ("123456789", "Juan", "Pérez"),
    )
    test_db.commit()

    # Intentar crear sin archivo
    response = logged_in_client.post(URL_BASE, data=INCAPACIDAD_FORM_DATA)

    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "PDF" in data["error"]


def test_incapacidad_datos_faltantes_creacion(logged_in_client):
    """
    Test 2: Intentar crear incapacidad sin campos obligatorios (400).
    """
    datos_invalidos = {
        "usuario_id": "123456789",
        "tipo_incapacidad": "Enfermedad General"
        # Faltan: fecha_inicio, dias_incapacidad
    }

    response = logged_in_client.post(URL_BASE, data=datos_invalidos)

    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "Faltan campos obligatorios" in data["error"]


def test_crear_incapacidad_sin_permiso(client):
    """
    Test 3: Intentar crear sin estar loggeado, esperando 401 Unauthorized.
    """
    response = client.post(URL_BASE, data=INCAPACIDAD_FORM_DATA)

    assert response.status_code == 401


# ----------------------------------------------------------------------
# 2. TESTS DE LECTURA (GET) Y FILTROS
# ----------------------------------------------------------------------


def test_listar_incapacidades_exito(logged_in_client, test_db):
    """
    Test 4: Listar todas las incapacidades después de crear una.
    """
    # Crear usuario y empresa
    test_db.execute(
        """
        INSERT INTO empresas (nit, nombre_empresa)
        VALUES (?, ?)
    """,
        ("800555", "Empresa Test SA"),
    )

    test_db.execute(
        """
        INSERT INTO usuarios (numeroId, primerNombre, primerApellido, empresa_nit)
        VALUES (?, ?, ?, ?)
    """,
        ("123456789", "Juan", "Pérez", "800555"),
    )

    # Crear una incapacidad de prueba
    test_db.execute(
        """
        INSERT INTO incapacidades (usuario_id, tipo_incapacidad, fecha_inicio, dias_incapacidad, estado)
        VALUES (?, ?, ?, ?, ?)
    """,
        ("123456789", "Enfermedad General", "2025-01-01", 5, "Registrada"),
    )

    test_db.commit()

    response = logged_in_client.get(URL_BASE)

    # Assertions
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["tipo_incapacidad"] == "Enfermedad General"


def test_listar_incapacidades_vacia(logged_in_client):
    """
    Test 5: Listar incapacidades cuando la tabla está vacía.
    """
    response = logged_in_client.get(URL_BASE)

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_listar_incapacidades_con_filtro_usuario(logged_in_client, test_db):
    """
    Test 6: Listar incapacidades filtrando por usuario_id.
    """
    # Crear usuarios
    test_db.execute(
        """
        INSERT INTO usuarios (numeroId, primerNombre, primerApellido)
        VALUES (?, ?, ?)
    """,
        ("111111111", "Usuario", "Uno"),
    )

    test_db.execute(
        """
        INSERT INTO usuarios (numeroId, primerNombre, primerApellido)
        VALUES (?, ?, ?)
    """,
        ("222222222", "Usuario", "Dos"),
    )

    # Crear incapacidades para cada usuario
    test_db.execute(
        """
        INSERT INTO incapacidades (usuario_id, tipo_incapacidad, fecha_inicio, dias_incapacidad, estado)
        VALUES (?, ?, ?, ?, ?)
    """,
        ("111111111", "Tipo 1", "2025-01-01", 3, "Registrada"),
    )

    test_db.execute(
        """
        INSERT INTO incapacidades (usuario_id, tipo_incapacidad, fecha_inicio, dias_incapacidad, estado)
        VALUES (?, ?, ?, ?, ?)
    """,
        ("222222222", "Tipo 2", "2025-01-02", 7, "Registrada"),
    )

    test_db.commit()

    # Filtrar por usuario_id
    response = logged_in_client.get(f"{URL_BASE}?usuario_id=111111111")

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["usuario_id"] == "111111111"


# --- Fin test_incapacidades.py ---
