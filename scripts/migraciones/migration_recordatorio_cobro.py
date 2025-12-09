#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
migration_recordatorio_cobro.py
================================
Migración: Agregar columna 'fecha_recordatorio_cobro' a la tabla deudas_cartera
Autor: Senior Backend Developer
Fecha: 2025-11-30 (Agenda de Cobros Personalizada)
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


def verificar_tabla_existe(cursor, tabla):
    """Verifica si la tabla existe"""
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tabla}'")
    return cursor.fetchone() is not None


def verificar_columna_existe(cursor, tabla, columna):
    """Verifica si la columna ya existe en la tabla"""
    cursor.execute(f"PRAGMA table_info({tabla})")
    columnas = [col[1] for col in cursor.fetchall()]
    return columna in columnas


def ejecutar_migracion():
    """Ejecuta la migración de la columna fecha_recordatorio_cobro"""
    print("\n" + "="*80)
    print("MIGRACIÓN: Agregar columna 'fecha_recordatorio_cobro' a tabla deudas_cartera")
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

        # Verificar si la tabla deudas_cartera existe
        print("\n📋 Verificando tabla 'deudas_cartera'...")

        if not verificar_tabla_existe(cursor, 'deudas_cartera'):
            print("❌ ERROR: La tabla 'deudas_cartera' no existe")
            print("\n⚠️  ALTERNATIVA: Agregando columna a tabla 'empresas'...")

            # Si no existe deudas_cartera, agregar a empresas
            if not verificar_tabla_existe(cursor, 'empresas'):
                print("❌ ERROR: Tampoco existe la tabla 'empresas'")
                conn.close()
                sys.exit(1)

            tabla_objetivo = 'empresas'
        else:
            print("   ✅ Tabla 'deudas_cartera' encontrada")
            tabla_objetivo = 'deudas_cartera'

        # Verificar si la columna ya existe
        print(f"\n📋 Verificando si columna 'fecha_recordatorio_cobro' ya existe en '{tabla_objetivo}'...")

        if verificar_columna_existe(cursor, tabla_objetivo, 'fecha_recordatorio_cobro'):
            print("⚠️  La columna 'fecha_recordatorio_cobro' ya existe")
            respuesta = input("¿Deseas continuar de todos modos? (s/n): ").lower()
            if respuesta != 's':
                print("❌ Migración cancelada")
                conn.close()
                sys.exit(0)
        else:
            print("   ✅ Columna no existe, procediendo con la migración...")

        # PASO 1: Agregar columna fecha_recordatorio_cobro
        print(f"\n📋 PASO 1: Agregando columna 'fecha_recordatorio_cobro' a tabla '{tabla_objetivo}'...")

        cursor.execute(f"""
            ALTER TABLE {tabla_objetivo}
            ADD COLUMN fecha_recordatorio_cobro TEXT DEFAULT NULL
        """)

        print("   ✅ Columna 'fecha_recordatorio_cobro' agregada exitosamente")

        # PASO 2: Verificar cambios
        print("\n📋 PASO 2: Verificando cambios...")

        cursor.execute(f"SELECT COUNT(*) FROM {tabla_objetivo}")
        total_registros = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM {tabla_objetivo} WHERE fecha_recordatorio_cobro IS NULL")
        total_sin_recordatorio = cursor.fetchone()[0]

        print(f"   ✅ Total registros en '{tabla_objetivo}': {total_registros}")
        print(f"   ✅ Registros sin recordatorio programado: {total_sin_recordatorio}")

        # PASO 3: Verificar estructura de tabla
        print(f"\n📋 PASO 3: Verificando estructura de tabla '{tabla_objetivo}'...")

        cursor.execute(f"PRAGMA table_info({tabla_objetivo})")
        columnas = cursor.fetchall()

        print(f"\n   📊 Tabla '{tabla_objetivo}': {len(columnas)} columnas")

        # Mostrar solo las últimas 10 columnas para no saturar
        print("   Últimas 10 columnas:")
        for col in columnas[-10:]:
            col_id, nombre, tipo, notnull, default, pk = col
            nullable = "NOT NULL" if notnull else "NULL"
            primary = "PRIMARY KEY" if pk else ""
            default_val = f"DEFAULT {default}" if default else ""
            print(f"      - {nombre:<30} {tipo:<10} {nullable:<10} {primary} {default_val}")

        # Commit de cambios
        conn.commit()

        # RESULTADO
        print("\n" + "="*80)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("="*80)
        print("\nRESUMEN:")
        print(f"  ✓ Columna 'fecha_recordatorio_cobro' agregada a tabla '{tabla_objetivo}'")
        print(f"  ✓ Total registros: {total_registros}")
        print(f"  ✓ Backup creado: {backup_path}")
        print("\nOBJETIVO CUMPLIDO: Sistema listo para agendar recordatorios de cobro")
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
    print(" "*15 + "AGENDA DE COBROS PERSONALIZADA")
    print("="*80)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    resultado = ejecutar_migracion()

    if resultado:
        print("\n[RESULTADO FINAL] Migración exitosa - Sistema listo para recordatorios")
    else:
        print("\n[RESULTADO FINAL] Migración fallida - Revisar logs")

    print("="*80 + "\n")
