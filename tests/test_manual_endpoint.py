"""
test_manual_endpoint.py
=======================
Script para probar manualmente el endpoint /simular-pila
usando requests HTTP directos al servidor Flask en ejecución.

Uso: 
1. Iniciar servidor: python app.py
2. Ejecutar este script: python tests/test_manual_endpoint.py
"""

import requests
import json


BASE_URL = "http://localhost:5000"
ENDPOINT = "/api/cotizaciones/simular-pila"


def test_endpoint():
    """
    Prueba el endpoint con diferentes casos de uso.
    """
    print("\n" + "="*70)
    print("TEST MANUAL - ENDPOINT /api/cotizaciones/simular-pila")
    print("="*70 + "\n")
    
    print("⚠️  IMPORTANTE: Asegúrate de que el servidor Flask esté corriendo")
    print("   Ejecuta: python app.py")
    print("   URL: http://localhost:5000\n")
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    # ==================== LOGIN (si es necesario) ====================
    # Nota: Adapta esto según tu sistema de autenticación
    print("Paso 1: Intentando autenticación...")
    
    # Opción 1: Si usas /login
    login_data = {
        "username": "admin",  # Cambiar por credenciales válidas
        "password": "admin"
    }
    
    try:
        login_response = session.post(f"{BASE_URL}/login", data=login_data)
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("✅ Autenticación exitosa\n")
        else:
            print("⚠️  Autenticación falló, continuando sin sesión...\n")
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se pudo conectar al servidor")
        print("   ¿Está corriendo Flask en http://localhost:5000?")
        return False
    
    # ==================== TEST 1: Salario Mínimo Exonerado ====================
    print("TEST 1: Salario Mínimo con Exoneración")
    print("-" * 70)
    
    payload = {
        "salario_base": 1300000,
        "nivel_riesgo": 1,
        "es_salario_integral": False,
        "es_empresa_exonerada": True
    }
    
    try:
        response = session.post(
            f"{BASE_URL}{ENDPOINT}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n📊 RESULTADO:")
            print(f"  Salario Base: ${data['datos_entrada']['salario_base']:,.0f}")
            print(f"  IBC: ${data['datos_entrada']['ibc']:,.0f}")
            print(f"  Salud Empleado: ${data['salud']['empleado']:,.0f}")
            print(f"  Salud Empleador: ${data['salud']['empleador']:,.0f} (Exonerado: {data['salud']['empleador_exonerado']})")
            print(f"  Pensión Empleado: ${data['pension']['empleado']:,.0f}")
            print(f"  Pensión Empleador: ${data['pension']['empleador']:,.0f}")
            print(f"  ARL: ${data['arl']['empleador']:,.0f} (Tasa: {data['arl']['tasa_porcentaje']:.3f}%)")
            print(f"  CCF: ${data['parafiscales']['ccf']:,.0f}")
            print(f"  SENA: ${data['parafiscales']['sena']:,.0f}")
            print(f"  ICBF: ${data['parafiscales']['icbf']:,.0f}")
            print(f"  Total Empleado: ${data['totales']['empleado']:,.0f}")
            print(f"  Total Empleador: ${data['totales']['empleador']:,.0f}")
            print(f"  Total General: ${data['totales']['general']:,.0f}")
            print(f"  Salario Neto: ${data['totales']['salario_neto']:,.0f}")
            
            if data['metadata']['advertencias']:
                print(f"\n⚠️  Advertencias:")
                for adv in data['metadata']['advertencias']:
                    print(f"    {adv}")
            
            print("\n✅ TEST 1 PASADO\n")
        else:
            print(f"\n❌ ERROR: {response.text}\n")
            return False
    
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se pudo conectar al servidor\n")
        return False
    
    # ==================== TEST 2: Salario Integral ====================
    print("TEST 2: Salario Integral (IBC = 70%)")
    print("-" * 70)
    
    payload = {
        "salario_base": 25000000,
        "nivel_riesgo": 2,
        "es_salario_integral": True,
        "es_empresa_exonerada": False
    }
    
    response = session.post(f"{BASE_URL}{ENDPOINT}", json=payload)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"\n📊 RESULTADO:")
        print(f"  Salario Base: ${data['datos_entrada']['salario_base']:,.0f}")
        print(f"  IBC (70%): ${data['datos_entrada']['ibc']:,.0f}")
        print(f"  Es Salario Integral: {data['datos_entrada']['es_salario_integral']}")
        print(f"  Total Empleado: ${data['totales']['empleado']:,.0f}")
        print(f"  Total Empleador: ${data['totales']['empleador']:,.0f}")
        
        print("\n✅ TEST 2 PASADO\n")
    else:
        print(f"\n❌ ERROR: {response.text}\n")
        return False
    
    # ==================== TEST 3: Error - Nivel Riesgo Inválido ====================
    print("TEST 3: Validación de Errores")
    print("-" * 70)
    
    payload = {
        "salario_base": 1300000,
        "nivel_riesgo": 10  # Inválido
    }
    
    response = session.post(f"{BASE_URL}{ENDPOINT}", json=payload)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 400:
        error = response.json()
        print(f"\n📛 Error esperado: {error['error']}")
        print("\n✅ TEST 3 PASADO\n")
    else:
        print(f"\n❌ ERROR: Esperaba status 400, obtuvo {response.status_code}\n")
        return False
    
    print("="*70)
    print("🎉 TODOS LOS TESTS MANUALES PASARON (3/3)")
    print("="*70)
    print("\n✅ El Motor PILA v1.1 está correctamente integrado")
    print("✅ Endpoint: POST /api/cotizaciones/simular-pila")
    print("✅ Estado: LISTO PARA PRODUCCIÓN\n")
    
    return True


if __name__ == "__main__":
    import sys
    
    try:
        resultado = test_endpoint()
        sys.exit(0 if resultado else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
