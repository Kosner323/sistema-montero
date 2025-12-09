"""
Script de migración para agregar tipo_cotizante a tabla usuarios
Ejecuta la migración SQL usando Python y sqlite3
"""

import sqlite3
import os

# Ruta a la base de datos
DB_PATH = r"data\mi_sistema.db"  # Base de datos principal del proyecto

# SQL de migración (versión compatible con SQLite)
MIGRATION_SQL = """
-- Agregar columna tipo_cotizante (SQLite no permite DEFAULT NOT NULL en ALTER TABLE)
ALTER TABLE usuarios 
ADD COLUMN tipo_cotizante TEXT;

-- Actualizar valores existentes a 'Dependiente' por defecto
UPDATE usuarios 
SET tipo_cotizante = 'Dependiente' 
WHERE tipo_cotizante IS NULL;

-- Crear índice para optimizar queries por tipo
CREATE INDEX IF NOT EXISTS idx_usuarios_tipo_cotizante 
ON usuarios(tipo_cotizante);

-- Verificar resultado
SELECT COUNT(*) as total_usuarios FROM usuarios;
"""

def ejecutar_migracion():
    """Ejecuta la migración SQL"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ ERROR: Base de datos no encontrada en {DB_PATH}")
        return False
    
    print("=" * 70)
    print(" MIGRACIÓN: Agregar tipo_cotizante a tabla usuarios")
    print("=" * 70)
    print()
    
    try:
        # Conectar a la BD
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("✓ Conectado a la base de datos")
        
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(usuarios)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'tipo_cotizante' in columns:
            print("⚠️ La columna 'tipo_cotizante' ya existe. Migración omitida.")
            conn.close()
            return True
        
        print("✓ Columna 'tipo_cotizante' no existe. Procediendo con migración...")
        print()
        
        # Ejecutar cada statement SQL
        for statement in MIGRATION_SQL.split(';'):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                cursor.execute(statement)
                print(f"✓ Ejecutado: {statement[:60]}...")
        
        conn.commit()
        
        # Verificar resultado
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        total = cursor.fetchone()[0]
        
        cursor.execute("PRAGMA table_info(usuarios)")
        columns_after = cursor.fetchall()
        
        conn.close()
        
        print()
        print("=" * 70)
        print(" RESULTADO DE LA MIGRACIÓN")
        print("=" * 70)
        print(f"✅ Migración completada exitosamente")
        print(f"✅ Total usuarios en la tabla: {total}")
        print(f"✅ Columnas de la tabla usuarios:")
        
        for col in columns_after:
            col_name = col[1]
            col_type = col[2]
            col_default = col[4]
            is_new = "🆕 NUEVA" if col_name == 'tipo_cotizante' else ""
            print(f"   - {col_name} ({col_type}) {is_new}")
            if col_name == 'tipo_cotizante':
                print(f"     Default: '{col_default}'")
        
        print()
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR en migración: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    exito = ejecutar_migracion()
    
    if exito:
        print("\n✅ MIGRACIÓN COMPLETADA CON ÉXITO")
        print("\nPróximos pasos:")
        print("1. Actualizar formularios frontend para incluir tipo_cotizante")
        print("2. Modificar lógica de cálculo PILA según tipo")
        print("3. Actualizar endpoints API para manejar el nuevo campo")
    else:
        print("\n❌ MIGRACIÓN FALLÓ")
        exit(1)
