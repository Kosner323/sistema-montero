"""
TEST DE VERIFICACION - CORRECCION CELERY TASKS
================================================
Verifica que las correcciones en celery_tasks.py sean correctas
"""

import os
import re
import ast

print("=" * 80)
print("TEST DE VERIFICACION - CORRECCION CELERY TASKS")
print("=" * 80)
print()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CELERY_FILE = os.path.join(BASE_DIR, "celery_tasks.py")
ORM_MODELS_FILE = os.path.join(BASE_DIR, "models", "orm_models.py")

# ==============================================================================
# TEST 1: VERIFICAR MODELO USUARIO
# ==============================================================================
print("TEST 1: VERIFICAR ATRIBUTO DE EMAIL EN MODELO USUARIO")
print("-" * 80)

with open(ORM_MODELS_FILE, 'r', encoding='utf-8') as f:
    orm_content = f.read()

# Buscar la definición de correoElectronico
correo_field = re.search(r'correoElectronico\s*=\s*Column', orm_content)
email_field = re.search(r'(?<!correo)email\s*=\s*Column', orm_content)

if correo_field:
    print("   PASS - Campo 'correoElectronico' encontrado en modelo Usuario")
else:
    print("   FAIL - Campo 'correoElectronico' NO encontrado")

if email_field:
    print("   WARNING - Campo 'email' encontrado (posible duplicado)")
else:
    print("   PASS - Campo 'email' NO existe (correcto)")

print()

# ==============================================================================
# TEST 2: VERIFICAR CORRECCIONES EN CELERY_TASKS.PY
# ==============================================================================
print("TEST 2: VERIFICAR CORRECCIONES EN celery_tasks.py")
print("-" * 80)

with open(CELERY_FILE, 'r', encoding='utf-8') as f:
    celery_content = f.read()

# Buscar usos incorrectos de .email
empleado_email_matches = re.findall(r'empleado\.email(?!\w)', celery_content)
usuario_email_matches = re.findall(r'Usuario\.email(?!\w)', celery_content)

print(f"   Usos incorrectos de 'empleado.email': {len(empleado_email_matches)}")
if empleado_email_matches:
    print(f"      FAIL - Aun existen {len(empleado_email_matches)} referencias a .email")
else:
    print(f"      PASS - No hay referencias incorrectas a empleado.email")

print(f"   Usos incorrectos de 'Usuario.email': {len(usuario_email_matches)}")
if usuario_email_matches:
    print(f"      FAIL - Aun existen {len(usuario_email_matches)} referencias a Usuario.email")
else:
    print(f"      PASS - No hay referencias incorrectas a Usuario.email")

print()

# Buscar usos correctos de correoElectronico
correo_electronico_matches = re.findall(r'correoElectronico', celery_content)
print(f"   Usos de 'correoElectronico': {len(correo_electronico_matches)}")
if len(correo_electronico_matches) >= 2:  # Al menos 2 (query + getattr)
    print(f"      PASS - Campo correcto 'correoElectronico' en uso")
else:
    print(f"      WARNING - Pocas referencias a correoElectronico")

print()

# ==============================================================================
# TEST 3: VERIFICAR MANEJO DE ERRORES ROBUSTO
# ==============================================================================
print("TEST 3: VERIFICAR MANEJO DE ERRORES ROBUSTO")
print("-" * 80)

# Buscar bloques try/except en check_expiring_tutelas
try_blocks = re.findall(r'try:', celery_content)
except_blocks = re.findall(r'except\s+\w+\s+as\s+\w+:', celery_content)

print(f"   Bloques 'try:' encontrados: {len(try_blocks)}")
print(f"   Bloques 'except ... as ...:' encontrados: {len(except_blocks)}")

# Verificar que hay try/except específicos
has_tutela_error = 'tutela_error' in celery_content
has_email_error = 'email_error' in celery_content
has_notif_error = 'notif_error' in celery_content

print()
print(f"   {'PASS' if has_tutela_error else 'FAIL'} - Manejo de error por tutela individual")
print(f"   {'PASS' if has_email_error else 'FAIL'} - Manejo de error en envío de email")
print(f"   {'PASS' if has_notif_error else 'FAIL'} - Manejo de error en notificación in-app")

print()

# ==============================================================================
# TEST 4: VERIFICAR USO DE GETATTR PARA SEGURIDAD
# ==============================================================================
print("TEST 4: VERIFICAR USO DE getattr() PARA ACCESO SEGURO")
print("-" * 80)

has_getattr = "getattr(empleado, 'correoElectronico', None)" in celery_content

if has_getattr:
    print("   PASS - Se usa getattr() para acceso seguro al atributo correoElectronico")
else:
    print("   WARNING - No se encontró getattr(), podría causar AttributeError")

print()

# ==============================================================================
# TEST 5: VERIFICAR CONTINUE EN BUCLE
# ==============================================================================
print("TEST 5: VERIFICAR USO DE 'continue' PARA NO ROMPER BUCLE")
print("-" * 80)

continue_count = celery_content.count('continue')

print(f"   Usos de 'continue': {continue_count}")
if continue_count >= 3:  # Al menos 3 (sin empleado, sin correo, error general)
    print("   PASS - El bucle continúa aunque falle un elemento individual")
else:
    print("   WARNING - Podría no haber suficientes 'continue' para robustez")

print()

# ==============================================================================
# TEST 6: VERIFICAR CONTADORES DE ÉXITO/FALLO
# ==============================================================================
print("TEST 6: VERIFICAR CONTADORES DE NOTIFICACIONES")
print("-" * 80)

has_enviadas_counter = 'notificaciones_enviadas' in celery_content
has_fallidas_counter = 'notificaciones_fallidas' in celery_content

if has_enviadas_counter and has_fallidas_counter:
    print("   PASS - Contadores de notificaciones enviadas/fallidas implementados")
else:
    print("   FAIL - Faltan contadores de éxito/fallo")

print()

# ==============================================================================
# TEST 7: VERIFICAR SINTAXIS PYTHON
# ==============================================================================
print("TEST 7: VERIFICAR SINTAXIS PYTHON")
print("-" * 80)

try:
    ast.parse(celery_content)
    print("   PASS - Sintaxis Python válida (sin errores de parsing)")
except SyntaxError as e:
    print(f"   FAIL - Error de sintaxis: {e}")

print()

# ==============================================================================
# TEST 8: VERIFICAR LOGS INFORMATIVOS
# ==============================================================================
print("TEST 8: VERIFICAR LOGS INFORMATIVOS")
print("-" * 80)

success_logs = re.findall(r'\[SUCCESS\]', celery_content)
warn_logs = re.findall(r'\[WARN\]', celery_content)
error_logs = re.findall(r'\[ERROR\]', celery_content)

print(f"   Logs [SUCCESS]: {len(success_logs)}")
print(f"   Logs [WARN]: {len(warn_logs)}")
print(f"   Logs [ERROR]: {len(error_logs)}")

if len(success_logs) > 0 and len(warn_logs) > 0 and len(error_logs) > 0:
    print("   PASS - Logs completos con diferentes niveles de severidad")
else:
    print("   WARNING - Podría faltar algún tipo de log")

print()

# ==============================================================================
# RESUMEN FINAL
# ==============================================================================
print("=" * 80)
print("RESUMEN DE VERIFICACION")
print("=" * 80)
print()

all_checks = [
    correo_field is not None and email_field is None,  # Modelo correcto
    len(empleado_email_matches) == 0,  # Sin .email
    len(usuario_email_matches) == 0,  # Sin Usuario.email
    len(correo_electronico_matches) >= 2,  # Usa correoElectronico
    has_tutela_error and has_email_error and has_notif_error,  # Manejo de errores
    has_getattr,  # Acceso seguro
    continue_count >= 3,  # Continue en bucle
    has_enviadas_counter and has_fallidas_counter  # Contadores
]

passed = sum(all_checks)
total = len(all_checks)

print(f"   Tests pasados: {passed}/{total}")
print()

if passed == total:
    print("   =====================================================")
    print("   RESULTADO: TODAS LAS CORRECCIONES APLICADAS")
    print("   =====================================================")
    print()
    print("   Cambios implementados:")
    print("   1. empleado.email → empleado.correoElectronico")
    print("   2. Usuario.email → Usuario.correoElectronico")
    print("   3. getattr() para acceso seguro al atributo")
    print("   4. try/except individual por tutela")
    print("   5. try/except para envío de email")
    print("   6. try/except para notificación in-app")
    print("   7. continue para no romper bucle si falla un elemento")
    print("   8. Contadores de notificaciones_enviadas/fallidas")
    print("   9. Logs informativos [SUCCESS], [WARN], [ERROR]")
    print()
    print("   PROXIMO PASO:")
    print("   Ejecutar prueba con:")
    print("   python -c \"from celery_tasks import check_expiring_tutelas; check_expiring_tutelas()\"")
else:
    print("   =====================================================")
    print("   RESULTADO: ALGUNAS VERIFICACIONES FALLARON")
    print("   =====================================================")
    print()
    print("   Revisar los tests que fallaron arriba.")

print()
print("=" * 80)
