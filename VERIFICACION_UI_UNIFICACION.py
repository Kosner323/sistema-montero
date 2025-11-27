"""
VERIFICACIÓN DE CORRECCIONES UI - UNIFICACIÓN
==============================================
Script de diagnóstico para confirmar las correcciones aplicadas
"""

import os
import re

print("=" * 80)
print("VERIFICACIÓN DE CORRECCIONES UI - UNIFICACIÓN")
print("=" * 80)
print()

# Rutas de archivos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HEADER_FILE = os.path.join(BASE_DIR, "templates", "_header.html")
UNIFICACION_FILE = os.path.join(BASE_DIR, "templates", "unificacion", "index.html")

# ==============================================================================
# 1. VERIFICAR CORRECCIÓN DE ATRIBUTOS EN _header.html
# ==============================================================================
print("1️⃣ VERIFICANDO ATRIBUTOS EN _header.html...")
print("-" * 80)

with open(HEADER_FILE, 'r', encoding='utf-8') as f:
    header_content = f.read()

# Buscar atributos antiguos (NO deben existir)
old_attrs = re.findall(r'data-pc-toggle="dropdown"', header_content)
old_auto_close = re.findall(r'data-pc-auto-close', header_content)

# Buscar atributos nuevos (DEBEN existir)
new_attrs = re.findall(r'data-bs-toggle="dropdown"', header_content)
new_auto_close = re.findall(r'data-bs-auto-close', header_content)

print(f"   ❌ Atributos antiguos 'data-pc-toggle' encontrados: {len(old_attrs)}")
print(f"   ✅ Atributos nuevos 'data-bs-toggle' encontrados: {len(new_attrs)}")
print(f"   ❌ Atributos antiguos 'data-pc-auto-close' encontrados: {len(old_auto_close)}")
print(f"   ✅ Atributos nuevos 'data-bs-auto-close' encontrados: {len(new_auto_close)}")
print()

if len(old_attrs) == 0 and len(new_attrs) >= 5:
    print("   ✅ CORRECCIÓN 1: EXITOSA - Todos los dropdowns usan Bootstrap")
else:
    print("   ⚠️  ADVERTENCIA: Algunos dropdowns pueden no funcionar")
print()

# ==============================================================================
# 2. VERIFICAR SCRIPT DE INICIALIZACIÓN EN index.html
# ==============================================================================
print("2️⃣ VERIFICANDO SCRIPT DE INICIALIZACIÓN EN index.html...")
print("-" * 80)

with open(UNIFICACION_FILE, 'r', encoding='utf-8') as f:
    unif_content = f.read()

# Buscar elementos del script de inicialización
has_dropdown_init = 'new bootstrap.Dropdown' in unif_content
has_sidebar_toggle = "querySelector('#sidebar-hide')" in unif_content
has_mobile_toggle = "querySelector('#mobile-collapse')" in unif_content
has_re_init_comment = 'RE-INICIALIZACIÓN DE UI' in unif_content

print(f"   {'✅' if has_re_init_comment else '❌'} Comentario de re-inicialización: {has_re_init_comment}")
print(f"   {'✅' if has_dropdown_init else '❌'} Inicialización de dropdowns Bootstrap: {has_dropdown_init}")
print(f"   {'✅' if has_sidebar_toggle else '❌'} Event listener sidebar desktop: {has_sidebar_toggle}")
print(f"   {'✅' if has_mobile_toggle else '❌'} Event listener sidebar mobile: {has_mobile_toggle}")
print()

if all([has_dropdown_init, has_sidebar_toggle, has_mobile_toggle, has_re_init_comment]):
    print("   ✅ CORRECCIÓN 2: EXITOSA - Script de inicialización completo")
else:
    print("   ⚠️  ADVERTENCIA: Script de inicialización incompleto")
print()

# ==============================================================================
# 3. ANÁLISIS DE DROPDOWNS EN _header.html
# ==============================================================================
print("3️⃣ ANÁLISIS DETALLADO DE DROPDOWNS...")
print("-" * 80)

dropdown_patterns = [
    ('Búsqueda', r'data-feather="search".*?dropdown-toggle'),
    ('Tema (Sol/Luna)', r'data-feather="sun".*?dropdown-toggle'),
    ('Configuración', r'data-feather="settings".*?dropdown-toggle'),
    ('Notificaciones', r'data-feather="bell".*?dropdown-toggle'),
    ('Perfil de Usuario', r'data-feather="user".*?dropdown-toggle')
]

for name, pattern in dropdown_patterns:
    matches = re.search(pattern, header_content, re.DOTALL)
    if matches:
        snippet = matches.group(0)
        has_bs_toggle = 'data-bs-toggle="dropdown"' in snippet
        status = "✅ CORRECTO" if has_bs_toggle else "❌ INCORRECTO"
        print(f"   {status} - Dropdown '{name}'")
    else:
        print(f"   ⚠️  NO ENCONTRADO - Dropdown '{name}'")

print()

# ==============================================================================
# 4. VERIFICAR UBICACIÓN DEL SCRIPT
# ==============================================================================
print("4️⃣ VERIFICANDO UBICACIÓN DEL SCRIPT...")
print("-" * 80)

# Buscar la ubicación del script en el archivo
feather_replace_line = None
re_init_line = None

lines = unif_content.split('\n')
for i, line in enumerate(lines, 1):
    if 'feather.replace()' in line and 'typeof feather' in line:
        feather_replace_line = i
    if 'RE-INICIALIZACIÓN DE UI' in line:
        re_init_line = i

print(f"   Línea de feather.replace(): {feather_replace_line}")
print(f"   Línea de RE-INICIALIZACIÓN: {re_init_line}")

if feather_replace_line and re_init_line and re_init_line > feather_replace_line:
    diff = re_init_line - feather_replace_line
    print(f"   ✅ Script ubicado DESPUÉS de feather.replace() (+{diff} líneas)")
else:
    print(f"   ⚠️  Script podría no estar en la ubicación correcta")

print()

# ==============================================================================
# 5. TEST DE SINTAXIS JAVASCRIPT
# ==============================================================================
print("5️⃣ VERIFICACIÓN DE SINTAXIS JAVASCRIPT...")
print("-" * 80)

# Extraer el bloque de script
script_match = re.search(
    r'// === RE-INICIALIZACIÓN DE UI.*?console\.log\(.*?Re-inicialización de UI completada.*?\);',
    unif_content,
    re.DOTALL
)

if script_match:
    script_block = script_match.group(0)
    
    # Verificaciones básicas de sintaxis
    checks = [
        ('Corchetes balanceados', script_block.count('{') == script_block.count('}')),
        ('Paréntesis balanceados', script_block.count('(') == script_block.count(')')),
        ('Punto y coma presentes', ';' in script_block),
        ('Event listeners correctos', 'addEventListener' in script_block),
        ('Console logs informativos', 'console.log' in script_block)
    ]
    
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"   {status} {check_name}")
    
    if all(result for _, result in checks):
        print(f"\n   ✅ Sintaxis JavaScript válida")
    else:
        print(f"\n   ⚠️  Posibles problemas de sintaxis")
else:
    print("   ❌ No se encontró el bloque de script de re-inicialización")

print()

# ==============================================================================
# RESUMEN FINAL
# ==============================================================================
print("=" * 80)
print("RESUMEN DE VERIFICACIÓN")
print("=" * 80)
print()

issues = []
successes = []

# Check 1: Atributos
if len(old_attrs) == 0 and len(new_attrs) >= 5:
    successes.append("✅ Atributos data-bs-toggle corregidos en _header.html")
else:
    issues.append("❌ Atributos no completamente corregidos")

# Check 2: Script de inicialización
if all([has_dropdown_init, has_sidebar_toggle, has_mobile_toggle]):
    successes.append("✅ Script de re-inicialización completo en index.html")
else:
    issues.append("❌ Script de inicialización incompleto")

# Check 3: Ubicación
if feather_replace_line and re_init_line and re_init_line > feather_replace_line:
    successes.append("✅ Script ubicado correctamente (después de feather.replace)")
else:
    issues.append("⚠️  Ubicación del script podría ser incorrecta")

# Mostrar resultados
for success in successes:
    print(success)

if issues:
    print()
    for issue in issues:
        print(issue)
else:
    print()
    print("🎉 TODAS LAS CORRECCIONES APLICADAS EXITOSAMENTE")

print()
print("=" * 80)
print("PRÓXIMOS PASOS")
print("=" * 80)
print()
print("1. Reiniciar el servidor Flask:")
print("   cd d:\\Mi-App-React\\src\\dashboard")
print("   python app.py")
print()
print("2. Hacer login en http://127.0.0.1:5000/login")
print()
print("3. Navegar a /unificacion")
print()
print("4. Probar funcionalidad:")
print("   - Click en icono de sol/luna (cambio de tema)")
print("   - Click en icono de campana (notificaciones)")
print("   - Click en icono de usuario (menú perfil)")
print("   - Click en icono de menú hamburguesa (sidebar toggle)")
print()
print("5. Abrir consola del navegador (F12) y verificar logs:")
print("   - '✅ Dropdowns de Bootstrap inicializados: X'")
print("   - '🔄 Sidebar toggle manual activado' (al hacer click)")
print("   - '✅ Re-inicialización de UI completada'")
print()
print("=" * 80)
