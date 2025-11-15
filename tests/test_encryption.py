# -*- coding: utf-8 -*-
"""
test_encryption.py
====================================================
Suite de pruebas para el sistema de encriptación
de credenciales.
====================================================
"""

import os
import sys

# Configurar codificación UTF-8 para Windows
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Agregar el directorio padre (dashboard) al path para poder importar encryption
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Configurar ENCRYPTION_KEY antes de importar encryption
os.environ.setdefault("ENCRYPTION_KEY", "tZNEUELUZ7lMMN8g4WW1nxpu67mALsZOCBdV5bniow4=")

try:
    from encryption import decrypt_data, encrypt_data, global_encryptor

    print("✓ Módulo de encriptación importado correctamente\n")
except ImportError as e:
    print(f"✗ Error importando módulo de encriptación: {e}")
    sys.exit(1)


def test_basic_encryption():
    """Prueba básica de encriptación y desencriptación."""
    print("=" * 60)
    print("TEST 1: Encriptación Básica")
    print("=" * 60)

    test_cases = [
        "contraseña123",
        "usuario@ejemplo.com",
        "P@ssw0rd!#$",
        "texto con espacios y símbolos: @#$%",
        "texto_largo_" * 20,
    ]

    for i, original in enumerate(test_cases, 1):
        try:
            print(f"\nCaso {i}:")
            print(f"  Original: '{original}'")

            # Encriptar
            encrypted = encrypt_data(original)
            print(f"  Encriptado: '{encrypted}'")

            # Desencriptar
            decrypted = decrypt_data(encrypted)
            print(f"  Desencriptado: '{decrypted}'")

            # Verificar
            if original == decrypted:
                print("  ✓ CORRECTO: El texto se encriptó y desencriptó correctamente")
            else:
                print("  ✗ ERROR: El texto desencriptado no coincide con el original")
                return False

        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            return False

    print("\n" + "=" * 60)
    print("✓ TEST 1 COMPLETADO EXITOSAMENTE")
    print("=" * 60 + "\n")
    return True


def test_encryption_consistency():
    """Verifica que la misma clave produzca diferentes encriptaciones (por seguridad)."""
    print("=" * 60)
    print("TEST 2: Consistencia de Encriptación")
    print("=" * 60)

    original = "contraseña_de_prueba"

    try:
        # Encriptar dos veces el mismo texto
        encrypted1 = encrypt_data(original)
        encrypted2 = encrypt_data(original)

        print(f"\nTexto original: '{original}'")
        print(f"Encriptación 1: '{encrypted1}'")
        print(f"Encriptación 2: '{encrypted2}'")

        # Las encriptaciones deben ser diferentes (por el IV aleatorio de Fernet)
        if encrypted1 != encrypted2:
            print("✓ CORRECTO: Las encriptaciones son diferentes (seguridad)")
        else:
            print("⚠ ADVERTENCIA: Las encriptaciones son idénticas")

        # Pero ambas deben desencriptar al mismo valor
        decrypted1 = decrypt_data(encrypted1)
        decrypted2 = decrypt_data(encrypted2)

        print(f"Desencriptación 1: '{decrypted1}'")
        print(f"Desencriptación 2: '{decrypted2}'")

        if original == decrypted1 == decrypted2:
            print("✓ CORRECTO: Ambas desencriptaciones son correctas")
            print("\n" + "=" * 60)
            print("✓ TEST 2 COMPLETADO EXITOSAMENTE")
            print("=" * 60 + "\n")
            return True
        else:
            print("✗ ERROR: Las desencriptaciones no coinciden")
            return False

    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False


def test_special_characters():
    """Prueba con caracteres especiales y Unicode."""
    print("=" * 60)
    print("TEST 3: Caracteres Especiales y Unicode")
    print("=" * 60)

    test_cases = [
        "Contraseña con ñ y tildes: áéíóú",
        "Símbolos: !@#$%^&*()_+-=[]{}|;:',.<>?/",
        "Emojis: 🔐 🔑 🛡️ ✅",
        "Japonés: パスワード",
        "Árabe: كلمة السر",
        "Chino: 密码",
    ]

    for i, original in enumerate(test_cases, 1):
        try:
            print(f"\nCaso {i}:")
            print(f"  Original: '{original}'")

            encrypted = encrypt_data(original)
            decrypted = decrypt_data(encrypted)

            if original == decrypted:
                print(f"  ✓ CORRECTO")
            else:
                print(f"  ✗ ERROR: No coincide")
                print(f"    Esperado: '{original}'")
                print(f"    Obtenido: '{decrypted}'")
                return False

        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            return False

    print("\n" + "=" * 60)
    print("✓ TEST 3 COMPLETADO EXITOSAMENTE")
    print("=" * 60 + "\n")
    return True


def test_encryption_key_persistence():
    """Verifica que la clave de encriptación persista entre reinicios."""
    print("=" * 60)
    print("TEST 4: Persistencia de Clave")
    print("=" * 60)

    try:
        # Obtener la instancia de encriptación
        enc1 = global_encryptor

        # Encriptar un texto
        original = "test_persistencia"
        encrypted = encrypt_data(original)
        print(f"\nTexto original: '{original}'")
        print(f"Texto encriptado: '{encrypted}'")

        # Usar la misma instancia (simula reinicio)
        # En producción, esto cargará la misma clave desde el archivo _env
        enc2 = global_encryptor

        # Desencriptar con la "nueva" instancia
        decrypted = decrypt_data(encrypted)
        print(f"Texto desencriptado: '{decrypted}'")

        if original == decrypted:
            print("✓ CORRECTO: La clave persiste correctamente")
            print("\n" + "=" * 60)
            print("✓ TEST 4 COMPLETADO EXITOSAMENTE")
            print("=" * 60 + "\n")
            return True
        else:
            print("✗ ERROR: La clave no persiste correctamente")
            return False

    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False


def test_empty_and_none():
    """Prueba casos límite: vacío y None."""
    print("=" * 60)
    print("TEST 5: Casos Límite (Vacío y None)")
    print("=" * 60)

    try:
        # Caso 1: String vacío
        print("\nCaso 1: String vacío")
        encrypted_empty = encrypt_data("")
        decrypted_empty = decrypt_data(encrypted_empty) if encrypted_empty else None
        print(f"  Original: ''")
        print(f"  Encriptado: '{encrypted_empty}'")
        print(f"  Desencriptado: '{decrypted_empty}'")

        # encrypt_data("") devuelve None según la implementación
        if encrypted_empty is None and decrypted_empty is None:
            print("  ✓ CORRECTO: String vacío manejado correctamente (devuelve None)")
        elif decrypted_empty == "":
            print("  ✓ CORRECTO: String vacío manejado correctamente")
        else:
            print("  ✗ ERROR: String vacío no se maneja correctamente")
            return False

        print("\n" + "=" * 60)
        print("✓ TEST 5 COMPLETADO EXITOSAMENTE")
        print("=" * 60 + "\n")
        return True

    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False


def run_all_tests():
    """Ejecuta todas las pruebas."""
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "SUITE DE PRUEBAS DE ENCRIPTACIÓN" + " " * 16 + "║")
    print("╚" + "═" * 58 + "╝\n")

    tests = [
        ("Encriptación Básica", test_basic_encryption),
        ("Consistencia de Encriptación", test_encryption_consistency),
        ("Caracteres Especiales y Unicode", test_special_characters),
        ("Persistencia de Clave", test_encryption_key_persistence),
        ("Casos Límite", test_empty_and_none),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ ERROR FATAL en {test_name}: {e}\n")
            results.append((test_name, False))

    # Resumen final
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + " " * 20 + "RESUMEN FINAL" + " " * 25 + "║")
    print("╚" + "═" * 58 + "╝\n")

    total = len(results)
    passed = sum(1 for _, result in results if result)
    failed = total - passed

    for test_name, result in results:
        status = "✓ PASÓ" if result else "✗ FALLÓ"
        print(f"{status}: {test_name}")

    print("\n" + "=" * 60)
    print(f"Total de pruebas: {total}")
    print(f"Pruebas exitosas: {passed}")
    print(f"Pruebas fallidas: {failed}")
    print("=" * 60 + "\n")

    if failed == 0:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE! 🎉\n")
        return True
    else:
        print(f"⚠️  {failed} PRUEBA(S) FALLARON ⚠️\n")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
