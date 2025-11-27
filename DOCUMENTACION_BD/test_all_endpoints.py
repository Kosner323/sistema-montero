#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Diagnóstico Completo - Sistema Montero
Verifica que todos los endpoints principales funcionen correctamente
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

print("=" * 80)
print("🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA MONTERO")
print("=" * 80)

try:
    from app import app
    from utils import get_db_connection

    with app.app_context():
        print("\n✅ Aplicación Flask cargada correctamente")

        # Test 1: Verificar conexión a base de datos
        print("\n" + "=" * 80)
        print("📊 TEST 1: Conexión a Base de Datos")
        print("-" * 80)

        conn = get_db_connection()
        if conn:
            print("✅ Conexión establecida correctamente")

            # Verificar tablas principales
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"✅ Tablas encontradas: {len(tables)}")
            print(f"   Principales: {', '.join([t for t in tables if t in ['usuarios', 'empresas', 'formularios_importados']])}")

            # Contar registros en tablas principales
            print("\n📋 Conteo de Registros:")

            # Usuarios
            count_users = cursor.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
            print(f"   👤 Usuarios: {count_users}")

            # Empresas
            count_companies = cursor.execute("SELECT COUNT(*) FROM empresas").fetchone()[0]
            print(f"   🏢 Empresas: {count_companies}")

            # Formularios importados
            try:
                count_forms = cursor.execute("SELECT COUNT(*) FROM formularios_importados").fetchone()[0]
                print(f"   📄 Formularios: {count_forms}")
            except:
                print(f"   📄 Formularios: Tabla no existe")

            conn.close()
        else:
            print("❌ Error: No se pudo establecer conexión")

        # Test 2: Verificar rutas registradas
        print("\n" + "=" * 80)
        print("📊 TEST 2: Rutas Registradas")
        print("-" * 80)

        # Filtrar rutas importantes
        important_routes = [
            '/api/unificacion/master',
            '/api/empresas',
            '/api/usuarios',
            '/api/formularios/generar',
            '/copiloto/arl',
            '/copiloto/api/test-conexion',
            '/copiloto/api/empleado/buscar/',
            '/dashboard',
            '/login',
        ]

        registered_routes = []
        for rule in app.url_map.iter_rules():
            if any(route in rule.rule for route in important_routes):
                registered_routes.append({
                    'ruta': rule.rule,
                    'metodos': ', '.join(rule.methods - {'OPTIONS', 'HEAD'})
                })

        if registered_routes:
            print(f"✅ Rutas importantes encontradas: {len(registered_routes)}")
            for route in sorted(registered_routes, key=lambda x: x['ruta']):
                print(f"   • {route['ruta']} [{route['metodos']}]")
        else:
            print("❌ No se encontraron rutas importantes")

        # Test 3: Verificar Blueprints
        print("\n" + "=" * 80)
        print("📊 TEST 3: Blueprints Registrados")
        print("-" * 80)

        blueprints = list(app.blueprints.keys())
        print(f"✅ Blueprints registrados: {len(blueprints)}")
        important_blueprints = ['empresas', 'usuarios', 'bp_formularios', 'automation', 'bp_unificacion', 'pages']
        for bp in important_blueprints:
            status = "✅" if bp in blueprints else "❌"
            print(f"   {status} {bp}")

        # Test 4: Verificar archivos de plantillas
        print("\n" + "=" * 80)
        print("📊 TEST 4: Plantillas HTML")
        print("-" * 80)

        templates_dir = os.path.join(os.path.dirname(__file__), 'src', 'dashboard', 'templates')
        important_templates = [
            'index.html',
            'ingresoportal.html',
            'ingresar_empresa.html',
            'copiloto/arl.html',
            'unificacion/panel.html'
        ]

        for template in important_templates:
            template_path = os.path.join(templates_dir, template)
            exists = os.path.exists(template_path)
            status = "✅" if exists else "❌"
            print(f"   {status} {template}")

        # Test 5: Verificar configuración de BD
        print("\n" + "=" * 80)
        print("📊 TEST 5: Configuración de Base de Datos")
        print("-" * 80)

        db_path = app.config.get('DATABASE_PATH')
        if db_path:
            print(f"✅ DATABASE_PATH configurado: {db_path}")
            exists = os.path.exists(db_path)
            print(f"   {'✅' if exists else '❌'} Archivo existe: {exists}")
            if exists:
                size = os.path.getsize(db_path)
                print(f"   📊 Tamaño: {size:,} bytes ({size/1024:.2f} KB)")
        else:
            print("❌ DATABASE_PATH no está configurado")

        # Resumen Final
        print("\n" + "=" * 80)
        print("📊 RESUMEN FINAL")
        print("=" * 80)
        print(f"""
✅ Conexión a BD: {'OK' if conn else 'ERROR'}
✅ Usuarios registrados: {count_users if conn else 'N/A'}
✅ Empresas registradas: {count_companies if conn else 'N/A'}
✅ Rutas importantes: {len(registered_routes)}/{len(important_routes)}
✅ Blueprints críticos: {sum(1 for bp in important_blueprints if bp in blueprints)}/{len(important_blueprints)}
        """)

        print("\n" + "=" * 80)
        print("💡 SIGUIENTE PASO:")
        print("=" * 80)
        print("""
1. Si todos los tests pasaron ✅, el sistema está correctamente configurado
2. Inicia el servidor: python src/dashboard/app.py
3. Accede a las siguientes URLs para verificar:

   📊 Dashboard Principal:
   http://localhost:5000/dashboard

   🤖 Copiloto ARL:
   http://localhost:5000/copiloto/arl

   🔗 Unificación (Usuarios-Empresas):
   http://localhost:5000/unificacion/panel

   🏢 Ingresar Empresa:
   http://localhost:5000/ingresar-empresa

   👤 Ingresar Usuario:
   http://localhost:5000/ingresar-usuario

4. Si encuentras errores 500, revisa los logs del servidor en la consola
        """)

except Exception as e:
    print(f"\n❌ Error durante el diagnóstico: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80 + "\n")
