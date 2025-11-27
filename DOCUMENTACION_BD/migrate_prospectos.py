#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Migración: Actualizar tabla marketing_prospectos
==========================================================
Este script migra la tabla marketing_prospectos de la estructura antigua
(nombre_completo) a la nueva estructura B2B (nombre_empresa + nombre_contacto).

Ejecutar SOLO UNA VEZ para migrar datos existentes.

Fecha: 2025-01-17
"""

import sqlite3
import sys
import os
from pathlib import Path

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Ruta a la base de datos
DB_PATH = Path(__file__).parent / "src" / "dashboard" / "data" / "mi_sistema.db"

print("=" * 70)
print("🔄 MIGRACIÓN: Actualizar tabla marketing_prospectos")
print("=" * 70)

def migrate():
    """
    Migra la tabla marketing_prospectos a la nueva estructura B2B.
    """
    try:
        # Conectar a la BD
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 1. Verificar si la tabla tiene la columna antigua
        cursor.execute("PRAGMA table_info(marketing_prospectos)")
        columns = [col[1] for col in cursor.fetchall()]

        print(f"\n📋 Columnas actuales: {', '.join(columns)}")

        # 2. Si tiene la columna antigua (nombre_completo), hacer migración
        if 'nombre_completo' in columns and 'nombre_empresa' not in columns:
            print("\n⚠️  Tabla con estructura antigua detectada. Iniciando migración...\n")

            # 2.1 Crear tabla temporal con la nueva estructura
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS marketing_prospectos_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_empresa TEXT NOT NULL,
                    nombre_contacto TEXT NOT NULL,
                    telefono_contacto TEXT,
                    correo_contacto TEXT,
                    interes_servicio TEXT,
                    origen TEXT DEFAULT 'Web',
                    estado TEXT DEFAULT 'Nuevo',
                    notas TEXT,
                    fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP,
                    fecha_contacto TEXT,
                    fecha_conversion TEXT,
                    valor_estimado REAL DEFAULT 0.0,
                    asignado_a TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✓ Tabla temporal creada")

            # 2.2 Migrar datos (asumiendo que nombre_completo es el contacto)
            cursor.execute("""
                INSERT INTO marketing_prospectos_new
                (id, nombre_empresa, nombre_contacto, telefono_contacto, correo_contacto,
                 interes_servicio, origen, estado, notas, fecha_registro, fecha_contacto,
                 valor_estimado, asignado_a, created_at, updated_at)
                SELECT
                    id,
                    'Empresa ' || nombre_completo as nombre_empresa,
                    nombre_completo as nombre_contacto,
                    telefono as telefono_contacto,
                    correo as correo_contacto,
                    interes as interes_servicio,
                    origen,
                    estado,
                    notas,
                    fecha_registro,
                    fecha_contacto,
                    valor_estimado,
                    asignado_a,
                    created_at,
                    updated_at
                FROM marketing_prospectos
            """)
            print("✓ Datos migrados a tabla temporal")

            # 2.3 Eliminar tabla antigua y renombrar
            cursor.execute("DROP TABLE marketing_prospectos")
            cursor.execute("ALTER TABLE marketing_prospectos_new RENAME TO marketing_prospectos")
            print("✓ Tabla renombrada")

            # 2.4 Recrear índices
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_marketing_prospectos_estado
                ON marketing_prospectos(estado)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_marketing_prospectos_origen
                ON marketing_prospectos(origen)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_marketing_prospectos_fecha
                ON marketing_prospectos(fecha_registro)
            """)
            print("✓ Índices recreados")

            # 2.5 Confirmar cambios
            conn.commit()
            print("\n✅ Migración completada exitosamente!")

        elif 'nombre_empresa' in columns:
            print("\n✅ La tabla ya tiene la estructura nueva. No se requiere migración.")

        else:
            # Tabla no existe, crearla con la nueva estructura
            print("\n⚠️  Tabla no existe. Creando con estructura nueva...\n")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS marketing_prospectos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_empresa TEXT NOT NULL,
                    nombre_contacto TEXT NOT NULL,
                    telefono_contacto TEXT,
                    correo_contacto TEXT,
                    interes_servicio TEXT,
                    origen TEXT DEFAULT 'Web',
                    estado TEXT DEFAULT 'Nuevo',
                    notas TEXT,
                    fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP,
                    fecha_contacto TEXT,
                    fecha_conversion TEXT,
                    valor_estimado REAL DEFAULT 0.0,
                    asignado_a TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Crear índices
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_marketing_prospectos_estado
                ON marketing_prospectos(estado)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_marketing_prospectos_origen
                ON marketing_prospectos(origen)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_marketing_prospectos_fecha
                ON marketing_prospectos(fecha_registro)
            """)

            # Insertar datos de ejemplo
            cursor.execute("""
                INSERT OR IGNORE INTO marketing_prospectos
                (id, nombre_empresa, nombre_contacto, telefono_contacto, correo_contacto,
                 origen, interes_servicio, estado)
                VALUES
                (1, 'Distribuidora ABC S.A.S', 'María González', '3001234567',
                 'maria.gonzalez@distribuidoraabc.com', 'Redes Sociales', 'Seguridad Social', 'Nuevo'),
                (2, 'Constructora El Sol Ltda', 'Carlos Ramírez', '3109876543',
                 'carlos.ramirez@elsol.com', 'Referido', 'Nómina', 'Contactado'),
                (3, 'TechStart Colombia SAS', 'Ana Martínez', '3157894561',
                 'ana.martinez@techstart.co', 'Web', 'Asesoría Integral', 'Calificado')
            """)

            conn.commit()
            print("✓ Tabla creada con estructura nueva")
            print("✓ Datos de ejemplo insertados")
            print("\n✅ Configuración completada exitosamente!")

        # Verificar resultado final
        cursor.execute("SELECT COUNT(*) FROM marketing_prospectos")
        total = cursor.fetchone()[0]
        print(f"\n📊 Total de prospectos en la BD: {total}")

        conn.close()

    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    print(f"\n📁 Ruta de BD: {DB_PATH}")

    if not DB_PATH.exists():
        print(f"\n❌ Error: La base de datos no existe en {DB_PATH}")
        sys.exit(1)

    migrate()
    print("\n" + "=" * 70)
    print("✅ Proceso finalizado correctamente")
    print("=" * 70)
