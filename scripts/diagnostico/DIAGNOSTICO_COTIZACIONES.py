# -*- coding: utf-8 -*-
"""
DIAGNÓSTICO COMPLETO - MÓDULO COTIZACIONES
==========================================
Verifica la configuración de seguridad y permisos del módulo de cotizaciones.
"""

import sys
import os

# Agregar el directorio dashboard al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*80)
print("DIAGNÓSTICO DEL MÓDULO COTIZACIONES")
print("="*80)
print()

# 1. VERIFICAR IMPORTACIÓN DEL BLUEPRINT
print("1️⃣ VERIFICANDO IMPORTACIÓN DEL BLUEPRINT...")
try:
    from routes.cotizaciones import bp_cotizaciones
    print(f"   ✅ Blueprint importado correctamente")
    print(f"   📦 Nombre: {bp_cotizaciones.name}")
    print(f"   🔗 URL Prefix: {bp_cotizaciones.url_prefix}")
    print()
except Exception as e:
    print(f"   ❌ ERROR al importar blueprint: {e}")
    import traceback
    traceback.print_exc()
    print()

# 2. VERIFICAR RUTAS REGISTRADAS
print("2️⃣ VERIFICANDO RUTAS REGISTRADAS EN EL BLUEPRINT...")
try:
    from routes.cotizaciones import bp_cotizaciones
    print(f"   📋 Rutas registradas:")
    for rule in bp_cotizaciones.url_map.iter_rules() if hasattr(bp_cotizaciones, 'url_map') else []:
        print(f"      - {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
    
    # Si no tiene url_map, intentar ver las funciones registradas
    if not hasattr(bp_cotizaciones, 'url_map'):
        print("   ℹ️  El blueprint no está registrado aún en la app")
        print("   📋 Rutas definidas en el blueprint (sin registrar):")
        # Listar las view_functions
        if hasattr(bp_cotizaciones, 'deferred_functions'):
            for func in bp_cotizaciones.deferred_functions:
                print(f"      - {func}")
    print()
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print()

# 3. VERIFICAR REGISTRO EN APP.PY
print("3️⃣ VERIFICANDO REGISTRO EN APP.PY...")
try:
    import app
    from routes.cotizaciones import bp_cotizaciones as bp_expected
    
    # Crear instancia de app
    flask_app = app.create_app()
    
    # Verificar si el blueprint está registrado
    blueprint_registered = False
    for bp_name, bp_obj in flask_app.blueprints.items():
        if bp_name == 'bp_cotizaciones' or bp_obj == bp_expected:
            blueprint_registered = True
            print(f"   ✅ Blueprint registrado como: '{bp_name}'")
            print(f"   🔗 URL Prefix: {bp_obj.url_prefix}")
            break
    
    if not blueprint_registered:
        print(f"   ❌ Blueprint NO está registrado en la app")
        print(f"   📋 Blueprints registrados:")
        for bp_name in flask_app.blueprints.keys():
            print(f"      - {bp_name}")
    print()
    
    # 4. VERIFICAR RUTAS DE LA APP
    print("4️⃣ VERIFICANDO RUTAS DE LA APP...")
    print("   📋 Rutas relacionadas con 'cotizaciones':")
    found_routes = False
    for rule in flask_app.url_map.iter_rules():
        if 'cotizaciones' in rule.rule.lower() or 'simulador' in rule.rule.lower() or 'pila' in rule.rule.lower():
            found_routes = True
            methods = ', '.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
            print(f"      - {rule.rule:<50} [{methods}]  → {rule.endpoint}")
    
    if not found_routes:
        print("   ⚠️  No se encontraron rutas de cotizaciones/simulador")
    print()
    
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print()

# 5. VERIFICAR DECORADOR LOGIN_REQUIRED
print("5️⃣ VERIFICANDO DECORADOR LOGIN_REQUIRED...")
try:
    from utils import login_required
    print(f"   ✅ Decorador login_required importado correctamente")
    print(f"   📝 Función: {login_required.__name__}")
    print()
    
    # Verificar el código del decorador
    import inspect
    source = inspect.getsource(login_required)
    
    # Buscar restricciones
    if 'ALLOWED' in source or 'WHITELIST' in source or 'PROTECTED' in source:
        print("   ⚠️  POSIBLE RESTRICCIÓN ENCONTRADA EN LOGIN_REQUIRED:")
        lines = source.split('\n')
        for i, line in enumerate(lines):
            if 'ALLOWED' in line or 'WHITELIST' in line or 'PROTECTED' in line:
                print(f"      Línea {i+1}: {line.strip()}")
        print()
    else:
        print("   ✅ No se encontraron restricciones de blueprints en login_required")
        print()
    
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print()

# 6. VERIFICAR ESTRUCTURA DE SESSION
print("6️⃣ VERIFICANDO CONFIGURACIÓN DE SESSION...")
try:
    from app import create_app
    flask_app = create_app()
    
    print(f"   📋 Configuración de sesión:")
    print(f"      - SECRET_KEY: {'***' if flask_app.config.get('SECRET_KEY') else '❌ NO CONFIGURADA'}")
    print(f"      - SESSION_COOKIE_NAME: {flask_app.config.get('SESSION_COOKIE_NAME', 'session')}")
    print(f"      - SESSION_COOKIE_SECURE: {flask_app.config.get('SESSION_COOKIE_SECURE', False)}")
    print(f"      - SESSION_COOKIE_HTTPONLY: {flask_app.config.get('SESSION_COOKIE_HTTPONLY', True)}")
    print(f"      - SESSION_COOKIE_SAMESITE: {flask_app.config.get('SESSION_COOKIE_SAMESITE', 'Lax')}")
    print(f"      - PERMANENT_SESSION_LIFETIME: {flask_app.config.get('PERMANENT_SESSION_LIFETIME', 'default')}")
    print()
    
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print()

# 7. VERIFICAR ENDPOINTS ESPECÍFICOS
print("7️⃣ VERIFICANDO ENDPOINTS ESPECÍFICOS...")
try:
    from app import create_app
    flask_app = create_app()
    
    endpoints_to_check = [
        '/api/cotizaciones',
        '/api/cotizaciones/simulador',
        '/api/cotizaciones/simular-pila',
        '/api/empresas'
    ]
    
    print(f"   📋 Verificando existencia de endpoints:")
    with flask_app.test_request_context():
        for endpoint in endpoints_to_check:
            try:
                # Intentar hacer match de la ruta
                adapter = flask_app.url_map.bind('')
                match = adapter.match(endpoint, method='GET')
                print(f"      ✅ {endpoint:<40} → {match[0]}")
            except Exception as e:
                print(f"      ❌ {endpoint:<40} → NO ENCONTRADO")
    print()
    
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print()

# 8. TEST DE AUTENTICACIÓN SIMULADA
print("8️⃣ TEST DE AUTENTICACIÓN SIMULADA...")
try:
    from app import create_app
    flask_app = create_app()
    
    with flask_app.test_client() as client:
        # Intentar acceder sin autenticación
        print("   📝 Intentando acceder a /api/cotizaciones/simulador sin autenticación...")
        response = client.get('/api/cotizaciones/simulador')
        print(f"      Status Code: {response.status_code}")
        print(f"      Response: {response.get_json() if response.is_json else response.data[:100]}")
        
        if response.status_code == 401:
            print("      ✅ Protección funcionando correctamente (401 esperado)")
        elif response.status_code == 404:
            print("      ❌ Ruta no encontrada (404) - EL PROBLEMA ESTÁ AQUÍ")
        elif response.status_code == 302:
            print(f"      ✅ Redirección a login (302): {response.location}")
        else:
            print(f"      ⚠️  Código inesperado: {response.status_code}")
        print()
        
        # Intentar con sesión simulada
        print("   📝 Intentando acceder CON sesión activa simulada...")
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'test_user'
        
        response = client.get('/api/cotizaciones/simulador')
        print(f"      Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("      ✅ Acceso exitoso con sesión activa")
        elif response.status_code == 404:
            print("      ❌ Ruta no encontrada (404) - BLUEPRINT NO REGISTRADO")
        else:
            print(f"      ⚠️  Código inesperado: {response.status_code}")
            print(f"      Response: {response.get_json() if response.is_json else response.data[:200]}")
        print()
    
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print()

# RESUMEN FINAL
print("="*80)
print("DIAGNÓSTICO COMPLETADO")
print("="*80)
print()
print("📊 RESUMEN:")
print("   Si ves '❌ Ruta no encontrada (404)' en el test, el problema es:")
print("   → El blueprint NO está registrado correctamente en app.py")
print()
print("   Si ves '✅ Protección funcionando (401)' sin sesión:")
print("   → El decorador @login_required está funcionando")
print()
print("   Si ves '✅ Acceso exitoso (200)' con sesión:")
print("   → TODO funciona correctamente, el problema está en el frontend/cookies")
print()
print("🔍 ACCIONES RECOMENDADAS:")
print("   1. Verificar que bp_cotizacion está en app.py línea 229")
print("   2. Verificar que no hay comentarios (#) en esa línea")
print("   3. Reiniciar el servidor Flask")
print("   4. Limpiar cookies del navegador")
print("   5. Verificar que el login guarda user_id en session")
print()
