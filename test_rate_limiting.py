# -*- coding: utf-8 -*-
"""
Script de prueba para verificar el Rate Limiting en endpoints de autenticación.
"""
import requests
import time

BASE_URL = "http://127.0.0.1:5000/api"

def test_login_rate_limit():
    """Prueba el rate limiting del endpoint /api/login (5 por minuto)."""
    print("\n" + "="*70)
    print("PRUEBA 1: Rate Limiting en /api/login (Límite: 5 por minuto)")
    print("="*70)

    login_data = {
        "email": "test@example.com",
        "password": "wrongpassword"
    }

    for i in range(1, 8):
        try:
            response = requests.post(
                f"{BASE_URL}/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )

            print(f"\nIntento {i}:")
            print(f"  Status Code: {response.status_code}")

            if response.status_code == 429:
                print(f"  ✅ Rate Limit Activado!")
                print(f"  Mensaje: {response.json().get('error', 'Too Many Requests')}")
                print(f"  Headers: {dict(response.headers)}")
                break
            elif response.status_code in [401, 422]:
                print(f"  ✓ Solicitud procesada (credenciales incorrectas esperado)")
                print(f"  Respuesta: {response.json()}")
            else:
                print(f"  Respuesta: {response.json()}")

        except Exception as e:
            print(f"  ❌ Error: {e}")

        time.sleep(0.5)  # Pequeña pausa entre solicitudes


def test_register_rate_limit():
    """Prueba el rate limiting del endpoint /api/register (10 por hora)."""
    print("\n" + "="*70)
    print("PRUEBA 2: Rate Limiting en /api/register (Límite: 10 por hora)")
    print("="*70)

    for i in range(1, 13):
        register_data = {
            "nombre": f"Test User {i}",
            "email": f"test{i}@example.com",
            "password": "Test1234!",
            "telefono": "1234567890",
            "fecha_nacimiento": "1990-01-01"
        }

        try:
            response = requests.post(
                f"{BASE_URL}/register",
                json=register_data,
                headers={"Content-Type": "application/json"}
            )

            print(f"\nIntento {i}:")
            print(f"  Status Code: {response.status_code}")

            if response.status_code == 429:
                print(f"  ✅ Rate Limit Activado!")
                print(f"  Mensaje: {response.json().get('error', 'Too Many Requests')}")
                print(f"  Headers: {dict(response.headers)}")
                break
            elif response.status_code in [201, 409, 422]:
                print(f"  ✓ Solicitud procesada")
                print(f"  Respuesta: {response.json()}")
            else:
                print(f"  Respuesta: {response.json()}")

        except Exception as e:
            print(f"  ❌ Error: {e}")

        time.sleep(0.3)


def check_server_status():
    """Verifica si el servidor está corriendo."""
    try:
        response = requests.get("http://127.0.0.1:5000/hello", timeout=2)
        if response.status_code == 200:
            print("✅ Servidor está corriendo correctamente")
            return True
    except requests.exceptions.ConnectionError:
        print("❌ Error: El servidor no está corriendo en http://127.0.0.1:5000")
        print("   Por favor, inicia el servidor con: python app.py")
        return False
    except Exception as e:
        print(f"❌ Error al conectar con el servidor: {e}")
        return False


if __name__ == "__main__":
    print("="*70)
    print("SCRIPT DE PRUEBA - RATE LIMITING CON FLASK-LIMITER")
    print("="*70)

    if not check_server_status():
        exit(1)

    # Ejecutar pruebas
    test_login_rate_limit()

    print("\n" + "-"*70)
    print("Esperando 3 segundos antes de la siguiente prueba...")
    print("-"*70)
    time.sleep(3)

    test_register_rate_limit()

    print("\n" + "="*70)
    print("PRUEBAS COMPLETADAS")
    print("="*70)
    print("\nNotas:")
    print("- Los límites se resetean automáticamente después del período establecido")
    print("- Login: 5 solicitudes por minuto")
    print("- Register: 10 solicitudes por hora")
    print("- En producción, considera usar Redis para el almacenamiento")
    print("="*70)
