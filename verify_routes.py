#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Verificación de Rutas
Ejecuta este script para verificar que todas las rutas estén registradas correctamente
"""

import sys
import os

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def verify_routes():
    """Verifica que todas las rutas estén registradas correctamente"""

    print("=" * 80)
    print("VERIFICACIÓN DE RUTAS - SISTEMA MONTERO")
    print("=" * 80)

    app = create_app()

    print("\n📋 TODAS LAS RUTAS REGISTRADAS:\n")

    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': ', '.join(sorted(rule.methods - {'HEAD', 'OPTIONS'})),
            'path': rule.rule
        })

    # Ordenar por path
    routes.sort(key=lambda x: x['path'])

    # Buscar específicamente la ruta de configuración
    config_route_found = False
    user_settings_routes = []

    for route in routes:
        # Filtrar rutas estáticas
        if route['path'].startswith('/static'):
            continue

        # Buscar rutas de configuración
        if 'configuracion' in route['path'] or 'user_settings' in route['endpoint']:
            config_route_found = True
            user_settings_routes.append(route)
            print(f"✅ {route['methods']:12} {route['path']:50} -> {route['endpoint']}")
        else:
            print(f"   {route['methods']:12} {route['path']:50} -> {route['endpoint']}")

    print("\n" + "=" * 80)
    print("🔍 VERIFICACIÓN DE MÓDULO DE CONFIGURACIÓN")
    print("=" * 80)

    if config_route_found:
        print("\n✅ ÉXITO: El módulo de configuración está correctamente registrado\n")
        print("Rutas encontradas:")
        for route in user_settings_routes:
            print(f"  • {route['methods']:12} {route['path']:50}")

        print("\n💡 Para acceder:")
        print(f"  1. Inicia sesión en: http://localhost:5000/login")
        print(f"  2. Luego accede a:   http://localhost:5000/configuracion")

    else:
        print("\n❌ ERROR: No se encontró la ruta /configuracion")
        print("\nPosibles causas:")
        print("  1. El servidor no se reinició después de agregar el blueprint")
        print("  2. Hay un error en el archivo user_settings.py")
        print("  3. El blueprint no está correctamente importado en app.py")

        print("\nSoluciones:")
        print("  1. Reinicia el servidor Flask")
        print("  2. Verifica que app.py tenga:")
        print("     - from routes.user_settings import user_settings_bp")
        print("     - app.register_blueprint(user_settings_bp)")

    print("\n" + "=" * 80)
    print(f"Total de rutas registradas: {len([r for r in routes if not r['path'].startswith('/static')])}")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    verify_routes()
