#!/usr/bin/env python3
"""
✅ VALIDADOR DE CONFIGURACIÓN DE ALEMBIC
========================================

Script para verificar que Alembic está correctamente configurado
en el Sistema Montero.

Uso:
    python validate_alembic_setup.py

Verifica:
    1. Instalación de Alembic
    2. Estructura de directorios
    3. Archivos de configuración
    4. Base de datos accesible
    5. Estado de migraciones
"""

import os
import sys
from pathlib import Path


# Colores para terminal
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    END = "\033[0m"
    BOLD = "\033[1m"


def print_header():
    """Imprime encabezado"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'VALIDACIÓN DE CONFIGURACIÓN DE ALEMBIC':^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'Sistema Montero':^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")


def print_check(item, status, details=""):
    """Imprime resultado de verificación"""
    if status:
        icon = f"{Colors.GREEN}✅{Colors.END}"
        status_text = f"{Colors.GREEN}OK{Colors.END}"
    else:
        icon = f"{Colors.RED}❌{Colors.END}"
        status_text = f"{Colors.RED}FALLO{Colors.END}"

    print(f"{icon} {item:.<50} {status_text}")
    if details:
        print(f"   {Colors.YELLOW}→ {details}{Colors.END}")


def check_alembic_installed():
    """Verifica si Alembic está instalado"""
    try:
        import alembic

        version = alembic.__version__
        print_check("Alembic instalado", True, f"Versión: {version}")
        return True
    except ImportError:
        print_check("Alembic instalado", False, "Instalar con: pip install alembic")
        return False


def check_sqlalchemy_installed():
    """Verifica si SQLAlchemy está instalado"""
    try:
        import sqlalchemy

        version = sqlalchemy.__version__
        print_check("SQLAlchemy instalado", True, f"Versión: {version}")
        return True
    except ImportError:
        print_check("SQLAlchemy instalado", False, "Instalar con: pip install sqlalchemy")
        return False


def check_file_exists(filepath, description):
    """Verifica si un archivo existe"""
    exists = os.path.exists(filepath)
    print_check(
        description,
        exists,
        f"Ruta: {filepath}" if exists else f"No encontrado: {filepath}",
    )
    return exists


def check_directory_structure():
    """Verifica la estructura de directorios"""
    print(f"\n{Colors.BOLD}📁 Verificando estructura de directorios...{Colors.END}\n")

    checks = {
        "migrations/": "Directorio de migraciones",
        "migrations/versions/": "Directorio de versiones",
        "alembic.ini": "Archivo de configuración",
        "migrations/env.py": "Script de entorno",
        "migrations/script.py.mako": "Template de migración",
    }

    results = []
    for path, desc in checks.items():
        result = check_file_exists(path, desc)
        results.append(result)

    return all(results)


def check_initial_migration():
    """Verifica si existe la migración inicial"""
    print(f"\n{Colors.BOLD}🔄 Verificando migraciones...{Colors.END}\n")

    versions_dir = Path("migrations/versions")
    if not versions_dir.exists():
        print_check("Directorio de versiones", False)
        return False

    migrations = list(versions_dir.glob("*.py"))
    migrations = [m for m in migrations if not m.name.startswith("__")]

    if not migrations:
        print_check("Migraciones encontradas", False, "No hay archivos de migración")
        return False

    print_check("Migraciones encontradas", True, f"{len(migrations)} migración(es)")

    # Verificar migración inicial
    initial = versions_dir / "001_initial_schema.py"
    has_initial = initial.exists()
    print_check(
        "Migración inicial (001)",
        has_initial,
        "001_initial_schema.py" if has_initial else "No encontrada",
    )

    # Listar todas las migraciones
    print(f"\n   {Colors.CYAN}Migraciones disponibles:{Colors.END}")
    for mig in sorted(migrations):
        print(f"   • {mig.name}")

    return has_initial


def check_database():
    """Verifica acceso a la base de datos"""
    print(f"\n{Colors.BOLD}💾 Verificando base de datos...{Colors.END}\n")

    # Intentar obtener ruta de la BD
    try:
        from config_rutas import RUTA_BASE_DE_DATOS

        db_path = RUTA_BASE_DE_DATOS
        print_check("Config de rutas", True, f"Usando: {db_path}")
    except ImportError:
        db_path = "data/mi_sistema.db"
        print_check("Config de rutas", True, f"Ruta correcta: {db_path}")

    # Verificar si existe la BD
    db_exists = os.path.exists(db_path)
    print_check("Base de datos existe", db_exists, f"Ruta: {db_path}")

    if not db_exists:
        return False

    # Intentar conectar
    try:
        import sqlite3

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Verificar tabla de versiones de Alembic
        cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='alembic_version'
        """
        )
        has_alembic_table = cursor.fetchone() is not None

        if has_alembic_table:
            cursor.execute("SELECT version_num FROM alembic_version")
            version = cursor.fetchone()
            if version:
                print_check("Estado de migración", True, f"Versión actual: {version[0]}")
            else:
                print_check("Estado de migración", True, "Sin versión (BD nueva)")
        else:
            print_check("Tabla de versiones Alembic", False, "BD no inicializada con Alembic")

        # Contar tablas
        cursor.execute(
            """
            SELECT COUNT(*) FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """
        )
        table_count = cursor.fetchone()[0]
        print_check("Tablas en BD", True, f"{table_count} tabla(s)")

        conn.close()
        return True

    except Exception as e:
        print_check("Conexión a BD", False, f"Error: {str(e)}")
        return False


def check_helper_scripts():
    """Verifica scripts de ayuda"""
    print(f"\n{Colors.BOLD}🔧 Verificando scripts de ayuda...{Colors.END}\n")

    scripts = {
        "manage_migrations.py": "Script gestor de migraciones",
        "GUIA_MIGRACIONES_ALEMBIC.md": "Guía de uso",
        "migrations/README.md": "README de migraciones",
    }

    results = []
    for path, desc in scripts.items():
        result = check_file_exists(path, desc)
        results.append(result)

    return all(results)


def print_summary(checks_passed):
    """Imprime resumen final"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}📊 RESUMEN DE VALIDACIÓN{Colors.END}\n")

    total = len(checks_passed)
    passed = sum(checks_passed)
    failed = total - passed

    if passed == total:
        status_color = Colors.GREEN
        status_text = "✅ CONFIGURACIÓN CORRECTA"
    elif passed > total / 2:
        status_color = Colors.YELLOW
        status_text = "⚠️  CONFIGURACIÓN PARCIAL"
    else:
        status_color = Colors.RED
        status_text = "❌ CONFIGURACIÓN INCOMPLETA"

    print(f"{status_color}{status_text}{Colors.END}")
    print(f"\nVerificaciones: {passed}/{total} pasadas ({passed*100//total}%)")
    print(f"  {Colors.GREEN}✅ Pasadas: {passed}{Colors.END}")
    print(f"  {Colors.RED}❌ Fallidas: {failed}{Colors.END}")

    print(f"\n{Colors.BOLD}🎯 PRÓXIMOS PASOS:{Colors.END}\n")

    if passed == total:
        print(f"{Colors.GREEN}¡Todo está listo para usar Alembic!{Colors.END}")
        print(f"\nComandos útiles:")
        print(f"  • Ver estado: {Colors.CYAN}python manage_migrations.py status{Colors.END}")
        print(f"  • Ver guía: {Colors.CYAN}cat GUIA_MIGRACIONES_ALEMBIC.md{Colors.END}")
    else:
        if not checks_passed[0]:  # Alembic
            print(f"1. Instalar Alembic: {Colors.CYAN}pip install alembic{Colors.END}")
        if not checks_passed[1]:  # SQLAlchemy
            print(f"2. Instalar SQLAlchemy: {Colors.CYAN}pip install sqlalchemy{Colors.END}")
        if not checks_passed[2]:  # Estructura
            print(f"3. Crear estructura: {Colors.CYAN}alembic init migrations{Colors.END}")
        print(f"\nConsulta la guía: {Colors.CYAN}GUIA_MIGRACIONES_ALEMBIC.md{Colors.END}")

    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")


def main():
    """Función principal"""
    print_header()

    checks = []

    # 1. Verificar instalación de dependencias
    print(f"{Colors.BOLD}📦 Verificando dependencias...{Colors.END}\n")
    checks.append(check_alembic_installed())
    checks.append(check_sqlalchemy_installed())

    # 2. Verificar estructura de directorios
    checks.append(check_directory_structure())

    # 3. Verificar migraciones
    checks.append(check_initial_migration())

    # 4. Verificar base de datos
    checks.append(check_database())

    # 5. Verificar scripts de ayuda
    checks.append(check_helper_scripts())

    # Resumen final
    print_summary(checks)

    # Retornar código de salida
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
