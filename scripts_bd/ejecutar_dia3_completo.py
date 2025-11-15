# -*- coding: utf-8 -*-
"""
EJECUTOR COMPLETO DÍA 3
=======================
Script maestro que ejecuta todo el proceso del Día 3
(Versión corregida para Windows)
"""

import os
import subprocess
import sys
from datetime import datetime

# --- RUTA CORREGIDA ---
# Directorio donde se encuentra este script (scripts_bd)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# ----------------------


def print_banner(title, width=80):
    print("\n" + "=" * width)
    print(title.center(width))
    print("=" * width + "\n")


def print_step(step_num, title):
    print(f"\n{'▓' * 80}")
    print(f"▓  PASO {step_num}: {title}")
    print(f"{'▓' * 80}\n")


def run_script(script_name, description):
    print(f"🚀 Ejecutando: {script_name}")
    print(f"📝 {description}\n")
    print("-" * 80)

    # --- RUTA CORREGIDA ---
    script_path = os.path.join(SCRIPT_DIR, script_name)
    # ----------------------

    try:
        result = subprocess.run(
            [sys.executable, script_path],  # Usar la ruta completa al script
            capture_output=False,
            text=True,
            encoding="utf-8",  # Añadido para Windows
        )

        print("-" * 80)

        if result.returncode == 0:
            print(f"✅ {script_name} completado exitosamente\n")
            return True, result.returncode
        else:
            print(f"❌ {script_name} falló con código: {result.returncode}\n")
            return False, result.returncode

    except FileNotFoundError:
        print(f"❌ ERROR: No se encontró el script {script_path}")
        print(f"   Asegúrate de que todos los archivos del Día 3 estén en la carpeta 'scripts_bd'")
        return False, -1

    except Exception as e:
        print(f"❌ ERROR ejecutando {script_name}: {e}\n")
        return False, -1


def check_files_exist():
    required_files = [
        "verificar_prerequisitos_dia3.py",
        "dia3_migrar_credenciales.py",
        "validar_dia3.py",
    ]

    missing = []
    for file in required_files:
        # --- RUTA CORREGIDA ---
        if not os.path.exists(os.path.join(SCRIPT_DIR, file)):
            missing.append(file)

    if missing:
        print("❌ ERROR: Faltan archivos necesarios en 'scripts_bd':")
        for file in missing:
            print(f"   • {file}")
        return False

    return True


def main_interactive():
    print_banner("🎯 DÍA 3: MIGRACIÓN DE CREDENCIALES - MODO INTERACTIVO")

    print(
        """
Este script ejecutará los 3 pasos del Día 3:
  1️⃣  Verificar pre-requisitos
  2️⃣  Ejecutar migración de credenciales
  3️⃣  Validar resultados
Se te pedirá confirmación antes de cada paso.
    """
    )

    if not check_files_exist():
        return False

    # PASO 1
    print_step(1, "VERIFICACIÓN DE PRE-REQUISITOS")
    respuesta = input("¿Ejecutar verificación de pre-requisitos? (s/n): ").lower()
    if respuesta != "s":
        print("❌ Proceso cancelado por el usuario")
        return False

    success, code = run_script(
        "verificar_prerequisitos_dia3.py",
        "Verifica que el sistema esté listo para la migración",
    )

    if not success:
        print("❌ La verificación de pre-requisitos falló")
        print("   Corrige los errores antes de continuar")
        return False

    # PASO 2
    print_step(2, "MIGRACIÓN DE CREDENCIALES")
    print("⚠️  IMPORTANTE: Se creará un respaldo automático de la BD.")
    respuesta = input("¿Proceder con la migración? (s/n): ").lower()
    if respuesta != "s":
        print("❌ Migración cancelada por el usuario")
        return False

    success, code = run_script(
        "dia3_migrar_credenciales.py",
        "Migra las credenciales de texto plano a encriptado",
    )

    if not success:
        print("❌ La migración falló")
        print("   Revisa los logs y el respaldo en backups/")
        return False

    # PASO 3
    print_step(3, "VALIDACIÓN DE RESULTADOS")
    respuesta = input("¿Ejecutar validación de resultados? (s/n): ").lower()
    if respuesta != "s":
        print("⚠️  Se recomienda ejecutar la validación")
        return True

    success, code = run_script(
        "validar_dia3.py",
        "Valida que todas las credenciales estén correctamente encriptadas",
    )

    if not success:
        print("⚠️  La validación encontró problemas")

    return success


def main_auto():
    print_banner("🎯 DÍA 3: MIGRACIÓN DE CREDENCIALES - MODO AUTOMÁTICO")
    print("⚠️  MODO AUTOMÁTICO ACTIVADO")
    respuesta = input("\n¿Confirmas que deseas ejecutar en modo automático? (s/n): ").lower()
    if respuesta != "s":
        print("❌ Proceso cancelado por el usuario")
        return False

    print("\n🚀 Iniciando ejecución automática...\n")

    if not check_files_exist():
        return False

    # PASO 1
    print_step(1, "VERIFICACIÓN DE PRE-REQUISITOS")
    success, _ = run_script("verificar_prerequisitos_dia3.py", "Verificando sistema...")
    if not success:
        print("❌ ABORTANDO: Pre-requisitos no cumplidos")
        return False

    # PASO 2
    print_step(2, "MIGRACIÓN DE CREDENCIALES")
    success, _ = run_script("dia3_migrar_credenciales.py", "Migrando credenciales...")
    if not success:
        print("❌ ABORTANDO: Migración falló")
        return False

    # PASO 3
    print_step(3, "VALIDACIÓN DE RESULTADOS")
    success, _ = run_script("validar_dia3.py", "Validando resultados...")

    return success


def print_summary(success):
    print("\n" + "=" * 80)
    print("📊 RESUMEN FINAL DEL DÍA 3")
    print("=" * 80)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n🕐 Completado: {timestamp}")

    if success:
        print("✅ ¡DÍA 3 COMPLETADO EXITOSAMENTE!")
        print("   Tu sistema ahora es mucho más seguro 🔒")
    else:
        print("⚠️  EL DÍA 3 ENCONTRÓ PROBLEMAS")
        print("   Revisa los mensajes de error arriba")

    print("=" * 80 + "\n")


def main():
    print("Selecciona el modo de ejecución:")
    print("  1. Interactivo (se pide confirmación en cada paso)")
    print("  2. Automático (ejecuta todo sin preguntar)")
    print("  3. Salir")

    while True:
        opcion = input("\nOpción (1-3): ").strip()

        if opcion == "1":
            success = main_interactive()
            break
        elif opcion == "2":
            success = main_auto()
            break
        elif opcion == "3":
            print("👋 Saliendo...")
            return
        else:
            print("❌ Opción inválida. Intenta de nuevo.")

    print_summary(success)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario (Ctrl+C)")
        sys.exit(130)
