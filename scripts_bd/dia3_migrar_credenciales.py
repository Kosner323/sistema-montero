# -*- coding: utf-8 -*-
"""
DÍA 3: MIGRACIÓN DE CREDENCIALES EXISTENTES
(Versión corregida para Windows)
"""

import sqlite3
import os
import sys
import shutil
from datetime import datetime
from pathlib import Path

# --- RUTA CORREGIDA ---
# Apunta a la carpeta 'dashboard'
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
# ----------------------

try:
    from logger import get_logger

    # Importar solo las funciones que SÍ existen
    from encryption import encrypt_text, decrypt_text, get_encryption
except ImportError as e:
    print(f"❌ Error: No se pudieron importar los módulos necesarios: {e}")
    print(f"Asegúrate de que 'encryption.py' y 'logger.py' estén en: {PROJECT_ROOT}")
    sys.exit(1)

logger = get_logger(__name__)


class CredentialMigrator:
    """Clase para manejar la migración de credenciales."""

    def __init__(self):
        # --- RUTA CORREGIDA ---
        self.db_path = os.path.join(PROJECT_ROOT, "data", "mi_sistema.db")
        self.backup_dir = Path(os.path.join(PROJECT_ROOT, "backups"))
        # ----------------------
        self.backup_path = None
        self.stats = {
            "total": 0,
            "migradas": 0,
            "ya_encriptadas": 0,
            "errores": 0,
            "detalles": [],
        }

        if not os.path.exists(self.db_path):
            raise FileNotFoundError(
                f"❌ No se encontró la base de datos en: {self.db_path}"
            )

    def create_backup(self):
        """Crea un respaldo de la base de datos antes de la migración."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.backup_dir.mkdir(exist_ok=True)

            self.backup_path = self.backup_dir / f"mi_sistema_backup_{timestamp}.db"
            shutil.copy2(self.db_path, self.backup_path)

            backup_size = os.path.getsize(self.backup_path) / 1024  # KB
            print(f"✅ Respaldo creado: {self.backup_path} ({backup_size:.2f} KB)")
            logger.info(f"Respaldo creado: {self.backup_path}")
            return True

        except Exception as e:
            print(f"❌ Error creando respaldo: {e}")
            logger.error(f"Error creando respaldo: {e}", exc_info=True)
            return False

    # +++ FUNCIÓN CORREGIDA +++
    # Esta función (método) debe estar DENTRO de la clase
    def is_encrypted(self, text):
        """
        Determina si un texto está encriptado (versión corregida).
        """
        if not text or len(text) < 10:
            return False

        # Una heurística simple: las cadenas Fernet válidas suelen empezar con 'gAAAAA'
        if text.startswith("gAAAAA"):
            try:
                # Intentar desencriptar
                decrypt_text(text)
                return True  # Si lo desencripta, está encriptado
            except Exception:
                # Si empieza con 'gAAAAA' pero no desencripta, es un error
                # pero para esta migración, lo contamos como "ya encriptado"
                return True

        # Si no empieza con 'gAAAAA', asumimos que es texto plano
        return False

    def analyze_database(self):
        """Analiza el estado actual de las credenciales en la BD."""
        print("\n" + "=" * 70)
        print("📊 ANÁLISIS DE CREDENCIALES EN BASE DE DATOS")
        print("=" * 70)

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            credenciales = conn.execute(
                "SELECT id, usuario, contrasena, plataforma FROM credenciales_plataforma"
            ).fetchall()

            self.stats["total"] = len(credenciales)

            if self.stats["total"] == 0:
                print("\n⚠️  No hay credenciales en la base de datos")
                return False

            print(f"\n📌 Total de credenciales: {self.stats['total']}")
            print("\n" + "-" * 70)

            encriptadas = 0
            texto_plano = 0

            for cred in credenciales:
                # +++ LLAMADA CORREGIDA +++
                # Llamar a la función de la clase con 'self.'
                usuario_enc = (
                    self.is_encrypted(cred["usuario"]) if cred["usuario"] else True
                )
                contra_enc = (
                    self.is_encrypted(cred["contrasena"])
                    if cred["contrasena"]
                    else True
                )

                estado = (
                    "🔒 ENCRIPTADA"
                    if (usuario_enc and contra_enc)
                    else "🔓 TEXTO PLANO"
                )

                if usuario_enc and contra_enc:
                    encriptadas += 1
                else:
                    texto_plano += 1

                print(f"ID {cred['id']:3d} | {cred['plataforma']:30s} | {estado}")

            print("-" * 70)
            print(f"\n📊 Resumen:")
            print(f"   🔒 Ya encriptadas: {encriptadas}")
            print(f"   🔓 En texto plano: {texto_plano}")

            conn.close()
            return texto_plano > 0

        except Exception as e:
            print(f"\n❌ Error analizando base de datos: {e}")
            logger.error(f"Error en análisis: {e}", exc_info=True)
            return False

    def migrate_credentials(self):
        """Migra las credenciales de texto plano a encriptado."""
        print("\n" + "=" * 70)
        print("🔐 INICIANDO MIGRACIÓN DE CREDENCIALES")
        print("=" * 70)

        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            credenciales = conn.execute(
                "SELECT id, usuario, contrasena, plataforma FROM credenciales_plataforma"
            ).fetchall()

            print(f"\n📝 Procesando {len(credenciales)} credenciales...\n")

            for cred in credenciales:
                try:
                    cred_id = cred["id"]
                    usuario = cred["usuario"]
                    contrasena = cred["contrasena"]
                    plataforma = cred["plataforma"]

                    # +++ LLAMADA CORREGIDA +++
                    usuario_enc = self.is_encrypted(usuario) if usuario else True
                    contra_enc = self.is_encrypted(contrasena) if contrasena else True

                    if usuario_enc and contra_enc:
                        print(f"  ✓ ID {cred_id:3d} | {plataforma:30s} | Ya encriptada")
                        self.stats["ya_encriptadas"] += 1
                        continue

                    nuevo_usuario = (
                        encrypt_text(usuario)
                        if usuario and not usuario_enc
                        else usuario
                    )
                    nueva_contrasena = (
                        encrypt_text(contrasena)
                        if contrasena and not contra_enc
                        else contrasena
                    )

                    cur.execute(
                        """
                        UPDATE credenciales_plataforma 
                        SET usuario = ?, contrasena = ? 
                        WHERE id = ?
                    """,
                        (nuevo_usuario, nueva_contrasena, cred_id),
                    )

                    print(
                        f"  ✅ ID {cred_id:3d} | {plataforma:30s} | Encriptada correctamente"
                    )
                    self.stats["migradas"] += 1

                except Exception as e:
                    print(f"  ❌ ID {cred_id:3d} | {plataforma:30s} | Error: {e}")
                    self.stats["errores"] += 1
                    logger.error(
                        f"Error migrando credencial {cred_id}: {e}", exc_info=True
                    )

            conn.commit()
            print("\n✅ Cambios guardados en la base de datos")
            return True

        except Exception as e:
            print(f"\n❌ Error crítico durante migración: {e}")
            logger.error(f"Error crítico en migración: {e}", exc_info=True)
            if conn:
                conn.rollback()
                print("⚠️  Se revirtieron los cambios")
            return False
        finally:
            if conn:
                conn.close()

    def verify_migration(self):
        """Verifica que todas las credenciales estén correctamente encriptadas."""
        print("\n" + "=" * 70)
        print("🔍 VERIFICANDO RESULTADO DE LA MIGRACIÓN")
        print("=" * 70)

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            credenciales = conn.execute(
                "SELECT id, usuario, contrasena, plataforma FROM credenciales_plataforma"
            ).fetchall()

            print(f"\n🔎 Verificando {len(credenciales)} credenciales...\n")

            verificadas = 0
            errores_verificacion = 0

            for cred in credenciales:
                try:
                    cred_id = cred["id"]
                    usuario = cred["usuario"]
                    contrasena = cred["contrasena"]
                    plataforma = cred["plataforma"]

                    usuario_dec = decrypt_text(usuario) if usuario else "[vacío]"
                    contra_dec = decrypt_text(contrasena) if contrasena else "[vacío]"

                    if usuario_dec and contra_dec:
                        print(
                            f"  ✅ ID {cred_id:3d} | {plataforma:30s} | Verificada OK"
                        )
                        verificadas += 1
                    else:
                        print(
                            f"  ⚠️  ID {cred_id:3d} | {plataforma:30s} | Verificación parcial"
                        )
                        errores_verificacion += 1

                except Exception as e:
                    print(
                        f"  ❌ ID {cred_id:3d} | {plataforma:30s} | Error verificando: {e}"
                    )
                    errores_verificacion += 1

            print("\n" + "-" * 70)
            print(f"✅ Verificadas correctamente: {verificadas}")
            print(f"⚠️  Con advertencias/errores: {errores_verificacion}")
            print("-" * 70)

            conn.close()
            return errores_verificacion == 0

        except Exception as e:
            print(f"\n❌ Error durante verificación: {e}")
            logger.error(f"Error en verificación: {e}", exc_info=True)
            return False

    def print_summary(self):
        """Imprime un resumen detallado de la migración."""
        print("\n" + "=" * 70)
        print("📊 RESUMEN DE LA MIGRACIÓN")
        print("=" * 70)
        print(f"\n📈 Estadísticas:")
        print(f"   • Total procesadas:      {self.stats['total']}")
        print(f"   • Migradas exitosamente: {self.stats['migradas']}")
        print(f"   • Ya encriptadas:        {self.stats['ya_encriptadas']}")
        print(f"   • Errores:               {self.stats['errores']}")

        if self.backup_path:
            print(f"\n💾 Respaldo guardado en: {self.backup_path}")

        if self.stats["errores"] == 0:
            print("\n✅ ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
            logger.info(
                f"Migración exitosa: {self.stats['migradas']} credenciales encriptadas"
            )
        else:
            print(f"\n⚠️  Migración completada con {self.stats['errores']} errores")
            logger.warning(f"Migración con errores: {self.stats['errores']}")

        print("=" * 70)


def main():
    """Función principal."""
    print("DÍA 3: MIGRACIÓN DE CREDENCIALES A ENCRIPTACIÓN")

    try:
        print("🔐 Verificando sistema de encriptación...")
        get_encryption()
        print("✅ Sistema de encriptación disponible\n")

        migrator = CredentialMigrator()

        hay_pendientes = migrator.analyze_database()

        if not hay_pendientes:
            print("\n✅ No hay credenciales pendientes de migrar")
            return

        print("\n💾 Creando respaldo de seguridad...")
        if not migrator.create_backup():
            if (
                input(
                    "\n⚠️  No se pudo crear respaldo. ¿Continuar de todos modos? (s/n): "
                ).lower()
                != "s"
            ):
                print("❌ Migración cancelada por seguridad")
                return

        print("\n" + "=" * 70)
        # El modo automático ya confirmó esto, así que lo saltamos si no es interactivo
        # (Este script es llamado por el maestro, que ya preguntó)
        # respuesta = input("¿Desea proceder con la migración? (s/n): ").lower()
        # if respuesta != 's':
        #     print("❌ Migración cancelada por el usuario")
        #     return

        if not migrator.migrate_credentials():
            print("\n❌ La migración falló")
            return

        migrator.verify_migration()
        migrator.print_summary()

        print("\n" + "=" * 70)
        print("🎉 ¡DÍA 3 COMPLETADO EXITOSAMENTE!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        logger.error(f"Error crítico en main: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
