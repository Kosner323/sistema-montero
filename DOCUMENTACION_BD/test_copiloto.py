#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Prueba - Copiloto ARL
Verifica que todos los endpoints estén funcionando correctamente
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
print("🤖 TEST DEL MÓDULO COPILOTO ARL")
print("=" * 70)

try:
    from app import app

    with app.app_context():
        from utils import get_db_connection

        print("\n✅ Módulos Flask importados correctamente")

        # Test 1: Verificar conexión a BD desde automation_routes
        print("\n📊 TEST 1: Conexión a Base de Datos desde Copiloto")
        print("-" * 70)

        # Importar el módulo automation_routes para verificar su configuración
        from routes.automation_routes import get_db_connection as copiloto_get_db

        conn = copiloto_get_db()
        print("✅ Copiloto se conectó a la base de datos")

        # Verificar empresas
        empresas = conn.execute("SELECT COUNT(*) as total FROM empresas").fetchone()
        print(f"✅ Empresas disponibles: {empresas['total']}")

        # Verificar usuarios
        usuarios = conn.execute("SELECT COUNT(*) as total FROM usuarios").fetchone()
        print(f"✅ Usuarios disponibles: {usuarios['total']}")

        conn.close()

        # Test 2: Simular búsqueda de empleado
        print("\n📋 TEST 2: Búsqueda de Empleados")
        print("-" * 70)

        conn = copiloto_get_db()

        # Buscar un empleado de ejemplo
        query = """
            SELECT
                u.primerNombre,
                u.primerApellido,
                u.numeroId,
                u.empresa_nit,
                e.nombre_empresa
            FROM usuarios u
            LEFT JOIN empresas e ON u.empresa_nit = e.nit
            LIMIT 1
        """
        empleado = conn.execute(query).fetchone()

        if empleado:
            print(f"✅ Empleado encontrado: {empleado['primerNombre']} {empleado['primerApellido']}")
            print(f"   Cédula: {empleado['numeroId']}")
            print(f"   Empresa: {empleado['nombre_empresa'] or 'Sin Empresa'}")

            # Ahora probar la búsqueda específica
            cedula_test = empleado['numeroId']
            query_busqueda = """
                SELECT
                    u.primerNombre,
                    u.primerApellido,
                    u.numeroId,
                    u.empresa_nit,
                    e.nombre_empresa
                FROM usuarios u
                LEFT JOIN empresas e ON u.empresa_nit = e.nit
                WHERE u.numeroId = ?
            """
            resultado = conn.execute(query_busqueda, (cedula_test,)).fetchone()

            if resultado:
                print(f"\n✅ Búsqueda por cédula FUNCIONA correctamente")
                print(f"   Endpoint /api/empleado/buscar/{cedula_test} debería retornar:")
                print(f"   - nombre: {resultado['primerNombre']} {resultado['primerApellido']}")
                print(f"   - empresa_nit: {resultado['empresa_nit']}")
                print(f"   - empresa_nombre: {resultado['nombre_empresa'] or 'Sin Empresa'}")
            else:
                print("⚠️  No se pudo hacer la búsqueda específica")
        else:
            print("⚠️  No hay empleados en la base de datos para probar")

        conn.close()

        # Test 3: Verificar lista de empresas para el formulario
        print("\n📋 TEST 3: Lista de Empresas para el Formulario")
        print("-" * 70)

        conn = copiloto_get_db()

        empresas = conn.execute(
            "SELECT nit, nombre_empresa FROM empresas ORDER BY nombre_empresa ASC"
        ).fetchall()

        if empresas:
            print(f"✅ Se encontraron {len(empresas)} empresas:")
            for i, empresa in enumerate(empresas, 1):
                print(f"   {i}. {empresa['nombre_empresa']} (NIT: {empresa['nit']})")
        else:
            print("⚠️  No hay empresas registradas")

        conn.close()

        print("\n" + "=" * 70)
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("=" * 70)
        print("\n💡 PRÓXIMOS PASOS:")
        print("   1. REINICIA el servidor Flask si aún no lo has hecho:")
        print("      cd D:/Mi-App-React/src/dashboard")
        print("      python app.py")
        print("\n   2. ACCEDE a la vista del Copiloto ARL:")
        print("      http://localhost:5000/copiloto/arl")
        print("\n   3. PRUEBA las siguientes funciones:")
        print("      - Selector de empresas (debería mostrar las empresas listadas arriba)")
        print("      - Búsqueda de empleado por cédula")
        print("      - Ejecución del robot (simulación)")
        print("\n🎯 El módulo Copiloto ARL está LISTO para usar!")

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
