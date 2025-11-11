#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_day1.py
====================================================
Script de validación final para verificar que el
problema de ENCRYPTION_KEY está completamente resuelto.
====================================================
"""

import os
import sys

# --- RUTA CORREGIDA PARA WINDOWS ---
# __file__ es la ruta de este script (scripts_bd/validate_day1.py)
# os.path.dirname(__file__) es 'scripts_bd/'
# os.path.dirname(os.path.dirname(__file__)) es 'dashboard/'
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ------------------------------------


def check_env_file():
    """Verifica que el archivo _env existe y tiene ENCRYPTION_KEY"""
    print("=" * 70)
    print("1️⃣  VERIFICANDO ARCHIVO _ENV")
    print("=" * 70)

    env_path = os.path.join(PROJECT_ROOT, "_env")

    if not os.path.exists(env_path):
        print(f"❌ ERROR: Archivo _env no encontrado en {env_path}")
        return False

    print(f"✅ Archivo _env existe: {env_path}")

    # Leer el archivo y buscar ENCRYPTION_KEY
    with open(env_path, "r", encoding="utf-8") as f:
        content = f.read()
        lines = content.split("\n")

    encryption_line = None
    for i, line in enumerate(lines, 1):
        if line.startswith("ENCRYPTION_KEY="):
            encryption_line = line
            print(f"✅ Línea ENCRYPTION_KEY encontrada (línea {i})")
            break

    if not encryption_line:
        print("❌ ERROR: No se encontró la línea ENCRYPTION_KEY")
        return False

    # Verificar que no está vacía
    key_value = encryption_line.split("=", 1)[1].strip()

    if not key_value:
        print("❌ ERROR: ENCRYPTION_KEY está vacía")
        return False

    print(f"✅ ENCRYPTION_KEY tiene valor: {key_value[:20]}...{key_value[-10:]}")
    print(f"   Longitud: {len(key_value)} caracteres")

    # Verificar longitud esperada (44 caracteres para Fernet)
    if len(key_value) != 44:
        print(
            f"⚠️  ADVERTENCIA: Longitud inesperada (esperado: 44, actual: {len(key_value)})"
        )
    else:
        print("✅ Longitud correcta para clave Fernet (44 caracteres)")

    print()
    return True


def check_encryption_module():
    """Verifica que el módulo de encriptación funciona"""
    print("=" * 70)
    print("2️⃣  VERIFICANDO MÓDULO DE ENCRIPTACIÓN")
    print("=" * 70)

    try:
        # Cambiar al directorio del proyecto
        sys.path.insert(0, PROJECT_ROOT)

        # Importar módulo
        from encryption import encrypt_text, decrypt_text

        print("✅ Módulo 'encryption' importado correctamente")

        # Probar encriptación básica
        test_text = "prueba_validacion_dia1"
        print(f"\n🧪 Probando encriptación...")
        print(f"   Texto original: '{test_text}'")

        encrypted = encrypt_text(test_text)
        print(f"   ✅ Texto encriptado: '{encrypted[:30]}...'")

        decrypted = decrypt_text(encrypted)
        print(f"   Texto desencriptado: '{decrypted}'")

        if test_text == decrypted:
            print("   ✅ Encriptación y desencriptación funcionan correctamente")
            print()
            return True
        else:
            print("   ❌ ERROR: El texto desencriptado no coincide")
            print()
            return False

    except ImportError as e:
        print(f"❌ ERROR: No se pudo importar el módulo de encriptación: {e}")
        print("   Asegúrate de que 'encryption.py' esté en la carpeta 'dashboard'")
        print()
        return False
    except Exception as e:
        print(f"❌ ERROR durante la prueba de encriptación: {e}")
        print()
        return False


def check_env_loading():
    """Verifica que se puede cargar la clave desde el entorno"""
    print("=" * 70)
    print("3️⃣  VERIFICANDO CARGA DE VARIABLES DE ENTORNO")
    print("=" * 70)

    try:
        # Intentar cargar con dotenv
        from dotenv import load_dotenv

        env_path = os.path.join(PROJECT_ROOT, "_env")
        load_dotenv(env_path)

        encryption_key = os.getenv("ENCRYPTION_KEY")

        if encryption_key and encryption_key.strip():
            print("✅ ENCRYPTION_KEY cargada correctamente desde _env")
            print(f"   Valor: {encryption_key[:20]}...{encryption_key[-10:]}")
            print()
            return True
        else:
            print("❌ ERROR: ENCRYPTION_KEY no se pudo cargar o está vacía")
            print()
            return False

    except ImportError:
        print("⚠️  python-dotenv no está instalado")
        print("   El sistema puede cargar _env manualmente")
        print()
        return True  # No es crítico si usa otro método
    except Exception as e:
        print(f"❌ ERROR cargando variables de entorno: {e}")
        print()
        return False


def generate_report(checks):
    """Genera reporte final de validación"""
    print()
    print("=" * 70)
    print("📊 REPORTE FINAL DE VALIDACIÓN - DÍA 1")
    print("=" * 70)
    print()

    total = len(checks)
    passed = sum(1 for check in checks if check["passed"])

    for check in checks:
        status = "✅ PASÓ" if check["passed"] else "❌ FALLÓ"
        print(f"{status} | {check['name']}")

    print()
    print("-" * 70)
    print(f"Total de verificaciones: {total}")
    print(f"Verificaciones exitosas: {passed}")
    print(f"Verificaciones fallidas: {total - passed}")
    print("-" * 70)
    print()

    if passed == total:
        print("🎉 ¡ÉXITO! Todas las verificaciones pasaron")
        print()
        print("✅ ENCRYPTION_KEY está completamente configurada")
        print("✅ El sistema de encriptación funciona correctamente")
        print("✅ Día 1 completado exitosamente")
        print()
        print("📋 Próximo paso: Día 2 - Resolver problemas de encoding UTF-8")
        return True
    else:
        print("⚠️  ADVERTENCIA: Algunas verificaciones fallaron")
        print()
        print("Por favor, revisa los errores anteriores y corrige los problemas.")
        return False


def main():
    """Función principal"""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "VALIDACIÓN DÍA 1 - ENCRYPTION_KEY" + " " * 20 + "║")
    print("╚" + "═" * 68 + "╝")
    print()

    checks = []

    # Check 1: Archivo _env
    check1_passed = check_env_file()
    checks.append({"name": "Archivo _env con ENCRYPTION_KEY", "passed": check1_passed})

    # Check 2: Módulo de encriptación
    check2_passed = check_encryption_module()
    checks.append({"name": "Módulo de encriptación funcional", "passed": check2_passed})

    # Check 3: Carga de variables
    check3_passed = check_env_loading()
    checks.append({"name": "Carga de variables de entorno", "passed": check3_passed})

    # Generar reporte final
    success = generate_report(checks)

    # Código de salida
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
