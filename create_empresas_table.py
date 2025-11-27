# -*- coding: utf-8 -*-
"""
Script para crear la tabla empresas con TODOS los campos necesarios
en la base de datos montero.db
"""

import sqlite3
import sys

DB_PATH = r"D:\Mi-App-React\src\dashboard\montero.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS empresas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Informacion basica
    nombre_empresa TEXT,
    tipo_identificacion_empresa TEXT,
    nit TEXT UNIQUE,
    direccion_empresa TEXT,
    telefono_empresa TEXT,
    correo_empresa TEXT,
    ciudad_empresa TEXT,

    -- Ubicacion
    departamento TEXT,

    -- Informacion de empresa
    tipo_empresa TEXT,
    sector_economico TEXT,
    num_empleados INTEGER,
    fecha_constitucion TEXT,

    -- Datos bancarios
    banco TEXT,
    tipo_cuenta TEXT,
    numero_cuenta TEXT,

    -- Seguridad social
    arl TEXT,
    ccf TEXT,
    ibc_empresa TEXT,
    afp_empresa TEXT,
    arl_empresa TEXT,

    -- Representante legal
    rep_legal_nombre TEXT,
    rep_legal_tipo_id TEXT,
    rep_legal_numero_id TEXT,
    rep_legal_telefono TEXT,
    rep_legal_correo TEXT,

    -- Rutas de archivos
    ruta_carpeta TEXT,
    ruta_firma TEXT,
    ruta_logo TEXT,
    ruta_rut TEXT,
    ruta_camara_comercio TEXT,
    ruta_cedula_representante TEXT,
    ruta_arl TEXT,
    ruta_cuenta_bancaria TEXT,
    ruta_carta_autorizacion TEXT,

    -- Timestamps
    created_at TEXT DEFAULT (datetime('now','localtime'))
)
"""

def crear_tabla_empresas():
    print("\n" + "="*70)
    print("CREACION DE TABLA EMPRESAS - COMPLETA")
    print("="*70)
    print(f"Base de datos: {DB_PATH}\n")

    try:
        # Conectar
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        print("[OK] Conexion establecida")

        # Crear tabla
        cursor.execute(CREATE_TABLE_SQL)
        conn.commit()
        print("[OK] Tabla 'empresas' creada exitosamente")

        # Verificar estructura
        cursor.execute("PRAGMA table_info(empresas)")
        columnas = cursor.fetchall()
        print(f"\n[INFO] Total de columnas creadas: {len(columnas)}")
        print("\nColumnas:")
        for col in columnas:
            print(f"  - {col[1]} ({col[2]})")

        conn.close()
        print("\n" + "="*70)
        print("[OK] Tabla creada correctamente")
        print("="*70)
        return True

    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    exito = crear_tabla_empresas()
    sys.exit(0 if exito else 1)
