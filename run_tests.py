#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_tests.py
====================================================
Script para ejecutar los tests del Sistema Montero
====================================================
"""

import subprocess
import sys
import os
from pathlib import Path


class TestRunner:
    """Ejecutor de tests con diferentes opciones."""

    def __init__(self):
        self.project_root = Path(__file__).parent

    def print_banner(self, title):
        """Imprime un banner."""
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70 + "\n")

    def run_all_tests(self):
        """Ejecuta todos los tests."""
        self.print_banner("EJECUTANDO TODOS LOS TESTS")

        cmd = ["pytest", "-v"]
        return subprocess.run(cmd, cwd=self.project_root).returncode

    def run_with_coverage(self):
        """Ejecuta tests con reporte de cobertura."""
        self.print_banner("EJECUTANDO TESTS CON COVERAGE")

        cmd = [
            "pytest",
            "-v",
            "--cov=.",
            "--cov-report=html",
            "--cov-report=term-missing",
        ]

        result = subprocess.run(cmd, cwd=self.project_root)

        if result.returncode == 0:
            print("\n✅ Reporte de coverage generado en: htmlcov/index.html")

        return result.returncode

    def run_unit_tests(self):
        """Ejecuta solo tests unitarios."""
        self.print_banner("EJECUTANDO TESTS UNITARIOS")

        cmd = ["pytest", "-v", "-m", "unit"]
        return subprocess.run(cmd, cwd=self.project_root).returncode

    def run_integration_tests(self):
        """Ejecuta solo tests de integración."""
        self.print_banner("EJECUTANDO TESTS DE INTEGRACIÓN")

        cmd = ["pytest", "-v", "-m", "integration"]
        return subprocess.run(cmd, cwd=self.project_root).returncode

    def run_security_tests(self):
        """Ejecuta solo tests de seguridad."""
        self.print_banner("EJECUTANDO TESTS DE SEGURIDAD")

        cmd = ["pytest", "-v", "-m", "security"]
        return subprocess.run(cmd, cwd=self.project_root).returncode

    def run_specific_file(self, filename):
        """Ejecuta tests de un archivo específico."""
        self.print_banner(f"EJECUTANDO TESTS DE: {filename}")

        cmd = ["pytest", "-v", filename]
        return subprocess.run(cmd, cwd=self.project_root).returncode

    def run_fast_tests(self):
        """Ejecuta solo tests rápidos (excluye lentos)."""
        self.print_banner("EJECUTANDO TESTS RÁPIDOS")

        cmd = ["pytest", "-v", "-m", "not slow"]
        return subprocess.run(cmd, cwd=self.project_root).returncode

    def run_with_html_report(self):
        """Ejecuta tests y genera reporte HTML."""
        self.print_banner("EJECUTANDO TESTS CON REPORTE HTML")

        cmd = ["pytest", "-v", "--html=test_report.html", "--self-contained-html"]

        result = subprocess.run(cmd, cwd=self.project_root)

        if result.returncode == 0:
            print("\n✅ Reporte HTML generado en: test_report.html")

        return result.returncode

    def show_coverage_report(self):
        """Muestra el reporte de coverage en el navegador."""
        import webbrowser

        coverage_file = self.project_root / "htmlcov" / "index.html"

        if coverage_file.exists():
            print(f"\n📊 Abriendo reporte de coverage...")
            webbrowser.open(f"file://{coverage_file}")
        else:
            print("\n❌ No se encontró reporte de coverage.")
            print("   Ejecuta: python run_tests.py --coverage")

    def check_dependencies(self):
        """Verifica que pytest esté instalado."""
        try:
            import pytest

            print(f"✅ pytest {pytest.__version__} instalado")
            return True
        except ImportError:
            print("❌ pytest no está instalado")
            print("\nInstalar con:")
            print("  pip install -r requirements-test.txt")
            return False


def print_help():
    """Imprime la ayuda."""
    help_text = """
╔══════════════════════════════════════════════════════════════════╗
║                   SISTEMA DE TESTS - MONTERO                     ║
╚══════════════════════════════════════════════════════════════════╝

Uso: python run_tests.py [opción]

Opciones disponibles:
  (ninguna)          Ejecuta todos los tests con coverage
  --all              Ejecuta todos los tests
  --unit             Ejecuta solo tests unitarios
  --integration      Ejecuta solo tests de integración
  --security         Ejecuta solo tests de seguridad
  --fast             Ejecuta tests rápidos (excluye lentos)
  --coverage         Ejecuta tests con reporte de coverage detallado
  --html             Genera reporte HTML de los tests
  --show-coverage    Abre el reporte de coverage en el navegador
  --auth             Ejecuta solo tests de auth.py
  --encryption       Ejecuta solo tests de encryption.py
  --check            Verifica dependencias
  --help, -h         Muestra esta ayuda

Ejemplos:
  python run_tests.py                    # Tests con coverage
  python run_tests.py --unit             # Solo unitarios
  python run_tests.py --auth             # Solo auth
  python run_tests.py --fast             # Tests rápidos
  python run_tests.py --show-coverage    # Ver reporte

Para más opciones de pytest:
  pytest --help
"""
    print(help_text)


def main():
    """Función principal."""
    runner = TestRunner()

    # Si no hay argumentos, ejecutar con coverage
    if len(sys.argv) == 1:
        return runner.run_with_coverage()

    option = sys.argv[1].lower()

    if option in ["--help", "-h"]:
        print_help()
        return 0

    elif option == "--check":
        return 0 if runner.check_dependencies() else 1

    elif option == "--all":
        return runner.run_all_tests()

    elif option == "--unit":
        return runner.run_unit_tests()

    elif option == "--integration":
        return runner.run_integration_tests()

    elif option == "--security":
        return runner.run_security_tests()

    elif option == "--fast":
        return runner.run_fast_tests()

    elif option == "--coverage":
        return runner.run_with_coverage()

    elif option == "--html":
        return runner.run_with_html_report()

    elif option == "--show-coverage":
        runner.show_coverage_report()
        return 0

    elif option == "--auth":
        return runner.run_specific_file("test_auth.py")

    elif option == "--encryption":
        return runner.run_specific_file("test_encryption_pytest.py")

    else:
        print(f"❌ Opción desconocida: {option}")
        print("Usa --help para ver las opciones disponibles")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrumpidos por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
