"""
DIAGNOSTICO DE DROPDOWNS - UNIFICACION.HTML
============================================
Verifica que los dropdowns de Bootstrap estan funcionando
"""

import os
import re

print("=" * 80)
print("DIAGNOSTICO DE DROPDOWNS - UNIFICACION.HTML")
print("=" * 80)
print()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UNIFICACION_FILE = os.path.join(BASE_DIR, "templates", "unificacion", "index.html")

with open(UNIFICACION_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

print("VERIFICACION 1: Bootstrap CDN")
print("-" * 80)
bootstrap_cdn = re.search(r'bootstrap@[\d.]+/dist/js/bootstrap\.bundle\.min\.js', content)
if bootstrap_cdn:
    print(f"   OK - Bootstrap CDN encontrado: {bootstrap_cdn.group(0)}")
else:
    print(f"   ERROR - No se encontro el CDN de Bootstrap")
print()

print("VERIFICACION 2: Script de Inicializacion")
print("-" * 80)
has_setTimeout = 'setTimeout(function()' in content
has_dispose = 'dispose()' in content
has_new_dropdown = 'new bootstrap.Dropdown' in content
has_boundary = "boundary: 'viewport'" in content

print(f"   {'OK' if has_setTimeout else 'FAIL'} - Usa setTimeout para esperar carga")
print(f"   {'OK' if has_dispose else 'FAIL'} - Destruye instancias previas (dispose)")
print(f"   {'OK' if has_new_dropdown else 'FAIL'} - Crea nuevas instancias de Dropdown")
print(f"   {'OK' if has_boundary else 'FAIL'} - Configura boundary viewport")
print()

print("VERIFICACION 3: Configuracion de Dropdowns")
print("-" * 80)
config_match = re.search(r'new bootstrap\.Dropdown\([^,]+,\s*{([^}]+)}', content)
if config_match:
    config_text = config_match.group(1)
    print(f"   Configuracion encontrada:")
    for line in config_text.strip().split('\n'):
        print(f"      {line.strip()}")
else:
    print(f"   WARNING - No se encontro configuracion de dropdowns")
print()

print("VERIFICACION 4: Timeout Value")
print("-" * 80)
timeout_match = re.search(r'setTimeout\([^,]+,\s*(\d+)\)', content)
if timeout_match:
    timeout_val = timeout_match.group(1)
    print(f"   Timeout configurado: {timeout_val}ms")
    if int(timeout_val) >= 500:
        print(f"   OK - Tiempo suficiente para cargar Bootstrap")
    else:
        print(f"   WARNING - Podria ser insuficiente, recomendado >= 500ms")
else:
    print(f"   ERROR - No se encontro timeout")
print()

print("VERIFICACION 5: Console Logs de Debug")
print("-" * 80)
logs = re.findall(r"console\.log\(['\"]([^'\"]+)['\"]", content)
bootstrap_logs = [log for log in logs if 'Bootstrap' in log or 'Dropdowns' in log or 'UI' in log]
print(f"   Logs de debug encontrados: {len(bootstrap_logs)}")
for log in bootstrap_logs:
    print(f"      - {log}")
print()

print("=" * 80)
print("RECOMENDACIONES")
print("=" * 80)
print()
print("1. Abre la pagina /unificacion en el navegador")
print("2. Presiona F12 para abrir Developer Tools")
print("3. Ve a la pestaña Console")
print("4. Busca estos mensajes:")
print("   - 'Iniciando re-inicializacion de UI...'")
print("   - 'Bootstrap detectado, inicializando dropdowns...'")
print("   - 'Dropdowns de Bootstrap inicializados: X'")
print("   - 'Re-inicializacion de UI completada'")
print()
print("5. Si ves errores como:")
print("   - 'Bootstrap is not defined'")
print("   - 'bootstrap.Dropdown is not a constructor'")
print("   Significa que Bootstrap no se cargo correctamente")
print()
print("6. Prueba hacer click en:")
print("   - Icono de sol/luna (tema)")
print("   - Icono de campana (notificaciones)")
print("   - Icono de usuario (perfil)")
print()
print("=" * 80)
