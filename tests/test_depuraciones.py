# -*- coding: utf-8 -*-
"""
Tests para el Módulo de Depuraciones - routes/depuraciones.py
========================================================
Día 9 del plan de cobertura de tests.
"""

import pytest

# --- CONSTANTES DE PRUEBA ---
URL_BASE = "/api/depuraciones"

# ----------------------------------------------------------------------
# 1. TESTS DE LECTURA (GET) - PENDIENTES
# ----------------------------------------------------------------------


def test_listar_pendientes_vacia(logged_in_client):
    """
    Test 1: Listar depuraciones pendientes cuando la tabla está vacía.
    """
    response = logged_in_client.get(f"{URL_BASE}/pendientes")

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_listar_pendientes_con_datos(logged_in_client, test_db):
    """
    Test 2: Listar depuraciones pendientes después de crear una.
    """
    # Crear un usuario para tener datos válidos
    test_db.execute(
        """
        INSERT INTO usuarios (numeroId, primerNombre, primerApellido, fechaIngreso)
        VALUES (?, ?, ?, ?)
    """,
        ("123456789", "Juan", "Pérez", "2023-01-01"),
    )

    # Crear una depuración pendiente
    test_db.execute(
        """
        INSERT INTO depuraciones_pendientes (entidad_tipo, entidad_id, entidad_nombre, causa, estado, fecha_sugerida)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        ("usuario", "123456789", "Empleado: Juan Pérez (CC 123456789)", "Inactividad (+1 año)", "Pendiente", "2025-01-14"),
    )

    test_db.commit()

    response = logged_in_client.get(f"{URL_BASE}/pendientes")

    # Assertions
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["entidad_nombre"] == "Empleado: Juan Pérez (CC 123456789)"
    assert data[0]["estado"] == "Pendiente"


# ----------------------------------------------------------------------
# 2. TESTS DE INICIAR PROCESO (POST)
# ----------------------------------------------------------------------


def test_iniciar_proceso_sin_usuarios_antiguos(logged_in_client, test_db):
    """
    Test 3: Iniciar proceso de depuración sin usuarios antiguos.
    """
    # Crear un usuario reciente (no antiguo)
    test_db.execute(
        """
        INSERT INTO usuarios (numeroId, primerNombre, primerApellido, fechaIngreso)
        VALUES (?, ?, ?, ?)
    """,
        ("111111111", "Usuario", "Reciente", "2024-12-01"),
    )

    test_db.commit()

    response = logged_in_client.post(f"{URL_BASE}/iniciar")

    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert data["nuevos_pendientes"] == 0


def test_iniciar_proceso_con_usuarios_antiguos(logged_in_client, test_db):
    """
    Test 4: Iniciar proceso de depuración con usuarios antiguos (+1 año).
    """
    # Crear un usuario antiguo
    test_db.execute(
        """
        INSERT INTO usuarios (numeroId, primerNombre, primerApellido, fechaIngreso)
        VALUES (?, ?, ?, ?)
    """,
        ("222222222", "Usuario", "Antiguo", "2023-01-01"),
    )

    test_db.commit()

    response = logged_in_client.post(f"{URL_BASE}/iniciar")

    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert data["nuevos_pendientes"] >= 1


# ----------------------------------------------------------------------
# 3. TESTS DE RESOLUCIÓN (PUT)
# ----------------------------------------------------------------------


def test_resolver_depuracion_aprobar(logged_in_client, test_db):
    """
    Test 5: Aprobar una depuración (elimina el registro original).
    """
    # Crear usuario
    test_db.execute(
        """
        INSERT INTO usuarios (numeroId, primerNombre, primerApellido, fechaIngreso)
        VALUES (?, ?, ?, ?)
    """,
        ("333333333", "Usuario", "AEliminar", "2023-01-01"),
    )

    # Crear depuración pendiente
    test_db.execute(
        """
        INSERT INTO depuraciones_pendientes (entidad_tipo, entidad_id, entidad_nombre, causa, estado, fecha_sugerida)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (
            "usuario",
            "333333333",
            "Empleado: Usuario AEliminar (CC 333333333)",
            "Inactividad (+1 año)",
            "Pendiente",
            "2025-01-14",
        ),
    )

    test_db.commit()

    # Obtener el ID de la depuración creada
    depuracion = test_db.execute("SELECT id FROM depuraciones_pendientes WHERE entidad_id = ?", ("333333333",)).fetchone()
    depuracion_id = depuracion["id"]

    # Aprobar la depuración
    response = logged_in_client.put(f"{URL_BASE}/{depuracion_id}/resolver", json={"accion": "aprobar"})

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] == True
    assert "Depuración Aprobada" in data["message"]

    # Verificar que el usuario fue eliminado
    usuario = test_db.execute("SELECT * FROM usuarios WHERE numeroId = ?", ("333333333",)).fetchone()
    assert usuario is None

    # Verificar que el estado cambió a 'Aprobada'
    depuracion_actualizada = test_db.execute(
        "SELECT estado FROM depuraciones_pendientes WHERE id = ?", (depuracion_id,)
    ).fetchone()
    assert depuracion_actualizada["estado"] == "Aprobada"


def test_resolver_depuracion_rechazar(logged_in_client, test_db):
    """
    Test 6: Rechazar una depuración (mantiene el registro original).
    """
    # Crear usuario
    test_db.execute(
        """
        INSERT INTO usuarios (numeroId, primerNombre, primerApellido, fechaIngreso)
        VALUES (?, ?, ?, ?)
    """,
        ("444444444", "Usuario", "AConservar", "2023-01-01"),
    )

    # Crear depuración pendiente
    test_db.execute(
        """
        INSERT INTO depuraciones_pendientes (entidad_tipo, entidad_id, entidad_nombre, causa, estado, fecha_sugerida)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (
            "usuario",
            "444444444",
            "Empleado: Usuario AConservar (CC 444444444)",
            "Inactividad (+1 año)",
            "Pendiente",
            "2025-01-14",
        ),
    )

    test_db.commit()

    # Obtener el ID de la depuración creada
    depuracion = test_db.execute("SELECT id FROM depuraciones_pendientes WHERE entidad_id = ?", ("444444444",)).fetchone()
    depuracion_id = depuracion["id"]

    # Rechazar la depuración
    response = logged_in_client.put(f"{URL_BASE}/{depuracion_id}/resolver", json={"accion": "rechazar"})

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] == True
    assert "Depuración Rechazada" in data["message"]

    # Verificar que el usuario NO fue eliminado
    usuario = test_db.execute("SELECT * FROM usuarios WHERE numeroId = ?", ("444444444",)).fetchone()
    assert usuario is not None

    # Verificar que el estado cambió a 'Rechazada'
    depuracion_actualizada = test_db.execute(
        "SELECT estado FROM depuraciones_pendientes WHERE id = ?", (depuracion_id,)
    ).fetchone()
    assert depuracion_actualizada["estado"] == "Rechazada"


def test_resolver_depuracion_sin_accion(logged_in_client, test_db):
    """
    Test 7: Intentar resolver sin especificar 'accion' (debe devolver 400).
    """
    # Crear una depuración pendiente
    test_db.execute(
        """
        INSERT INTO depuraciones_pendientes (entidad_tipo, entidad_id, entidad_nombre, causa, estado, fecha_sugerida)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        ("usuario", "555555555", "Test", "Test", "Pendiente", "2025-01-14"),
    )

    test_db.commit()

    depuracion = test_db.execute("SELECT id FROM depuraciones_pendientes WHERE entidad_id = ?", ("555555555",)).fetchone()
    depuracion_id = depuracion["id"]

    # Intentar resolver sin 'accion'
    response = logged_in_client.put(f"{URL_BASE}/{depuracion_id}/resolver", json={})

    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "accion" in data["error"].lower()


def test_resolver_depuracion_no_existe(logged_in_client):
    """
    Test 8: Intentar resolver una depuración con ID inexistente (debe devolver 404).
    """
    response = logged_in_client.put(f"{URL_BASE}/999999/resolver", json={"accion": "aprobar"})

    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data
    assert "no encontrado" in data["error"].lower()


# --- Fin test_depuraciones.py ---
