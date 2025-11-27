#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Validación Pre-CI
====================================================
Ejecuta las mismas validaciones que GitHub Actions antes de hacer push.
Esto te permite detectar y corregir errores localmente.
====================================================

Uso:
    python validar_pre_ci.py

Salida:
    ✅ = Todo OK, puedes hacer push
    ❌ = Hay errores que debes corregir primero
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Tuple, List

# --- AJUSTE CRÍTICO 1: Para resolver el UnicodeDecodeError de PowerShell y black ---
# Este ajuste debe hacerse al inicio.
if sys.platform == "win32":
    try:
        # Intenta forzar la codificación de la consola a UTF-8 para evitar errores con caracteres especiales
        # Esto ayuda a black y a la salida de los logs.
        subprocess.run(["chcp", "65001"], shell=True, check=True, capture_output=True, text=True)
    except Exception:
        pass  # Ignorar si falla, no es crítico para la funcionalidad, solo para la estética en consola.
# ---------------------------------------------------------------------------------

# Colores para terminal
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_header(text: str):
    """Imprime un encabezado llamativo"""
    print(f"\n{BLUE}{BOLD}{'=' * 70}{RESET}")
    print(f"{BLUE}{BOLD}{text:^70}{RESET}")
    print(f"{BLUE}{BOLD}{'=' * 70}{RESET}\n")


def print_section(text: str):
    """Imprime una sección"""
    print(f"\n{YELLOW}{'─' * 70}{RESET}")
    print(f"{YELLOW}{BOLD}▶ {text}{RESET}")
    print(f"{YELLOW}{'─' * 70}{RESET}")


def print_success(text: str):
    """Imprime mensaje de éxito"""
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text: str):
    """Imprime mensaje de error"""
    print(f"{RED}❌ {text}{RESET}")


def print_warning(text: str):
    """Imprime mensaje de advertencia"""
    print(f"{YELLOW}⚠️  {text}{RESET}")


def run_command(cmd: List[str], description: str) -> Tuple[bool, str]:
    """
    Ejecuta un comando y retorna el resultado.

    Args:
        cmd: Lista con el comando y argumentos
        description: Descripción de lo que hace el comando

    Returns:
        (success: bool, output: str)
    """
    try:
        # Usar encoding UTF-8 para capturar correctamente la salida en Windows/PowerShell
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",  # Uso de UTF-8 para evitar UnicodeDecodeError
            errors="ignore",
            timeout=300,  # 5 minutos máximo
        )

        success = result.returncode == 0
        output = result.stdout + result.stderr

        return success, output

    except subprocess.TimeoutExpired:
        return False, f"Timeout: {description} tomó más de 5 minutos"

    except FileNotFoundError:
        return False, f"Comando no encontrado: {cmd[0]}"

    except Exception as e:
        return False, f"Error inesperado: {str(e)}"


def check_environment():
    """Verifica el entorno de desarrollo"""
    print_section("1️⃣  Verificando Entorno")

    issues = []

    # Verificar Python
    python_version = sys.version_info
    if python_version.major < 3 or python_version.minor < 9:
        issues.append(f"Python debe ser 3.9+, encontrado: {python_version.major}.{python_version.minor}")
        print_error(f"Python {python_version.major}.{python_version.minor} (necesitas 3.9+)")
    else:
        print_success(f"Python {python_version.major}.{python_version.minor}")

    # Verificar directorios
    for directory in ["data", "logs", "formularios_pdf"]:
        if not Path(directory).exists():
            print_warning(f"Directorio '{directory}' no existe (se creará en CI)")
        else:
            print_success(f"Directorio '{directory}' existe")

    # Verificar .env
    if not Path(".env").exists():
        issues.append("Archivo .env no encontrado")
        print_error("Archivo .env no encontrado (crítico para desarrollo)")
    else:
        print_success("Archivo .env existe")

        # Verificar variables críticas en .env
        try:
            with open(".env", "r", encoding="utf-8") as f:
                env_content = f.read()

            critical_vars = ["SECRET_KEY", "ENCRYPTION_KEY", "FLASK_ENV"]
            for var in critical_vars:
                if var in env_content:
                    print_success(f"Variable {var} definida en .env")
                else:
                    issues.append(f"Variable {var} falta en .env")
                    print_error(f"Variable {var} falta en .env")
        except UnicodeDecodeError:
            issues.append("Error de codificación al leer .env. Asegúrate de que sea UTF-8.")
            print_error("Error al leer .env (Codificación)")

    # Verificar requirements.txt
    if not Path("requirements.txt").exists():
        issues.append("Archivo requirements.txt no encontrado")
        print_error("requirements.txt no encontrado")
    else:
        print_success("requirements.txt existe")

    return len(issues) == 0, issues


def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    print_section("2️⃣  Verificando Dependencias")

    dependencies = {
        "flask": "Flask",
        "pytest": "pytest",
        "cryptography": "cryptography",
        "sqlalchemy": "SQLAlchemy",
        "PyPDF2": "PyPDF2",  # Se añade la dependencia que causó problemas anteriormente
    }

    issues = []

    for module, name in dependencies.items():
        try:
            __import__(module)
            print_success(f"{name} instalado")
        except ImportError:
            issues.append(f"{name} no está instalado")
            print_error(f"{name} no está instalado")

    return len(issues) == 0, issues


def check_imports():
    """Verifica que los módulos principales se puedan importar"""
    print_section("3️⃣  Verificando Imports de Módulos")

    # --- AJUSTE CRÍTICO 2: Añadir la carpeta 'routes' a la ruta de búsqueda de Python ---
    # Esto permite que 'import routes.auth' (o 'import auth' si es directo) funcione.
    # Como el archivo auth.py está en D:\Mi-App-React\src\dashboard\routes, debemos añadir 'routes'.
    sys.path.append(str(Path.cwd() / "routes"))

    # Ahora el módulo 'auth' se puede importar como 'auth' si hay un __init__.py en 'routes',
    # o como 'routes.auth' que es lo más seguro.

    modules = [
        ("app", "Aplicación principal"),
        ("auth", "Módulo de autenticación (auth.py)"),  # Intentamos el import directo
        ("encryption", "Módulo de encriptación"),
        ("logger", "Sistema de logging"),
    ]

    issues = []

    # Configurar variables de entorno para imports
    os.environ["FLASK_ENV"] = "testing"
    os.environ.setdefault("SECRET_KEY", "test-key-validation")
    os.environ.setdefault("ENCRYPTION_KEY", "HLh9Yfi7v5-QnQ4WYALaTPIC__LX-VqCK01eJBNK8Zw=")
    os.environ.setdefault("DATABASE_PATH", ":memory:")

    for module_name, description in modules:
        try:
            # Intentar el import directo (ej: import auth)
            __import__(module_name)
            print_success(f"{description}")
        except ModuleNotFoundError as e:
            # Si falla el directo, intentar el import por paquete (ej: import routes.auth)
            if module_name == "auth":
                try:
                    __import__("routes.auth")
                    print_success(f"{description} (en routes/)")
                except Exception as sub_e:
                    issues.append(f"Error al importar {module_name} (ni directo ni en routes/): {str(sub_e)}")
                    print_error(f"{description}: {str(sub_e)[:60]}...")
            else:
                issues.append(f"Error al importar {module_name}: {str(e)}")
                print_error(f"{description}: {str(e)[:60]}...")
        except Exception as e:
            issues.append(f"Error al importar {module_name}: {str(e)}")
            print_error(f"{description}: {str(e)[:60]}...")

    return len(issues) == 0, issues


def run_tests():
    """Ejecuta los tests con pytest"""
    print_section("4️⃣  Ejecutando Tests")

    # Configurar entorno para tests
    os.environ["FLASK_ENV"] = "testing"
    os.environ["SECRET_KEY"] = "test-secret-key-validation"
    os.environ["ENCRYPTION_KEY"] = "HLh9Yfi7v5-QnQ4WYALaTPIC__LX-VqCK01eJBNK8Zw="
    os.environ["DATABASE_PATH"] = ":memory:"
    os.environ["LOG_LEVEL"] = "ERROR"

    success, output = run_command(["pytest", "-v", "--tb=short"], "Ejecutar tests")

    if success:
        print_success("Todos los tests pasaron")

        # Extraer resumen de tests
        lines = output.split("\n")
        for line in lines:
            if "passed" in line.lower() or "failed" in line.lower():
                print(f"  {line.strip()}")
    else:
        print_error("Algunos tests fallaron")
        print("\nOutput de pytest (últimas 20 líneas):")
        print("-" * 70)
        lines = output.split("\n")
        for line in lines[-20:]:
            print(f"  {line}")

    return success, [output] if not success else []


def check_code_style():
    """Verifica el estilo del código con black"""
    print_section("5️⃣  Verificando Estilo de Código")

    issues = []

    # Verificar si black está instalado
    try:
        __import__("black")
    except ImportError:
        print_warning("Black no está instalado (opcional)")
        return True, []

    # Ahora el comando debería funcionar mejor con la codificación ajustada
    success, output = run_command(["black", "--check", "--diff", "."], "Verificar formato con Black")

    if success:
        print_success("Código formateado correctamente")
    else:
        print_warning("Código necesita formateo (ejecuta: black .)")
        issues.append("Código necesita formateo con Black")

    # Si hubo error de decodificación, reportarlo como issue (aunque no sea crítico)
    if not success and ("cannot decode byte" in output or "UnicodeDecodeError" in output):
        issues.append("Error de codificación en Black. Ejecuta 'black .' directamente.")

    return True, issues  # No es crítico, retornar True


def generate_report(all_checks):
    """Genera un reporte final"""
    print_header("📊 REPORTE FINAL")

    total_checks = len(all_checks)
    passed_checks = sum(1 for check in all_checks if check["success"])

    print(f"Checks ejecutados: {total_checks}")
    print(f"Checks pasados:    {passed_checks}")
    print(f"Checks fallidos:   {total_checks - passed_checks}")

    print("\n" + "─" * 70 + "\n")

    for check in all_checks:
        symbol = "✅" if check["success"] else "❌"
        color = GREEN if check["success"] else RED
        print(f"{color}{symbol} {check['name']}{RESET}")

        if not check["success"] and check["issues"]:
            for issue in check["issues"][:3]:  # Mostrar máximo 3 issues
                print(f"   • {issue}")

    print("\n" + "─" * 70 + "\n")

    if passed_checks == total_checks:
        print(f"{GREEN}{BOLD}🎉 ¡EXCELENTE! Todo está listo para hacer push{RESET}")
        print(f"{GREEN}Puedes ejecutar: git push{RESET}")
        return True
    else:
        print(f"{RED}{BOLD}⚠️  HAY PROBLEMAS QUE CORREGIR{RESET}")
        print(f"{RED}Corrígelos antes de hacer push para evitar que falle el CI{RESET}")
        return False


def main():
    """Función principal"""
    print_header("🔍 VALIDACIÓN PRE-CI - SISTEMA MONTERO")

    print("Este script verifica que tu código pase las validaciones del CI")
    print("antes de hacer push a GitHub.\n")

    # Ejecutar todos los checks
    all_checks = []

    # Check 1: Entorno
    success, issues = check_environment()
    all_checks.append({"name": "Entorno de Desarrollo", "success": success, "issues": issues})

    # Check 2: Dependencias
    success, issues = check_dependencies()
    all_checks.append({"name": "Dependencias Instaladas", "success": success, "issues": issues})

    # Check 3: Imports
    success, issues = check_imports()
    all_checks.append({"name": "Imports de Módulos", "success": success, "issues": issues})

    # Check 4: Tests
    success, issues = run_tests()
    all_checks.append({"name": "Tests con Pytest", "success": success, "issues": issues})

    # Check 5: Estilo
    success, issues = check_code_style()
    all_checks.append({"name": "Estilo de Código", "success": success, "issues": issues})

    # Generar reporte
    all_passed = generate_report(all_checks)

    # Exit code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}⚠️  Validación interrumpida por el usuario{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{RED}❌ Error inesperado: {str(e)}{RESET}")
        sys.exit(1)
