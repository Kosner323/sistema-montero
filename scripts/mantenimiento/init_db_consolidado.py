#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
            SCRIPT DE INICIALIZACIÓN CONSOLIDADA DE BASE DE DATOS
================================================================================
Fecha: 2025-12-09
Descripción: Script único que sincroniza la BD con los modelos ORM.
             Reemplaza todos los scripts fix_db_* individuales.

USO:
    python scripts/mantenimiento/init_db_consolidado.py

IMPORTANTE: Este script NO elimina datos existentes, solo agrega columnas/tablas
            faltantes de forma segura.
================================================================================
"""

import os
import sys
import sqlite3
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()

DB_PATH = os.getenv("DATABASE_PATH", "data/mi_sistema.db")


def print_header(msg):
    print("\n" + "=" * 70)
    print(f"  {msg}")
    print("=" * 70)


def print_ok(msg):
    print(f"  ✅ {msg}")


def print_skip(msg):
    print(f"  ⏭️  {msg}")


def print_error(msg):
    print(f"  ❌ {msg}")


def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    return column in columns


def table_exists(cursor, table):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cursor.fetchone() is not None


def add_column_if_missing(cursor, table, column, col_type, default=None):
    """Agrega una columna si no existe"""
    if column_exists(cursor, table, column):
        return False
    
    sql = f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"
    if default is not None:
        sql += f" DEFAULT {default}"
    
    cursor.execute(sql)
    return True


def create_table_afiliaciones(cursor):
    """Crea la tabla afiliaciones si no existe"""
    if table_exists(cursor, 'afiliaciones'):
        print_skip("Tabla 'afiliaciones' ya existe")
        return False
    
    cursor.execute("""
        CREATE TABLE afiliaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            tipo_entidad TEXT NOT NULL,
            estado TEXT DEFAULT 'PENDIENTE',
            ruta_archivo TEXT,
            fecha_actualizacion TEXT DEFAULT CURRENT_TIMESTAMP,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    """)
    
    # Crear índices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_afiliaciones_usuario ON afiliaciones(usuario_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_afiliaciones_estado ON afiliaciones(estado)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_afiliaciones_tipo ON afiliaciones(tipo_entidad)")
    
    print_ok("Tabla 'afiliaciones' creada con índices")
    return True


def sync_empresas(cursor):
    """Sincroniza columnas de la tabla empresas"""
    print_header("TABLA: empresas")
    
    columnas = [
        # Representante legal
        ("rep_legal_telefono", "TEXT", None),
        ("rep_legal_correo", "TEXT", None),
        # Bancarias
        ("banco", "TEXT", None),
        ("tipo_cuenta", "TEXT", None),
        ("numero_cuenta", "TEXT", None),
        # Operativas
        ("sector_economico", "TEXT", None),
        ("num_empleados", "INTEGER", None),
        ("tipo_empresa", "TEXT", None),
        ("fecha_constitucion", "TEXT", None),
        # Rutas de archivos
        ("ruta_carpeta", "TEXT", None),
        ("ruta_firma", "TEXT", None),
        ("ruta_logo", "TEXT", None),
        ("ruta_rut", "TEXT", None),
        ("ruta_camara_comercio", "TEXT", None),
        ("ruta_cedula_representante", "TEXT", None),
        ("ruta_arl", "TEXT", None),
        ("ruta_cuenta_bancaria", "TEXT", None),
        ("ruta_carta_autorizacion", "TEXT", None),
        # Auditoría
        ("updated_at", "TEXT", None),
    ]
    
    count = 0
    for col, tipo, default in columnas:
        if add_column_if_missing(cursor, 'empresas', col, tipo, default):
            print_ok(f"Columna agregada: {col} ({tipo})")
            count += 1
        else:
            print_skip(f"Ya existe: {col}")
    
    return count


def sync_usuarios(cursor):
    """Sincroniza columnas de la tabla usuarios"""
    print_header("TABLA: usuarios")
    
    columnas = [
        # Laborales
        ("cargo", "TEXT", None),
        ("tipo_contrato", "TEXT", None),
        # Residencia
        ("municipioResidencia", "TEXT", None),
        ("departamentoResidencia", "TEXT", None),
        ("paisResidencia", "TEXT", None),
        # Autenticación
        ("password_hash", "TEXT", None),
        ("estado", "TEXT", "'activo'"),
        ("role", "TEXT", "'empleado'"),
        ("username", "TEXT", None),
        # Rutas de archivos
        ("ruta_carpeta", "TEXT", None),
        ("ruta_firma", "TEXT", None),
        ("documento_url", "TEXT", None),
        # Auditoría
        ("updated_at", "TEXT", None),
    ]
    
    count = 0
    for col, tipo, default in columnas:
        if add_column_if_missing(cursor, 'usuarios', col, tipo, default):
            print_ok(f"Columna agregada: {col} ({tipo})")
            count += 1
        else:
            print_skip(f"Ya existe: {col}")
    
    return count


def sync_tutelas(cursor):
    """Sincroniza columnas de la tabla tutelas"""
    print_header("TABLA: tutelas")
    
    columnas = [
        ("documento_soporte", "TEXT", None),
        ("updated_at", "TEXT", None),
    ]
    
    count = 0
    for col, tipo, default in columnas:
        if add_column_if_missing(cursor, 'tutelas', col, tipo, default):
            print_ok(f"Columna agregada: {col} ({tipo})")
            count += 1
        else:
            print_skip(f"Ya existe: {col}")
    
    return count


def main():
    print("\n" + "=" * 70)
    print("  🔧 SINCRONIZACIÓN CONSOLIDADA DE BASE DE DATOS")
    print("=" * 70)
    print(f"  📂 Base de datos: {DB_PATH}")
    print(f"  🕐 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not os.path.exists(DB_PATH):
        print_error(f"No se encontró la base de datos: {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        total_changes = 0
        
        # Sincronizar tablas existentes
        total_changes += sync_empresas(cursor)
        total_changes += sync_usuarios(cursor)
        total_changes += sync_tutelas(cursor)
        
        # Crear tablas faltantes
        print_header("TABLAS NUEVAS")
        if create_table_afiliaciones(cursor):
            total_changes += 1
        
        # Guardar cambios
        conn.commit()
        
        print_header("RESUMEN")
        if total_changes > 0:
            print_ok(f"Se aplicaron {total_changes} cambios a la base de datos")
        else:
            print_ok("La base de datos ya está sincronizada con los modelos ORM")
        
        conn.close()
        return True
        
    except Exception as e:
        print_error(f"Error durante la sincronización: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
