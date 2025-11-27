#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar el schema REAL de la tabla usuarios
"""
import sys
import os

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Agregar el path del dashboard al PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'dashboard'))

print("=" * 70)
print("🔍 VERIFICACIÓN DEL SCHEMA DE LA TABLA USUARIOS")
print("=" * 70)

try:
    from app import app

    with app.app_context():
        from utils import get_db_connection

        conn = get_db_connection()

        # Obtener información de la tabla usuarios
        cursor = conn.execute("PRAGMA table_info(usuarios)")
        columns = cursor.fetchall()

        print("\n📋 COLUMNAS DE LA TABLA 'usuarios':")
        print("-" * 70)
        print(f"{'#':<5} {'Nombre':<25} {'Tipo':<15} {'Not Null':<10} {'Default'}")
        print("-" * 70)

        for col in columns:
            cid, name, ctype, notnull, default_val, pk = col
            print(f"{cid:<5} {name:<25} {ctype:<15} {'Sí' if notnull else 'No':<10} {default_val or 'NULL'}")

        print("\n" + "=" * 70)
        print(f"✅ Total de columnas: {len(columns)}")
        print("=" * 70)

        # Verificar si existe la columna 'nombre_completo'
        column_names = [col[1] for col in columns]
        if 'nombre_completo' in column_names:
            print("\n⚠️  ¡ADVERTENCIA! La columna 'nombre_completo' EXISTE en la tabla")
        else:
            print("\n✅ La columna 'nombre_completo' NO EXISTE en la tabla (correcto)")

        conn.close()

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
