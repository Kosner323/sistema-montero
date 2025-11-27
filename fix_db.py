#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Migración de Base de Datos
=====================================
Agrega columnas faltantes a las tablas 'empresas' y 'usuarios'
para soportar almacenamiento de rutas de archivos.

Uso:
    python fix_db.py

Fecha: 2025-11-24
"""

import os
import sqlite3
import sys
from datetime import datetime


# ==================== CONFIGURACIÓN ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "mi_sistema.db")

# Columnas a agregar por tabla
COLUMNAS_EMPRESAS = [
    "ruta_carpeta",
    "ruta_firma",
    "ruta_logo",
    "ruta_rut",
    "ruta_camara_comercio",
    "ruta_cedula_representante",
    "ruta_arl",
    "ruta_cuenta_bancaria",
    "ruta_carta_autorizacion"
]

COLUMNAS_USUARIOS = [
    "ruta_carpeta",
    "ruta_firma",
    "documento_url"
]


# ==================== FUNCIONES AUXILIARES ====================

def conectar_db(db_path):
    """
    Conecta a la base de datos SQLite.
    
    Args:
        db_path: Ruta al archivo .db
        
    Returns:
        sqlite3.Connection: Objeto de conexión
    """
    if not os.path.exists(db_path):
        print(f"❌ ERROR: No se encontró la base de datos en: {db_path}")
        print(f"\n💡 SOLUCIÓN: Verifica que la ruta sea correcta.")
        sys.exit(1)
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        print(f"✅ Conexión exitosa a: {db_path}")
        return conn
    except Exception as e:
        print(f"❌ ERROR al conectar a la base de datos: {e}")
        sys.exit(1)


def obtener_columnas_existentes(conn, tabla):
    """
    Obtiene la lista de columnas existentes en una tabla.
    
    Args:
        conn: Conexión a la base de datos
        tabla: Nombre de la tabla
        
    Returns:
        list: Lista de nombres de columnas
    """
    try:
        cursor = conn.execute(f"PRAGMA table_info({tabla})")
        columnas = [row[1] for row in cursor.fetchall()]  # row[1] es el nombre de la columna
        return columnas
    except Exception as e:
        print(f"❌ ERROR al obtener columnas de '{tabla}': {e}")
        return []


def agregar_columna(conn, tabla, columna, tipo="TEXT"):
    """
    Agrega una columna a la tabla si no existe.
    
    Args:
        conn: Conexión a la base de datos
        tabla: Nombre de la tabla
        columna: Nombre de la columna a agregar
        tipo: Tipo de dato de la columna (default: TEXT)
        
    Returns:
        bool: True si se agregó, False si ya existía o hubo error
    """
    try:
        sql = f"ALTER TABLE {tabla} ADD COLUMN {columna} {tipo};"
        conn.execute(sql)
        conn.commit()
        return True
    except sqlite3.OperationalError as e:
        # Si el error es "duplicate column name", la columna ya existe
        if "duplicate column name" in str(e).lower():
            return False
        else:
            print(f"   ❌ ERROR SQL: {e}")
            return False
    except Exception as e:
        print(f"   ❌ ERROR inesperado: {e}")
        return False


def crear_backup(db_path):
    """
    Crea un backup de la base de datos antes de modificarla.
    
    Args:
        db_path: Ruta al archivo .db
        
    Returns:
        str: Ruta del archivo backup
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.replace(".db", f"_backup_{timestamp}.db")
    
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backup creado: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"⚠️  ADVERTENCIA: No se pudo crear backup: {e}")
        return None


def verificar_tabla_existe(conn, tabla):
    """
    Verifica si una tabla existe en la base de datos.
    
    Args:
        conn: Conexión a la base de datos
        tabla: Nombre de la tabla
        
    Returns:
        bool: True si existe, False si no
    """
    try:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (tabla,)
        )
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"❌ ERROR al verificar tabla '{tabla}': {e}")
        return False


# ==================== FUNCIÓN PRINCIPAL ====================

def migrar_base_de_datos():
    """
    Ejecuta la migración completa de la base de datos.
    """
    global DB_PATH
    
    print("\n" + "="*80)
    print(" "*25 + "MIGRACIÓN DE BASE DE DATOS")
    print("="*80 + "\n")
    
    # 1. Verificar ruta de la base de datos
    print(f"📂 Ruta de la base de datos: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"\n❌ ERROR: No se encontró el archivo de base de datos.")
        print(f"\n💡 BUSCAR EN UBICACIONES ALTERNATIVAS:")
        
        # Buscar en ubicaciones alternativas
        ubicaciones_alternativas = [
            os.path.join(BASE_DIR, "mi_sistema.db"),
            os.path.join(BASE_DIR, "..", "data", "mi_sistema.db"),
            os.path.join(os.getcwd(), "data", "mi_sistema.db"),
            os.path.join(BASE_DIR, "data", "montero.db")
        ]
        
        for ubicacion in ubicaciones_alternativas:
            if os.path.exists(ubicacion):
                print(f"   ✅ Encontrado en: {ubicacion}")
                respuesta = input(f"\n¿Usar esta base de datos? (s/n): ")
                if respuesta.lower() == 's':
                    DB_PATH = ubicacion
                    break
        else:
            print("\n❌ No se encontró ninguna base de datos.")
            sys.exit(1)
    
    # 2. Crear backup
    print("\n" + "-"*80)
    print("PASO 1: CREAR BACKUP")
    print("-"*80)
    backup_path = crear_backup(DB_PATH)
    
    # 3. Conectar a la base de datos
    print("\n" + "-"*80)
    print("PASO 2: CONECTAR A BASE DE DATOS")
    print("-"*80)
    conn = conectar_db(DB_PATH)
    
    # 4. Migrar tabla EMPRESAS
    print("\n" + "-"*80)
    print("PASO 3: MIGRAR TABLA 'empresas'")
    print("-"*80)
    
    if not verificar_tabla_existe(conn, "empresas"):
        print("⚠️  La tabla 'empresas' no existe. Saltando...")
    else:
        columnas_existentes = obtener_columnas_existentes(conn, "empresas")
        print(f"📋 Columnas actuales: {', '.join(columnas_existentes)}")
        print(f"\n🔄 Agregando {len(COLUMNAS_EMPRESAS)} columnas nuevas...")
        
        agregadas = 0
        ya_existian = 0
        
        for columna in COLUMNAS_EMPRESAS:
            if columna in columnas_existentes:
                print(f"   ⏭️  '{columna}' ya existe")
                ya_existian += 1
            else:
                if agregar_columna(conn, "empresas", columna, "TEXT"):
                    print(f"   ✅ '{columna}' agregada")
                    agregadas += 1
                else:
                    print(f"   ❌ '{columna}' falló")
        
        print(f"\n📊 Resultado tabla 'empresas':")
        print(f"   ✅ Columnas agregadas: {agregadas}")
        print(f"   ⏭️  Ya existían: {ya_existian}")
    
    # 5. Migrar tabla USUARIOS
    print("\n" + "-"*80)
    print("PASO 4: MIGRAR TABLA 'usuarios'")
    print("-"*80)
    
    if not verificar_tabla_existe(conn, "usuarios"):
        print("⚠️  La tabla 'usuarios' no existe. Saltando...")
    else:
        columnas_existentes = obtener_columnas_existentes(conn, "usuarios")
        print(f"📋 Columnas actuales: {', '.join(columnas_existentes)}")
        print(f"\n🔄 Agregando {len(COLUMNAS_USUARIOS)} columnas nuevas...")
        
        agregadas = 0
        ya_existian = 0
        
        for columna in COLUMNAS_USUARIOS:
            if columna in columnas_existentes:
                print(f"   ⏭️  '{columna}' ya existe")
                ya_existian += 1
            else:
                if agregar_columna(conn, "usuarios", columna, "TEXT"):
                    print(f"   ✅ '{columna}' agregada")
                    agregadas += 1
                else:
                    print(f"   ❌ '{columna}' falló")
        
        print(f"\n📊 Resultado tabla 'usuarios':")
        print(f"   ✅ Columnas agregadas: {agregadas}")
        print(f"   ⏭️  Ya existían: {ya_existian}")
    
    # 6. Verificar cambios
    print("\n" + "-"*80)
    print("PASO 5: VERIFICAR CAMBIOS")
    print("-"*80)
    
    if verificar_tabla_existe(conn, "empresas"):
        columnas_empresas_final = obtener_columnas_existentes(conn, "empresas")
        print(f"✅ Tabla 'empresas' tiene {len(columnas_empresas_final)} columnas")
        
        # Verificar que todas las columnas requeridas existan
        faltantes = [c for c in COLUMNAS_EMPRESAS if c not in columnas_empresas_final]
        if faltantes:
            print(f"   ⚠️  Columnas faltantes: {', '.join(faltantes)}")
        else:
            print(f"   ✅ Todas las columnas requeridas están presentes")
    
    if verificar_tabla_existe(conn, "usuarios"):
        columnas_usuarios_final = obtener_columnas_existentes(conn, "usuarios")
        print(f"✅ Tabla 'usuarios' tiene {len(columnas_usuarios_final)} columnas")
        
        # Verificar que todas las columnas requeridas existan
        faltantes = [c for c in COLUMNAS_USUARIOS if c not in columnas_usuarios_final]
        if faltantes:
            print(f"   ⚠️  Columnas faltantes: {', '.join(faltantes)}")
        else:
            print(f"   ✅ Todas las columnas requeridas están presentes")
    
    # 7. Cerrar conexión
    conn.close()
    print("\n" + "="*80)
    print(" "*25 + "MIGRACIÓN COMPLETADA")
    print("="*80)
    
    if backup_path:
        print(f"\n💡 Si algo salió mal, puedes restaurar el backup:")
        print(f"   copy \"{backup_path}\" \"{DB_PATH}\"")
    
    print("\n✅ La base de datos ha sido actualizada correctamente.")
    print("   Ahora puedes reiniciar la aplicación Flask.\n")


# ==================== PUNTO DE ENTRADA ====================

if __name__ == "__main__":
    try:
        migrar_base_de_datos()
    except KeyboardInterrupt:
        print("\n\n⚠️  Migración cancelada por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
