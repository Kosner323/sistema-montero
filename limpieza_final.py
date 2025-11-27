# -*- coding: utf-8 -*-
"""
SCRIPT DE LIMPIEZA FINAL - SISTEMA MONTERO
Elimina bases de datos fantasmas y deja solo la oficial.
"""
import os
import time

def limpiar_sistema():
    # 1. Definir la ruta base del proyecto
    base_dir = os.path.dirname(os.path.abspath(__file__)) # src/dashboard
    root_dir = os.path.abspath(os.path.join(base_dir, "..", "..")) # Raíz del proyecto
    
    # 2. Definir la intocable (LA REAL)
    db_real = os.path.abspath(os.path.join(base_dir, "data", "mi_sistema.db"))
    
    print(f"🛡️  BASE DE DATOS PROTEGIDA: {db_real}")
    print("=" * 60)
    
    # 3. Lista de archivos a ELIMINAR (Rutas relativas o absolutas detectadas en el escaneo)
    archivos_basura = [
        # El impostor vacío que usaba el robot antes
        os.path.join(base_dir, "instance", "mi_sistema.db"),
        # Bases de datos viejas o vacías en la raíz del dashboard
        os.path.join(base_dir, "database.db"),
        os.path.join(base_dir, "formularios.db"),
        # Archivos externos viejos
        os.path.join(root_dir, "MONTERO_NEGOCIO", "BASE_DE_DATOS", "formularios.db")
    ]
    
    eliminados = 0
    
    print("\n🗑️  INICIANDO ELIMINACIÓN...")
    for archivo in archivos_basura:
        ruta_completa = os.path.abspath(archivo)
        
        # Doble chequeo de seguridad: NO borrar la real
        if ruta_completa == db_real:
            print(f"⚠️  SKIP: Se intentó borrar la DB real por error: {ruta_completa}")
            continue
            
        if os.path.exists(ruta_completa):
            try:
                os.remove(ruta_completa)
                print(f"✅ ELIMINADO: {ruta_completa}")
                eliminados += 1
            except Exception as e:
                print(f"❌ ERROR al eliminar {ruta_completa}: {e}")
        else:
            print(f"👻 No encontrado (ya no existe): {ruta_completa}")

    # 4. Limpiar carpetas vacías (opcional, ej: instance)
    folder_instance = os.path.join(base_dir, "instance")
    if os.path.exists(folder_instance) and not os.listdir(folder_instance):
        try:
            os.rmdir(folder_instance)
            print(f"✅ CARPETA VACÍA ELIMINADA: {folder_instance}")
        except:
            pass

    print("\n" + "=" * 60)
    print(f"✨ LIMPIEZA COMPLETADA. Archivos eliminados: {eliminados}")
    print("   Tu sistema ahora es más ligero y seguro.")
    print("=" * 60)

if __name__ == "__main__":
    limpiar_sistema()
    time.sleep(2)
