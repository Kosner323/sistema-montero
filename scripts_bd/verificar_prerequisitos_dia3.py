# -*- coding: utf-8 -*-
"""
VERIFICADOR DE PRE-REQUISITOS - DÍA 3
(Versión corregida para Windows)
"""

import os
import sqlite3
import sys
from pathlib import Path

# --- RUTA CORREGIDA ---
# Apunta a la carpeta 'dashboard'
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ----------------------


class PreRequisitesChecker:
    def __init__(self):
        self.checks = []
        self.errors = []
        self.warnings = []

    def add_check(self, name, status, message=""):
        self.checks.append({"name": name, "status": status, "message": message})
        if status == "error":
            self.errors.append(name)
        elif status == "warning":
            self.warnings.append(name)

    def check_python_version(self):
        version = sys.version_info
        if version.major >= 3 and version.minor >= 7:
            self.add_check(
                "Versión de Python",
                "ok",
                f"Python {version.major}.{version.minor}.{version.micro}",
            )
            return True
        else:
            self.add_check(
                "Versión de Python",
                "error",
                f"Python {version.major}.{version.minor} - Se requiere 3.7+",
            )
            return False

    def check_modules(self):
        all_ok = True
        # --- RUTA CORREGIDA ---
        # Añadir la carpeta 'dashboard' al path para encontrar encryption y logger
        sys.path.insert(0, PROJECT_ROOT)
        # ----------------------

        modules_to_check = [
            ("encryption", "encryption.py"),
            ("logger", "logger.py"),
            ("sqlite3", "Built-in"),
        ]

        for module_name, description in modules_to_check:
            try:
                __import__(module_name)
                self.add_check(f"Módulo: {module_name}", "ok", f"Disponible ({description})")
            except ImportError as e:
                self.add_check(f"Módulo: {module_name}", "error", f"No encontrado - {str(e)}")
                all_ok = False
        return all_ok

    def check_encryption_key(self):
        # --- RUTA CORREGIDA ---
        env_path = os.path.join(PROJECT_ROOT, "_env")
        # ----------------------

        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    content = f.read()
                if "ENCRYPTION_KEY=" in content:
                    for line in content.split("\n"):
                        if line.startswith("ENCRYPTION_KEY="):
                            key_value = line.split("=", 1)[1].strip()
                            if len(key_value) > 40:
                                self.add_check(
                                    "ENCRYPTION_KEY",
                                    "ok",
                                    f"Configurada en _env ({len(key_value)} caracteres)",
                                )
                                return True
                            else:
                                self.add_check(
                                    "ENCRYPTION_KEY",
                                    "warning",
                                    f"Encontrada pero muy corta ({len(key_value)} caracteres)",
                                )
                                return False
            except Exception as e:
                self.add_check("ENCRYPTION_KEY", "error", f"Error leyendo {env_path}: {e}")
                return False

        self.add_check("ENCRYPTION_KEY", "error", "No encontrada en archivo _env")
        return False

    def check_database(self):
        # --- RUTA CORREGIDA ---
        db_path = os.path.join(PROJECT_ROOT, "data", "mi_sistema.db")
        # ----------------------

        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='credenciales_plataforma'")

                if cur.fetchone():
                    cur.execute("SELECT COUNT(*) FROM credenciales_plataforma")
                    count = cur.fetchone()[0]
                    size = os.path.getsize(db_path) / 1024  # KB
                    self.add_check(
                        "Base de datos",
                        "ok",
                        f"{db_path} - {count} credenciales - {size:.2f} KB",
                    )
                    conn.close()
                    return True, db_path, count
                else:
                    self.add_check(
                        "Base de datos",
                        "error",
                        f"{db_path} existe pero falta tabla credenciales_plataforma",
                    )
                    conn.close()
            except Exception as e:
                self.add_check("Base de datos", "error", f"Error accediendo a {db_path}: {e}")
        else:
            self.add_check("Base de datos", "error", f"No se encontró mi_sistema.db en {db_path}")
        return False, None, 0

    def check_backup_directory(self):
        # --- RUTA CORREGIDA ---
        backup_dir = Path(os.path.join(PROJECT_ROOT, "backups"))
        # ----------------------

        if backup_dir.exists():
            if backup_dir.is_dir():
                backups = list(backup_dir.glob("mi_sistema_backup_*.db"))
                self.add_check(
                    "Directorio de respaldos",
                    "ok",
                    f"backups/ existe - {len(backups)} respaldos previos",
                )
                return True
            else:
                self.add_check(
                    "Directorio de respaldos",
                    "error",
                    "backups/ existe pero no es un directorio",
                )
                return False
        else:
            try:
                backup_dir.mkdir()
                self.add_check("Directorio de respaldos", "ok", "backups/ creado exitosamente")
                return True
            except Exception as e:
                self.add_check(
                    "Directorio de respaldos",
                    "error",
                    f"No se pudo crear backups/: {e}",
                )
                return False

    # (El resto de las funciones de chequeo (disk_space, permissions) son genéricas y no necesitan cambios)
    def check_disk_space(self):
        try:
            stat = os.statvfs(PROJECT_ROOT)
            free_space_mb = (stat.f_bavail * stat.f_frsize) / (1024 * 1024)
            if free_space_mb > 100:
                self.add_check("Espacio en disco", "ok", f"{free_space_mb:.0f} MB disponibles")
                return True
            else:
                self.add_check(
                    "Espacio en disco",
                    "error",
                    f"Espacio insuficiente: {free_space_mb:.0f} MB",
                )
                return False
        except:
            self.add_check(
                "Espacio en disco",
                "warning",
                "No se pudo verificar (Windows - OK por ahora)",
            )
            return True  # Permitir continuar en Windows

    def check_permissions(self):
        test_file = os.path.join(PROJECT_ROOT, ".test_permissions")
        try:
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            self.add_check(
                "Permisos de escritura",
                "ok",
                "Puede escribir en el directorio del proyecto",
            )
            return True
        except Exception as e:
            self.add_check("Permisos de escritura", "error", f"No se puede escribir: {e}")
            return False

    def print_results(self):
        print("=" * 80)
        print("📋 RESULTADOS DE VERIFICACIÓN DE PRE-REQUISITOS")
        print("=" * 80)
        for check in self.checks:
            icon = "✅" if check["status"] == "ok" else "⚠️" if check["status"] == "warning" else "❌"
            print(f"{icon} {check['name']}")
            if check["message"]:
                print(f"   → {check['message']}")
            print()

        print("=" * 80)
        print("📊 RESUMEN")
        print("=" * 80)
        total = len(self.checks)
        ok = sum(1 for c in self.checks if c["status"] == "ok")
        warnings = len(self.warnings)
        errors = len(self.errors)
        print(f"✅ Exitosas:   {ok}/{total}")
        print(f"⚠️  Advertencias: {warnings}/{total}")
        print(f"❌ Errores:    {errors}/{total}")
        print("=" * 80)

        if errors == 0:
            print("\n🎉 ¡SISTEMA LISTO PARA MIGRACIÓN!")
            print("   Puedes ejecutar: python scripts_bd/dia3_migrar_credenciales.py")
            return True
        else:
            print(f"\n❌ HAY {errors} ERROR(ES) QUE DEBEN RESOLVERSE")
            print("   Corrige los errores antes de ejecutar la migración")
            return False


def main():
    print("VERIFICADOR DE PRE-REQUISITOS - DÍA 3")
    print("🔍 Iniciando verificaciones...\n")
    checker = PreRequisitesChecker()
    checker.check_python_version()
    checker.check_modules()
    checker.check_encryption_key()
    checker.check_database()
    checker.check_backup_directory()
    checker.check_disk_space()
    checker.check_permissions()
    checker.print_results()

    if checker.errors:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
