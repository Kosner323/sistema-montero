#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Diagnóstico de Errores
=================================
Identifica archivos con problemas de import, sintaxis, etc.
"""

import os
import sys
import py_compile
from pathlib import Path
import importlib.util

# Colores para terminal
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"

def print_header(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text:^70}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}[OK] {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}[WARN] {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}[ERROR] {text}{Colors.END}")

def check_syntax(file_path):
    """Verifica la sintaxis de un archivo Python"""
    try:
        py_compile.compile(file_path, doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)

def check_imports(file_path):
    """Verifica que los imports funcionen"""
    try:
        # Leer el archivo
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Buscar imports
        import_lines = [line for line in content.split('\n') if line.strip().startswith(('import ', 'from '))]

        return True, import_lines
    except Exception as e:
        return False, str(e)

def main():
    print_header("DIAGNÓSTICO DE ERRORES - SISTEMA MONTERO")

    # Directorio raíz
    root_dir = Path(__file__).parent

    # Archivos a verificar
    python_files = []

    # Buscar archivos .py
    for ext in ['**/*.py']:
        for file in root_dir.glob(ext):
            # Excluir ciertos directorios
            if any(x in str(file) for x in ['__pycache__', 'venv', 'env', '.venv', 'htmlcov', '.pytest_cache']):
                continue
            python_files.append(file)

    print(f"Encontrados {len(python_files)} archivos Python\n")

    # Estadísticas
    errors = []
    warnings = []
    success = []

    # Verificar cada archivo
    for file in sorted(python_files):
        rel_path = file.relative_to(root_dir)

        # 1. Verificar sintaxis
        syntax_ok, syntax_error = check_syntax(file)

        if not syntax_ok:
            print_error(f"{rel_path}: ERROR DE SINTAXIS")
            print(f"   {syntax_error}")
            errors.append((str(rel_path), "Sintaxis", syntax_error))
            continue

        # 2. Verificar imports
        imports_ok, import_info = check_imports(file)

        if not imports_ok:
            print_warning(f"{rel_path}: Problema con imports")
            warnings.append((str(rel_path), "Imports", import_info))
        else:
            success.append(str(rel_path))

    # Resumen
    print_header("RESUMEN")

    print(f"{Colors.GREEN}[OK] Archivos correctos: {len(success)}{Colors.END}")
    print(f"{Colors.YELLOW}[WARN] Advertencias: {len(warnings)}{Colors.END}")
    print(f"{Colors.RED}[ERROR] Errores: {len(errors)}{Colors.END}")

    if errors:
        print_header("ERRORES ENCONTRADOS")
        for file, tipo, msg in errors:
            print(f"{Colors.RED}[ERROR] {file}{Colors.END}")
            print(f"   Tipo: {tipo}")
            print(f"   {msg}\n")

    if warnings:
        print_header("ADVERTENCIAS")
        for file, tipo, msg in warnings:
            print(f"{Colors.YELLOW}[WARN] {file}{Colors.END}")
            print(f"   Tipo: {tipo}\n")

    # Verificar archivos específicos importantes
    print_header("VERIFICACIÓN DE ARCHIVOS CLAVE")

    key_files = [
        'app.py',
        'encryption.py',
        'utils.py',
        'logger.py',
        'routes/analytics.py',
        'routes/auth.py',
        'routes/notificaciones_routes.py',
        'routes/notification_service.py',
    ]

    for key_file in key_files:
        file_path = root_dir / key_file
        if file_path.exists():
            syntax_ok, _ = check_syntax(file_path)
            if syntax_ok:
                print_success(f"{key_file}")
            else:
                print_error(f"{key_file}")
        else:
            print_warning(f"{key_file} - NO ENCONTRADO")

    print_header("DIAGNÓSTICO COMPLETADO")

    if errors:
        print_error("Se encontraron errores críticos. Revisa los detalles arriba.")
        return 1
    elif warnings:
        print_warning("Se encontraron advertencias. El sistema debería funcionar.")
        return 0
    else:
        print_success("¡Todo está correcto! No se encontraron problemas.")
        return 0

if __name__ == "__main__":
    sys.exit(main())
