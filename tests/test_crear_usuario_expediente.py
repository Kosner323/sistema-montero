# -*- coding: utf-8 -*-
"""
TEST: Verificacion de Creacion de Expediente de Usuario
========================================================
Prueba que al crear un usuario se genere automaticamente:
- Carpeta principal en USUARIOS/{numeroId}
- 10 subcarpetas obligatorias
- Archivo datos_usuario.txt
- Firma digital (opcional)
"""

import os
import requests
import json
from datetime import datetime

# =====================================================
# CONFIGURACION DE LA PRUEBA
# =====================================================
BASE_URL = "http://127.0.0.1:5000"  # Ajusta el puerto si es diferente
ENDPOINT = f"{BASE_URL}/api/usuarios"
RUTA_BASE_EXPEDIENTES = r"D:\Mi-App-React\MONTERO_NEGOCIO\MONTERO_TOTAL\USUARIOS"

# Datos de prueba (Modo JSON)
USUARIO_PRUEBA = {
    "nombre_completo": "Juan Carlos Perez Lopez",
    "email": "juan.perez.test@gmail.com",
    "tipo_documento": "CC",
    "numero_documento": "9999999999",  # ID unico para prueba
    "telefono": "3001234567",
    "cargo": "Auxiliar Administrativo",
    "empresa_nit": "999999999"
}

# =====================================================
# FUNCIONES DE VALIDACION
# =====================================================

def verificar_estructura_carpetas(numero_id):
    """Verifica que se hayan creado todas las carpetas y archivos"""
    print("\n" + "="*60)
    print("VERIFICANDO ESTRUCTURA DE EXPEDIENTE")
    print("="*60)

    carpeta_usuario = os.path.join(RUTA_BASE_EXPEDIENTES, str(numero_id))

    # 1. Verificar carpeta principal
    if os.path.exists(carpeta_usuario):
        print(f"[OK] Carpeta principal creada: {carpeta_usuario}")
    else:
        print(f"[ERROR] Carpeta principal NO existe: {carpeta_usuario}")
        return False

    # 2. Verificar subcarpetas obligatorias
    subcarpetas_esperadas = [
        "BENEFICIARIOS",
        "DEPURACIONES",
        "EMPRESAS_AFILIADAS",
        "INCAPACIDADES",
        "MORAS",
        "NOVEDADES",
        "PLANILLAS",
        "RECIBOS",
        "TUTELAS",
        "USUARIOS Y CONTRASEÑAS"
    ]

    print("\nVerificando subcarpetas:")
    for subcarpeta in subcarpetas_esperadas:
        ruta = os.path.join(carpeta_usuario, subcarpeta)
        if os.path.exists(ruta):
            print(f"   [OK] {subcarpeta}")
        else:
            print(f"   [FALTA] {subcarpeta}")
            return False

    # 3. Verificar archivo datos_usuario.txt
    archivo_datos = os.path.join(carpeta_usuario, "datos_usuario.txt")
    if os.path.exists(archivo_datos):
        print(f"\n[OK] Archivo datos_usuario.txt creado")
        # Mostrar primeras lineas
        with open(archivo_datos, "r", encoding="utf-8") as f:
            primeras_lineas = f.read(300)
            print(f"   Contenido (primeras lineas):\n{primeras_lineas}...")
    else:
        print(f"[ERROR] datos_usuario.txt NO existe")
        return False

    # 4. Listar todos los archivos y carpetas creados
    print(f"\nEstructura completa generada:")
    for root, dirs, files in os.walk(carpeta_usuario):
        nivel = root.replace(carpeta_usuario, '').count(os.sep)
        indent = ' ' * 2 * nivel
        print(f'{indent}[DIR] {os.path.basename(root)}/')
        subindent = ' ' * 2 * (nivel + 1)
        for file in files:
            print(f'{subindent}[FILE] {file}')

    return True


def crear_usuario_prueba():
    """Crea un usuario de prueba usando el endpoint"""
    print("\n" + "="*60)
    print("INICIANDO PRUEBA DE CREACION DE USUARIO")
    print("="*60)
    print(f"Endpoint: {ENDPOINT}")
    print(f"Datos de prueba: {json.dumps(USUARIO_PRUEBA, indent=2, ensure_ascii=False)}")

    try:
        # Hacer POST request
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            ENDPOINT,
            json=USUARIO_PRUEBA,
            headers=headers,
            timeout=10
        )

        print(f"\nRespuesta del servidor:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")

        if response.status_code in [200, 201]:
            print("\n[OK] Usuario creado exitosamente en la base de datos")
            return True
        elif response.status_code == 409:
            print("\n[AVISO] El usuario ya existe (esto es normal si ya corriste la prueba antes)")
            print("   Continuando con la verificacion de carpetas...")
            return True
        else:
            print(f"\n[ERROR] Error al crear usuario: {response.status_code}")
            print(f"   Detalles: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("\n[ERROR] No se pudo conectar al servidor Flask")
        print("   Asegurate de que el servidor este corriendo en http://127.0.0.1:5000")
        print("   Ejecuta: python src/dashboard/app.py")
        return False
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
        return False


def limpiar_usuario_prueba():
    """Elimina la carpeta de prueba para poder repetir el test"""
    numero_id = USUARIO_PRUEBA["numero_documento"]
    carpeta_usuario = os.path.join(RUTA_BASE_EXPEDIENTES, str(numero_id))

    if os.path.exists(carpeta_usuario):
        import shutil
        respuesta = input(f"\nDeseas eliminar la carpeta de prueba {numero_id}? (s/n): ")
        if respuesta.lower() == 's':
            shutil.rmtree(carpeta_usuario)
            print(f"[OK] Carpeta eliminada: {carpeta_usuario}")
        else:
            print("[INFO] Carpeta conservada para inspeccion manual")


# =====================================================
# EJECUCION DE LA PRUEBA
# =====================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("TEST DE GENERACION DE EXPEDIENTES DE USUARIO")
    print("="*60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Paso 1: Crear usuario
    if not crear_usuario_prueba():
        print("\n[FALLO] PRUEBA FALLIDA: No se pudo crear el usuario")
        exit(1)

    # Paso 2: Verificar estructura de carpetas
    numero_id = USUARIO_PRUEBA["numero_documento"]
    if verificar_estructura_carpetas(numero_id):
        print("\n" + "="*60)
        print("PRUEBA EXITOSA!")
        print("="*60)
        print("[OK] Usuario creado en base de datos")
        print("[OK] Carpeta principal creada")
        print("[OK] 10 subcarpetas creadas")
        print("[OK] Archivo datos_usuario.txt generado")
        print("\nEL SISTEMA DE EXPEDIENTES FUNCIONA CORRECTAMENTE!")

        # Preguntar si desea limpiar
        limpiar_usuario_prueba()
    else:
        print("\n" + "="*60)
        print("PRUEBA FALLIDA")
        print("="*60)
        print("[ERROR] La estructura de expediente NO se genero correctamente")
        print("   Revisa los logs del servidor Flask para mas detalles")
        exit(1)
