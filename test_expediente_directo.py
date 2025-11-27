# -*- coding: utf-8 -*-
"""
TEST DIRECTO: Verificacion de Funcion generar_expediente_usuario
=================================================================
Prueba directa de la funcion sin pasar por el endpoint HTTP
"""

import sys
import os

# Agregar el path del proyecto
sys.path.insert(0, r'D:\Mi-App-React\src\dashboard')

# Importar la funcion directamente
from routes.usuarios import generar_expediente_usuario

# =====================================================
# DATOS DE PRUEBA
# =====================================================

USUARIO_PRUEBA = {
    "numeroId": "9999999999",
    "tipoId": "CC",
    "primerNombre": "Juan",
    "segundoNombre": "Carlos",
    "primerApellido": "Perez",
    "segundoApellido": "Lopez",
    "correoElectronico": "juan.perez.test@gmail.com",
    "telefonoCelular": "3001234567",
    "sexoBiologico": "Masculino",
    "fechaNacimiento": "1990-01-15",
    "nacionalidad": "Colombiana",
    "direccion": "Calle 123 # 45-67",
    "empresa_nit": "999999999"
}

# =====================================================
# EJECUTAR PRUEBA
# =====================================================

print("="*60)
print("TEST DIRECTO DE generar_expediente_usuario()")
print("="*60)

print("\nDatos de prueba:")
for key, value in USUARIO_PRUEBA.items():
    print(f"  {key}: {value}")

print("\n" + "="*60)
print("EJECUTANDO FUNCION...")
print("="*60)

# Llamar a la funcion
resultado = generar_expediente_usuario(USUARIO_PRUEBA, firma_base64=None)

# Mostrar resultado
print("\n" + "="*60)
print("RESULTADO:")
print("="*60)
print(f"Success: {resultado['success']}")
print(f"Path: {resultado['path']}")
print(f"\nArchivos creados ({len(resultado['files_created'])}):")
for archivo in resultado['files_created']:
    print(f"  [OK] {archivo}")

if resultado['errors']:
    print(f"\nErrores ({len(resultado['errors'])}):")
    for error in resultado['errors']:
        print(f"  [ERROR] {error}")

# Verificar que la carpeta existe
if os.path.exists(resultado['path']):
    print("\n" + "="*60)
    print("VERIFICACION DE ESTRUCTURA:")
    print("="*60)

    # Listar contenido
    for root, dirs, files in os.walk(resultado['path']):
        nivel = root.replace(resultado['path'], '').count(os.sep)
        indent = '  ' * nivel
        print(f"{indent}[DIR] {os.path.basename(root)}/")
        subindent = '  ' * (nivel + 1)
        for file in files:
            print(f"{subindent}[FILE] {file}")

    print("\n" + "="*60)
    print("PRUEBA EXITOSA!")
    print("="*60)
    print("[OK] La funcion generar_expediente_usuario() funciona correctamente")
    print(f"[OK] Carpeta creada en: {resultado['path']}")

    # Preguntar si desea eliminar
    respuesta = input("\nDeseas eliminar la carpeta de prueba? (s/n): ")
    if respuesta.lower() == 's':
        import shutil
        shutil.rmtree(resultado['path'])
        print(f"[OK] Carpeta eliminada")
    else:
        print("[INFO] Carpeta conservada para inspeccion manual")
else:
    print("\n[ERROR] La carpeta NO se creo!")
