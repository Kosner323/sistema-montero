#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fix_empresa_nit_nullable.py
============================
Script de migracion para permitir que el campo empresa_nit sea NULL.

CAMBIO DE LOGICA DE NEGOCIO:
- La entidad Usuario ahora es INDEPENDIENTE
- NO es obligatorio tener una empresa asignada
- Se elimina la restriccion NOT NULL de empresa_nit

Autor: Claude Code
Fecha: 2025-11-29
"""

import sqlite3
import os
import shutil
from datetime import datetime
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Ruta a la base de datos
DB_PATH = r"d:\Mi-App-React\data\mi_sistema.db"
BACKUP_DIR = r"d:\Mi-App-React\data\backups"


def crear_backup():
    """Crear backup de la base de datos antes de modificarla"""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"mi_sistema_backup_{timestamp}.db")

    shutil.copy2(DB_PATH, backup_path)
    print(f"[OK] Backup creado: {backup_path}")
    return backup_path


def migrar_tabla_usuarios():
    """Elimina la restriccion NOT NULL de empresa_nit"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print("\n" + "="*80)
        print("INICIANDO MIGRACION: Permitir empresa_nit NULL")
        print("="*80 + "\n")

        # 1. Verificar estructura actual
        print("[1] Verificando estructura actual...")
        cursor.execute("PRAGMA table_info(usuarios)")
        columnas_actuales = cursor.fetchall()

        print("   Columnas actuales:")
        for col in columnas_actuales:
            if col[1] == 'empresa_nit':
                print(f"      > {col[1]}: NOT NULL = {col[3]}")

        # 2. Crear tabla temporal con ESTRUCTURA EXACTA (solo cambiar empresa_nit)
        print("\n[2] Creando tabla temporal sin restriccion NOT NULL...")
        # Primero eliminar tabla temporal si existe (de intento anterior)
        cursor.execute("DROP TABLE IF EXISTS usuarios_temp")
        cursor.execute("""
            CREATE TABLE usuarios_temp (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_nit TEXT,  -- [OK] REMOVIDO NOT NULL (UNICO CAMBIO)
                tipoId TEXT,
                numeroId TEXT,
                primerNombre TEXT,
                segundoNombre TEXT,
                primerApellido TEXT,
                segundoApellido TEXT,
                sexoBiologico TEXT,
                sexoIdentificacion TEXT,
                nacionalidad TEXT,
                fechaNacimiento TEXT,
                paisNacimiento TEXT,
                departamentoNacimiento TEXT,
                municipioNacimiento TEXT,
                direccion TEXT,
                telefonoCelular TEXT,
                telefonoFijo TEXT,
                correoElectronico TEXT,
                comunaBarrio TEXT,
                afpNombre TEXT,
                afpCosto FLOAT,
                epsNombre TEXT,
                epsCosto FLOAT,
                arlNombre TEXT,
                arlCosto FLOAT,
                ccfNombre TEXT,
                ccfCosto FLOAT,
                administracion TEXT,
                ibc FLOAT,
                claseRiesgoARL TEXT,
                fechaIngreso TEXT,
                created_at TEXT,
                password_hash VARCHAR(255),
                role VARCHAR(50) DEFAULT 'user'
            )
        """)
        print("   [OK] Tabla temporal creada")

        # 3. Copiar todos los datos a la tabla temporal
        print("\n[3] Copiando datos de usuarios a usuarios_temp...")
        cursor.execute("""
            INSERT INTO usuarios_temp
            SELECT * FROM usuarios
        """)
        rows_copied = cursor.rowcount
        print(f"   [OK] {rows_copied} registros copiados")

        # 4. Eliminar tabla original
        print("\n[4] Eliminando tabla original...")
        cursor.execute("DROP TABLE usuarios")
        print("   [OK] Tabla usuarios eliminada")

        # 5. Renombrar tabla temporal
        print("\n[5] Renombrando usuarios_temp -> usuarios...")
        cursor.execute("ALTER TABLE usuarios_temp RENAME TO usuarios")
        print("   [OK] Tabla renombrada")

        # 6. Recrear indices
        print("\n[6] Recreando indices...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_usuarios_empresa
                ON usuarios(empresa_nit)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_usuarios_nombre
                ON usuarios(primerNombre, primerApellido)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_usuarios_email
                ON usuarios(correoElectronico)
        """)
        print("   [OK] Indices recreados")

        # 7. Recrear trigger
        print("\n[7] Recreando trigger updated_at...")
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS trg_usuarios_updated_at
            AFTER UPDATE ON usuarios
            FOR EACH ROW
            BEGIN
                UPDATE usuarios
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = NEW.id;
            END
        """)
        print("   [OK] Trigger recreado")

        # 8. Verificar nueva estructura
        print("\n[8] Verificando nueva estructura...")
        cursor.execute("PRAGMA table_info(usuarios)")
        columnas_nuevas = cursor.fetchall()

        for col in columnas_nuevas:
            if col[1] == 'empresa_nit':
                print(f"   > {col[1]}: NOT NULL = {col[3]} (0 = permite NULL)")

        # 9. Confirmar cambios
        conn.commit()
        print("\n[OK] MIGRACION COMPLETADA EXITOSAMENTE")
        print("="*80)

        # 10. Prueba de insercion con empresa_nit NULL
        print("\n[TEST] PRUEBA DE INSERCION CON empresa_nit = NULL...")
        try:
            cursor.execute("""
                INSERT INTO usuarios (
                    empresa_nit, tipoId, numeroId, primerNombre, primerApellido
                ) VALUES (NULL, 'CC', 'TEST_NULL_123', 'Kevin', 'Prueba')
            """)
            conn.commit()
            print("   [OK] INSERT con empresa_nit=NULL funciono correctamente")

            # Eliminar registro de prueba
            cursor.execute("DELETE FROM usuarios WHERE numeroId = 'TEST_NULL_123'")
            conn.commit()
            print("   [OK] Registro de prueba eliminado")

        except sqlite3.IntegrityError as e:
            print(f"   [ERROR] La prueba fallo - {e}")
            return False

        return True

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] DURANTE LA MIGRACION: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        conn.close()


def verificar_migracion():
    """Verifica que la migracion fue exitosa"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Contar usuarios con empresa_nit NULL
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE empresa_nit IS NULL")
        null_count = cursor.fetchone()[0]

        # Contar usuarios totales
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        total_count = cursor.fetchone()[0]

        print("\n" + "="*80)
        print("VERIFICACION POST-MIGRACION")
        print("="*80)
        print(f"Total de usuarios: {total_count}")
        print(f"Usuarios sin empresa (NULL): {null_count}")
        print(f"Usuarios con empresa: {total_count - null_count}")
        print("="*80 + "\n")

    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 80)
    print(" " * 10 + "MIGRACION DE BASE DE DATOS - empresa_nit NULLABLE")
    print("=" * 80 + "\n")

    # 1. Crear backup
    print("PASO 1: Creando backup de seguridad...")
    backup_path = crear_backup()

    # 2. Ejecutar migracion
    print("\nPASO 2: Ejecutando migracion...")
    success = migrar_tabla_usuarios()

    if success:
        # 3. Verificar
        print("\nPASO 3: Verificando migracion...")
        verificar_migracion()

        print("\n[SUCCESS] MIGRACION COMPLETADA CON EXITO")
        print(f"[BACKUP] Disponible en: {backup_path}")
        print("\n[PROXIMOS PASOS]:")
        print("   1. Reiniciar el servidor Flask")
        print("   2. Probar crear un usuario sin empresa")
        print("   3. Verificar que el campo empresa_nit se guarde como NULL\n")
    else:
        print("\n[ERROR] LA MIGRACION FALLO")
        print(f"[BACKUP] Puedes restaurar el backup desde: {backup_path}\n")
