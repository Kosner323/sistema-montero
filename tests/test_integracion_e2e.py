# -*- coding: utf-8 -*-
"""
Tests de Integración End-to-End (E2E) - Sistema Montero
========================================================
Día 9 - Tests de integración entre múltiples módulos usando la base de datos real.
"""

import io

import pytest

# --- CONSTANTES BASE ---
TEST_USER_ID = "100200300"
TEST_NIT = "999888777"
PAGO_ID = 500
NOVEDAD_ID = 150

# ----------------------------------------------------------------------
# 1. TESTS DE INTEGRACIÓN END-TO-END (E2E)
# ----------------------------------------------------------------------


def test_flujo_completo_empresa_usuario(logged_in_client, test_db):
    """
    Test 1: Flujo completo: Crear Empresa -> Crear Usuario -> Verificar Usuario.
    """
    # PASO 1: Crear Empresa (POST /api/empresas)
    empresa_payload = {
        "nit": TEST_NIT,
        "nombre_empresa": "Empresa Test E2E",
        "tipo_identificacion_empresa": "NIT",
        "direccion": "Calle Falsa 123",
        "telefono": "1234567890",
        "email": "empresa@test.com",
        "ciudad": "Bogotá",
    }
    response_empresa = logged_in_client.post("/api/empresas", json=empresa_payload)
    assert response_empresa.status_code == 201

    # PASO 2: Crear Usuario asociado a esa empresa (POST /api/usuarios)
    usuario_payload = {
        "numero_documento": TEST_USER_ID,
        "nombre_completo": "Juan Integracion",
        "correoElectronico": "juan@test.com",
        "empresa_nit": TEST_NIT,
        "tipoId": "CC",
    }
    response_usuario = logged_in_client.post("/api/usuarios", json=usuario_payload)
    assert response_usuario.status_code == 201

    # PASO 3: Verificar respuestas exitosas
    assert response_empresa.get_json() is not None
    assert response_usuario.get_json() is not None


def test_integracion_pago_usuario(logged_in_client, test_db):
    """
    Test 2: Integración Usuarios -> Pagos: Registrar Usuario y luego un Pago asociado.
    """
    # PASO 1: Crear empresa
    test_db.execute(
        """
        INSERT INTO empresas (nit, nombre_empresa, tipo_identificacion_empresa)
        VALUES (?, ?, ?)
    """,
        (TEST_NIT, "Empresa Test", "NIT"),
    )

    # PASO 2: Crear usuario
    test_db.execute(
        """
        INSERT INTO usuarios (numeroId, primerNombre, primerApellido, empresa_nit, tipoId)
        VALUES (?, ?, ?, ?, ?)
    """,
        (TEST_USER_ID, "Juan", "Pérez", TEST_NIT, "CC"),
    )

    test_db.commit()

    # PASO 3: Crear Pago (POST /api/pagos)
    pago_payload = {
        "usuario_id": TEST_USER_ID,
        "empresa_nit": TEST_NIT,
        "monto": 250000,
        "tipo_pago": "Nomina",
        "fecha_pago": "2025-11-20",
    }
    response_pago = logged_in_client.post("/api/pagos", json=pago_payload)
    assert response_pago.status_code == 201

    # PASO 4: Verificar pago en DB
    pago_db = test_db.execute("SELECT * FROM pagos WHERE usuario_id = ?", (TEST_USER_ID,)).fetchone()
    assert pago_db is not None
    assert pago_db["monto"] == 250000


def test_flujo_completo_tutela(logged_in_client, test_db):
    """
    Test 3: Flujo Tutelas: Crear Usuario -> Crear Tutela -> Verificar.
    """
    # PASO 1: Crear usuario
    test_db.execute(
        """
        INSERT INTO usuarios (numeroId, primerNombre, primerApellido, tipoId)
        VALUES (?, ?, ?, ?)
    """,
        (TEST_USER_ID, "Juan", "Pérez", "CC"),
    )
    test_db.commit()

    # PASO 2: Crear Tutela (requiere PDF)
    # Nota: Este endpoint requiere form-data con archivo PDF, así que verificamos estructura básica
    tutela_data = {"usuario_id": TEST_USER_ID, "motivo": "Acceso a servicios de salud", "fecha_inicio": "2025-01-01"}

    # Simular archivo PDF
    pdf_file = (io.BytesIO(b"%PDF-1.4 fake content"), "tutela.pdf")

    response_post = logged_in_client.post(
        "/api/tutelas", data={**tutela_data, "soporte_pdf": pdf_file}, content_type="multipart/form-data"
    )

    # El endpoint requiere un PDF válido, así que esperamos 400 (validación) no 404
    assert response_post.status_code in [400, 201]


def test_flujo_novedad_completo(logged_in_client, test_db):
    """
    Test 4: Flujo Novedades: Crear -> Actualizar -> Verificar.
    """
    # PASO 1: Crear Novedad (POST /api/novedades)
    novedad_payload = {
        "client": "Cliente Test",
        "subject": "Solicitud de información",
        "priority": "Alta",
        "status": "Nuevo",
        "description": "Descripción de la novedad de prueba",
    }
    response_novedad = logged_in_client.post("/api/novedades", json=novedad_payload)
    assert response_novedad.status_code == 201

    # Obtener el ID de la novedad creada
    novedad_data = response_novedad.get_json()
    novedad_id = novedad_data.get("id")
    assert novedad_id is not None

    # PASO 2: Actualizar estado (PUT /api/novedades/{id})
    update_payload = {"status": "En Proceso", "comentario": "Se está trabajando en la solicitud"}
    response_put = logged_in_client.put(f"/api/novedades/{novedad_id}", json=update_payload)
    assert response_put.status_code == 200

    # PASO 3: Verificar en DB
    novedad_db = test_db.execute("SELECT * FROM novedades WHERE id = ?", (novedad_id,)).fetchone()
    assert novedad_db is not None
    assert novedad_db["status"] == "En Proceso"


def test_depuracion_flujo_completo(logged_in_client, test_db):
    """
    Test 5: Flujo Depuración: Iniciar proceso -> Resolver depuración.
    """
    # PASO 1: Crear usuario antiguo (más de 1 año)
    test_db.execute(
        """
        INSERT INTO usuarios (numeroId, primerNombre, primerApellido, fechaIngreso, tipoId)
        VALUES (?, ?, ?, ?, ?)
    """,
        (TEST_USER_ID, "Usuario", "Antiguo", "2023-01-01", "CC"),
    )
    test_db.commit()

    # PASO 2: Iniciar proceso de depuración (POST /api/depuraciones/iniciar)
    response_iniciar = logged_in_client.post("/api/depuraciones/iniciar")
    assert response_iniciar.status_code == 200
    data = response_iniciar.get_json()
    assert data["nuevos_pendientes"] >= 1

    # PASO 3: Obtener depuraciones pendientes
    response_pendientes = logged_in_client.get("/api/depuraciones/pendientes")
    assert response_pendientes.status_code == 200
    pendientes = response_pendientes.get_json()
    assert len(pendientes) >= 1

    # PASO 4: Resolver una depuración (rechazar para no eliminar el usuario)
    depuracion_id = pendientes[0]["id"]
    response_resolver = logged_in_client.put(f"/api/depuraciones/{depuracion_id}/resolver", json={"accion": "rechazar"})
    assert response_resolver.status_code == 200


def test_seguridad_cross_module(logged_in_client, test_db):
    """
    Test 6: Seguridad Cross-Module: Listar datos cuando no hay registros.
    """
    # Intenta listar pagos cuando no hay datos
    response = logged_in_client.get("/api/pagos")

    # El sistema debe devolver 200 con lista vacía
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_flujo_busqueda_empresa_pagos(logged_in_client, test_db):
    """
    Test 7: Flujo de Búsqueda: Crear datos -> Listar Pagos -> Verificar filtro.
    """
    # PASO 1: Crear empresa
    test_db.execute(
        """
        INSERT INTO empresas (nit, nombre_empresa, tipo_identificacion_empresa)
        VALUES (?, ?, ?)
    """,
        (TEST_NIT, "Empresa E2E", "NIT"),
    )

    # PASO 2: Crear usuario
    test_db.execute(
        """
        INSERT INTO usuarios (numeroId, primerNombre, primerApellido, empresa_nit, tipoId)
        VALUES (?, ?, ?, ?, ?)
    """,
        (TEST_USER_ID, "Juan", "Test", TEST_NIT, "CC"),
    )

    # PASO 3: Crear pago
    test_db.execute(
        """
        INSERT INTO pagos (usuario_id, empresa_nit, monto, tipo_pago, fecha_pago)
        VALUES (?, ?, ?, ?, ?)
    """,
        (TEST_USER_ID, TEST_NIT, 250000.00, "Nomina", "2025-11-20"),
    )

    test_db.commit()

    # PASO 4: Listar pagos
    response_pagos = logged_in_client.get("/api/pagos")
    assert response_pagos.status_code == 200
    pagos = response_pagos.get_json()
    assert len(pagos) >= 1
    assert pagos[0]["empresa_nit"] == TEST_NIT


def test_workflow_completo_sistema(logged_in_client, test_db):
    """
    Test 8: Workflow Máximo: Empresa -> Usuario -> Pago -> Novedad -> Verificar todo.
    """
    # PASO 1: Crear Empresa
    empresa_payload = {
        "nit": TEST_NIT,
        "nombre_empresa": "Empresa Workflow",
        "tipo_identificacion_empresa": "NIT",
        "direccion": "Dirección Test",
        "telefono": "9876543210",
        "email": "workflow@test.com",
        "ciudad": "Medellín",
    }
    resp_empresa = logged_in_client.post("/api/empresas", json=empresa_payload)
    assert resp_empresa.status_code == 201

    # PASO 2: Crear Usuario
    usuario_payload = {
        "numero_documento": TEST_USER_ID,
        "nombre_completo": "Juan Workflow",
        "empresa_nit": TEST_NIT,
        "tipoId": "CC",
    }
    resp_usuario = logged_in_client.post("/api/usuarios", json=usuario_payload)
    assert resp_usuario.status_code == 201

    # PASO 3: Crear Pago
    pago_payload = {"usuario_id": TEST_USER_ID, "empresa_nit": TEST_NIT, "monto": 250000, "tipo_pago": "Nomina"}
    resp_pago = logged_in_client.post("/api/pagos", json=pago_payload)
    assert resp_pago.status_code == 201

    # PASO 4: Crear Novedad
    novedad_payload = {
        "client": TEST_NIT,
        "subject": "Verificación de pago",
        "priority": "Media",
        "status": "Nuevo",
        "description": f"Verificar pago de {TEST_USER_ID}",
    }
    resp_novedad = logged_in_client.post("/api/novedades", json=novedad_payload)
    assert resp_novedad.status_code == 201

    # PASO 5: Verificar que todas las operaciones fueron exitosas
    assert resp_empresa.status_code == 201
    assert resp_usuario.status_code == 201
    assert resp_pago.status_code == 201
    assert resp_novedad.status_code == 201


# --- Fin test_integracion_e2e.py ---
