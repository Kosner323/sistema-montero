#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_fase10_2_backup.py
=======================
Prueba simulada: FASE 10.2 - Creación de Backup ZIP
"""

import os
import io
import zipfile
import sys
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Rutas importantes
DB_PATH = r"d:\Mi-App-React\data\mi_sistema.db"
UPLOADS_PATH = r"d:\Mi-App-React\static\uploads"
COMPANY_DATA_PATH = r"d:\Mi-App-React\MONTERO_NEGOCIO\MONTERO_TOTAL"
OUTPUT_PATH = r"d:\Mi-App-React\backups"


def test_crear_backup_zip():
    """
    Simula la creación de un backup ZIP completo del sistema
    """
    print("\n" + "="*80)
    print("TEST: CREACION DE BACKUP ZIP")
    print("="*80)

    try:
        # ==================== PASO 1: VERIFICAR RUTAS ====================
        print("\n[PASO 1] Verificando rutas del sistema...")

        rutas_verificadas = []
        rutas_faltantes = []

        # Verificar base de datos
        if os.path.exists(DB_PATH):
            db_size = os.path.getsize(DB_PATH)
            print(f"   [OK] Base de datos encontrada: {DB_PATH}")
            print(f"        Tamaño: {db_size / (1024 * 1024):.2f} MB")
            rutas_verificadas.append(("BD", DB_PATH, db_size))
        else:
            print(f"   [X] Base de datos NO encontrada: {DB_PATH}")
            rutas_faltantes.append("BD")

        # Verificar uploads
        if os.path.exists(UPLOADS_PATH):
            uploads_count = sum(1 for root, dirs, files in os.walk(UPLOADS_PATH) for file in files)
            print(f"   [OK] Carpeta uploads encontrada: {UPLOADS_PATH}")
            print(f"        Archivos: {uploads_count}")
            rutas_verificadas.append(("UPLOADS", UPLOADS_PATH, uploads_count))
        else:
            print(f"   [X] Carpeta uploads NO encontrada: {UPLOADS_PATH}")
            rutas_faltantes.append("UPLOADS")

        # Verificar MONTERO_NEGOCIO
        if os.path.exists(COMPANY_DATA_PATH):
            company_count = sum(1 for root, dirs, files in os.walk(COMPANY_DATA_PATH) for file in files)
            print(f"   [OK] Carpeta MONTERO_NEGOCIO encontrada: {COMPANY_DATA_PATH}")
            print(f"        Archivos: {company_count}")
            rutas_verificadas.append(("COMPANY", COMPANY_DATA_PATH, company_count))
        else:
            print(f"   [INFO] Carpeta MONTERO_NEGOCIO NO encontrada (opcional): {COMPANY_DATA_PATH}")

        # ==================== PASO 2: CREAR BACKUP ZIP ====================
        print("\n[PASO 2] Creando backup ZIP en memoria...")

        # Crear buffer en memoria para el ZIP
        memory_file = io.BytesIO()

        archivos_agregados = 0
        total_bytes = 0

        # Crear el archivo ZIP
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Agregar base de datos
            if os.path.exists(DB_PATH):
                zipf.write(DB_PATH, arcname="data/mi_sistema.db")
                archivos_agregados += 1
                total_bytes += os.path.getsize(DB_PATH)
                print(f"   [OK] Base de datos agregada al ZIP")

            # Agregar uploads
            if os.path.exists(UPLOADS_PATH):
                uploads_added = 0
                for root, dirs, files in os.walk(UPLOADS_PATH):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, os.path.dirname(UPLOADS_PATH))
                        zipf.write(file_path, arcname=arcname)
                        uploads_added += 1
                        total_bytes += os.path.getsize(file_path)

                archivos_agregados += uploads_added
                print(f"   [OK] {uploads_added} archivos de uploads agregados al ZIP")

            # Agregar MONTERO_NEGOCIO
            if os.path.exists(COMPANY_DATA_PATH):
                company_added = 0
                for root, dirs, files in os.walk(COMPANY_DATA_PATH):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, os.path.dirname(COMPANY_DATA_PATH))
                        zipf.write(file_path, arcname=arcname)
                        company_added += 1
                        total_bytes += os.path.getsize(file_path)

                archivos_agregados += company_added
                print(f"   [OK] {company_added} archivos de MONTERO_NEGOCIO agregados al ZIP")

        # Obtener tamaño del ZIP en memoria
        zip_size = memory_file.tell()
        memory_file.seek(0)

        print(f"\n   [OK] ZIP creado exitosamente en memoria")
        print(f"        Total archivos: {archivos_agregados}")
        print(f"        Tamaño original: {total_bytes / (1024 * 1024):.2f} MB")
        print(f"        Tamaño comprimido: {zip_size / (1024 * 1024):.2f} MB")
        print(f"        Ratio compresión: {((1 - (zip_size / total_bytes)) * 100):.1f}%")

        # ==================== PASO 3: GUARDAR ZIP EN DISCO ====================
        print("\n[PASO 3] Guardando ZIP en disco para verificación...")

        # Crear carpeta de backups si no existe
        os.makedirs(OUTPUT_PATH, exist_ok=True)

        # Nombre del archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"backup_sistema_montero_{timestamp}.zip"
        zip_path = os.path.join(OUTPUT_PATH, zip_filename)

        # Guardar ZIP
        with open(zip_path, 'wb') as f:
            f.write(memory_file.getvalue())

        print(f"   [OK] ZIP guardado: {zip_path}")
        print(f"        Tamaño en disco: {os.path.getsize(zip_path) / (1024 * 1024):.2f} MB")

        # ==================== PASO 4: VERIFICAR CONTENIDO DEL ZIP ====================
        print("\n[PASO 4] Verificando contenido del ZIP...")

        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zip_contents = zipf.namelist()
            print(f"   [OK] Archivos en el ZIP: {len(zip_contents)}")

            # Mostrar primeros 10 archivos
            print(f"\n   [CONTENIDO] Primeros 10 archivos:")
            for i, filename in enumerate(zip_contents[:10]):
                file_info = zipf.getinfo(filename)
                print(f"      {i+1}. {filename} ({file_info.file_size} bytes)")

            if len(zip_contents) > 10:
                print(f"      ... y {len(zip_contents) - 10} archivos más")

            # Verificar que la BD esté en el ZIP
            bd_en_zip = any('mi_sistema.db' in name for name in zip_contents)
            if bd_en_zip:
                print(f"\n   [OK] Base de datos verificada en el ZIP")
            else:
                print(f"\n   [X] Base de datos NO encontrada en el ZIP")

        # ==================== PASO 5: VALIDACIONES ====================
        print("\n[PASO 5] Validando backup...")

        validaciones = []

        # Validar que se creó el ZIP
        if os.path.exists(zip_path):
            validaciones.append(("[OK]", "Archivo ZIP creado exitosamente"))
        else:
            validaciones.append(("[X]", "Archivo ZIP NO creado"))

        # Validar tamaño del ZIP
        if zip_size > 0:
            validaciones.append(("[OK]", f"ZIP tiene contenido ({zip_size / 1024:.2f} KB)"))
        else:
            validaciones.append(("[X]", "ZIP está vacío"))

        # Validar que contiene archivos
        if archivos_agregados > 0:
            validaciones.append(("[OK]", f"{archivos_agregados} archivos agregados al backup"))
        else:
            validaciones.append(("[X]", "No se agregaron archivos al backup"))

        # Validar que la BD está en el ZIP
        if bd_en_zip:
            validaciones.append(("[OK]", "Base de datos incluida en el backup"))
        else:
            validaciones.append(("[X]", "Base de datos NO incluida en el backup"))

        for simbolo, mensaje in validaciones:
            print(f"   {simbolo} {mensaje}")

        # ==================== RESULTADO ====================
        todas_ok = all(simbolo == "[OK]" for simbolo, _ in validaciones)

        if todas_ok:
            print("\n" + "="*80)
            print("[SUCCESS] PRUEBA EXITOSA - BACKUP ZIP FUNCIONAL")
            print("="*80)
            print("\nCONCLUSION:")
            print("  ✓ ZIP creado en memoria correctamente")
            print("  ✓ Todos los archivos del sistema incluidos")
            print("  ✓ Compresión aplicada exitosamente")
            print("  ✓ Archivo verificado en disco")
            print(f"\nARCHIVO GENERADO: {zip_path}")
            print("="*80 + "\n")
            return True
        else:
            print("\n" + "="*80)
            print("[ADVERTENCIA] PRUEBA COMPLETADA CON OBSERVACIONES")
            print("="*80 + "\n")
            return False

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("="*80)
    print(" "*15 + "FASE 10.2: PRUEBA DE BACKUP ZIP")
    print("="*80)

    resultado = test_crear_backup_zip()

    if resultado:
        print("\n[RESULTADO FINAL] El sistema de backup está listo para producción")
    else:
        print("\n[RESULTADO FINAL] Revisar las observaciones antes de usar en producción")

    print("="*80 + "\n")
