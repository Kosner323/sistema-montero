"""
tests/test_api_simulacion.py
============================
Pruebas de Integración para el Endpoint POST /api/cotizaciones/simular-pila

Verifica que el Motor PILA v1.1 esté correctamente integrado con la API REST
y que las respuestas JSON sean correctas.

Autor: Sistema Montero
Fecha: 26/11/2025
"""

import json
import pytest
from decimal import Decimal


# ==================== TESTS DE INTEGRACIÓN ====================

def test_simulacion_salario_minimo_exonerado(client, auth_headers):
    """
    Test 1: Salario mínimo con empresa exonerada (caso más común).
    
    Verifica:
    - HTTP 200
    - Salud Empleador = $0 (exoneración aplicada)
    - CCF > $0 (siempre se calcula)
    - Todos los campos presentes
    """
    payload = {
        "salario_base": 1300000,
        "nivel_riesgo": 1,
        "es_salario_integral": False,
        "es_empresa_exonerada": True
    }
    
    response = client.post(
        "/api/cotizaciones/simular-pila",
        data=json.dumps(payload),
        headers=auth_headers,
        content_type="application/json"
    )
    
    assert response.status_code == 200, f"Esperaba 200, obtuvo {response.status_code}"
    
    data = response.get_json()
    
    # Verificar estructura de respuesta
    assert "datos_entrada" in data
    assert "salud" in data
    assert "pension" in data
    assert "arl" in data
    assert "parafiscales" in data
    assert "totales" in data
    assert "metadata" in data
    
    # Verificar datos de entrada
    assert data["datos_entrada"]["salario_base"] == 1300000
    assert data["datos_entrada"]["ibc"] == 1300000
    assert data["datos_entrada"]["nivel_riesgo_arl"] == 1
    assert data["datos_entrada"]["es_empresa_exonerada"] is True
    
    # Verificar exoneración de Salud Empleador
    assert data["salud"]["empleador"] == 0, "Salud Empleador debe ser $0 (exonerado)"
    assert data["salud"]["empleador_exonerado"] is True
    assert data["salud"]["empleado"] > 0, "Salud Empleado debe ser > $0"
    
    # Verificar CCF 4% SIEMPRE (corrección v1.1)
    assert data["parafiscales"]["ccf"] > 0, "CCF debe ser > $0 (se calcula siempre)"
    assert data["parafiscales"]["ccf"] == 52000, f"CCF esperado $52,000, obtuvo ${data['parafiscales']['ccf']}"
    
    # Verificar SENA/ICBF (aplican para salarios < 10 SMMLV)
    assert data["parafiscales"]["aplica_sena_icbf"] is True
    assert data["parafiscales"]["sena"] > 0
    assert data["parafiscales"]["icbf"] > 0
    
    # Verificar totales
    assert data["totales"]["empleado"] > 0
    assert data["totales"]["empleador"] > 0
    assert data["totales"]["general"] == data["totales"]["empleado"] + data["totales"]["empleador"]
    assert data["totales"]["salario_neto"] == 1300000 - data["totales"]["empleado"]
    
    # Verificar metadata
    assert "fecha_calculo" in data["metadata"]
    assert data["metadata"]["version_motor"] == "1.1.0"
    assert isinstance(data["metadata"]["advertencias"], list)
    
    print(f"✅ TEST 1 PASADO - Salario Mínimo Exonerado")
    print(f"   Total Empleado: ${data['totales']['empleado']:,.0f}")
    print(f"   Total Empleador: ${data['totales']['empleador']:,.0f}")
    print(f"   Salario Neto: ${data['totales']['salario_neto']:,.0f}")


def test_simulacion_salario_alto_sin_exoneracion(client, auth_headers):
    """
    Test 2: Salario alto sin exoneración (empresa grande).
    
    Verifica:
    - HTTP 200
    - Salud Empleador > $0 (NO exonerado)
    - SENA/ICBF = $0 (salario > 10 SMMLV)
    - CCF > $0 (siempre se calcula)
    """
    payload = {
        "salario_base": 15000000,
        "nivel_riesgo": 3,
        "es_salario_integral": False,
        "es_empresa_exonerada": False
    }
    
    response = client.post(
        "/api/cotizaciones/simular-pila",
        data=json.dumps(payload),
        headers=auth_headers,
        content_type="application/json"
    )
    
    assert response.status_code == 200
    data = response.get_json()
    
    # Verificar NO exoneración
    assert data["salud"]["empleador"] > 0, "Salud Empleador debe ser > $0 (NO exonerado)"
    assert data["salud"]["empleador_exonerado"] is False
    
    # Verificar que NO aplican SENA/ICBF (salario > 10 SMMLV)
    assert data["parafiscales"]["aplica_sena_icbf"] is False
    assert data["parafiscales"]["sena"] == 0
    assert data["parafiscales"]["icbf"] == 0
    
    # Verificar que CCF SÍ se calcula (corrección v1.1)
    assert data["parafiscales"]["ccf"] > 0, "CCF debe calcularse siempre"
    
    print(f"✅ TEST 2 PASADO - Salario Alto Sin Exoneración")
    print(f"   Salud Empleador: ${data['salud']['empleador']:,.0f} (NO exonerado)")
    print(f"   CCF: ${data['parafiscales']['ccf']:,.0f}")
    print(f"   SENA/ICBF: $0 (no aplican)")


def test_simulacion_salario_integral(client, auth_headers):
    """
    Test 3: Salario Integral (IBC = 70%).
    
    Verifica:
    - HTTP 200
    - IBC = 70% del salario base
    - Cálculos basados en IBC (no en salario completo)
    """
    payload = {
        "salario_base": 25000000,
        "nivel_riesgo": 2,
        "es_salario_integral": True,
        "es_empresa_exonerada": False
    }
    
    response = client.post(
        "/api/cotizaciones/simular-pila",
        data=json.dumps(payload),
        headers=auth_headers,
        content_type="application/json"
    )
    
    assert response.status_code == 200
    data = response.get_json()
    
    # Verificar IBC = 70%
    ibc_esperado = 25000000 * 0.70
    assert data["datos_entrada"]["ibc"] == ibc_esperado, f"IBC debe ser 70% del salario"
    assert data["datos_entrada"]["es_salario_integral"] is True
    
    # Verificar que los cálculos usan el IBC (no el salario completo)
    salud_empleado_esperado = ibc_esperado * 0.04  # 4% del IBC
    assert abs(data["salud"]["empleado"] - salud_empleado_esperado) < 1, \
        "Salud Empleado debe calcularse sobre IBC (70%)"
    
    print(f"✅ TEST 3 PASADO - Salario Integral")
    print(f"   Salario: ${payload['salario_base']:,.0f}")
    print(f"   IBC (70%): ${data['datos_entrada']['ibc']:,.0f}")
    print(f"   Salud Empleado: ${data['salud']['empleado']:,.0f}")


def test_simulacion_tope_ibc_25_smmlv(client, auth_headers):
    """
    Test 4: Salario que supera el tope de 25 SMMLV.
    
    Verifica:
    - HTTP 200
    - IBC limitado a $32,500,000 (25 × SMMLV 2025)
    - Flag ibc_limitado = True
    """
    payload = {
        "salario_base": 40000000,
        "nivel_riesgo": 4,
        "es_salario_integral": False,
        "es_empresa_exonerada": False
    }
    
    response = client.post(
        "/api/cotizaciones/simular-pila",
        data=json.dumps(payload),
        headers=auth_headers,
        content_type="application/json"
    )
    
    assert response.status_code == 200
    data = response.get_json()
    
    # Verificar tope de IBC
    IBC_MAXIMO = 1300000 * 25  # $32,500,000
    assert data["datos_entrada"]["ibc"] == IBC_MAXIMO, \
        f"IBC debe limitarse a 25 SMMLV (${IBC_MAXIMO:,})"
    assert data["datos_entrada"]["ibc_limitado"] is True
    
    print(f"✅ TEST 4 PASADO - Tope IBC 25 SMMLV")
    print(f"   Salario: ${payload['salario_base']:,.0f}")
    print(f"   IBC (tope): ${data['datos_entrada']['ibc']:,.0f}")
    print(f"   IBC limitado: {data['datos_entrada']['ibc_limitado']}")


# ==================== TESTS DE VALIDACIÓN DE ERRORES ====================

def test_error_campos_faltantes(client, auth_headers):
    """
    Test 5: Petición sin campos requeridos debe retornar HTTP 400.
    """
    payload = {
        "salario_base": 1300000
        # Falta nivel_riesgo
    }
    
    response = client.post(
        "/api/cotizaciones/simular-pila",
        data=json.dumps(payload),
        headers=auth_headers,
        content_type="application/json"
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "nivel_riesgo" in data["error"].lower()
    
    print(f"✅ TEST 5 PASADO - Error Campos Faltantes")


def test_error_salario_invalido(client, auth_headers):
    """
    Test 6: Salario con formato inválido debe retornar HTTP 400.
    """
    payload = {
        "salario_base": "mil trescientos mil",  # String en lugar de número
        "nivel_riesgo": 1
    }
    
    response = client.post(
        "/api/cotizaciones/simular-pila",
        data=json.dumps(payload),
        headers=auth_headers,
        content_type="application/json"
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    
    print(f"✅ TEST 6 PASADO - Error Salario Inválido")


def test_error_nivel_riesgo_invalido(client, auth_headers):
    """
    Test 7: Nivel de riesgo fuera de rango (1-5) debe retornar HTTP 400.
    """
    payload = {
        "salario_base": 1300000,
        "nivel_riesgo": 10  # Inválido (debe ser 1-5)
    }
    
    response = client.post(
        "/api/cotizaciones/simular-pila",
        data=json.dumps(payload),
        headers=auth_headers,
        content_type="application/json"
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "nivel de riesgo" in data["error"].lower() or "inválido" in data["error"].lower()
    
    print(f"✅ TEST 7 PASADO - Error Nivel Riesgo Inválido")


def test_error_salario_negativo(client, auth_headers):
    """
    Test 8: Salario negativo debe retornar HTTP 400.
    """
    payload = {
        "salario_base": -1000000,
        "nivel_riesgo": 1
    }
    
    response = client.post(
        "/api/cotizaciones/simular-pila",
        data=json.dumps(payload),
        headers=auth_headers,
        content_type="application/json"
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    
    print(f"✅ TEST 8 PASADO - Error Salario Negativo")


def test_error_json_vacio(client, auth_headers):
    """
    Test 9: Petición sin JSON debe retornar HTTP 400.
    """
    response = client.post(
        "/api/cotizaciones/simular-pila",
        headers=auth_headers
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    
    print(f"✅ TEST 9 PASADO - Error JSON Vacío")


# ==================== TEST DE AUTENTICACIÓN ====================

def test_endpoint_requiere_autenticacion(client):
    """
    Test 10: Endpoint debe requerir autenticación (sin token = HTTP 401/403).
    """
    payload = {
        "salario_base": 1300000,
        "nivel_riesgo": 1
    }
    
    response = client.post(
        "/api/cotizaciones/simular-pila",
        data=json.dumps(payload),
        content_type="application/json"
        # Sin headers de autenticación
    )
    
    # Puede ser 401 (Unauthorized) o 403 (Forbidden) dependiendo de la implementación
    assert response.status_code in [401, 403, 302], \
        f"Esperaba 401/403/302 (redirect), obtuvo {response.status_code}"
    
    print(f"✅ TEST 10 PASADO - Endpoint Requiere Autenticación")


# ==================== FIXTURES (si no existen en conftest.py) ====================

@pytest.fixture
def client():
    """
    Fixture que crea un cliente de pruebas de Flask.
    Si ya existe en conftest.py, este fixture será ignorado.
    """
    from app import create_app
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        yield client


@pytest.fixture
def auth_headers():
    """
    Fixture que proporciona headers de autenticación simulados.
    NOTA: Si tu sistema usa sesiones en lugar de headers, adapta esto.
    """
    # Opción 1: Si usas sesiones de Flask
    # Esta fixture puede necesitar ajustarse según tu implementación real
    return {
        "Content-Type": "application/json"
    }
    
    # Opción 2: Si usas tokens JWT
    # return {
    #     "Authorization": "Bearer <token_prueba>",
    #     "Content-Type": "application/json"
    # }


# ==================== EJECUCIÓN DIRECTA ====================

if __name__ == "__main__":
    """
    Ejecutar tests directamente con pytest.
    """
    import sys
    
    print("\n" + "="*70)
    print("TESTS DE INTEGRACIÓN - ENDPOINT /api/cotizaciones/simular-pila")
    print("="*70 + "\n")
    
    # Ejecutar pytest con verbosidad
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-s"  # Mostrar prints
    ])
    
    if exit_code == 0:
        print("\n" + "="*70)
        print("✅ TODOS LOS TESTS DE INTEGRACIÓN PASARON")
        print("="*70)
        print("\n🎉 El Motor PILA v1.1 está correctamente integrado con la API REST")
    else:
        print("\n" + "="*70)
        print("❌ ALGUNOS TESTS FALLARON")
        print("="*70)
    
    sys.exit(exit_code)
