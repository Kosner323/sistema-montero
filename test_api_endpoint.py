# -*- coding: utf-8 -*-
"""
Script para probar el endpoint de API que devuelve datos de empresa
"""
import requests
import json

# Configurar la URL
API_URL = "http://localhost:5000/api/empresas/900123456-1"

print("=" * 70)
print("PROBANDO ENDPOINT DE API")
print("=" * 70)
print(f"URL: {API_URL}\n")

try:
    # Hacer la petición GET
    response = requests.get(API_URL)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        empresa = response.json()

        print("\n[OK] Datos recibidos de la API:")
        print("-" * 70)
        print(json.dumps(empresa, indent=2, ensure_ascii=False))
        print("-" * 70)

        # Verificar campos específicos
        print("\n[VERIFICACION DE CAMPOS CLAVE]:")
        campos_verificar = [
            'nombre_empresa',
            'nit',
            'direccion_empresa',
            'telefono_empresa',
            'correo_empresa',
            'ciudad_empresa',
            'departamento',
            'tipo_empresa',
            'sector_economico',
            'banco',
            'rep_legal_nombre',
            'rep_legal_telefono',
            'rep_legal_correo'
        ]

        for campo in campos_verificar:
            valor = empresa.get(campo)
            estado = "✓" if valor else "✗"
            print(f"  {estado} {campo}: {valor if valor else '(vacío)'}")

        print("\n[OK] API funcionando correctamente!")

    elif response.status_code == 404:
        print("\n[ERROR] Empresa no encontrada")
        print(response.json())
    else:
        print(f"\n[ERROR] Error en la respuesta: {response.status_code}")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("\n[ERROR] No se pudo conectar al servidor")
    print("Asegúrate de que Flask esté corriendo en http://localhost:5000")
except Exception as e:
    print(f"\n[ERROR] Error inesperado: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
