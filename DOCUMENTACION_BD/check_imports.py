#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificar que todos los archivos de rutas importen get_db_connection correctamente
"""
import sys
import os
import re

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

routes_dir = os.path.join(os.path.dirname(__file__), 'src', 'dashboard', 'routes')

print("=" * 80)
print("🔍 VERIFICACIÓN DE IMPORTS EN ARCHIVOS DE RUTAS")
print("=" * 80)

files_with_issues = []

for filename in sorted(os.listdir(routes_dir)):
    if filename.endswith('.py') and not filename.startswith('__'):
        filepath = os.path.join(routes_dir, filename)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Verificar si usa get_db_connection
            uses_get_db_connection = 'get_db_connection()' in content

            # Verificar si importa get_db_connection
            imports_it = re.search(r'from.*utils import.*get_db_connection', content) is not None

            if uses_get_db_connection and not imports_it:
                print(f"❌ {filename:30} USA get_db_connection pero NO lo importa")
                files_with_issues.append(filename)
            elif uses_get_db_connection and imports_it:
                print(f"✅ {filename:30} Correcto")
            else:
                print(f"⏭️  {filename:30} No usa get_db_connection")

        except Exception as e:
            print(f"⚠️  {filename:30} Error al leer: {e}")

print("\n" + "=" * 80)
if files_with_issues:
    print(f"❌ ARCHIVOS CON PROBLEMAS: {len(files_with_issues)}")
    for f in files_with_issues:
        print(f"   • {f}")
else:
    print("✅ TODOS LOS ARCHIVOS ESTÁN CORRECTOS")
print("=" * 80)
