"""
Ejecutor de Migración: Sistema de Tareas Personal (Fase 11.2)
Crea la tabla tareas_usuario con datos de prueba
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = 'data/mi_sistema.db'

def ejecutar_migracion():
    """Ejecuta la migración SQL para crear tabla tareas_usuario"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ ERROR: Base de datos no encontrada en {DB_PATH}")
        return False
    
    print("="*60)
    print("🚀 MIGRACIÓN FASE 11.2: Sistema de Tareas Personal")
    print("="*60)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar si la tabla ya existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='tareas_usuario'
        """)
        
        if cursor.fetchone():
            print("⚠️  La tabla 'tareas_usuario' ya existe. Saltando creación...")
            
            # Mostrar estadísticas actuales
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN completada = 0 THEN 1 ELSE 0 END) as pendientes,
                    SUM(CASE WHEN completada = 1 THEN 1 ELSE 0 END) as completadas
                FROM tareas_usuario
            """)
            stats = cursor.fetchone()
            print(f"\n📊 Estadísticas actuales:")
            print(f"   Total tareas: {stats[0]}")
            print(f"   Pendientes: {stats[1]}")
            print(f"   Completadas: {stats[2]}")
            
        else:
            print("\n1️⃣  Creando tabla tareas_usuario...")
            
            # Crear tabla
            cursor.execute("""
                CREATE TABLE tareas_usuario (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    descripcion TEXT NOT NULL,
                    completada BOOLEAN NOT NULL DEFAULT 0,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES usuarios_portal(id) ON DELETE CASCADE
                )
            """)
            print("   ✅ Tabla creada exitosamente")
            
            # Crear índices
            print("\n2️⃣  Creando índices de búsqueda...")
            cursor.execute("""
                CREATE INDEX idx_tareas_user_id 
                ON tareas_usuario(user_id)
            """)
            print("   ✅ Índice idx_tareas_user_id creado")
            
            cursor.execute("""
                CREATE INDEX idx_tareas_user_completada 
                ON tareas_usuario(user_id, completada)
            """)
            print("   ✅ Índice idx_tareas_user_completada creado")
            
            # Insertar datos de prueba
            print("\n3️⃣  Insertando datos de prueba...")
            cursor.execute("""
                INSERT INTO tareas_usuario (user_id, descripcion, completada, created_at) VALUES
                    (1, 'Revisar planillas PILA de Enero 2025', 0, datetime('now')),
                    (1, 'Generar reporte de nómina para auditoría', 0, datetime('now')),
                    (1, 'Actualizar datos de nuevos afiliados', 1, datetime('now', '-1 day'))
            """)
            print("   ✅ 3 tareas de prueba insertadas (2 pendientes, 1 completada)")
            
            conn.commit()
        
        # Verificar estructura final
        print("\n4️⃣  Verificando estructura de tabla...")
        cursor.execute("PRAGMA table_info(tareas_usuario)")
        columns = cursor.fetchall()
        
        print("\n   Columnas creadas:")
        for col in columns:
            print(f"   - {col[1]:15} {col[2]:10} {'NOT NULL' if col[3] else 'NULL':10} Default: {col[4] or 'NULL'}")
        
        # Mostrar tareas de prueba
        print("\n5️⃣  Tareas de prueba insertadas:")
        cursor.execute("""
            SELECT id, descripcion, completada, created_at 
            FROM tareas_usuario 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        tareas = cursor.fetchall()
        
        for tarea in tareas:
            estado = "✅ COMPLETADA" if tarea[2] else "⏳ PENDIENTE"
            print(f"   [{tarea[0]}] {estado:15} {tarea[1]}")
            print(f"        Creada: {tarea[3]}")
        
        conn.close()
        
        print("\n" + "="*60)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("="*60)
        print("\n📝 Próximos pasos:")
        print("   1. Crear modelo ORM en orm_models.py")
        print("   2. Implementar endpoints en routes/tareas.py")
        print("   3. Registrar blueprint en app.py")
        print("   4. Ejecutar prueba con test_tareas_api.py")
        
        return True
        
    except sqlite3.Error as e:
        print(f"\n❌ ERROR en migración: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR inesperado: {e}")
        return False

if __name__ == "__main__":
    exito = ejecutar_migracion()
    exit(0 if exito else 1)
