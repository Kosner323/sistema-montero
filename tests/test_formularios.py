# -*- coding: utf-8 -*-
"""
Tests para el Módulo de Formularios - routes/formularios.py
==========================================================
Se enfoca en la subida, validación y manejo de archivos.
"""

import io  # Para manejar archivos en memoria

import pytest
from werkzeug.datastructures import FileStorage

# Datos de prueba para el archivo PDF
PDF_CONTENT = b"%PDF-1.7\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj"
FAKE_PDF = io.BytesIO(PDF_CONTENT)
PDF_SIZE = len(PDF_CONTENT)


# Falla si el archivo no existe
@pytest.fixture
def valid_pdf_file():
    """Crea un objeto FileStorage válido para un PDF."""
    return FileStorage(stream=io.BytesIO(PDF_CONTENT), filename="formulario_valido.pdf", content_type="application/pdf")


# --- TESTS DE SUBIDA Y CRUD ---


def test_subir_archivo_requires_login(client):
    """
    Test 1: Verifica que no se pueda subir un formulario sin iniciar sesión.
    """
    # Se usa la ruta de importación correcta: /api/formularios/importar
    response = client.post(
        "/api/formularios/importar", data={"archivo": (io.BytesIO(b"dummy"), "test.pdf"), "nombre": "Test Formulario"}
    )
    assert response.status_code == 401


def test_subir_pdf_valido_success(logged_in_client, valid_pdf_file, mocker):
    """
    Test 2: Verifica que se pueda subir un archivo PDF válido.
    """
    # Mock operaciones de sistema de archivos para evitar interacción con disco real
    mocker.patch("os.makedirs")
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("werkzeug.datastructures.FileStorage.save")

    response = logged_in_client.post(
        "/api/formularios/importar",
        data={"nombre": "Formulario de Prueba", "archivo": valid_pdf_file},
        content_type="multipart/form-data",
    )
    # 201 Created o 200 OK
    assert response.status_code in [201, 200]
    assert "message" in response.get_json()


def test_subir_archivo_invalido_type(logged_in_client):
    """
    Test 3: Verifica que se rechacen archivos con extensión no permitida.
    """
    # Intentar subir un .exe
    response = logged_in_client.post(
        "/api/formularios/importar",
        data={
            "nombre": "Archivo Invalido",
            "archivo": FileStorage(
                stream=io.BytesIO(b"malicious code"), filename="virus.exe", content_type="application/octet-stream"
            ),
        },
        content_type="multipart/form-data",
    )
    # 400 Bad Request
    assert response.status_code == 400
    assert "PDF" in response.get_json()["error"]


def test_listar_formularios_logged_in(logged_in_client):
    """
    Test 4: Verifica que se pueda listar los formularios.
    """
    response = logged_in_client.get("/api/formularios")
    assert response.status_code == 200
    # El endpoint devuelve una lista directamente, no un objeto con 'items'
    data = response.get_json()
    assert isinstance(data, list)


def test_descargar_archivo_not_found(logged_in_client):
    """
    Test 5: Intenta descargar un archivo que no existe (debe ser 404).
    """
    response = logged_in_client.get("/api/formularios/download/archivo_inexistente.pdf")
    assert response.status_code == 404


# --- TESTS ADICIONALES PARA COMPLETAR COBERTURA ---


def test_generar_formulario_exito(logged_in_client, test_db, mocker):
    """
    Test 6: Verifica que se pueda generar un formulario exitosamente.
    """
    # Insertar datos de prueba en la BD
    test_db.execute(
        """
        INSERT INTO formularios_importados (id, nombre, nombre_archivo, ruta_archivo)
        VALUES (1, 'Formulario Test', 'test_form.pdf', '/fake/path/test_form.pdf')
    """
    )
    test_db.execute(
        """
        INSERT INTO usuarios (id, numeroId, primerNombre, primerApellido, correoElectronico,
                             tipoId, direccion, telefonoFijo, telefonoCelular, comunaBarrio,
                             departamentoNacimiento, municipioNacimiento, paisNacimiento,
                             nacionalidad, fechaNacimiento, afpNombre, fechaIngreso, ibc, sexoBiologico)
        VALUES (1, '123456789', 'Juan', 'Perez', 'juan@test.com',
                'CC', 'Calle 1', '1234567', '3001234567', 'Centro',
                'Bogota', 'Bogota', 'Colombia', 'Colombiana', '1990-01-01',
                'Proteccion', '2020-01-01', 1000000, 'Masculino')
    """
    )
    test_db.execute(
        """
        INSERT INTO empresas (nit, nombre_empresa, tipo_identificacion_empresa, direccion_empresa,
                             telefono_empresa, correo_empresa, afp_empresa, arl_empresa,
                             ibc_empresa, departamento_empresa, ciudad_empresa)
        VALUES ('900123456', 'Empresa Test SA', 'NIT', 'Calle Empresa 123',
                '7654321', 'contacto@empresa.com', 'Proteccion', 'Sura',
                5000000, 'Bogota', 'Bogota')
    """
    )
    test_db.commit()

    # Mock para evitar operaciones de archivo real
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("os.makedirs")
    mocker.patch("builtins.open", mocker.mock_open())

    # Mock de PdfReader y PdfWriter
    mock_reader = mocker.MagicMock()
    mock_reader.pages = [mocker.MagicMock()]
    mock_reader.get_fields.return_value = {"campo1": "valor1"}

    mock_writer = mocker.MagicMock()
    mock_writer.pages = [mocker.MagicMock()]

    mocker.patch("routes.formularios.PdfReader", return_value=mock_reader)
    mocker.patch("routes.formularios.PdfWriter", return_value=mock_writer)

    # Realizar petición
    response = logged_in_client.post(
        "/api/formularios/generar", json={"formulario_id": 1, "usuario_id": 1, "empresa_nit": "900123456"}
    )

    # Verificar respuesta (debe devolver el PDF como archivo)
    assert response.status_code == 200
    assert response.mimetype == "application/pdf"


def test_generar_formulario_missing_data(logged_in_client):
    """
    Test 7: Verifica que se devuelva error si faltan datos para generar formulario.
    """
    response = logged_in_client.post(
        "/api/formularios/generar",
        json={
            "formulario_id": 1
            # Faltan usuario_id y empresa_nit
        },
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "IDs" in data["error"]


def test_eliminar_formulario_exito(logged_in_client, test_db, mocker):
    """
    Test 8: Verifica que se pueda eliminar un formulario exitosamente.
    """
    # Insertar formulario de prueba
    test_db.execute(
        """
        INSERT INTO formularios_importados (id, nombre, nombre_archivo, ruta_archivo)
        VALUES (1, 'Formulario a Eliminar', 'delete_test.pdf', '/fake/path/delete_test.pdf')
    """
    )
    test_db.commit()

    # Mock para operaciones de archivo
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("os.path.normpath", side_effect=lambda x: x)
    mocker.patch("os.remove")

    # Eliminar formulario
    response = logged_in_client.delete("/api/formularios/1")

    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert "eliminado" in data["message"]

    # Verificar que se eliminó de la BD
    result = test_db.execute("SELECT * FROM formularios_importados WHERE id = 1").fetchone()
    assert result is None


def test_eliminar_formulario_no_encontrado(logged_in_client):
    """
    Test 9: Verifica que se devuelva 404 al intentar eliminar un formulario inexistente.
    """
    response = logged_in_client.delete("/api/formularios/999")

    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data
    assert "no encontrado" in data["error"]
