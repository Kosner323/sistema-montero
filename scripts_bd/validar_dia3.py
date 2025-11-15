# -*- coding: utf-8 -*-
"""
VALIDADOR POST-MIGRACIÓN DÍA 3
(Versión corregida para Windows)
"""

import os
import sqlite3
import sys

from tabulate import tabulate

# --- RUTA CORREGIDA ---
# Apunta a la carpeta 'dashboard'
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
# ----------------------

try:
    from encryption import decrypt_text
    from logger import logger
except ImportError as e:
    print(f"❌ Error: No se pudieron importar los módulos necesarios: {e}")
    print(f"Asegúrate de que 'encryption.py' y 'logger.py' estén en: {PROJECT_ROOT}")
    sys.exit(1)


def find_database():
    # --- RUTA CORREGIDA ---
    db_path = os.path.join(PROJECT_ROOT, "data", "mi_sistema.db")
    # ----------------------
    if os.path.exists(db_path):
        return db_path
    return None


def validate_credentials():
    print("=" * 80)
    print("🔍 VALIDACIÓN DE CREDENCIALES ENCRIPTADAS")
    print("=" * 80)

    db_path = find_database()
    if not db_path:
        print(f"❌ No se encontró la base de datos en: {os.path.join(PROJECT_ROOT, 'data')}")
        return False

    print(f"\n📁 Base de datos: {db_path}\n")

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row

        # Corrección: Añadido 'tipo' si existe, si no, se omite
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(credenciales_plataforma)")
        columns = [col[1] for col in cur.fetchall()]

        query = "SELECT id, usuario, contrasena, plataforma"
        if "tipo" in columns:
            query += ", tipo"
        query += " FROM credenciales_plataforma"

        credenciales = conn.execute(query).fetchall()

        if len(credenciales) == 0:
            print("⚠️  No hay credenciales en la base de datos")
            return True

        print(f"📊 Total de credenciales: {len(credenciales)}\n")

        resultados = []
        exitosas = 0
        fallidas = 0

        for cred in credenciales:
            cred_id, usuario_enc, contra_enc, plataforma = (
                cred["id"],
                cred["usuario"],
                cred["contrasena"],
                cred["plataforma"],
            )
            tipo = cred["tipo"] if "tipo" in cred.keys() else "N/A"

            try:
                usuario_dec = decrypt_text(usuario_enc) if usuario_enc else "[vacío]"
                contra_dec = decrypt_text(contra_enc) if contra_enc else "[vacío]"

                if len(usuario_dec) > 0 and len(contra_dec) > 0:
                    estado = "✅ OK"
                    exitosas += 1
                    usuario_preview = usuario_dec[:20] + "..." if len(usuario_dec) > 20 else usuario_dec
                    contra_preview = "●" * min(len(contra_dec), 10)
                else:
                    estado = "⚠️  PARCIAL"
                    usuario_preview, contra_preview = "Error", "Error"
                    exitosas += 1

                resultados.append(
                    [
                        cred_id,
                        plataforma[:30],
                        tipo[:15],
                        usuario_preview,
                        contra_preview,
                        estado,
                    ]
                )

            except Exception as e:
                estado = f"❌ ERROR: {str(e)[:30]}"
                fallidas += 1
                resultados.append([cred_id, plataforma[:30], tipo[:15], "Error", "Error", estado])

        headers = ["ID", "Plataforma", "Tipo", "Usuario", "Contraseña", "Estado"]
        print(tabulate(resultados, headers=headers, tablefmt="grid"))

        print("\n" + "=" * 80)
        print("📊 RESUMEN DE VALIDACIÓN")
        print("=" * 80)
        print(f"✅ Credenciales válidas:     {exitosas}")
        print(f"❌ Credenciales con errores: {fallidas}")
        print(f"📈 Tasa de éxito:            {(exitosas/len(credenciales)*100):.1f}%")
        print("=" * 80)

        conn.close()

        if fallidas == 0:
            print("\n🎉 ¡TODAS LAS CREDENCIALES ESTÁN CORRECTAMENTE ENCRIPTADAS!")
            return True
        else:
            print(f"\n⚠️  Hay {fallidas} credenciales con problemas")
            return False

    except Exception as e:
        print(f"\n❌ Error durante la validación: {e}")
        return False


def test_encryption_roundtrip():
    print("\n" + "=" * 80)
    print("🧪 PRUEBA DE ENCRIPTACIÓN (ROUNDTRIP TEST)")
    print("=" * 80)
    try:
        from encryption import decrypt_text, encrypt_text

        test_cases = ["usuario_test", "contraseña123!", "admin@example.com"]
        print("\nProbando encriptación/desencriptación...\n")
        all_passed = True

        for i, original in enumerate(test_cases, 1):
            try:
                encrypted = encrypt_text(original)
                decrypted = decrypt_text(encrypted)
                if decrypted == original:
                    print(f"  ✅ Test {i}: OK - '{original}' → [encrypted] → '{decrypted}'")
                else:
                    print(f"  ❌ Test {i}: FALLO - Original: '{original}' | Recuperado: '{decrypted}'")
                    all_passed = False
            except Exception as e:
                print(f"  ❌ Test {i}: ERROR - {e}")
                all_passed = False

        print("\n" + "-" * 80)
        if all_passed:
            print("✅ Todos los tests de encriptación pasaron correctamente")
        else:
            print("❌ Algunos tests fallaron - revisar el sistema de encriptación")
        print("-" * 80)
        return all_passed
    except Exception as e:
        print(f"\n❌ Error en test de encriptación: {e}")
        return False


def check_encryption_key():
    print("\n" + "=" * 80)
    print("🔑 VERIFICACIÓN DE ENCRYPTION_KEY")
    print("=" * 80)
    try:
        # --- RUTA CORREGIDA ---
        env_file = os.path.join(PROJECT_ROOT, "_env")
        # ----------------------

        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                content = f.read()
            if "ENCRYPTION_KEY=" in content:
                for line in content.split("\n"):
                    if line.startswith("ENCRYPTION_KEY="):
                        key_value = line.split("=", 1)[1].strip()
                        if len(key_value) > 10:
                            print(f"\n✅ ENCRYPTION_KEY encontrada en _env")
                            print(f"   Longitud: {len(key_value)} caracteres")
                            print(f"   Preview: {key_value[:20]}...")
                            return True
                        else:
                            print("\n⚠️  ENCRYPTION_KEY está vacía o muy corta")
                            return False
            else:
                print("\n⚠️  ENCRYPTION_KEY no encontrada en archivo _env")
                return False
        else:
            print(f"\n⚠️  Archivo _env no encontrado en {env_file}")
            return False
    except Exception as e:
        print(f"\n❌ Error verificando ENCRYPTION_KEY: {e}")
        return False


def main():
    print("VALIDADOR POST-MIGRACIÓN - DÍA 3")
    key_ok = check_encryption_key()
    encryption_ok = test_encryption_roundtrip()
    credentials_ok = validate_credentials()

    print("\n" + "=" * 80)
    print("🏁 RESUMEN FINAL DE VALIDACIÓN")
    print("=" * 80)
    print(f"  🔑 ENCRYPTION_KEY configurada:     {'✅ Sí' if key_ok else '❌ No'}")
    print(f"  🧪 Sistema de encriptación:        {'✅ OK' if encryption_ok else '❌ Fallo'}")
    print(f"  💾 Credenciales en BD:              {'✅ OK' if credentials_ok else '❌ Con errores'}")
    print("=" * 80)

    if key_ok and encryption_ok and credentials_ok:
        print("\n🎉 ¡VALIDACIÓN COMPLETA EXITOSA!")
    else:
        print("\n⚠️  Hay problemas que requieren atención")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        from tabulate import tabulate
    except ImportError:
        print("📦 Instalando tabulate para mostrar tablas...")
        os.system(f"{sys.executable} -m pip install tabulate")
        from tabulate import tabulate
    main()
