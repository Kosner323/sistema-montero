# -*- coding: utf-8 -*-
"""
migrate_encrypt_credentials.py
====================================================
Script para migrar y encriptar las credenciales
existentes en la base de datos que están en texto plano.
====================================================

IMPORTANTE: Este script debe ejecutarse UNA SOLA VEZ
después de implementar el sistema de encriptación.
"""

import os
import sqlite3
import sys

from encryption import decrypt_text, encrypt_text
from logger import logger


def get_db_connection():
    """Obtiene una conexión a la base de datos."""
    DB_PATH = os.path.join(os.path.dirname(__file__), "data", "mi_sistema.db")
    if not os.path.exists(DB_PATH):
        DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "mi_sistema.db")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def is_encrypted(text):
    """
    Intenta determinar si un texto ya está encriptado.

    Args:
        text (str): Texto a verificar

    Returns:
        bool: True si parece estar encriptado, False si no
    """
    try:
        # Intentar desencriptar
        decrypted = decrypt_text(text)
        # Si la desencriptación produce un texto diferente, probablemente estaba encriptado
        return decrypted != text
    except:
        # Si falla la desencriptación, probablemente no está encriptado
        return False


def migrate_credentials():
    """
    Migra las credenciales existentes encriptándolas.
    """
    conn = None
    try:
        print("=" * 60)
        print("INICIANDO MIGRACIÓN DE ENCRIPTACIÓN DE CREDENCIALES")
        print("=" * 60)

        conn = get_db_connection()
        cur = conn.cursor()

        # Obtener todas las credenciales
        credenciales = conn.execute("SELECT id, usuario, contrasena, plataforma FROM credenciales_plataforma").fetchall()

        total = len(credenciales)
        print(f"\nTotal de credenciales encontradas: {total}")

        if total == 0:
            print("No hay credenciales para migrar.")
            return

        # Preguntar confirmación
        respuesta = input("\n¿Desea continuar con la migración? (s/n): ").lower()
        if respuesta != "s":
            print("Migración cancelada por el usuario.")
            return

        migradas = 0
        ya_encriptadas = 0
        errores = 0

        for credencial in credenciales:
            try:
                cred_id = credencial["id"]
                usuario = credencial["usuario"]
                contrasena = credencial["contrasena"]
                plataforma = credencial["plataforma"]

                # Verificar si ya están encriptadas
                usuario_encriptado = is_encrypted(usuario) if usuario else False
                contrasena_encriptada = is_encrypted(contrasena) if contrasena else False

                if usuario_encriptado and contrasena_encriptada:
                    print(f"✓ Credencial {cred_id} ({plataforma}) ya está encriptada")
                    ya_encriptadas += 1
                    continue

                # Encriptar si no están encriptadas
                nuevo_usuario = encrypt_text(usuario) if usuario and not usuario_encriptado else usuario
                nueva_contrasena = encrypt_text(contrasena) if contrasena and not contrasena_encriptada else contrasena

                # Actualizar en la base de datos
                cur.execute(
                    """
                    UPDATE credenciales_plataforma
                    SET usuario = ?, contrasena = ?
                    WHERE id = ?
                """,
                    (nuevo_usuario, nueva_contrasena, cred_id),
                )

                print(f"✓ Credencial {cred_id} ({plataforma}) encriptada correctamente")
                migradas += 1

            except Exception as e:
                print(f"✗ Error migrando credencial {cred_id}: {e}")
                logger.error(f"Error migrando credencial {cred_id}: {e}", exc_info=True)
                errores += 1

        # Confirmar cambios
        conn.commit()

        print("\n" + "=" * 60)
        print("RESUMEN DE LA MIGRACIÓN")
        print("=" * 60)
        print(f"Total procesadas:      {total}")
        print(f"Migradas exitosamente: {migradas}")
        print(f"Ya encriptadas:        {ya_encriptadas}")
        print(f"Errores:               {errores}")
        print("=" * 60)

        if errores == 0:
            print("\n✓ Migración completada exitosamente")
            logger.info(f"Migración completada: {migradas} credenciales encriptadas")
        else:
            print(f"\n⚠ Migración completada con {errores} errores")
            logger.warning(f"Migración completada con {errores} errores")

    except Exception as e:
        print(f"\n✗ Error crítico durante la migración: {e}")
        logger.error(f"Error crítico durante la migración: {e}", exc_info=True)
        if conn:
            conn.rollback()
        sys.exit(1)
    finally:
        if conn:
            conn.close()


def verify_encryption():
    """
    Verifica que las credenciales estén correctamente encriptadas.
    """
    conn = None
    try:
        print("\n" + "=" * 60)
        print("VERIFICANDO ENCRIPTACIÓN DE CREDENCIALES")
        print("=" * 60)

        conn = get_db_connection()

        # Obtener todas las credenciales
        credenciales = conn.execute("SELECT id, usuario, contrasena, plataforma FROM credenciales_plataforma").fetchall()

        print(f"\nVerificando {len(credenciales)} credenciales...\n")

        for credencial in credenciales:
            cred_id = credencial["id"]
            usuario = credencial["usuario"]
            contrasena = credencial["contrasena"]
            plataforma = credencial["plataforma"]

            try:
                # Intentar desencriptar
                usuario_desencriptado = decrypt_text(usuario) if usuario else "N/A"
                contrasena_desencriptada = decrypt_text(contrasena) if contrasena else "N/A"

                # Mostrar información (ocultando la contraseña)
                print(f"ID: {cred_id} | Plataforma: {plataforma}")
                print(f"  Usuario: {usuario_desencriptado}")
                print(f"  Contraseña: {'*' * len(contrasena_desencriptada)}")
                print()

            except Exception as e:
                print(f"✗ Error verificando credencial {cred_id}: {e}")

        print("=" * 60)
        print("Verificación completada")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error durante la verificación: {e}")
        logger.error(f"Error durante la verificación: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    print(
        """
╔══════════════════════════════════════════════════════════════╗
║  SCRIPT DE MIGRACIÓN DE ENCRIPTACIÓN DE CREDENCIALES        ║
╚══════════════════════════════════════════════════════════════╝

Este script encriptará todas las credenciales existentes en
la base de datos que actualmente están en texto plano.

IMPORTANTE:
- Asegúrese de tener un respaldo de la base de datos
- Este script debe ejecutarse UNA SOLA VEZ
- Las credenciales ya encriptadas no se modificarán

"""
    )

    # Menú de opciones
    print("Opciones:")
    print("1. Migrar y encriptar credenciales")
    print("2. Verificar encriptación")
    print("3. Salir")

    opcion = input("\nSeleccione una opción (1-3): ").strip()

    if opcion == "1":
        migrate_credentials()
    elif opcion == "2":
        verify_encryption()
    elif opcion == "3":
        print("Saliendo...")
    else:
        print("Opción no válida")
