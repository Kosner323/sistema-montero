#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para agregar polyfills de tema a todos los archivos HTML
Busca la línea que carga script.js y agrega los polyfills ANTES
"""
import sys
import os
import re

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Directorio de templates
templates_dir = os.path.join(os.path.dirname(__file__), 'src', 'dashboard', 'templates')

# Polyfills a insertar
polyfills_code = '''
    <script>
        // --- POLYFILLS PARA TEMA (Ejecutar ANTES de script.js) ---
        // Previene errores de ReferenceError cuando script.js intenta llamar estas funciones
        window.layout_change = window.layout_change || function() {};
        window.layout_theme_sidebar_change = window.layout_theme_sidebar_change || function() {};
        window.change_box_container = window.change_box_container || function() {};
        window.layout_caption_change = window.layout_caption_change || function() {};
        window.layout_rtl_change = window.layout_rtl_change || function() {};
        window.preset_change = window.preset_change || function() {};
        window.main_layout_change = window.main_layout_change || function() {};
    </script>
'''

def fix_html_file(filepath):
    """Agrega polyfills antes de script.js si no existen ya"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Verificar si ya tiene los polyfills
        if 'POLYFILLS PARA TEMA' in content or 'theme-polyfills.js' in content:
            return f"⏭️  SKIP (ya tiene polyfills)"

        # Buscar la línea que carga script.js
        pattern = r'(\s*<script\s+src="/assets/js/theme\.js"[^>]*></script>)'

        if re.search(pattern, content):
            # Insertar polyfills después de theme.js
            new_content = re.sub(
                pattern,
                r'\1' + polyfills_code,
                content,
                count=1
            )

            # Guardar archivo modificado
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)

            return "✅ ACTUALIZADO"
        else:
            return "⚠️  No encontró theme.js"

    except Exception as e:
        return f"❌ ERROR: {e}"

def process_all_templates():
    """Procesa todos los archivos HTML en templates"""
    print("=" * 80)
    print("🔧 AGREGANDO POLYFILLS DE TEMA A TODOS LOS ARCHIVOS HTML")
    print("=" * 80)

    count_updated = 0
    count_skipped = 0
    count_errors = 0

    # Procesar archivos en el directorio principal
    for root, dirs, files in os.walk(templates_dir):
        for filename in files:
            if filename.endswith('.html'):
                filepath = os.path.join(root, filename)
                relative_path = os.path.relpath(filepath, templates_dir)

                result = fix_html_file(filepath)
                print(f"{result:20} {relative_path}")

                if "ACTUALIZADO" in result:
                    count_updated += 1
                elif "SKIP" in result:
                    count_skipped += 1
                elif "ERROR" in result:
                    count_errors += 1

    print("\n" + "=" * 80)
    print("📊 RESUMEN")
    print("=" * 80)
    print(f"✅ Archivos actualizados: {count_updated}")
    print(f"⏭️  Archivos omitidos (ya tenían polyfills): {count_skipped}")
    print(f"⚠️  Archivos sin theme.js o con errores: {count_errors}")
    print("\n💡 Los polyfills previenen el error: 'main_layout_change is not defined'")
    print("=" * 80)

if __name__ == '__main__':
    process_all_templates()
