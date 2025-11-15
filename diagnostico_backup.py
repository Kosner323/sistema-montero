"""
Script de Diagnóstico del Sistema de Backups
Sistema Montero - v1.0
===========================================

Este script verifica que el sistema de backups esté
correctamente instalado y configurado.
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def print_header(title):
    """Imprime un encabezado formateado."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def check_python():
    """Verifica la instalación de Python."""
    print_header("VERIFICACIÓN DE PYTHON")

    version = sys.version
    print(f"✓ Python encontrado: {version}")

    version_info = sys.version_info
    if version_info.major >= 3 and version_info.minor >= 8:
        print(f"✓ Versión adecuada (3.8+)")
        return True
    else:
        print(f"✗ Se requiere Python 3.8 o superior")
        return False


def check_files():
    """Verifica que existan los archivos necesarios."""
    print_header("VERIFICACIÓN DE ARCHIVOS")

    archivos_requeridos = [
        "sistema_backup.py",
        "backup_config.ini",
        "instalar_backups.ps1",
        "INSTALAR_BACKUPS.bat",
        "MANUAL_BACKUPS.md",
    ]

    archivos_opcionales = ["ejecutar_backup.bat", "test_backup.bat", "restaurar_backup.bat"]

    todos_ok = True

    print("\nArchivos requeridos:")
    for archivo in archivos_requeridos:
        ruta = Path(archivo)
        if ruta.exists():
            tamano = ruta.stat().st_size
            print(f"  ✓ {archivo:<30} ({tamano:,} bytes)")
        else:
            print(f"  ✗ {archivo:<30} (NO ENCONTRADO)")
            todos_ok = False

    print("\nArchivos opcionales:")
    for archivo in archivos_opcionales:
        ruta = Path(archivo)
        if ruta.exists():
            print(f"  ✓ {archivo}")
        else:
            print(f"  ⚠ {archivo} (no instalado aún)")

    return todos_ok


def check_directories():
    """Verifica los directorios necesarios."""
    print_header("VERIFICACIÓN DE DIRECTORIOS")

    dir_backups = Path("backups")

    if dir_backups.exists():
        print(f"✓ Directorio de backups existe: {dir_backups.absolute()}")

        # Contar backups
        backups = list(dir_backups.glob("backup_*.zip"))
        print(f"  Backups encontrados: {len(backups)}")

        # Verificar log
        log_file = dir_backups / "backup.log"
        if log_file.exists():
            tamano = log_file.stat().st_size
            print(f"  ✓ Archivo de log existe ({tamano:,} bytes)")
        else:
            print(f"  ⚠ Archivo de log no existe (se creará al primer backup)")

        return True
    else:
        print(f"⚠ Directorio de backups no existe (se creará automáticamente)")
        return True


def check_scheduled_task():
    """Verifica si existe la tarea programada (solo Windows)."""
    print_header("VERIFICACIÓN DE TAREA PROGRAMADA")

    if sys.platform != "win32":
        print("⚠ No es Windows, tarea programada no aplicable")
        return True

    try:
        # Usar PowerShell para verificar la tarea
        cmd = ["powershell", "-Command", "Get-ScheduledTask -TaskName 'SistemaMonterBackup' -ErrorAction SilentlyContinue"]

        resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        if resultado.returncode == 0 and resultado.stdout.strip():
            print("✓ Tarea programada encontrada: SistemaMonterBackup")

            # Obtener información de la tarea
            cmd_info = [
                "powershell",
                "-Command",
                "Get-ScheduledTaskInfo -TaskName 'SistemaMonterBackup' -ErrorAction SilentlyContinue",
            ]

            info = subprocess.run(cmd_info, capture_output=True, text=True, timeout=10)
            if info.returncode == 0:
                print("\nInformación de la tarea:")
                for linea in info.stdout.split("\n"):
                    if any(x in linea for x in ["NextRunTime", "LastRunTime", "State"]):
                        print(f"  {linea.strip()}")

            return True
        else:
            print("⚠ Tarea programada no encontrada")
            print("  Ejecute INSTALAR_BACKUPS.bat para configurarla")
            return False

    except subprocess.TimeoutExpired:
        print("⚠ Tiempo de espera agotado al verificar tarea")
        return False
    except Exception as e:
        print(f"⚠ Error al verificar tarea programada: {e}")
        return False


def check_permissions():
    """Verifica permisos de escritura."""
    print_header("VERIFICACIÓN DE PERMISOS")

    test_file = Path("backups") / ".test_write"

    try:
        # Crear directorio si no existe
        Path("backups").mkdir(exist_ok=True)

        # Intentar escribir
        test_file.write_text("test")
        print(f"✓ Permisos de escritura correctos")

        # Limpiar
        test_file.unlink()
        return True

    except Exception as e:
        print(f"✗ Error de permisos: {e}")
        return False


def test_backup_system():
    """Prueba el sistema de backup."""
    print_header("PRUEBA DEL SISTEMA")

    print("Intentando importar módulo de backup...")

    try:
        # Intentar importar
        import sistema_backup

        print("✓ Módulo importado correctamente")

        # Intentar crear instancia
        sistema = sistema_backup.SistemaBackup()
        print("✓ Sistema de backup inicializado")

        # Listar backups
        backups = sistema.listar_backups()
        print(f"✓ Se pueden listar backups ({len(backups)} encontrados)")

        return True

    except Exception as e:
        print(f"✗ Error al probar el sistema: {e}")
        return False


def get_system_info():
    """Obtiene información del sistema."""
    print_header("INFORMACIÓN DEL SISTEMA")

    print(f"Sistema operativo: {sys.platform}")
    print(f"Versión de Python: {sys.version}")
    print(f"Directorio actual: {Path.cwd()}")
    print(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """Función principal del diagnóstico."""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                                                            ║")
    print("║        DIAGNÓSTICO DEL SISTEMA DE BACKUPS                 ║")
    print("║        Sistema Montero v1.0                               ║")
    print("║                                                            ║")
    print("╚════════════════════════════════════════════════════════════╝")

    # Ejecutar verificaciones
    resultados = {
        "Python": check_python(),
        "Archivos": check_files(),
        "Directorios": check_directories(),
        "Permisos": check_permissions(),
        "Sistema": test_backup_system(),
        "Tarea programada": check_scheduled_task(),
    }

    # Información del sistema
    get_system_info()

    # Resumen
    print_header("RESUMEN DEL DIAGNÓSTICO")

    total = len(resultados)
    exitosos = sum(1 for v in resultados.values() if v)
    porcentaje = (exitosos / total) * 100

    print(f"\nVerificaciones exitosas: {exitosos}/{total} ({porcentaje:.0f}%)")
    print()

    for nombre, resultado in resultados.items():
        simbolo = "✓" if resultado else "✗"
        estado = "OK" if resultado else "FALLO"
        print(f"  {simbolo} {nombre:<25} {estado}")

    print("\n" + "=" * 70)

    # Estado general
    if exitosos == total:
        print("\n✅ SISTEMA COMPLETAMENTE FUNCIONAL")
        print("\n   El sistema de backups está correctamente instalado")
        print("   y configurado. ¡Listo para usar!")
        return 0
    elif exitosos >= total * 0.7:
        print("\n⚠️  SISTEMA PARCIALMENTE FUNCIONAL")
        print("\n   El sistema está mayormente instalado pero tiene")
        print("   algunos problemas menores. Revise los detalles arriba.")
        return 1
    else:
        print("\n❌ SISTEMA NO FUNCIONAL")
        print("\n   Se detectaron problemas críticos. Por favor:")
        print("   1. Ejecute INSTALAR_BACKUPS.bat como Administrador")
        print("   2. Revise los errores mostrados arriba")
        print("   3. Consulte el MANUAL_BACKUPS.md")
        return 2


if __name__ == "__main__":
    try:
        exit_code = main()
        print("\n")
        input("Presione Enter para salir...")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nDiagnóstico interrumpido por el usuario.")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        import traceback

        traceback.print_exc()
        input("\nPresione Enter para salir...")
        sys.exit(1)
