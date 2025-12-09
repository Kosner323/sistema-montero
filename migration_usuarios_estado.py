#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
migration_usuarios_estado.py
=============================
Migración: Agregar columna 'estado' (TEXT, default 'Activo') a tabla usuarios
Fecha: 2025-11-29
Fase: 10.1 - Ciclo de Vida del Usuario
"""

import sqlite3
import sys
from datetime import datetime
import shutil

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = r"d:\Mi-App-React\data\mi_sistema.db"
BACKUP_FOLDER = r"d:\Mi-App-React\backups"


def migrate_usuarios_estado():
    """
    Agrega la columna 'estado' a la tabla usuarios con valor por defecto 'Activo'
    """
    print("\n" + "="*80)
    print("MIGRACION: Agregar columna 'estado' a tabla usuarios")
    print("="*80)

    # Crear backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{BACKUP_FOLDER}/mi_sistema_backup_{timestamp}.db"

    try:
        shutil.copy2(DB_PATH, backup_path)
        print(f"\n[OK] Backup creado: {backup_path}")
    except Exception as e:
        print(f"\n[ERROR] No se pudo crear backup: {e}")
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(usuarios)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        if 'estado' in column_names:
            print("\n[INFO] La columna 'estado' ya existe en la tabla usuarios")
            print("[SKIP] No es necesario ejecutar la migración")
            conn.close()
            return True

        print("\n[PASO 1] Verificando estructura actual de la tabla...")
        print(f"   Columnas actuales: {len(column_names)}")

        # ==================== AGREGAR COLUMNA estado ====================
        print("\n[PASO 2] Agregando columna 'estado' con valor por defecto 'Activo'...")

        cursor.execute("""
            ALTER TABLE usuarios
            ADD COLUMN estado TEXT DEFAULT 'Activo'
        """)

        conn.commit()
        print("   [OK] Columna 'estado' agregada exitosamente")

        # ==================== ACTUALIZAR REGISTROS EXISTENTES ====================
        print("\n[PASO 3] Actualizando registros existentes a estado 'Activo'...")

        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE estado IS NULL OR estado = ''")
        usuarios_sin_estado = cursor.fetchone()[0]

        if usuarios_sin_estado > 0:
            cursor.execute("""
                UPDATE usuarios
                SET estado = 'Activo'
                WHERE estado IS NULL OR estado = ''
            """)
            conn.commit()
            print(f"   [OK] {usuarios_sin_estado} usuarios actualizados a estado 'Activo'")
        else:
            print("   [OK] Todos los usuarios ya tienen estado asignado")

        # ==================== VERIFICACIÓN ====================
        print("\n[PASO 4] Verificando migración...")

        cursor.execute("PRAGMA table_info(usuarios)")
        columns_after = cursor.fetchall()

        estado_col = next((col for col in columns_after if col[1] == 'estado'), None)

        if estado_col:
            print(f"   [OK] Columna 'estado' verificada:")
            print(f"        - Nombre: {estado_col[1]}")
            print(f"        - Tipo: {estado_col[2]}")
            print(f"        - Default: {estado_col[4]}")
        else:
            print("   [ERROR] No se pudo verificar la columna 'estado'")
            return False

        # Verificar datos
        cursor.execute("SELECT estado, COUNT(*) FROM usuarios GROUP BY estado")
        estado_counts = cursor.fetchall()

        print("\n   [ESTADISTICAS] Distribución de estados:")
        for estado, count in estado_counts:
            print(f"        - {estado}: {count} usuarios")

        # ==================== RESULTADO ====================
        print("\n" + "="*80)
        print("[SUCCESS] MIGRACION EXITOSA")
        print("="*80)
        print("\nCambios realizados:")
        print("  ✓ Columna 'estado' agregada a tabla usuarios")
        print("  ✓ Valor por defecto: 'Activo'")
        print("  ✓ Registros existentes actualizados")
        print("\nValores permitidos:")
        print("  - 'Activo': Usuario activo en el sistema")
        print("  - 'Inactivo': Usuario desactivado (no se elimina)")
        print("\nBackup guardado en:")
        print(f"  {backup_path}")
        print("="*80 + "\n")

        return True

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
        print(f"\n[ROLLBACK] Restaurar desde backup si es necesario:")
        print(f"  {backup_path}")
        return False

    finally:
        conn.close()


if __name__ == "__main__":
    print("="*80)
    print(" "*15 + "FASE 10.1: CICLO DE VIDA DEL USUARIO")
    print("="*80)

    resultado = migrate_usuarios_estado()

    if resultado:
        print("\n[RESULTADO FINAL] Migración completada exitosamente")
        print("Ahora puedes usar el campo 'estado' para gestionar usuarios activos/inactivos")
    else:
        print("\n[RESULTADO FINAL] Migración fallida. Revisar errores arriba.")

    print("="*80 + "\n")
