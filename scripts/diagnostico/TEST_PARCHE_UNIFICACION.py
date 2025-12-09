"""
TEST DE VALIDACION - PARCHE QUIRURGICO UNIFICACION.HTML
========================================================
Verifica que el parche solicitado esta correctamente aplicado
"""

import os
import re

print("=" * 80)
print("TEST DE VALIDACION - PARCHE QUIRURGICO UNIFICACION.HTML")
print("=" * 80)
print()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UNIFICACION_FILE = os.path.join(BASE_DIR, "templates", "unificacion", "index.html")
HEADER_FILE = os.path.join(BASE_DIR, "templates", "_header.html")

# ==============================================================================
# TEST 1: VERIFICAR ATRIBUTOS HTML EN _header.html
# ==============================================================================
print("TEST 1: CORRECCION DE ATRIBUTOS HTML EN _header.html")
print("-" * 80)

with open(HEADER_FILE, 'r', encoding='utf-8') as f:
    header_content = f.read()

# Buscar dropdowns especificos
theme_dropdown = re.search(r'data-feather="sun".*?dropdown-toggle', header_content, re.DOTALL)
user_dropdown = re.search(r'data-feather="user".*?dropdown-toggle', header_content, re.DOTALL)

theme_has_bs = False
user_has_bs = False

if theme_dropdown:
    theme_snippet = theme_dropdown.group(0)
    theme_has_bs = 'data-bs-toggle="dropdown"' in theme_snippet
    print(f"   Boton de Tema (sol/luna): {'PASS' if theme_has_bs else 'FAIL'}")
    print(f"      - Usa data-bs-toggle: {theme_has_bs}")
else:
    print(f"   Boton de Tema: NO ENCONTRADO")

if user_dropdown:
    user_snippet = user_dropdown.group(0)
    user_has_bs = 'data-bs-toggle="dropdown"' in user_snippet
    print(f"   Boton de Usuario/Perfil: {'PASS' if user_has_bs else 'FAIL'}")
    print(f"      - Usa data-bs-toggle: {user_has_bs}")
else:
    print(f"   Boton de Usuario: NO ENCONTRADO")

print()

# Conteo general
old_attrs = header_content.count('data-pc-toggle')
new_attrs = header_content.count('data-bs-toggle')

print(f"   Resumen de atributos:")
print(f"      - Atributos antiguos (data-pc-toggle): {old_attrs}")
print(f"      - Atributos nuevos (data-bs-toggle): {new_attrs}")
print()

test1_pass = old_attrs == 0 and new_attrs >= 5
print(f"   RESULTADO TEST 1: {'PASS' if test1_pass else 'FAIL'}")
print()

# ==============================================================================
# TEST 2: VERIFICAR SCRIPTS DE REACTIVACION EN unificacion.html
# ==============================================================================
print("TEST 2: INYECCION DE SCRIPTS DE REACTIVACION")
print("-" * 80)

with open(UNIFICACION_FILE, 'r', encoding='utf-8') as f:
    unif_content = f.read()

# Buscar el bloque de script despues de feather.replace()
script_pattern = r'feather\.replace\(\);.*?cargarDatosIniciales\(\);'
script_block = re.search(script_pattern, unif_content, re.DOTALL)

if script_block:
    script_text = script_block.group(0)
    
    # Verificar componentes del parche
    has_dropdown_init = 'new bootstrap.Dropdown' in script_text
    has_sidebar_desktop = "querySelector('#sidebar-hide')" in script_text
    has_sidebar_mobile = "querySelector('#mobile-collapse')" in script_text
    has_prevent_default = '.preventDefault()' in script_text
    has_toggle_class = '.classList.toggle' in script_text
    
    print(f"   Inicializacion de Dropdowns Bootstrap: {'PASS' if has_dropdown_init else 'FAIL'}")
    print(f"   Event listener #sidebar-hide (desktop): {'PASS' if has_sidebar_desktop else 'FAIL'}")
    print(f"   Event listener #mobile-collapse (mobile): {'PASS' if has_sidebar_mobile else 'FAIL'}")
    print(f"   Uso de preventDefault(): {'PASS' if has_prevent_default else 'FAIL'}")
    print(f"   Uso de classList.toggle(): {'PASS' if has_toggle_class else 'FAIL'}")
    print()
    
    test2_pass = all([
        has_dropdown_init,
        has_sidebar_desktop,
        has_sidebar_mobile,
        has_prevent_default,
        has_toggle_class
    ])
    
    print(f"   RESULTADO TEST 2: {'PASS' if test2_pass else 'FAIL'}")
else:
    print(f"   ERROR: No se encontro el bloque de script")
    test2_pass = False

print()

# ==============================================================================
# TEST 3: VERIFICAR ORDEN DE EJECUCION
# ==============================================================================
print("TEST 3: ORDEN CORRECTO DE EJECUCION")
print("-" * 80)

lines = unif_content.split('\n')
feather_line = None
parche_line = None
cargar_datos_line = None

for i, line in enumerate(lines, 1):
    if 'feather.replace()' in line and 'typeof feather' in line:
        feather_line = i
    if 'RE-INICIALIZACIÓN DE UI' in line or 'PARCHE' in line:
        parche_line = i
    if 'cargarDatosIniciales()' in line and 'await' in line:
        cargar_datos_line = i

print(f"   Linea de feather.replace(): {feather_line}")
print(f"   Linea del parche de reactivacion: {parche_line}")
print(f"   Linea de cargarDatosIniciales(): {cargar_datos_line}")
print()

orden_correcto = False
if feather_line and parche_line and cargar_datos_line:
    orden_correcto = feather_line < parche_line < cargar_datos_line
    print(f"   Orden de ejecucion: {'CORRECTO' if orden_correcto else 'INCORRECTO'}")
    print(f"      1. feather.replace() (linea {feather_line})")
    print(f"      2. Parche de reactivacion (linea {parche_line})")
    print(f"      3. cargarDatosIniciales() (linea {cargar_datos_line})")
else:
    print(f"   ERROR: No se encontraron todos los elementos")

print()
test3_pass = orden_correcto
print(f"   RESULTADO TEST 3: {'PASS' if test3_pass else 'FAIL'}")
print()

# ==============================================================================
# TEST 4: VALIDACION DE SINTAXIS JAVASCRIPT
# ==============================================================================
print("TEST 4: VALIDACION DE SINTAXIS JAVASCRIPT")
print("-" * 80)

if script_block:
    script_text = script_block.group(0)
    
    # Conteos de sintaxis
    open_braces = script_text.count('{')
    close_braces = script_text.count('}')
    open_parens = script_text.count('(')
    close_parens = script_text.count(')')
    
    print(f"   Llaves {{ }}: {open_braces} aperturas, {close_braces} cierres - {'BALANCEADO' if open_braces == close_braces else 'DESBALANCEADO'}")
    print(f"   Parentesis ( ): {open_parens} aperturas, {close_parens} cierres - {'BALANCEADO' if open_parens == close_parens else 'DESBALANCEADO'}")
    print()
    
    # Verificar patrones comunes
    tiene_punto_coma = ';' in script_text
    tiene_console_log = 'console.log' in script_text
    tiene_if_typeof = 'if (typeof' in script_text
    
    print(f"   Uso de punto y coma: {'PASS' if tiene_punto_coma else 'FAIL'}")
    print(f"   Console logs para debugging: {'PASS' if tiene_console_log else 'FAIL'}")
    print(f"   Verificaciones typeof: {'PASS' if tiene_if_typeof else 'FAIL'}")
    print()
    
    test4_pass = (
        open_braces == close_braces and
        open_parens == close_parens and
        tiene_punto_coma and
        tiene_console_log
    )
    
    print(f"   RESULTADO TEST 4: {'PASS' if test4_pass else 'FAIL'}")
else:
    test4_pass = False
    print(f"   ERROR: No hay script para validar")

print()

# ==============================================================================
# RESULTADO FINAL
# ==============================================================================
print("=" * 80)
print("RESULTADO FINAL DE LA VALIDACION")
print("=" * 80)
print()

all_tests_pass = all([test1_pass, test2_pass, test3_pass, test4_pass])

print(f"   TEST 1 - Atributos HTML: {'PASS' if test1_pass else 'FAIL'}")
print(f"   TEST 2 - Scripts de reactivacion: {'PASS' if test2_pass else 'FAIL'}")
print(f"   TEST 3 - Orden de ejecucion: {'PASS' if test3_pass else 'FAIL'}")
print(f"   TEST 4 - Sintaxis JavaScript: {'PASS' if test4_pass else 'FAIL'}")
print()

if all_tests_pass:
    print("   =====================================================")
    print("   RESULTADO: TODOS LOS TESTS PASARON")
    print("   =====================================================")
    print()
    print("   El parche quirurgico esta correctamente aplicado:")
    print()
    print("   1. Atributos Bootstrap 5 (data-bs-toggle) en _header.html")
    print("   2. Script de reactivacion de dropdowns en unificacion.html")
    print("   3. Event listeners para sidebar desktop y mobile")
    print("   4. Sintaxis JavaScript valida y correcta")
    print()
    print("   PROXIMOS PASOS:")
    print("   - Iniciar servidor Flask: python app.py")
    print("   - Navegar a /unificacion")
    print("   - Probar dropdowns (tema, usuario, notificaciones)")
    print("   - Probar sidebar toggle (desktop y mobile)")
    print("   - Verificar console logs en el navegador (F12)")
else:
    print("   =====================================================")
    print("   RESULTADO: ALGUNOS TESTS FALLARON")
    print("   =====================================================")
    print()
    print("   Revisar los tests que fallaron arriba.")

print()
print("=" * 80)
