# -*- coding: utf-8 -*-
"""
Script de Validación del Entorno - Plan Coverage 80%
=====================================================
Sistema Montero - Verifica que todo esté listo para comenzar
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


class Colors:
    """Colores para terminal"""

    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_header(text: str):
    """Imprime un header decorativo"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text:^70}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}\n")


def print_success(text: str):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_warning(text: str):
    """Imprime advertencia"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_error(text: str):
    """Imprime error"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def check_python_version() -> bool:
    """Verifica la versión de Python"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor} (Se requiere 3.7+)")
        return False


def check_dependencies() -> Tuple[bool, List[str]]:
    """Verifica que las dependencias estén instaladas"""
    dependencies = ["pytest", "coverage", "flask", "werkzeug"]
    missing = []

    for dep in dependencies:
        try:
            __import__(dep.replace("-", "_"))
            print_success(f"{dep} instalado")
        except ImportError:
            print_error(f"{dep} NO instalado")
            missing.append(dep)

    return len(missing) == 0, missing


def check_project_structure() -> Tuple[bool, List[str]]:
    """Verifica la estructura del proyecto"""
    required_files = [
        "routes/auth.py",
        "app.py",
        "encryption.py",
        "conftest.py",
        "pytest.ini",
        "_env",
    ]

    missing = []
    for file in required_files:
        path = Path(file)
        if path.exists():
            print_success(f"{file} encontrado")
        else:
            print_warning(f"{file} NO encontrado")
            missing.append(file)

    return len(missing) == 0, missing


def check_database() -> bool:
    """Verifica que la base de datos exista"""
    db_path = Path("mi_sistema.db")
    if db_path.exists():
        size_mb = db_path.stat().st_size / (1024 * 1024)
        print_success(f"Base de datos encontrada ({size_mb:.2f} MB)")
        return True
    else:
        print_warning("Base de datos NO encontrada (se creará al ejecutar tests)")
        return False


def check_plan_files() -> Tuple[bool, List[str]]:
    """Verifica que los archivos del plan estén presentes"""
    plan_files = [
        "PLAN_COVERAGE_80_PERCENT.md",
        "GUIA_INICIO_RAPIDO.md",
        "RESUMEN_EJECUTIVO_COVERAGE.md",
        "INICIAR_DIA_1.py",
    ]

    missing = []
    for file in plan_files:
        path = Path(file)
        if path.exists():
            print_success(f"{file}")
        else:
            print_error(f"{file} NO encontrado")
            missing.append(file)

    return len(missing) == 0, missing


def check_test_files() -> bool:
    """Verifica que el directorio de tests y archivo test_auth.py existan"""
    tests_dir = Path("tests")
    test_auth = tests_dir / "test_auth.py"

    if not tests_dir.exists():
        print_error("Directorio 'tests/' NO existe")
        return False

    print_success("Directorio 'tests/' existe")

    if test_auth.exists():
        lines = len(test_auth.read_text().splitlines())
        print_success(f"test_auth.py encontrado ({lines} líneas)")
        return True
    else:
        print_error("test_auth.py NO encontrado")
        return False


def run_quick_test() -> bool:
    """Ejecuta un test rápido para verificar que todo funciona"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q"], capture_output=True, text=True, timeout=10
        )

        if result.returncode == 0:
            # Contar tests descubiertos
            output = result.stdout
            if "test" in output:
                print_success("pytest puede descubrir tests")
                return True
            else:
                print_warning("pytest funciona pero no encuentra tests")
                return False
        else:
            print_error("pytest tiene problemas")
            print(f"   Error: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print_error("pytest timeout (puede haber problemas)")
        return False
    except Exception as e:
        print_error(f"Error al ejecutar pytest: {str(e)[:100]}")
        return False


def generate_report(results: dict) -> str:
    """Genera un reporte de los resultados"""
    total_checks = sum(1 for v in results.values() if isinstance(v, bool))
    passed_checks = sum(1 for v in results.values() if v is True)
    percentage = (passed_checks / total_checks * 100) if total_checks > 0 else 0

    if percentage == 100:
        status = f"{Colors.GREEN}✅ EXCELENTE - Todo listo para comenzar{Colors.END}"
    elif percentage >= 80:
        status = f"{Colors.GREEN}✅ BUENO - Puedes comenzar con pequeños ajustes{Colors.END}"
    elif percentage >= 60:
        status = f"{Colors.YELLOW}⚠️  ACEPTABLE - Se requieren algunos ajustes{Colors.END}"
    else:
        status = f"{Colors.RED}❌ CRÍTICO - Se requieren ajustes importantes{Colors.END}"

    report = f"""
{Colors.BOLD}RESUMEN DE VALIDACIÓN:{Colors.END}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Checks Completados: {passed_checks}/{total_checks} ({percentage:.0f}%)
Estado: {status}

{Colors.BOLD}Detalles por Categoría:{Colors.END}
"""

    categories = {
        "Entorno": ["python_version"],
        "Dependencias": ["dependencies"],
        "Estructura Proyecto": ["project_structure", "database"],
        "Archivos del Plan": ["plan_files", "test_files"],
        "Funcionalidad": ["quick_test"],
    }

    for category, keys in categories.items():
        category_results = [results.get(k, False) for k in keys if k in results]
        passed = sum(1 for r in category_results if r is True)
        total = len(category_results)

        if passed == total:
            icon = f"{Colors.GREEN}✅{Colors.END}"
        elif passed > 0:
            icon = f"{Colors.YELLOW}⚠️ {Colors.END}"
        else:
            icon = f"{Colors.RED}❌{Colors.END}"

        report += f"  {icon} {category}: {passed}/{total}\n"

    return report


def show_next_steps(results: dict):
    """Muestra los próximos pasos basados en los resultados"""
    print(f"\n{Colors.BOLD}PRÓXIMOS PASOS:{Colors.END}")

    if not results.get("dependencies", True):
        print(f"\n{Colors.YELLOW}1. INSTALAR DEPENDENCIAS:{Colors.END}")
        print("   pip install pytest pytest-cov pytest-mock flask --break-system-packages")

    if not results.get("plan_files", True):
        print(f"\n{Colors.YELLOW}2. COPIAR ARCHIVOS DEL PLAN:{Colors.END}")
        print("   cp /mnt/user-data/outputs/PLAN_COVERAGE_80_PERCENT.md .")
        print("   cp /mnt/user-data/outputs/GUIA_INICIO_RAPIDO.md .")
        print("   cp /mnt/user-data/outputs/INICIAR_DIA_1.py .")
        print("   cp /mnt/user-data/outputs/RESUMEN_EJECUTIVO_COVERAGE.md .")

    if not results.get("test_files", True):
        print(f"\n{Colors.YELLOW}3. CONFIGURAR TESTS:{Colors.END}")
        print("   mkdir -p tests")
        print("   cp /mnt/user-data/outputs/tests/test_auth_completo.py tests/test_auth.py")

    total_checks = sum(1 for v in results.values() if isinstance(v, bool))
    passed_checks = sum(1 for v in results.values() if v is True)
    percentage = (passed_checks / total_checks * 100) if total_checks > 0 else 0

    if percentage >= 80:
        print(f"\n{Colors.GREEN}{Colors.BOLD}4. ¡COMENZAR DÍA 1!{Colors.END}")
        print(f"   {Colors.GREEN}python INICIAR_DIA_1.py{Colors.END}")
        print(f"   {Colors.GREEN}O directamente:{Colors.END}")
        print(f"   {Colors.GREEN}pytest tests/test_auth.py -v --cov=auth --cov-report=html{Colors.END}")


def main():
    """Función principal de validación"""
    print_header("VALIDACIÓN DEL ENTORNO - PLAN COVERAGE 80%")

    results = {}

    # 1. Verificar Python
    print(f"{Colors.BOLD}[1/6] Verificando versión de Python...{Colors.END}")
    results["python_version"] = check_python_version()

    # 2. Verificar dependencias
    print(f"\n{Colors.BOLD}[2/6] Verificando dependencias...{Colors.END}")
    deps_ok, missing_deps = check_dependencies()
    results["dependencies"] = deps_ok
    if missing_deps:
        print_warning(f"Faltan dependencias: {', '.join(missing_deps)}")

    # 3. Verificar estructura del proyecto
    print(f"\n{Colors.BOLD}[3/6] Verificando estructura del proyecto...{Colors.END}")
    struct_ok, missing_files = check_project_structure()
    results["project_structure"] = struct_ok

    # 4. Verificar base de datos
    print(f"\n{Colors.BOLD}[4/6] Verificando base de datos...{Colors.END}")
    results["database"] = check_database()

    # 5. Verificar archivos del plan
    print(f"\n{Colors.BOLD}[5/6] Verificando archivos del plan...{Colors.END}")
    plan_ok, missing_plan = check_plan_files()
    results["plan_files"] = plan_ok
    if missing_plan:
        print_warning(f"Faltan archivos: {', '.join(missing_plan)}")

    # 6. Verificar archivos de tests
    print(f"\n{Colors.BOLD}[6/6] Verificando archivos de tests...{Colors.END}")
    results["test_files"] = check_test_files()

    # 7. Test rápido (opcional)
    if results.get("dependencies", False):
        print(f"\n{Colors.BOLD}[BONUS] Ejecutando test rápido...{Colors.END}")
        results["quick_test"] = run_quick_test()

    # Generar y mostrar reporte
    print_header("REPORTE FINAL")
    report = generate_report(results)
    print(report)

    # Mostrar próximos pasos
    show_next_steps(results)

    # Mensaje final
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}\n")

    total_checks = sum(1 for v in results.values() if isinstance(v, bool))
    passed_checks = sum(1 for v in results.values() if v is True)
    percentage = (passed_checks / total_checks * 100) if total_checks > 0 else 0

    if percentage >= 80:
        print(f"{Colors.GREEN}{Colors.BOLD}¡Todo listo para conquistar ese 80% de coverage! 🚀{Colors.END}\n")
        return 0
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}Por favor completa los pasos anteriores antes de comenzar.{Colors.END}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
