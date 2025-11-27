#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Diagnóstico - Endpoint /copiloto/arl
Verifica qué está pasando con la carga de empresas
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
print("🔍 DIAGNÓSTICO DEL ENDPOINT /copiloto/arl")
print("=" * 70)

try:
    from app import app

    with app.app_context():
        print("\n📊 TEST 1: Verificar función arl() del blueprint automation")
        print("-" * 70)

        # Importar el blueprint
        from routes.automation_routes import automation_bp, get_db_connection

        # Simular la ejecución de la ruta /copiloto/arl
        print("✅ Blueprint automation_bp importado correctamente")

        # Conectar a la base de datos usando la misma función que usa automation_routes
        conn = get_db_connection()
        print("✅ Conexión a BD establecida desde automation_routes")

        # Ejecutar la misma consulta que usa la vista
        empresas = conn.execute(
            "SELECT nit, nombre_empresa FROM empresas ORDER BY nombre_empresa ASC"
        ).fetchall()

        print(f"\n📋 Resultados de la consulta:")
        print(f"Total de empresas encontradas: {len(empresas)}")

        if empresas:
            print("\nEmpresas que DEBERÍAN aparecer en el selector:")
            for i, empresa in enumerate(empresas, 1):
                print(f"   {i}. {empresa['nombre_empresa']} (NIT: {empresa['nit']})")
        else:
            print("⚠️  No se encontraron empresas en la consulta")

        conn.close()

        # Test 2: Verificar si la ruta está registrada
        print("\n📊 TEST 2: Verificar rutas registradas")
        print("-" * 70)

        copiloto_routes = [rule for rule in app.url_map.iter_rules() if '/copiloto' in rule.rule]

        if copiloto_routes:
            print("✅ Rutas del Copiloto registradas:")
            for route in copiloto_routes:
                print(f"   - {route.rule} [{', '.join(route.methods - {'OPTIONS', 'HEAD'})}]")
        else:
            print("❌ No hay rutas del copiloto registradas")

        # Test 3: Verificar configuración de la BD en automation_routes
        print("\n📊 TEST 3: Verificar ruta de BD que usa automation_routes")
        print("-" * 70)

        # Intentar obtener la ruta real que está usando
        import sqlite3
        test_conn = get_db_connection()

        # SQLite no tiene una forma directa de obtener la ruta, pero podemos verificar
        cursor = test_conn.execute("PRAGMA database_list")
        db_info = cursor.fetchall()

        for db in db_info:
            print(f"Base de datos conectada: {db[2]}")

        test_conn.close()

        print("\n" + "=" * 70)
        print("💡 SIGUIENTE PASO:")
        print("=" * 70)
        print("\n1. REINICIA el servidor Flask completamente:")
        print("   - Presiona Ctrl+C en la terminal del servidor")
        print("   - Ejecuta nuevamente: python src/dashboard/app.py")
        print("\n2. ACCEDE a la ruta con sesión iniciada:")
        print("   - Primero haz login en: http://localhost:5000/login")
        print("   - Luego accede a: http://localhost:5000/copiloto/arl")
        print("\n3. VERIFICA en la consola del navegador (F12) si hay errores JavaScript")
        print("\n⚠️  Si el problema persiste, envíame:")
        print("   - Screenshot de la página")
        print("   - Logs del servidor Flask")
        print("   - Errores de la consola del navegador\n")

except Exception as e:
    print(f"❌ Error durante el diagnóstico: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
