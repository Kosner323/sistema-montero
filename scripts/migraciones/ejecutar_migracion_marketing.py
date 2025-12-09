"""
=====================================================================
MIGRACIÓN: CAMPAÑAS DE MARKETING
Ejecuta la creación de tabla campanas_marketing con datos de prueba
=====================================================================
"""

import sqlite3
import os
from datetime import datetime

def ejecutar_migracion():
    """Ejecuta la migración de campanas_marketing"""
    
    # Ruta de la base de datos (consistente con app.py)
    base_dir = os.path.dirname(__file__)
    db_path = os.path.join(base_dir, 'src', 'dashboard', 'data', 'mi_sistema.db')
    migration_path = os.path.join(base_dir, 'migrations', '20251130_campanas_marketing.sql')
    
    print("\n" + "="*70)
    print("MIGRACION: CAMPANAS DE MARKETING")
    print("="*70)
    
    # Verificar que existe la BD
    if not os.path.exists(db_path):
        print(f"[ERROR] Base de datos no encontrada: {db_path}")
        return False
    
    # Verificar que existe el archivo SQL
    if not os.path.exists(migration_path):
        print(f"[ERROR] Archivo de migracion no encontrado: {migration_path}")
        return False
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Leer el archivo SQL
        with open(migration_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Ejecutar el script SQL
        cursor.executescript(sql_script)
        conn.commit()
        
        # Verificar la creación
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='campanas_marketing'")
        tabla_existe = cursor.fetchone()
        
        if tabla_existe:
            print("[OK] Tabla 'campanas_marketing' creada exitosamente")
            
            # Verificar columnas
            cursor.execute("PRAGMA table_info(campanas_marketing)")
            columnas = cursor.fetchall()
            print(f"\nColumnas creadas ({len(columnas)}):")
            for col in columnas:
                print(f"   - {col[1]} ({col[2]})")
            
            # Verificar índices
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='campanas_marketing'")
            indices = cursor.fetchall()
            print(f"\nIndices creados ({len(indices)}):")
            for idx in indices:
                print(f"   - {idx[0]}")
            
            # Verificar datos de prueba
            cursor.execute("SELECT COUNT(*) FROM campanas_marketing")
            count = cursor.fetchone()[0]
            print(f"\n[OK] {count} campanas de prueba insertadas")
            
            # Mostrar campañas
            cursor.execute("SELECT id, nombre, plataforma, estado, presupuesto FROM campanas_marketing")
            campanas = cursor.fetchall()
            print("\nCampanas creadas:")
            for c in campanas:
                print(f"   {c[0]}. {c[1]} - {c[2]} ({c[3]}) - ${c[4]:,.0f}")
            
            print("\n[OK] MIGRACION COMPLETADA EXITOSAMENTE")
            print("="*70)
            
        else:
            print("[ERROR] Error: La tabla no fue creada")
            return False
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Error durante la migracion: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    resultado = ejecutar_migracion()
    sys.exit(0 if resultado else 1)
