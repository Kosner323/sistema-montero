#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Diagnóstico - Probar Endpoints DENTRO del contexto de Flask
=====================================================================
"""

import sys
import os

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Agregar el path del dashboard al PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'dashboard'))

print("=" * 70)
print("🔍 DIAGNÓSTICO DE ENDPOINTS - Portal Montero (Contexto Flask)")
print("=" * 70)

try:
    # Importar la app de Flask
    from app import app
    from utils import get_db_connection

    print("✅ Módulos Flask importados correctamente")

    # Ejecutar dentro del contexto de la aplicación
    with app.app_context():
        print("\n📊 TEST 1: Conexión a Base de Datos (Contexto Flask)")
        print("-" * 70)

        conn = get_db_connection()
        print(f"✅ Conexión establecida exitosamente")

        # Probar consulta de usuarios
        usuarios = conn.execute("SELECT COUNT(*) as total FROM usuarios").fetchone()
        print(f"✅ Total de usuarios en BD: {usuarios['total']}")

        # Probar consulta de empresas
        empresas = conn.execute("SELECT COUNT(*) as total FROM empresas").fetchone()
        print(f"✅ Total de empresas en BD: {empresas['total']}")

        # Probar consulta de usuarios con columnas específicas
        print("\n📋 TEST 2: Consulta de Usuarios (columnas específicas)")
        print("-" * 70)
        usuarios_sample = conn.execute("""
            SELECT id, primerNombre, primerApellido, numeroId, correoElectronico, empresa_nit
            FROM usuarios
            LIMIT 3
        """).fetchall()

        if usuarios_sample:
            print(f"✅ Consulta exitosa - Muestra de {len(usuarios_sample)} usuarios:")
            for i, u in enumerate(usuarios_sample, 1):
                nombre_completo = f"{u['primerNombre']} {u['primerApellido']}"
                print(f"   {i}. {nombre_completo} (ID: {u['numeroId']})")
        else:
            print("⚠️  No hay usuarios en la base de datos")

        # Probar consulta de empresas
        print("\n📋 TEST 3: Consulta de Empresas")
        print("-" * 70)
        empresas_sample = conn.execute("""
            SELECT nit, nombre_empresa
            FROM empresas
            LIMIT 3
        """).fetchall()

        if empresas_sample:
            print(f"✅ Consulta exitosa - Muestra de {len(empresas_sample)} empresas:")
            for i, e in enumerate(empresas_sample, 1):
                print(f"   {i}. {e['nombre_empresa']} (NIT: {e['nit']})")
        else:
            print("⚠️  No hay empresas en la base de datos")

        conn.close()

        print("\n" + "=" * 70)
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("=" * 70)
        print("\n💡 CONCLUSIÓN:")
        print("   - La base de datos está accesible")
        print("   - Las consultas SQL funcionan correctamente")
        print("   - Los datos están disponibles")
        print("   - La conexión funciona correctamente en contexto Flask\n")
        print("🚀 PRÓXIMO PASO:")
        print("   1. REINICIA el servidor Flask (Ctrl+C y ejecutar: python src/dashboard/app.py)")
        print("   2. PRUEBA acceder a /usuarios/gestion y /empresas desde el navegador")
        print("   3. VERIFICA que los selectores ahora muestren datos")

except ImportError as ie:
    print(f"❌ Error importando módulos: {ie}")
    print("   Asegúrate de estar en el directorio correcto del proyecto")
    import traceback
    traceback.print_exc()

except Exception as e:
    print(f"❌ Error durante las pruebas: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
