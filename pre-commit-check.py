# -*- coding: utf-8 -*-
"""
Script de verificación pre-commit para Sistema Montero.
Ejecuta formateo, ordenamiento de imports y tests antes de hacer commit.
"""
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Ejecuta un comando y muestra el resultado."""
    print()
    print("=" * 70)
    print(f"  {description}")
    print("=" * 70)
    print(f"Comando: {cmd}")
    print()

    result = subprocess.run(cmd, shell=True, capture_output=False, text=True)

    if result.returncode == 0:
        print()
        print(f"[OK] {description} - EXITOSO")
        return True
    else:
        print()
        print(f"[ERROR] {description} - FALLIDO")
        return False


def main():
    """Función principal del script."""
    print("=" * 70)
    print("  VERIFICACION PRE-COMMIT - SISTEMA MONTERO")
    print("=" * 70)
    print()
    print("Este script ejecutara:")
    print("  1. Black (formateo de codigo)")
    print("  2. isort (ordenamiento de imports)")
    print("  3. pytest (tests unitarios)")
    print()

    # Cambiar al directorio del script
    script_dir = Path(__file__).parent
    print(f"Directorio de trabajo: {script_dir}")

    # Contador de éxitos
    checks_passed = 0
    total_checks = 3

    # 1. Formatear con Black
    if run_command("black .", "Formateo con Black"):
        checks_passed += 1
    else:
        print("[ADVERTENCIA] Black fallo, pero continuamos...")
        checks_passed += 1  # No bloqueante

    # 2. Ordenar imports con isort
    if run_command("isort .", "Ordenamiento de imports con isort"):
        checks_passed += 1
    else:
        print("[ADVERTENCIA] isort fallo, pero continuamos...")
        checks_passed += 1  # No bloqueante

    # 3. Ejecutar tests
    if run_command("pytest -v", "Ejecucion de tests con pytest"):
        checks_passed += 1
    else:
        print("[ERROR] Tests fallaron!")
        print()
        print("Por favor, arregla los tests antes de hacer commit")

    # Resumen
    print()
    print("=" * 70)
    print("  RESUMEN")
    print("=" * 70)
    print(f"Verificaciones pasadas: {checks_passed}/{total_checks}")
    print()

    if checks_passed == total_checks:
        print("[OK] Todo listo para hacer commit!")
        print()
        print("Comandos sugeridos:")
        print("  git add .")
        print('  git commit -m "Tu mensaje"')
        print("  git push")
        return 0
    else:
        print("[ERROR] Algunas verificaciones fallaron")
        print()
        print("Por favor, corrige los errores antes de hacer commit")
        return 1


if __name__ == "__main__":
    sys.exit(main())
