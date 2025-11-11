#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_encryption_key.py
====================================================
Script para generar una ENCRYPTION_KEY y guardarla
en el archivo _env del sistema Montero.
====================================================
"""

import os
import sys
from cryptography.fernet import Fernet


def generate_encryption_key():
    """Genera una nueva clave de encriptación Fernet"""
    return Fernet.generate_key().decode()


def update_env_file(env_path, new_key):
    """
    Actualiza el archivo _env con la nueva clave de encriptación

    Args:
        env_path (str): Ruta al archivo _env
        new_key (str): Nueva clave de encriptación

    Returns:
        bool: True si se actualizó correctamente
    """
    try:
        # Leer el archivo actual
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Buscar y actualizar la línea ENCRYPTION_KEY
        key_found = False
        for i, line in enumerate(lines):
            if line.startswith("ENCRYPTION_KEY="):
                lines[i] = f"ENCRYPTION_KEY={new_key}\n"
                key_found = True
                print(f"✅ Línea ENCRYPTION_KEY encontrada en línea {i+1}")
                break

        if not key_found:
            lines.append(f"\nENCRYPTION_KEY={new_key}\n")
            print("✅ Línea ENCRYPTION_KEY agregada al final del archivo")

        # Escribir el archivo actualizado
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        print(f"✅ Archivo _env actualizado correctamente")
        return True

    except Exception as e:
        print(f"❌ Error actualizando archivo _env: {e}")
        return False


def main():
    """Función principal"""
    print("=" * 70)
    print("🔐 GENERADOR DE ENCRYPTION_KEY - SISTEMA MONTERO")
    print("=" * 70)
    print()

    # --- RUTA CORREGIDA PARA WINDOWS ---
    # __file__ es la ruta de este script (scripts_bd/fix_encryption_key.py)
    # os.path.dirname(__file__) es 'scripts_bd/'
    # os.path.dirname(os.path.dirname(__file__)) es 'dashboard/'
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(project_root, "_env")
    # ------------------------------------

    # Verificar que el archivo existe
    if not os.path.exists(env_path):
        print(f"❌ ERROR: No se encontró el archivo _env en: {env_path}")
        sys.exit(1)

    print(f"📁 Archivo _env encontrado: {env_path}")
    print()

    # Generar nueva clave
    print("🔑 Generando nueva ENCRYPTION_KEY...")
    new_key = generate_encryption_key()
    print(f"✅ Clave generada exitosamente")
    print(f"   Longitud: {len(new_key)} caracteres")
    print()

    # Mostrar la clave (con parte oculta por seguridad)
    print(f"🔐 Clave generada: {new_key[:20]}...{new_key[-10:]}")
    print()

    # Actualizar el archivo _env
    print("💾 Actualizando archivo _env...")
    if update_env_file(env_path, new_key):
        print()
        print("=" * 70)
        print("✅ ¡ÉXITO! ENCRYPTION_KEY generada y guardada correctamente")
        print("=" * 70)
        print()
        print("📋 PRÓXIMOS PASOS:")
        print("   1. Reiniciar el sistema para que cargue la nueva clave")
        print("   2. Verificar que el sistema de encriptación funciona correctamente")
        print("   3. Si tienes credenciales ya guardadas, necesitarás migrarlas")
        print()
        print("⚠️  IMPORTANTE: Guarda una copia de seguridad de esta clave")
        print("   Si la pierdes, no podrás desencriptar las credenciales guardadas")
        print()
        print(f"   ENCRYPTION_KEY={new_key}")
        print()
    else:
        print()
        print("❌ Error al actualizar el archivo _env")
        sys.exit(1)


if __name__ == "__main__":
    main()
