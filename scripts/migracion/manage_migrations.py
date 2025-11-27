#!/usr/bin/env python3
"""
🔄 GESTOR DE MIGRACIONES - SISTEMA MONTERO
==========================================

Script helper para gestionar migraciones de base de datos con Alembic.
Simplifica las operaciones comunes de migración.

Uso:
    python manage_migrations.py [comando]

Comandos disponibles:
    init        - Marca la BD actual con la migración inicial (solo primera vez)
    status      - Muestra el estado actual de las migraciones
    history     - Muestra el historial de migraciones
    upgrade     - Aplica migraciones pendientes
    downgrade   - Revierte la última migración
    create      - Crea una nueva migración (requiere mensaje)
    backup      - Crea un backup antes de migrar

Ejemplos:
    python manage_migrations.py init
    python manage_migrations.py status
    python manage_migrations.py upgrade
    python manage_migrations.py create "Agregar columna email_verificado"
"""

import os
import shutil
import sqlite3
import sys
from datetime import datetime
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


def print_header(text):
    """Imprime un encabezado formateado"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")


def print_success(text):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_warning(text):
    """Imprime mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_error(text):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_info(text):
    """Imprime mensaje informativo"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")


def get_database_path():
    """Obtiene la ruta de la base de datos"""
    # --- INICIO DE CORRECCIÓN ---
    # La ruta de la BD está en data/mi_sistema.db (como en alembic.ini)
    return "data/mi_sistema.db"
    # --- FIN DE CORRECCIÓN ---


def create_backup():
    """Crea un backup de la base de datos"""
    db_path = get_database_path()

    if not os.path.exists(db_path):
        print_warning(f"Base de datos no encontrada: {db_path}")
        return None

    # Crear directorio de backups si no existe
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)

    # Nombre del backup con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"backup_before_migration_{timestamp}.db"

    try:
        shutil.copy2(db_path, backup_path)
        print_success(f"Backup creado: {backup_path}")
        return str(backup_path)
    except Exception as e:
        print_error(f"Error creando backup: {e}")
        return None


def check_alembic_installed():
    """Verifica si Alembic está instalado"""
    try:
        import alembic

        return True
    except ImportError:
        print_error("Alembic no está instalado")
        print_info("Instalar con: pip install alembic")
        return False


def run_alembic_command(command):
    """Ejecuta un comando de Alembic"""
    if not check_alembic_installed():
        return False

    print_info(f"Ejecutando: alembic {command}")
    result = os.system(f"alembic {command}")
    return result == 0


def command_init():
    """Marca la base de datos con la migración inicial"""
    print_header("INICIALIZAR MIGRACIONES")

    print_info("Este comando marca tu base de datos actual como 'migrada'")
    print_info("Usa esto SOLO si tu base de datos YA tiene las tablas creadas")
    print()

    response = input("¿Tu base de datos ya tiene las tablas creadas? (s/n): ").lower()

    if response != "s":
        print_warning("Operación cancelada")
        return

    # Verificar que existe la base de datos
    db_path = get_database_path()
    if not os.path.exists(db_path):
        print_error(f"Base de datos no encontrada: {db_path}")
        print_info("Ejecuta primero 'upgrade' para crear las tablas")
        return

    # Marcar como migrada
    if run_alembic_command("stamp 001_initial_schema"):
        print_success("Base de datos marcada con migración inicial")
        print_info("Ahora puedes crear nuevas migraciones con 'create'")
    else:
        print_error("Error al marcar la base de datos")


def command_status():
    """Muestra el estado de las migraciones"""
    print_header("ESTADO DE MIGRACIONES")
    run_alembic_command("current")


def command_history():
    """Muestra el historial de migraciones"""
    print_header("HISTORIAL DE MIGRACIONES")
    run_alembic_command("history")


def command_upgrade():
    """Aplica las migraciones pendientes"""
    print_header("APLICAR MIGRACIONES")

    # Crear backup antes de migrar
    print_info("Creando backup de seguridad...")
    backup = create_backup()

    if not backup:
        response = input("No se pudo crear backup. ¿Continuar de todas formas? (s/n): ").lower()
        if response != "s":
            print_warning("Operación cancelada")
            return

    # Aplicar migraciones
    print_info("Aplicando migraciones...")
    if run_alembic_command("upgrade head"):
        print_success("Migraciones aplicadas exitosamente")
    else:
        print_error("Error al aplicar migraciones")
        if backup:
            print_info(f"Puedes restaurar el backup desde: {backup}")


def command_downgrade():
    """Revierte la última migración"""
    print_header("REVERTIR MIGRACIÓN")

    print_warning("⚠️  ADVERTENCIA: Esto revertirá la última migración")
    print_info("Asegúrate de tener un backup antes de continuar")
    print()

    response = input("¿Estás seguro de revertir? (s/n): ").lower()

    if response != "s":
        print_warning("Operación cancelada")
        return

    # Crear backup
    backup = create_backup()

    # Revertir
    if run_alembic_command("downgrade -1"):
        print_success("Migración revertida")
    else:
        print_error("Error al revertir migración")


def command_create(message=None):
    """Crea una nueva migración"""
    print_header("CREAR NUEVA MIGRACIÓN")

    if not message:
        message = input("Describe los cambios de esta migración: ").strip()

    if not message:
        print_error("Debes proporcionar un mensaje para la migración")
        return

    # Crear migración
    if run_alembic_command(f'revision -m "{message}"'):
        print_success("Migración creada exitosamente")
        print_info("Edita el archivo en migrations/versions/ y agrega tus cambios")
        print_info("Luego ejecuta 'upgrade' para aplicarla")
    else:
        print_error("Error al crear migración")


def command_backup():
    """Crea un backup manual"""
    print_header("CREAR BACKUP")
    backup = create_backup()
    if backup:
        print_success("Backup creado exitosamente")


def show_help():
    """Muestra la ayuda"""
    print(__doc__)


def main():
    """Función principal"""

    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    commands = {
        "init": command_init,
        "status": command_status,
        "history": command_history,
        "upgrade": command_upgrade,
        "downgrade": command_downgrade,
        "backup": command_backup,
        "help": show_help,
    }

    if command == "create":
        message = sys.argv[2] if len(sys.argv) > 2 else None
        command_create(message)
    elif command in commands:
        commands[command]()
    else:
        print_error(f"Comando desconocido: {command}")
        print_info("Usa 'help' para ver los comandos disponibles")


if __name__ == "__main__":
    main()
