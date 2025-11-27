"""
test_integracion_pila_simple.py
================================
Test simplificado de integración sin dependencias de autenticación.
Valida que el Motor PILA v1.1 funcione correctamente con la API.

Ejecutar: python tests/test_integracion_pila_simple.py
"""

import sys
import json
from pathlib import Path

# Agregar path del dashboard al sistema
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app


def test_endpoint_simular_pila():
    """
    Test de integración básico sin autenticación compleja.
    Valida que el endpoint /simular-pila funcione correctamente.
    """
    print("\n" + "="*70)
    print("TEST DE INTEGRACIÓN - MOTOR PILA v1.1 + API REST")
    print("="*70 + "\n")
    
    # Crear app de pruebas
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        # Simular login (método simple sin DB real)
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'test_user'
            sess['empresa_actual'] = 1
        
        # ==================== TEST 1: Salario Mínimo Exonerado ====================
        print("TEST 1: Salario Mínimo con Exoneración")
        print("-" * 70)
        
        payload = {
            "salario_base": 1300000,
            "nivel_riesgo": 1,
            "es_salario_integral": False,
            "es_empresa_exonerada": True
        }
        
        response = client.post(
            "/api/cotizaciones/simular-pila",
            data=json.dumps(payload),
            content_type="application/json"
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            
            print(f"✅ Salario Base: ${data['datos_entrada']['salario_base']:,.0f}")
            print(f"✅ IBC: ${data['datos_entrada']['ibc']:,.0f}")
            print(f"✅ Salud Empleado: ${data['salud']['empleado']:,.0f}")
            print(f"✅ Salud Empleador: ${data['salud']['empleador']:,.0f} (Exonerado: {data['salud']['empleador_exonerado']})")
            print(f"✅ CCF: ${data['parafiscales']['ccf']:,.0f}")
            print(f"✅ Total Empleado: ${data['totales']['empleado']:,.0f}")
            print(f"✅ Total Empleador: ${data['totales']['empleador']:,.0f}")
            print(f"✅ Salario Neto: ${data['totales']['salario_neto']:,.0f}")
            
            # Validaciones
            assert data['salud']['empleador'] == 0, "Salud Empleador debe ser $0 (exonerado)"
            assert data['salud']['empleador_exonerado'] is True
            assert data['parafiscales']['ccf'] == 52000, f"CCF esperado $52,000, obtuvo ${data['parafiscales']['ccf']}"
            
            print("\n✅ TEST 1 PASADO\n")
        else:
            print(f"❌ ERROR: {response.get_json()}\n")
            return False
        
        # ==================== TEST 2: Salario Alto Sin Exoneración ====================
        print("TEST 2: Salario Alto Sin Exoneración")
        print("-" * 70)
        
        payload = {
            "salario_base": 15000000,
            "nivel_riesgo": 3,
            "es_salario_integral": False,
            "es_empresa_exonerada": False
        }
        
        response = client.post(
            "/api/cotizaciones/simular-pila",
            data=json.dumps(payload),
            content_type="application/json"
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            
            print(f"✅ Salario Base: ${data['datos_entrada']['salario_base']:,.0f}")
            print(f"✅ Salud Empleador: ${data['salud']['empleador']:,.0f} (NO exonerado)")
            print(f"✅ CCF: ${data['parafiscales']['ccf']:,.0f}")
            print(f"✅ SENA: ${data['parafiscales']['sena']:,.0f} (No aplica > 10 SMMLV)")
            print(f"✅ ICBF: ${data['parafiscales']['icbf']:,.0f} (No aplica > 10 SMMLV)")
            print(f"✅ Total Empleador: ${data['totales']['empleador']:,.0f}")
            
            # Validaciones
            assert data['salud']['empleador'] > 0, "Salud Empleador debe ser > $0 (NO exonerado)"
            assert data['salud']['empleador_exonerado'] is False
            assert data['parafiscales']['ccf'] > 0, "CCF debe calcularse siempre"
            assert data['parafiscales']['sena'] == 0, "SENA no debe aplicar (salario > 10 SMMLV)"
            assert data['parafiscales']['icbf'] == 0, "ICBF no debe aplicar (salario > 10 SMMLV)"
            
            print("\n✅ TEST 2 PASADO\n")
        else:
            print(f"❌ ERROR: {response.get_json()}\n")
            return False
        
        # ==================== TEST 3: Salario Integral ====================
        print("TEST 3: Salario Integral (IBC = 70%)")
        print("-" * 70)
        
        payload = {
            "salario_base": 25000000,
            "nivel_riesgo": 2,
            "es_salario_integral": True,
            "es_empresa_exonerada": False
        }
        
        response = client.post(
            "/api/cotizaciones/simular-pila",
            data=json.dumps(payload),
            content_type="application/json"
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            
            ibc_esperado = 25000000 * 0.70
            
            print(f"✅ Salario Base: ${data['datos_entrada']['salario_base']:,.0f}")
            print(f"✅ IBC (70%): ${data['datos_entrada']['ibc']:,.0f}")
            print(f"✅ Es Salario Integral: {data['datos_entrada']['es_salario_integral']}")
            print(f"✅ Total Empleado: ${data['totales']['empleado']:,.0f}")
            
            # Validaciones
            assert data['datos_entrada']['ibc'] == ibc_esperado, "IBC debe ser 70% del salario"
            assert data['datos_entrada']['es_salario_integral'] is True
            
            print("\n✅ TEST 3 PASADO\n")
        else:
            print(f"❌ ERROR: {response.get_json()}\n")
            return False
        
        # ==================== TEST 4: Tope IBC 25 SMMLV ====================
        print("TEST 4: Tope IBC 25 SMMLV")
        print("-" * 70)
        
        payload = {
            "salario_base": 40000000,
            "nivel_riesgo": 4,
            "es_salario_integral": False,
            "es_empresa_exonerada": False
        }
        
        response = client.post(
            "/api/cotizaciones/simular-pila",
            data=json.dumps(payload),
            content_type="application/json"
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            
            IBC_MAXIMO = 1300000 * 25
            
            print(f"✅ Salario Base: ${data['datos_entrada']['salario_base']:,.0f}")
            print(f"✅ IBC (tope): ${data['datos_entrada']['ibc']:,.0f}")
            print(f"✅ IBC Limitado: {data['datos_entrada']['ibc_limitado']}")
            print(f"✅ Total General: ${data['totales']['general']:,.0f}")
            
            # Validaciones
            assert data['datos_entrada']['ibc'] == IBC_MAXIMO, f"IBC debe limitarse a ${IBC_MAXIMO:,}"
            assert data['datos_entrada']['ibc_limitado'] is True
            
            print("\n✅ TEST 4 PASADO\n")
        else:
            print(f"❌ ERROR: {response.get_json()}\n")
            return False
        
        # ==================== TEST 5: Error - Nivel Riesgo Inválido ====================
        print("TEST 5: Validación de Errores - Nivel Riesgo Inválido")
        print("-" * 70)
        
        payload = {
            "salario_base": 1300000,
            "nivel_riesgo": 10  # Inválido
        }
        
        response = client.post(
            "/api/cotizaciones/simular-pila",
            data=json.dumps(payload),
            content_type="application/json"
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 400:
            error = response.get_json()
            print(f"✅ Error esperado: {error['error']}")
            print("\n✅ TEST 5 PASADO\n")
        else:
            print(f"❌ ERROR: Esperaba status 400, obtuvo {response.status_code}\n")
            return False
    
    print("="*70)
    print("🎉 TODOS LOS TESTS DE INTEGRACIÓN PASARON (5/5)")
    print("="*70)
    print("\n✅ El Motor PILA v1.1 está correctamente integrado con la API REST")
    print("✅ Endpoint: POST /api/cotizaciones/simular-pila")
    print("✅ Versión Motor: 1.1.0")
    print("✅ Estado: LISTO PARA PRODUCCIÓN\n")
    
    return True


if __name__ == "__main__":
    try:
        resultado = test_endpoint_simular_pila()
        sys.exit(0 if resultado else 1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
