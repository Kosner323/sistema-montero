#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
================================================================================
                    SCRIPT DE MIGRACIÓN - TABLA AFILIACIONES
================================================================================
Autor: Sistema Montero - Claude (Anthropic)
Fecha: 24 de Noviembre de 2025
Descripción: Crea la tabla 'afiliaciones' para controlar el estado de las
             afiliaciones de los empleados (EPS, ARL, PENSIÓN, CAJA).
================================================================================
"""

import os
import sys
import sqlite3
from datetime import datetime

# ==================== CONFIGURACIÓN ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "mi_sistema.db")


# ==================== FUNCIONES ====================

def conectar_db(db_path):
    """
    Conecta a la base de datos SQLite.
    
    Args:
        db_path (str): Ruta al archivo de base de datos
        
    Returns:
        sqlite3.Connection: Conexión a la BD
    """
    try:
        if not os.path.exists(db_path):
            print(f"ERROR: No se encontro el archivo de base de datos: {db_path}")
            sys.exit(1)
        
        conn = sqlite3.connect(db_path)
        print(f"OK: Conexion exitosa a: {db_path}")
        return conn
    except Exception as e:
        print(f"ERROR al conectar a la BD: {e}")
        sys.exit(1)


def crear_tabla_afiliaciones(conn):
    """
    Crea la tabla afiliaciones si no existe.
    
    Args:
        conn (sqlite3.Connection): Conexión a la BD
    """
    try:
        cursor = conn.cursor()
        
        # Verificar si ya existe la tabla
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='afiliaciones'
        """)
        
        if cursor.fetchone():
            print("AVISO: La tabla 'afiliaciones' ya existe. No se creara nuevamente.")
            return
        
        # Crear tabla
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS afiliaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                tipo_entidad TEXT NOT NULL CHECK(tipo_entidad IN ('EPS', 'ARL', 'PENSION', 'CAJA')),
                estado TEXT DEFAULT 'PENDIENTE' CHECK(estado IN ('PENDIENTE', 'COMPLETADO')),
                ruta_archivo TEXT,
                fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        print("OK: Tabla 'afiliaciones' creada exitosamente")
        
        # Crear índices para optimizar búsquedas
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_afiliaciones_usuario 
            ON afiliaciones(usuario_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_afiliaciones_estado 
            ON afiliaciones(estado)
        """)
        
        conn.commit()
        print("OK: Indices creados exitosamente")
        
    except Exception as e:
        print(f"ERROR al crear tabla: {e}")
        conn.rollback()
        sys.exit(1)


def verificar_estructura(conn):
    """
    Verifica y muestra la estructura de la tabla creada.
    
    Args:
        conn (sqlite3.Connection): Conexión a la BD
    """
    try:
        cursor = conn.cursor()
        
        # Obtener estructura
        cursor.execute("PRAGMA table_info(afiliaciones)")
        columnas = cursor.fetchall()
        
        print("\n" + "=" * 80)
        print("ESTRUCTURA DE LA TABLA 'afiliaciones'")
        print("=" * 80)
        print(f"\n{'ID':<5} {'Nombre':<25} {'Tipo':<15} {'Not Null':<10} {'Default'}")
        print("-" * 80)
        
        for col in columnas:
            col_id, nombre, tipo, not_null, default, pk = col
            not_null_str = "SI" if not_null else "NO"
            default_str = default if default else ""
            print(f"{col_id:<5} {nombre:<25} {tipo:<15} {not_null_str:<10} {default_str}")
        
        print("-" * 80)
        print(f"Total de columnas: {len(columnas)}")
        
        # Mostrar restricciones
        cursor.execute("SELECT sql FROM sqlite_master WHERE name='afiliaciones'")
        sql = cursor.fetchone()[0]
        
        print("\n" + "=" * 80)
        print("RESTRICCIONES Y VALIDACIONES")
        print("=" * 80)
        print("\n1. tipo_entidad: Solo acepta 'EPS', 'ARL', 'PENSION', 'CAJA'")
        print("2. estado: Solo acepta 'PENDIENTE', 'COMPLETADO'")
        print("3. usuario_id: Referencia a tabla usuarios (ON DELETE CASCADE)")
        print("4. fecha_actualizacion: Se establece automaticamente al crear")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"ERROR al verificar estructura: {e}")


def crear_datos_prueba(conn):
    """
    Crea registros de prueba para los usuarios existentes.
    
    Args:
        conn (sqlite3.Connection): Conexión a la BD
    """
    try:
        cursor = conn.cursor()
        
        # Obtener algunos usuarios de prueba
        cursor.execute("SELECT id FROM usuarios LIMIT 5")
        usuarios = cursor.fetchall()
        
        if not usuarios:
            print("\nAVISO: No hay usuarios en la BD. No se crearan datos de prueba.")
            return
        
        print("\n" + "=" * 80)
        print("CREAR DATOS DE PRUEBA (Opcional)")
        print("=" * 80)
        
        respuesta = input("\nDesea crear registros de afiliaciones de prueba? (s/n): ").strip().lower()
        
        if respuesta != 's':
            print("OK: No se crearon datos de prueba")
            return
        
        # Crear afiliaciones para cada usuario
        entidades = ['EPS', 'ARL', 'PENSION', 'CAJA']
        count = 0
        
        for usuario in usuarios:
            usuario_id = usuario[0]
            for entidad in entidades:
                cursor.execute("""
                    INSERT INTO afiliaciones (usuario_id, tipo_entidad, estado)
                    VALUES (?, ?, 'PENDIENTE')
                """, (usuario_id, entidad))
                count += 1
        
        conn.commit()
        print(f"\nOK: Se crearon {count} registros de afiliaciones de prueba")
        print(f"    - {len(usuarios)} usuarios")
        print(f"    - {len(entidades)} entidades por usuario")
        
    except Exception as e:
        print(f"ERROR al crear datos de prueba: {e}")
        conn.rollback()


# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    """
    Ejecuta la migración completa.
    """
    print("\n" + "=" * 80)
    print(" " * 25 + "MIGRACIÓN DE BASE DE DATOS")
    print(" " * 20 + "TABLA: afiliaciones")
    print("=" * 80 + "\n")
    
    # 1. Conectar a BD
    print("PASO 1: CONECTAR A BASE DE DATOS")
    print("-" * 80)
    conn = conectar_db(DB_PATH)
    print()
    
    # 2. Crear tabla
    print("PASO 2: CREAR TABLA 'afiliaciones'")
    print("-" * 80)
    crear_tabla_afiliaciones(conn)
    print()
    
    # 3. Verificar estructura
    print("PASO 3: VERIFICAR ESTRUCTURA")
    print("-" * 80)
    verificar_estructura(conn)
    print()
    
    # 4. Datos de prueba (opcional)
    crear_datos_prueba(conn)
    
    # 5. Cerrar conexión
    conn.close()
    print("\n" + "=" * 80)
    print(" " * 25 + "MIGRACIÓN COMPLETADA")
    print("=" * 80)
    print("\nLa tabla 'afiliaciones' esta lista para usar.")
    print("Ahora puedes ejecutar el backend para gestionar afiliaciones.\n")


if __name__ == "__main__":
    main()
