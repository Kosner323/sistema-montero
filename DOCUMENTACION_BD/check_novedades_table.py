#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificar y Crear Tabla de Novedades
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

print("=" * 80)
print("🔍 VERIFICACIÓN DE TABLA NOVEDADES")
print("=" * 80)

try:
    from app import app
    from utils import get_db_connection

    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar si existe la tabla
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='novedades'")
        table_exists = cursor.fetchone() is not None

        if table_exists:
            print("✅ La tabla 'novedades' existe")

            # Mostrar estructura
            cursor.execute("PRAGMA table_info(novedades)")
            columns = cursor.fetchall()
            print(f"\n📋 Estructura de la tabla ({len(columns)} columnas):")
            for col in columns:
                print(f"   • {col[1]} ({col[2]})")

            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM novedades")
            count = cursor.fetchone()[0]
            print(f"\n📊 Registros en la tabla: {count}")

        else:
            print("❌ La tabla 'novedades' NO existe")
            print("\n💡 Creando la tabla...")

            # Crear tabla según el esquema usado en novedades.py
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS novedades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    status TEXT NOT NULL,
                    priorityText TEXT,
                    idType TEXT,
                    idNumber TEXT,
                    firstName TEXT,
                    lastName TEXT,
                    nationality TEXT,
                    gender TEXT,
                    birthDate TEXT,
                    phone TEXT,
                    department TEXT,
                    city TEXT,
                    address TEXT,
                    neighborhood TEXT,
                    email TEXT,
                    beneficiaries TEXT,
                    eps TEXT,
                    arl TEXT,
                    arlClass TEXT,
                    ccf TEXT,
                    pensionFund TEXT,
                    ibc REAL,
                    description TEXT,
                    radicado TEXT,
                    solutionDescription TEXT,
                    creationDate TEXT,
                    updateDate TEXT,
                    assignedTo TEXT,
                    history TEXT
                )
            """)
            conn.commit()
            print("✅ Tabla 'novedades' creada exitosamente")

            # Verificar creación
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='novedades'")
            if cursor.fetchone():
                print("✅ Verificación: La tabla ahora existe en la base de datos")
            else:
                print("❌ Error: La tabla no se creó correctamente")

        conn.close()

        print("\n" + "=" * 80)
        print("✅ VERIFICACIÓN COMPLETA")
        print("=" * 80)
        print("\n💡 Ahora puedes acceder a: http://localhost:5000/novedades")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80 + "\n")
