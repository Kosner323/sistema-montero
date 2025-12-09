# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║            MIGRACIÓN DE BASE DE DATOS - TABLA EMPRESAS                    ║
║                                                                           ║
║  Agrega columnas faltantes a la tabla 'empresas' para almacenar          ║
║  todos los datos del formulario de registro de empresas.                 ║
║                                                                           ║
║  COLUMNAS A AGREGAR:                                                      ║
║  - Datos de ubicación: departamento                                      ║
║  - Datos de empresa: tipo_empresa, sector_economico, num_empleados       ║
║  - Datos bancarios: banco, tipo_cuenta, numero_cuenta                    ║
║  - Seguridad social: arl, ccf, ibc_empresa, afp_empresa, arl_empresa     ║
║  - Rep. Legal: rep_legal_tipo_id, rep_legal_numero_id,                   ║
║                rep_legal_telefono, rep_legal_correo                       ║
║  - Otros: fecha_constitucion                                             ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import sqlite3
import sys
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════

DB_PATH = r"D:\Mi-App-React\src\dashboard\montero.db"

# Definición de columnas a agregar: (nombre, tipo, valor_default)
COLUMNAS_NUEVAS = [
    # Ubicación
    ("departamento", "TEXT", None),

    # Información de empresa
    ("tipo_empresa", "TEXT", None),
    ("sector_economico", "TEXT", None),
    ("num_empleados", "INTEGER", None),
    ("fecha_constitucion", "TEXT", None),

    # Datos bancarios
    ("banco", "TEXT", None),
    ("tipo_cuenta", "TEXT", None),
    ("numero_cuenta", "TEXT", None),

    # Seguridad social
    ("arl", "TEXT", None),
    ("ccf", "TEXT", None),
    ("ibc_empresa", "TEXT", None),
    ("afp_empresa", "TEXT", None),
    ("arl_empresa", "TEXT", None),

    # Representante legal (campos adicionales)
    ("rep_legal_tipo_id", "TEXT", None),
    ("rep_legal_numero_id", "TEXT", None),
    ("rep_legal_telefono", "TEXT", None),
    ("rep_legal_correo", "TEXT", None),
]


# ═══════════════════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════════════════════════════════

def columna_existe(cursor, tabla, columna):
    """Verifica si una columna existe en una tabla"""
    cursor.execute(f"PRAGMA table_info({tabla})")
    columnas_actuales = [row[1] for row in cursor.fetchall()]
    return columna in columnas_actuales


def agregar_columna(cursor, tabla, nombre_columna, tipo_dato, valor_default=None):
    """Agrega una columna a una tabla si no existe"""
    try:
        if valor_default is not None:
            sql = f"ALTER TABLE {tabla} ADD COLUMN {nombre_columna} {tipo_dato} DEFAULT {valor_default}"
        else:
            sql = f"ALTER TABLE {tabla} ADD COLUMN {nombre_columna} {tipo_dato}"

        cursor.execute(sql)
        print(f"[OK] Columna '{nombre_columna}' ({tipo_dato}) agregada exitosamente")
        return True
    except sqlite3.OperationalError as e:
        print(f"[ERROR] Error al agregar '{nombre_columna}': {e}")
        return False


def verificar_tabla_existe(cursor, nombre_tabla):
    """Verifica si una tabla existe en la base de datos"""
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name=?
    """, (nombre_tabla,))
    return cursor.fetchone() is not None


# ═══════════════════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL DE MIGRACIÓN
# ═══════════════════════════════════════════════════════════════════════════

def ejecutar_migracion():
    """Ejecuta la migración de la tabla empresas"""
    print("\n" + "="*80)
    print("MIGRACIÓN DE BASE DE DATOS - TABLA EMPRESAS")
    print("="*80)
    print(f"Base de datos: {DB_PATH}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        print("[OK] Conexion a base de datos establecida\n")

        # Verificar que la tabla 'empresas' existe
        if not verificar_tabla_existe(cursor, "empresas"):
            print("[ERROR] ERROR: La tabla 'empresas' no existe en la base de datos")
            print("   Crea la tabla primero antes de ejecutar esta migracion")
            return False

        print("[OK] Tabla 'empresas' encontrada\n")

        # Mostrar estructura actual
        cursor.execute("PRAGMA table_info(empresas)")
        columnas_actuales = cursor.fetchall()
        print(f"[INFO] Columnas actuales en 'empresas': {len(columnas_actuales)}")
        for col in columnas_actuales:
            print(f"   - {col[1]} ({col[2]})")

        print("\n" + "-"*80)
        print("INICIANDO PROCESO DE MIGRACIÓN")
        print("-"*80 + "\n")

        # Agregar columnas nuevas
        columnas_agregadas = 0
        columnas_ya_existentes = 0
        columnas_con_error = 0

        for nombre, tipo, default in COLUMNAS_NUEVAS:
            print(f"Procesando columna '{nombre}' ({tipo})...", end=" ")

            if columna_existe(cursor, "empresas", nombre):
                print(f"[WARN] Ya existe")
                columnas_ya_existentes += 1
            else:
                if agregar_columna(cursor, "empresas", nombre, tipo, default):
                    columnas_agregadas += 1
                else:
                    columnas_con_error += 1

        # Commit de cambios
        if columnas_agregadas > 0:
            conn.commit()
            print("\n[OK] Cambios guardados en la base de datos")

        # Resumen final
        print("\n" + "="*80)
        print("RESUMEN DE MIGRACION")
        print("="*80)
        print(f"[OK] Columnas agregadas:      {columnas_agregadas}")
        print(f"[WARN] Columnas ya existentes:  {columnas_ya_existentes}")
        print(f"[ERROR] Columnas con error:      {columnas_con_error}")
        print(f"[INFO] Total procesadas:        {len(COLUMNAS_NUEVAS)}")
        print("="*80)

        # Verificar estructura final
        cursor.execute("PRAGMA table_info(empresas)")
        columnas_finales = cursor.fetchall()
        print(f"\n[OK] Columnas totales despues de migracion: {len(columnas_finales)}")

        conn.close()
        print("\n[OK] Migracion completada exitosamente")
        return True

    except sqlite3.Error as e:
        print(f"\n[ERROR] ERROR DE BASE DE DATOS: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        return False


# ═══════════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n[!] ADVERTENCIA: Este script modificara la estructura de la base de datos")
    print("   Asegurate de tener un respaldo antes de continuar\n")

    respuesta = input("Deseas continuar con la migracion? (s/n): ")

    if respuesta.lower() == 's':
        exito = ejecutar_migracion()
        sys.exit(0 if exito else 1)
    else:
        print("\n[X] Migracion cancelada por el usuario")
        sys.exit(0)
