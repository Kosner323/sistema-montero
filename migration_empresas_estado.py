#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
migration_empresas_estado.py
============================
Migración: Agregar columna 'estado' a la tabla empresas
Autor: Senior Backend Developer
Fecha: 2025-11-30 (Fase 10.4)
"""

import sys
import os
import sqlite3
import shutil
from datetime import datetime

# Fix encoding para Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configuración
DATABASE_PATH = r"d:\Mi-App-React\data\mi_sistema.db"
BACKUP_DIR = r"d:\Mi-App-React\backups"


def crear_backup():
    """Crea un backup de la base de datos antes de la migración"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"mi_sistema_backup_{timestamp}.db")

    print(f"\n📦 Creando backup: {backup_path}")
    shutil.copy2(DATABASE_PATH, backup_path)
    print(f"✅ Backup creado exitosamente")

    return backup_path


def verificar_columna_existe(cursor):
    """Verifica si la columna 'estado' ya existe"""
    cursor.execute("PRAGMA table_info(empresas)")
    columnas = [col[1] for col in cursor.fetchall()]
    return 'estado' in columnas


def ejecutar_migracion():
    """Ejecuta la migración de la columna estado"""
    print("\n" + "="*80)
    print("MIGRACIÓN: Agregar columna 'estado' a tabla empresas")
    print("="*80)

    # Verificar que existe la base de datos
    if not os.path.exists(DATABASE_PATH):
        print(f"❌ ERROR: Base de datos no encontrada en {DATABASE_PATH}")
        sys.exit(1)

    print(f"✅ Base de datos encontrada: {DATABASE_PATH}")

    # Crear backup
    backup_path = crear_backup()

    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Verificar si la columna ya existe
        print("\n📋 Verificando si columna 'estado' ya existe...")

        if verificar_columna_existe(cursor):
            print("⚠️  La columna 'estado' ya existe en la tabla empresas")
            respuesta = input("¿Deseas continuar de todos modos? (s/n): ").lower()
            if respuesta != 's':
                print("❌ Migración cancelada")
                conn.close()
                sys.exit(0)

        # PASO 1: Agregar columna estado
        print("\n📋 PASO 1: Agregando columna 'estado' a tabla empresas...")

        cursor.execute("""
            ALTER TABLE empresas
            ADD COLUMN estado TEXT DEFAULT 'Activa'
        """)

        print("   ✅ Columna 'estado' agregada exitosamente")

        # PASO 2: Actualizar registros existentes
        print("\n📋 PASO 2: Actualizando registros existentes...")

        cursor.execute("""
            UPDATE empresas
            SET estado = 'Activa'
            WHERE estado IS NULL OR estado = ''
        """)

        filas_actualizadas = cursor.rowcount
        print(f"   ✅ {filas_actualizadas} empresas actualizadas a estado 'Activa'")

        # PASO 3: Verificar cambios
        print("\n📋 PASO 3: Verificando cambios...")

        cursor.execute("SELECT COUNT(*) FROM empresas WHERE estado = 'Activa'")
        total_activas = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM empresas")
        total_empresas = cursor.fetchone()[0]

        print(f"   ✅ Total empresas: {total_empresas}")
        print(f"   ✅ Empresas activas: {total_activas}")

        # PASO 4: Verificar estructura de tabla
        print("\n📋 PASO 4: Verificando estructura de tabla...")

        cursor.execute("PRAGMA table_info(empresas)")
        columnas = cursor.fetchall()

        print(f"\n   📊 Tabla 'empresas': {len(columnas)} columnas")
        for col in columnas:
            col_id, nombre, tipo, notnull, default, pk = col
            nullable = "NOT NULL" if notnull else "NULL"
            primary = "PRIMARY KEY" if pk else ""
            default_val = f"DEFAULT {default}" if default else ""
            print(f"      - {nombre:<25} {tipo:<10} {nullable:<10} {primary} {default_val}")

        # Commit de cambios
        conn.commit()

        # RESULTADO
        print("\n" + "="*80)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("="*80)
        print("\nRESUMEN:")
        print(f"  ✓ Columna 'estado' agregada a tabla empresas")
        print(f"  ✓ {filas_actualizadas} registros actualizados")
        print(f"  ✓ Backup creado: {backup_path}")
        print("\nOBJETIVO CUMPLIDO: Empresas ahora soportan soft delete")
        print("="*80 + "\n")

        conn.close()
        return True

    except Exception as e:
        print(f"\n❌ ERROR durante la migración: {e}")
        import traceback
        traceback.print_exc()

        print(f"\n🔄 Restaurando desde backup: {backup_path}")
        try:
            shutil.copy2(backup_path, DATABASE_PATH)
            print("✅ Base de datos restaurada")
        except Exception as restore_error:
            print(f"❌ Error al restaurar: {restore_error}")

        return False


if __name__ == "__main__":
    print("\n" + "="*80)
    print(" "*20 + "FASE 10.4: SOFT DELETE EMPRESAS")
    print("="*80)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    resultado = ejecutar_migracion()

    if resultado:
        print("\n[RESULTADO FINAL] Migración exitosa - Sistema listo para soft delete de empresas")
    else:
        print("\n[RESULTADO FINAL] Migración fallida - Revisar logs")

    print("="*80 + "\n")
