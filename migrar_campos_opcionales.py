# -*- coding: utf-8 -*-
"""
Script de Migración - Agregar Campos Opcionales a portal_users
==============================================================
Versión: 2.1 - SIN Snapchat y con RUTA DE BD CORREGIDA
Fecha: 5 de noviembre de 2025
Propósito: Agregar columnas telefono y fecha_nacimiento
"""

import sqlite3
import os
from datetime import datetime

# --- RUTA A LA BASE DE DATOS ACTUALIZADA ---
# Apunta a la carpeta 'data' donde está tu base de datos
DB_PATH = os.path.join("data", "mi_sistema.db")


def verificar_columna_existe(conn, tabla, columna):
    """Verifica si una columna ya existe en la tabla"""
    cursor = conn.execute(f"PRAGMA table_info({tabla})")
    columnas = [row[1] for row in cursor.fetchall()]
    return columna in columnas


def agregar_campos_opcionales():
    """Agrega los 2 campos opcionales a la tabla portal_users"""
    
    print("=" * 70)
    print("🔧 MIGRACIÓN: Agregar campos opcionales a portal_users (SIN Snapchat)")
    print("=" * 70)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Base de datos: {DB_PATH}")  # <-- Esto imprimirá 'data\mi_sistema.db'
    print()
    
    # Verificar que existe la base de datos
    if not os.path.exists(DB_PATH):
        print(f"❌ ERROR: No se encontró la base de datos en: {DB_PATH}")
        print("   Por favor, asegúrate de ejecutar este script desde la")
        print("   carpeta principal (D:\\Mi-App-React\\src\\dashboard)")
        return False
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("✅ Conexión exitosa a la base de datos")
        print()
        
        # Lista de columnas a agregar (SIN SNAPCHAT)
        columnas_nuevas = [
            ("telefono", "TEXT NULL", "Teléfono con código de país"),
            ("fecha_nacimiento", "TEXT NULL", "Fecha de nacimiento (YYYY-MM-DD)")
        ]
        
        columnas_agregadas = 0
        columnas_existentes = 0
        
        for nombre_columna, tipo_columna, descripcion in columnas_nuevas:
            print(f"🔍 Verificando columna '{nombre_columna}'...")
            
            if verificar_columna_existe(conn, "portal_users", nombre_columna):
                print(f"   ⚠️  La columna '{nombre_columna}' ya existe (se omite)")
                columnas_existentes += 1
            else:
                # Agregar la columna
                sql = f"ALTER TABLE portal_users ADD COLUMN {nombre_columna} {tipo_columna}"
                cursor.execute(sql)
                print(f"   ✅ Columna '{nombre_columna}' agregada exitosamente")
                print(f"      Descripción: {descripcion}")
                columnas_agregadas += 1
            
            print()
        
        # Confirmar cambios
        conn.commit()
        
        # Mostrar estructura final de la tabla
        print("=" * 70)
        print("📊 ESTRUCTURA FINAL DE LA TABLA portal_users")
        print("=" * 70)
        cursor.execute("PRAGMA table_info(portal_users)")
        columnas = cursor.fetchall()
        
        print(f"{'ID':<5} {'Nombre':<25} {'Tipo':<15} {'No Nulo':<10} {'Default':<15}")
        print("-" * 70)
        for col in columnas:
            col_id, nombre, tipo, no_nulo, default, pk = col
            no_nulo_str = "Sí" if no_nulo else "No"
            default_str = str(default) if default else "-"
            print(f"{col_id:<5} {nombre:<25} {tipo:<15} {no_nulo_str:<10} {default_str:<15}")
        
        print()
        print("=" * 70)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        print(f"   📊 Columnas agregadas: {columnas_agregadas}")
        print(f"   ⚠️  Columnas ya existentes: {columnas_existentes}")
        print(f"   📋 Total de columnas en portal_users: {len(columnas)}")
        print()
        print("🎯 PRÓXIMOS PASOS:")
        print("   1. Reinicia tu servidor Flask/Python")
        print("   2. Asegúrate de tener el archivo 'validation_models.py' en tu proyecto")
        print("   3. Verifica que auth.py esté actualizado para procesar los nuevos campos")
        print("=" * 70)
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ ERROR de base de datos: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR inesperado: {e}")
        return False


if __name__ == "__main__":
    print()
    exito = agregar_campos_opcionales()
    print()
    
    if exito:
        print("✅ Proceso completado exitosamente")
    else:
        print("❌ El proceso terminó con errores")
    
    input("\nPresiona ENTER para salir...")