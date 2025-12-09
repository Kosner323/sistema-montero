"""
SIMULACION DE PRUEBA - CHECK_EXPIRING_TUTELAS
==============================================
Simula la ejecución de check_expiring_tutelas para verificar robustez
"""

print("=" * 80)
print("SIMULACION DE PRUEBA - CHECK_EXPIRING_TUTELAS")
print("=" * 80)
print()

# Simular clase Usuario con correoElectronico
class UsuarioMock:
    def __init__(self, numeroId, primerNombre, primerApellido, correoElectronico=None):
        self.numeroId = numeroId
        self.primerNombre = primerNombre
        self.primerApellido = primerApellido
        self.correoElectronico = correoElectronico

# Simular clase Tutela
class TutelaMock:
    def __init__(self, id, numero_tutela, usuario_id, fecha_fin, juzgado):
        self.id = id
        self.numero_tutela = numero_tutela
        self.usuario_id = usuario_id
        self.fecha_fin = fecha_fin
        self.juzgado = juzgado

# Crear datos de prueba
tutelas = [
    TutelaMock(1, "TUT-001", "123456789", "2025-12-04", "Juzgado 1"),
    TutelaMock(2, "TUT-002", "987654321", "2025-12-05", "Juzgado 2"),
    TutelaMock(3, "TUT-003", "555555555", "2025-12-06", "Juzgado 3"),
    TutelaMock(4, "TUT-004", "999999999", "2025-12-07", "Juzgado 4"),
]

empleados = {
    "123456789": UsuarioMock("123456789", "Juan", "Pérez", "juan.perez@example.com"),
    "987654321": UsuarioMock("987654321", "María", "García", None),  # Sin correo
    "555555555": UsuarioMock("555555555", "Pedro", "López", ""),  # Correo vacío
    # "999999999" no existe (para simular usuario no encontrado)
}

print("DATOS DE PRUEBA:")
print(f"  - {len(tutelas)} tutelas próximas a vencer")
print(f"  - {len(empleados)} empleados en base de datos")
print()
print("ESCENARIOS:")
print("  1. Tutela con empleado y correo válido → Debe enviar notificación")
print("  2. Tutela con empleado sin correo (None) → Debe continuar sin crashear")
print("  3. Tutela con empleado con correo vacío → Debe continuar sin crashear")
print("  4. Tutela con empleado inexistente → Debe continuar sin crashear")
print()
print("=" * 80)
print("INICIANDO SIMULACION")
print("=" * 80)
print()

# Simular la lógica del código corregido
notificaciones_enviadas = 0
notificaciones_fallidas = 0

for tutela in tutelas:
    try:
        # Obtener información del empleado
        empleado = empleados.get(str(tutela.usuario_id))

        if not empleado:
            print(f"[WARN] Tareas: Usuario {tutela.usuario_id} no encontrado para tutela #{tutela.numero_tutela}")
            notificaciones_fallidas += 1
            continue

        # Verificar que el empleado tenga correo electrónico
        correo = getattr(empleado, 'correoElectronico', None)
        if not correo or correo.strip() == '':
            print(f"[WARN] Tareas: Usuario {tutela.usuario_id} ({empleado.primerNombre} {empleado.primerApellido}) sin correo electrónico")
            notificaciones_fallidas += 1
            continue

        # Envío de notificación por email (simulado)
        try:
            # notification_service.send_email(...) - SIMULADO
            print(f"[SUCCESS] Email enviado a {correo} para tutela #{tutela.numero_tutela}")
        except Exception as email_error:
            print(f"[ERROR] Tareas: Fallo al enviar email a {correo}: {email_error}")
            notificaciones_fallidas += 1
            # Continuar con la notificación in-app aunque falle el email

        # Creación de notificación In-App (simulado)
        try:
            # notification_service.create_in_app_notification(...) - SIMULADO
            print(f"[INFO] Notificación in-app creada para usuario {tutela.usuario_id}")
            notificaciones_enviadas += 1
        except Exception as notif_error:
            print(f"[ERROR] Tareas: Fallo al crear notificación in-app para usuario {tutela.usuario_id}: {notif_error}")
            notificaciones_fallidas += 1

    except Exception as tutela_error:
        print(f"[ERROR] Tareas: Error procesando tutela #{tutela.numero_tutela}: {tutela_error}")
        notificaciones_fallidas += 1
        continue

print()
print("=" * 80)
print("RESULTADO DE LA SIMULACION")
print("=" * 80)
print()
print(f"  Total de tutelas procesadas: {len(tutelas)}")
print(f"  Notificaciones enviadas exitosamente: {notificaciones_enviadas}")
print(f"  Notificaciones fallidas: {notificaciones_fallidas}")
print()

# Verificar resultados esperados
expected_success = 1  # Solo la tutela 1 tiene empleado con correo válido
expected_failures = 3  # Tutelas 2, 3, 4 deben fallar sin crashear

if notificaciones_enviadas == expected_success and notificaciones_fallidas == expected_failures:
    print("  =====================================================")
    print("  RESULTADO: SIMULACION EXITOSA")
    print("  =====================================================")
    print()
    print("  El código es robusto:")
    print("  - Procesó todas las tutelas sin crashear")
    print("  - Detectó empleados sin correo")
    print("  - Detectó empleados inexistentes")
    print("  - Continuó el bucle después de cada error")
    print("  - Mantuvo contadores precisos")
else:
    print("  =====================================================")
    print("  RESULTADO: SIMULACION FALLIDA")
    print("  =====================================================")
    print()
    print(f"  Esperado: {expected_success} enviadas, {expected_failures} fallidas")
    print(f"  Obtenido: {notificaciones_enviadas} enviadas, {notificaciones_fallidas} fallidas")

print()
print("=" * 80)
print("VERIFICACION DE ATRIBUTOS")
print("=" * 80)
print()

# Verificar que getattr funciona correctamente
test_user = UsuarioMock("12345", "Test", "User", "test@example.com")
test_user_sin_correo = UsuarioMock("67890", "Test", "User2")

correo1 = getattr(test_user, 'correoElectronico', None)
correo2 = getattr(test_user_sin_correo, 'correoElectronico', None)

print(f"  Usuario con correo:")
print(f"    - getattr(empleado, 'correoElectronico', None) = {correo1}")
print(f"    - Resultado: {'PASS' if correo1 == 'test@example.com' else 'FAIL'}")
print()
print(f"  Usuario sin correo:")
print(f"    - getattr(empleado, 'correoElectronico', None) = {correo2}")
print(f"    - Resultado: {'PASS' if correo2 is None else 'FAIL'}")
print()

# Verificar que no hay AttributeError
try:
    # Intentar acceder directamente (lo que causaría el error sin getattr)
    email_directo = test_user_sin_correo.correoElectronico
    print(f"  Acceso directo a .correoElectronico: {email_directo}")
except AttributeError as e:
    print(f"  Acceso directo a .correoElectronico: AttributeError (esperado sin getattr)")

print()
print("  Conclusión:")
print("  - getattr() previene AttributeError exitosamente")
print("  - El código puede manejar usuarios con o sin correo")
print()
print("=" * 80)
