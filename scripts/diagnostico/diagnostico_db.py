# -*- coding: utf-8 -*-
"""
RASTREADOR DE BASES DE DATOS - SISTEMA MONTERO
Este script busca todos los archivos .db y te dice cuál tiene los datos reales.
"""
import os
import sqlite3

def escanear_y_reportar():
    print("\n🕵️  INICIANDO RASTREO DE BASES DE DATOS...")
    print("==========================================")
    
    # 1. Definir dónde empezar a buscar (desde la raíz del proyecto hacia abajo)
    # Subimos 2 niveles desde dashboard/ para estar seguros
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    
    archivos_db = []
    
    # 2. Buscar archivos .db
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".db") and "node_modules" not in root:
                full_path = os.path.join(root, file)
                archivos_db.append(full_path)

    if not archivos_db:
        print("❌ ¡ALERTA! No se encontraron archivos .db en ninguna parte.")
        return

    print(f"✅ Se encontraron {len(archivos_db)} archivos de base de datos.\n")

    # 3. Auditar cada uno
    for db_path in archivos_db:
        print(f"📂 ANALIZANDO: {db_path}")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verificar Empresas
            try:
                count_emp = cursor.execute("SELECT COUNT(*) FROM empresas").fetchone()[0]
                print(f"   🏢 Empresas encontradas: {count_emp}")
            except:
                print("   ⚠️  Tabla 'empresas' NO existe.")

            # Verificar Usuarios
            try:
                count_usr = cursor.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
                print(f"   👥 Usuarios encontrados: {count_usr}")
            except:
                print("   ⚠️  Tabla 'usuarios' NO existe.")
            
            conn.close()
            print("------------------------------------------")
        except Exception as e:
            print(f"   ❌ Error leyendo archivo: {e}")
            print("------------------------------------------")

if __name__ == "__main__":
    escanear_y_reportar()
    input("\nPresiona ENTER para cerrar...")