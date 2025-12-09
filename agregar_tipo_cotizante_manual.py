import sqlite3

conn = sqlite3.connect('data/mi_sistema.db')
cursor = conn.cursor()

print("Agregando columna tipo_cotizante...")

try:
    # Paso 1: Agregar columna (sin DEFAULT ni NOT NULL en SQLite)
    cursor.execute("ALTER TABLE usuarios ADD COLUMN tipo_cotizante TEXT")
    print("✅ Columna agregada")
    
    # Paso 2: Establecer valor por defecto para registros existentes
    cursor.execute("UPDATE usuarios SET tipo_cotizante = 'Dependiente' WHERE tipo_cotizante IS NULL")
    print(f"✅ {cursor.rowcount} registros actualizados a 'Dependiente'")
    
    # Paso 3: Crear índice
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_tipo_cotizante ON usuarios(tipo_cotizante)")
    print("✅ Índice creado")
    
    conn.commit()
    
    # Verificar
    cursor.execute("PRAGMA table_info(usuarios)")
    cols = cursor.fetchall()
    tipo_col = [c for c in cols if c[1] == 'tipo_cotizante']
    
    if tipo_col:
        print(f"\n✅ ÉXITO: Columna 'tipo_cotizante' agregada correctamente")
        print(f"   Posición: {tipo_col[0][0]}")
        print(f"   Tipo: {tipo_col[0][2]}")
    else:
        print("\n❌ ERROR: Columna no agregada")
    
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE tipo_cotizante = 'Dependiente'")
    count = cursor.fetchone()[0]
    print(f"   Usuarios con tipo 'Dependiente': {count}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    conn.rollback()
finally:
    conn.close()
