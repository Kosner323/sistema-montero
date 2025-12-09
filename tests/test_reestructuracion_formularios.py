#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de validación para la reestructuración del módulo de formularios.
Verifica que:
1. Los archivos de templates existan
2. Las rutas estén correctamente registradas
3. Los blueprints estén importados en app.py
"""

import os
import sys

# Colores para terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✓{RESET} {msg}")

def print_error(msg):
    print(f"{RED}✗{RESET} {msg}")

def print_info(msg):
    print(f"{BLUE}ℹ{RESET} {msg}")

def print_warning(msg):
    print(f"{YELLOW}⚠{RESET} {msg}")

def check_file_exists(filepath, description):
    """Verifica si un archivo existe."""
    if os.path.exists(filepath):
        print_success(f"{description} existe")
        return True
    else:
        print_error(f"{description} NO encontrado")
        return False

def check_blueprint_registration():
    """Verifica que bp_formularios_pages esté registrado en app.py."""
    app_path = "app.py"
    if not os.path.exists(app_path):
        print_error("app.py no encontrado")
        return False
    
    with open(app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ("from routes.formularios import bp_formularios, bp_formularios_pages", "Importación de bp_formularios_pages"),
        ("app.register_blueprint(bp_formularios_pages)", "Registro de bp_formularios_pages"),
    ]
    
    all_ok = True
    for pattern, description in checks:
        if pattern in content:
            print_success(description)
        else:
            print_error(f"{description} NO encontrado")
            all_ok = False
    
    return all_ok

def check_routes_file():
    """Verifica que formularios.py tenga las rutas correctas."""
    routes_path = "routes/formularios.py"
    if not os.path.exists(routes_path):
        print_error("routes/formularios.py no encontrado")
        return False
    
    with open(routes_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ("bp_formularios_pages = Blueprint", "Definición de bp_formularios_pages"),
        ('@bp_formularios_pages.route("/")', "Ruta / (index)"),
        ('@bp_formularios_pages.route("/generador")', "Ruta /generador"),
        ('render_template("formularios/index.html")', "Renderizado de index.html"),
        ('render_template("formularios/generador.html")', "Renderizado de generador.html"),
    ]
    
    all_ok = True
    for pattern, description in checks:
        if pattern in content:
            print_success(description)
        else:
            print_error(f"{description} NO encontrado")
            all_ok = False
    
    return all_ok

def main():
    print("\n" + "="*70)
    print("  VALIDACIÓN DE REESTRUCTURACIÓN - MÓDULO FORMULARIOS")
    print("="*70 + "\n")
    
    all_checks_passed = True
    
    # 1. Verificar archivos de templates
    print_info("1. Verificando archivos de templates...")
    template_checks = [
        ("templates/formularios/index.html", "index.html (Dashboard)"),
        ("templates/formularios/generador.html", "generador.html (Generador PDF)"),
    ]
    
    for filepath, description in template_checks:
        if not check_file_exists(filepath, description):
            all_checks_passed = False
    
    print()
    
    # 2. Verificar configuración de rutas
    print_info("2. Verificando configuración de rutas en formularios.py...")
    if not check_routes_file():
        all_checks_passed = False
    
    print()
    
    # 3. Verificar registro de blueprints
    print_info("3. Verificando registro de blueprints en app.py...")
    if not check_blueprint_registration():
        all_checks_passed = False
    
    print()
    
    # Resumen final
    print("="*70)
    if all_checks_passed:
        print_success("TODAS LAS VERIFICACIONES PASARON ✓")
        print_info("\nRutas disponibles:")
        print("  • GET /formularios         → Dashboard de Afiliaciones")
        print("  • GET /formularios/generador → Generador de PDF (nueva pestaña)")
        print("\nPuedes iniciar el servidor con:")
        print("  python app.py")
    else:
        print_error("ALGUNAS VERIFICACIONES FALLARON ✗")
        print_warning("\nRevisa los errores anteriores y corrige los archivos necesarios.")
    
    print("="*70 + "\n")
    
    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    sys.exit(main())
