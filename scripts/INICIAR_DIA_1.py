# -*- coding: utf-8 -*-
"""
Script de Inicio Rápido - Día 1: Tests de auth.py
==================================================
Sistema Montero - Plan Coverage 80%
"""

import subprocess
import sys
from pathlib import Path


def print_banner(message):
    """Imprime un banner decorativo"""
    width = len(message) + 4
    print("\n" + "=" * width)
    print(f"  {message}")
    print("=" * width + "\n")


def main():
    print_banner("DÍA 1: TESTS DE AUTH.PY - INICIO")

    print("📋 CHECKLIST DE INICIO:")

    # 1. Verificar directorio de tests
    tests_dir = Path("tests")
    if not tests_dir.exists():
        print("  ❌ Error: Directorio 'tests/' no encontrado.")
        return 1
    else:
        print("  ✅ [1/3] Directorio 'tests/' existe")

    # 2. Verificar archivo de tests
    test_file = tests_dir / "test_auth.py"
    if not test_file.exists():
        print(f"  ❌ Error: Archivo de test no encontrado en: {test_file}")
        return 1
    else:
        print(f"  ✅ [2/3] Archivo 'tests/test_auth.py' encontrado")

    # 3. Verificar dependencias
    try:
        import pytest

        print(f"  ✅ [3/3] pytest {pytest.__version__} instalado")
    except ImportError:
        print("  ❌ Error: pytest no instalado")
        print("     Ejecuta: pip install pytest pytest-cov")
        return 1

    print("\n" + "=" * 60)
    print("EJECUTANDO TESTS DE AUTH.PY (DÍA 1)")
    print("=" * 60 + "\n")

    # Ejecutar tests con coverage
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/test_auth.py",
        "-v",
        "--cov=routes.auth",  # Apuntando al módulo correcto
        "--cov-report=term-missing",
        "--cov-report=html",
    ]

    result = subprocess.run(cmd, cwd=Path.cwd())

    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("✅ TESTS COMPLETADOS EXITOSAMENTE")
        print("=" * 60)
        print("\n📊 PRÓXIMOS PASOS:")
        print("  1. Revisa el reporte de COVERAGE arriba.")
        print("  2. Abre el reporte HTML: htmlcov/index.html")
        print("  3. ¡Has completado el Día 1!")
    else:
        print("\n" + "=" * 60)
        print("❌ ALGUNOS TESTS FALLARON")
        print("=" * 60)
        print("\n🔍 ACCIONES RECOMENDADAS:")
        print("  1. Revisa los errores en el reporte de pytest arriba.")
        print("  2. Asegúrate de que 'conftest.py' y 'pytest.ini' están actualizados.")

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
