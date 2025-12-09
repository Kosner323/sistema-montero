"""
========================================================================
MIGRACIÓN: Crear tabla 'egresos' para Caja Menor
========================================================================
Fecha: 2025-11-29
Autor: Senior Backend Developer
Descripción: Crea la tabla de egresos para registrar gastos rápidos
========================================================================
"""

import sys
import os
import sqlite3
from datetime import datetime

# Fix encoding para Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configuración
DATABASE_PATH = r"d:\Mi-App-React\data\mi_sistema.db"

def verificar_base_datos():
    """Verifica que la base de datos existe"""
    if not os.path.exists(DATABASE_PATH):
        print(f"❌ ERROR: Base de datos no encontrada en {DATABASE_PATH}")
        return False
    print(f"✅ Base de datos encontrada: {DATABASE_PATH}")
    return True

def crear_tabla_egresos(conn):
    """Crea la tabla 'egresos' con todos sus campos e índices"""
    cursor = conn.cursor()
    
    print("\n📋 PASO 1: Verificando si la tabla 'egresos' existe...")
    
    # Verificar si la tabla ya existe
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='egresos'
    """)
    
    if cursor.fetchone():
        print("⚠️  La tabla 'egresos' ya existe")
        respuesta = input("¿Deseas recrearla? (s/n): ").lower()
        if respuesta == 's':
            print("🗑️  Eliminando tabla existente...")
            cursor.execute("DROP TABLE egresos")
            conn.commit()
            print("✅ Tabla eliminada")
        else:
            print("ℹ️  Conservando tabla existente")
            return
    
    print("\n📋 PASO 2: Creando tabla 'egresos'...")
    
    # Crear tabla
    cursor.execute("""
        CREATE TABLE egresos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id TEXT,
            empresa_nit TEXT,
            monto REAL NOT NULL,
            concepto TEXT NOT NULL,
            categoria TEXT,
            metodo_pago TEXT DEFAULT 'Efectivo',
            fecha DATE NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            observaciones TEXT,
            ruta_comprobante TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(numeroId),
            FOREIGN KEY (empresa_nit) REFERENCES empresas(nit)
        )
    """)
    
    print("   ✅ Tabla 'egresos' creada exitosamente")
    
    print("\n📋 PASO 3: Creando índices...")
    
    # Crear índices para optimizar consultas
    indices = [
        ("idx_egresos_usuario", "usuario_id"),
        ("idx_egresos_empresa", "empresa_nit"),
        ("idx_egresos_fecha", "fecha"),
        ("idx_egresos_categoria", "categoria")
    ]
    
    for idx_name, column in indices:
        cursor.execute(f"""
            CREATE INDEX IF NOT EXISTS {idx_name} 
            ON egresos({column})
        """)
        print(f"   ✅ Índice '{idx_name}' creado")
    
    conn.commit()
    print("\n✅ Tabla 'egresos' e índices creados exitosamente")

def verificar_migracion(conn):
    """Verifica que la migración se realizó correctamente"""
    cursor = conn.cursor()
    
    print("\n📊 VERIFICACIÓN FINAL:")
    print("=" * 70)
    
    # Verificar estructura de la tabla
    cursor.execute("PRAGMA table_info(egresos)")
    columnas = cursor.fetchall()
    
    print(f"\n📋 Tabla 'egresos': {len(columnas)} columnas")
    for col in columnas:
        col_id, nombre, tipo, notnull, default, pk = col
        nullable = "NOT NULL" if notnull else "NULL"
        primary = "PRIMARY KEY" if pk else ""
        print(f"   - {nombre:<20} {tipo:<10} {nullable:<10} {primary}")
    
    # Verificar índices
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='index' AND tbl_name='egresos'
    """)
    indices = cursor.fetchall()
    
    print(f"\n🔍 Índices de 'egresos': {len(indices)}")
    for idx in indices:
        print(f"   - {idx[0]}")
    
    # Verificar foreign keys
    cursor.execute("PRAGMA foreign_key_list(egresos)")
    fks = cursor.fetchall()
    
    print(f"\n🔗 Foreign Keys: {len(fks)}")
    for fk in fks:
        print(f"   - {fk[2]}.{fk[3]} → {fk[4]}")
    
    print("\n" + "=" * 70)
    print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 70)

def main():
    """Función principal de migración"""
    print("\n" + "=" * 70)
    print("  🚀 MIGRACIÓN: Crear tabla 'egresos' (Caja Menor)")
    print("=" * 70)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")
    
    # Verificar base de datos
    if not verificar_base_datos():
        sys.exit(1)
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(DATABASE_PATH)
        conn.execute("PRAGMA foreign_keys = ON")  # Habilitar foreign keys
        
        # Crear tabla
        crear_tabla_egresos(conn)
        
        # Verificar migración
        verificar_migracion(conn)
        
        # Cerrar conexión
        conn.close()
        
        print("\n🎉 ¡Migración completada exitosamente!")
        
    except Exception as e:
        print(f"\n❌ ERROR durante la migración: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
