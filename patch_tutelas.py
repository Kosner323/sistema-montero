"""
Script de Parche: Agregar columna documento_soporte a tabla tutelas
Autor: Sistema Montero
Fecha: 17 de noviembre de 2025
Propósito: Actualizar el schema de la tabla tutelas para soportar almacenamiento de documentos PDF
"""

import sqlite3
import sys
from logger import logger


def check_column_exists(cursor, table_name, column_name):
    """
    Verifica si una columna existe en una tabla.
    
    Args:
        cursor: Cursor de SQLite
        table_name: Nombre de la tabla
        column_name: Nombre de la columna
    
    Returns:
        bool: True si la columna existe, False de lo contrario
    """
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    return column_name in column_names


def apply_patch():
    """
    Aplica el parche a la base de datos agregando la columna documento_soporte
    solo si no existe ya.
    """
    db_path = 'data/mi_sistema.db'
    
    try:
        # Conectar a la base de datos
        logger.info("🔌 Conectando a la base de datos...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si la tabla tutelas existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tutelas'")
        if not cursor.fetchone():
            logger.error("❌ La tabla 'tutelas' no existe en la base de datos")
            return False
        
        # Verificar si la columna ya existe
        if check_column_exists(cursor, 'tutelas', 'documento_soporte'):
            logger.warning("⚠️ La columna 'documento_soporte' ya existe en la tabla 'tutelas'")
            logger.info("✅ No se requieren cambios - el parche ya fue aplicado previamente")
            return True
        
        # Agregar la columna documento_soporte
        logger.info("📝 Agregando columna 'documento_soporte' a la tabla 'tutelas'...")
        cursor.execute("""
            ALTER TABLE tutelas 
            ADD COLUMN documento_soporte TEXT
        """)
        
        # Confirmar cambios
        conn.commit()
        
        # Verificar que la columna fue agregada exitosamente
        if check_column_exists(cursor, 'tutelas', 'documento_soporte'):
            logger.info("✅ Parche aplicado exitosamente")
            logger.info("📋 La tabla 'tutelas' ahora incluye la columna 'documento_soporte'")
            
            # Mostrar estructura actualizada
            cursor.execute("PRAGMA table_info(tutelas)")
            columns = cursor.fetchall()
            logger.info(f"📊 Estructura actualizada de la tabla 'tutelas': {len(columns)} columnas")
            for col in columns:
                logger.debug(f"   - {col[1]} ({col[2]})")
            
            return True
        else:
            logger.error("❌ Error: La columna no fue agregada correctamente")
            return False
            
    except sqlite3.Error as e:
        logger.error(f"❌ Error de SQLite: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")
        return False
    finally:
        if conn:
            conn.close()
            logger.info("🔌 Conexión a la base de datos cerrada")


def main():
    """Función principal del script."""
    logger.info("=" * 70)
    logger.info("PATCH: Agregar columna documento_soporte a tabla tutelas")
    logger.info("=" * 70)
    
    # Aplicar el parche
    success = apply_patch()
    
    # Mostrar resultado final
    logger.info("=" * 70)
    if success:
        logger.info("✅ PATCH COMPLETADO EXITOSAMENTE")
        logger.info("=" * 70)
        logger.info("")
        logger.info("Próximos pasos:")
        logger.info("  1. Mover archivos físicos a las nuevas rutas en MONTERO_TOTAL")
        logger.info("  2. Ejecutar: python migration_paths.py")
        logger.info("     (para sincronizar las rutas en la base de datos)")
        sys.exit(0)
    else:
        logger.error("❌ PATCH FALLÓ - Revisar los errores anteriores")
        logger.info("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
