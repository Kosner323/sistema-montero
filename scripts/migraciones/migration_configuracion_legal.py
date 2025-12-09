#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
migration_configuracion_legal.py
=================================
Migración: Crear tabla 'configuracion_legal' con valores iniciales
Fecha: 2025-11-29
Fase: 10.2 - Configuración Legal
"""

import sqlite3
import sys
from datetime import datetime
import shutil

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = r"d:\Mi-App-React\data\mi_sistema.db"
BACKUP_FOLDER = r"d:\Mi-App-React\backups"


def migrate_configuracion_legal():
    """
    Crea la tabla configuracion_legal y la puebla con valores iniciales
    """
    print("\n" + "="*80)
    print("MIGRACION: Crear tabla 'configuracion_legal'")
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
        # Verificar si la tabla ya existe
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='configuracion_legal'
        """)
        tabla_existe = cursor.fetchone()

        if tabla_existe:
            print("\n[INFO] La tabla 'configuracion_legal' ya existe")
            print("[SKIP] No es necesario ejecutar la migración")
            conn.close()
            return True

        # ==================== CREAR TABLA ====================
        print("\n[PASO 1] Creando tabla 'configuracion_legal'...")

        cursor.execute("""
            CREATE TABLE configuracion_legal (
                clave TEXT PRIMARY KEY,
                valor TEXT NOT NULL,
                descripcion TEXT,
                tipo_dato TEXT DEFAULT 'text',
                ultima_actualizacion TEXT,
                actualizado_por TEXT
            )
        """)

        conn.commit()
        print("   [OK] Tabla 'configuracion_legal' creada exitosamente")

        # ==================== INSERTAR VALORES INICIALES ====================
        print("\n[PASO 2] Insertando valores iniciales...")

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        valores_iniciales = [
            ('SMMLV', '1300000', 'Salario Mínimo Mensual Legal Vigente 2025', 'number', fecha_actual, 'Sistema'),
            ('AUX_TRANSPORTE', '162000', 'Auxilio de Transporte 2025', 'number', fecha_actual, 'Sistema'),
            ('UVT', '47065', 'Unidad de Valor Tributario 2025', 'number', fecha_actual, 'Sistema'),
            ('TASA_SALUD_EMPLEADO', '4.0', 'Porcentaje Salud Empleado', 'percentage', fecha_actual, 'Sistema'),
            ('TASA_SALUD_EMPLEADOR', '8.5', 'Porcentaje Salud Empleador', 'percentage', fecha_actual, 'Sistema'),
            ('TASA_PENSION_EMPLEADO', '4.0', 'Porcentaje Pensión Empleado', 'percentage', fecha_actual, 'Sistema'),
            ('TASA_PENSION_EMPLEADOR', '12.0', 'Porcentaje Pensión Empleador', 'percentage', fecha_actual, 'Sistema'),
            ('TASA_CCF', '4.0', 'Porcentaje Caja de Compensación Familiar', 'percentage', fecha_actual, 'Sistema'),
            ('TASA_SENA', '2.0', 'Porcentaje SENA', 'percentage', fecha_actual, 'Sistema'),
            ('TASA_ICBF', '3.0', 'Porcentaje ICBF', 'percentage', fecha_actual, 'Sistema')
        ]

        cursor.executemany("""
            INSERT INTO configuracion_legal (clave, valor, descripcion, tipo_dato, ultima_actualizacion, actualizado_por)
            VALUES (?, ?, ?, ?, ?, ?)
        """, valores_iniciales)

        conn.commit()
        print(f"   [OK] {len(valores_iniciales)} valores iniciales insertados")

        # Mostrar valores insertados
        print("\n   [VALORES CONFIGURADOS]:")
        for clave, valor, descripcion, tipo, _, _ in valores_iniciales:
            if tipo == 'percentage':
                print(f"      - {clave}: {valor}% ({descripcion})")
            elif tipo == 'number':
                print(f"      - {clave}: ${valor} ({descripcion})")
            else:
                print(f"      - {clave}: {valor} ({descripcion})")

        # ==================== VERIFICACIÓN ====================
        print("\n[PASO 3] Verificando migración...")

        cursor.execute("SELECT COUNT(*) FROM configuracion_legal")
        total_registros = cursor.fetchone()[0]

        if total_registros == len(valores_iniciales):
            print(f"   [OK] {total_registros} registros verificados en la tabla")
        else:
            print(f"   [ERROR] Se esperaban {len(valores_iniciales)} registros, se encontraron {total_registros}")
            return False

        # ==================== RESULTADO ====================
        print("\n" + "="*80)
        print("[SUCCESS] MIGRACION EXITOSA")
        print("="*80)
        print("\nCambios realizados:")
        print("  ✓ Tabla 'configuracion_legal' creada")
        print("  ✓ 10 valores legales iniciales insertados")
        print("\nUso:")
        print("  - GET /api/configuracion: Obtener todas las configuraciones")
        print("  - PUT /api/configuracion: Actualizar valores")
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
    print(" "*15 + "FASE 10.2: CONFIGURACION LEGAL")
    print("="*80)

    resultado = migrate_configuracion_legal()

    if resultado:
        print("\n[RESULTADO FINAL] Migración completada exitosamente")
        print("Ahora puedes usar el módulo de configuración legal")
    else:
        print("\n[RESULTADO FINAL] Migración fallida. Revisar errores arriba.")

    print("="*80 + "\n")
