# -*- coding: utf-8 -*-
"""
ORGANIZADOR DE DOCUMENTACIÓN - SISTEMA MONTERO
Mueve y clasifica archivos .md en carpetas temáticas.
"""
import os
import shutil

def organizar_documentacion():
    # 1. Configuración de Rutas
    base_dir = os.path.dirname(os.path.abspath(__file__)) # src/dashboard
    doc_root = os.path.join(base_dir, "DOCUMENTACION_BD")
    
    # Verificar que existe la carpeta de documentación
    if not os.path.exists(doc_root):
        print(f"⚠️ La carpeta {doc_root} no existe. Creándola...")
        os.makedirs(doc_root)
    
    # 2. Definir Categorías y Palabras Clave
    categorias = {
        "Seguridad": ["LOCKSCREEN", "AUTH", "LOGIN", "SEGURIDAD", "PERMISOS"],
        "Automatizacion_RPA": ["RPA", "ARL", "BOT", "COPILOTO", "AUTOMATION"],
        "Base_Datos": ["DB", "SQL", "SCHEMA", "MODELOS", "MIGRATION", "DATABASE"],
        "Proyecto_General": ["PROYECTO", "README", "TODO", "CHANGELOG", "INDICE", "INDEX", "MANUAL", "GUIA", "START", "QUICK", "LEEME", "DIA", "RESUMEN", "PLAN"],
        "Testing": ["TEST", "COVERAGE", "PYTEST"],
        "Otros": [] # Todo lo demás cae aquí
    }

    # Crear estructura de carpetas
    for cat in categorias:
        cat_path = os.path.join(doc_root, cat)
        os.makedirs(cat_path, exist_ok=True)

    # 3. Escanear y Mover desde DOCUMENTACION_BD raíz
    print("\n🧹 ORGANIZANDO DOCUMENTACIÓN EN SUBCARPETAS...")
    movidos = 0
    
    for filename in os.listdir(doc_root):
        # Solo procesar archivos .md en la raíz de DOCUMENTACION_BD
        file_path = os.path.join(doc_root, filename)
        
        if filename.lower().endswith(".md") and os.path.isfile(file_path):
            
            # Determinar categoría
            destino_cat = "Otros"
            name_upper = filename.upper()
            
            for cat, keywords in categorias.items():
                if cat != "Otros" and any(k in name_upper for k in keywords):
                    destino_cat = cat
                    break
            
            dest_folder = os.path.join(doc_root, destino_cat)
            dest_path = os.path.join(dest_folder, filename)
            
            try:
                shutil.move(file_path, dest_path)
                print(f"✅ {filename:50} → {destino_cat}/")
                movidos += 1
            except Exception as e:
                print(f"❌ Error moviendo {filename}: {e}")

    print("\n" + "="*40)
    print(f"✨ PROCESO COMPLETADO. Documentos organizados: {movidos}")
    print("="*40)

if __name__ == "__main__":
    organizar_documentacion()
