#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnóstico de Sistema de Generación de PDFs
Verifica que todo esté listo para generar PDFs
"""
import sys
import os

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Agregar el path del dashboard al PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'dashboard'))

print("=" * 80)
print("🔍 DIAGNÓSTICO DE SISTEMA DE GENERACIÓN DE PDFs")
print("=" * 80)

try:
    from app import app
    from utils import get_db_connection

    with app.app_context():
        print("\n✅ Aplicación Flask cargada correctamente")

        # Test 1: Verificar UPLOAD_FOLDER
        print("\n" + "=" * 80)
        print("📁 TEST 1: Configuración de Carpeta de Plantillas")
        print("-" * 80)

        upload_folder = app.config.get('UPLOAD_FOLDER')
        if upload_folder:
            print(f"✅ UPLOAD_FOLDER configurado: {upload_folder}")
            exists = os.path.exists(upload_folder)
            print(f"   {'✅' if exists else '❌'} Carpeta existe: {exists}")
            if not exists:
                print(f"   ⚠️  SOLUCIÓN: Crear carpeta con: mkdir \"{upload_folder}\"")
        else:
            print("❌ UPLOAD_FOLDER no está configurado en app.config")

        # Test 2: Verificar tabla formularios_importados
        print("\n" + "=" * 80)
        print("📊 TEST 2: Tabla de Formularios Importados")
        print("-" * 80)

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()

            # Verificar si existe la tabla
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='formularios_importados'")
            table_exists = cursor.fetchone() is not None

            if table_exists:
                print("✅ Tabla 'formularios_importados' existe")

                # Contar plantillas
                cursor.execute("SELECT COUNT(*) FROM formularios_importados")
                count = cursor.fetchone()[0]
                print(f"   📄 Plantillas importadas: {count}")

                if count > 0:
                    # Mostrar plantillas disponibles
                    cursor.execute("SELECT id, nombre, nombre_archivo FROM formularios_importados")
                    templates = cursor.fetchall()
                    print("\n   📋 Plantillas Disponibles:")
                    for t in templates:
                        print(f"      • ID {t['id']}: {t['nombre']} ({t['nombre_archivo']})")
                        # Verificar si el archivo físico existe
                        if upload_folder:
                            file_path = os.path.join(upload_folder, t['nombre_archivo'])
                            file_exists = os.path.exists(file_path)
                            print(f"         {'✅' if file_exists else '❌'} Archivo físico existe: {file_exists}")
                else:
                    print("\n   ⚠️  No hay plantillas importadas")
                    print("   💡 SOLUCIÓN: Importar una plantilla PDF desde la interfaz:")
                    print("      http://localhost:5000/formularios")
            else:
                print("❌ Tabla 'formularios_importados' NO existe")
                print("\n   💡 SOLUCIÓN: Crear la tabla con el siguiente SQL:")
                print("""
CREATE TABLE formularios_importados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    nombre_archivo TEXT NOT NULL,
    ruta_archivo TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
                """)

            # Test 3: Verificar datos de prueba
            print("\n" + "=" * 80)
            print("📊 TEST 3: Datos de Prueba Disponibles")
            print("-" * 80)

            # Contar usuarios
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            usuarios_count = cursor.fetchone()[0]
            print(f"   👤 Usuarios disponibles: {usuarios_count}")

            if usuarios_count > 0:
                cursor.execute("SELECT id, numeroId, primerNombre, primerApellido FROM usuarios LIMIT 3")
                usuarios = cursor.fetchall()
                print("\n   Ejemplos:")
                for u in usuarios:
                    print(f"      • ID {u['id']}: {u['primerNombre']} {u['primerApellido']} (CC: {u['numeroId']})")

            # Contar empresas
            cursor.execute("SELECT COUNT(*) FROM empresas")
            empresas_count = cursor.fetchone()[0]
            print(f"\n   🏢 Empresas disponibles: {empresas_count}")

            if empresas_count > 0:
                cursor.execute("SELECT nit, nombre_empresa FROM empresas LIMIT 3")
                empresas = cursor.fetchall()
                print("\n   Ejemplos:")
                for e in empresas:
                    print(f"      • NIT {e['nit']}: {e['nombre_empresa']}")

            conn.close()

            # Test 4: Verificar dependencias
            print("\n" + "=" * 80)
            print("📦 TEST 4: Dependencias de Python")
            print("-" * 80)

            try:
                from pypdf import PdfReader, PdfWriter
                print("✅ pypdf instalado correctamente")
            except ImportError:
                print("❌ pypdf NO está instalado")
                print("   💡 SOLUCIÓN: pip install pypdf")

            try:
                from werkzeug.utils import secure_filename
                print("✅ werkzeug instalado correctamente")
            except ImportError:
                print("❌ werkzeug NO está instalado")
                print("   💡 SOLUCIÓN: pip install werkzeug")

            # Test 5: Verificar carpeta de guardado de usuarios
            print("\n" + "=" * 80)
            print("📁 TEST 5: Carpeta de Guardado de PDFs Generados")
            print("-" * 80)

            user_data_folder = os.path.join("D:", os.sep, "Mi-App-React", "MONTERO_NEGOCIO", "MONTERO_TOTAL", "USUARIOS")
            print(f"   Carpeta base: {user_data_folder}")
            exists = os.path.exists(user_data_folder)
            print(f"   {'✅' if exists else '⚠️ '} Carpeta existe: {exists}")
            if not exists:
                print(f"   💡 La carpeta se creará automáticamente al generar el primer PDF")

            # Resumen Final
            print("\n" + "=" * 80)
            print("📊 RESUMEN")
            print("=" * 80)

            all_ok = True
            issues = []

            if not upload_folder or not os.path.exists(upload_folder):
                all_ok = False
                issues.append("❌ UPLOAD_FOLDER no configurado o no existe")

            if not table_exists:
                all_ok = False
                issues.append("❌ Tabla formularios_importados no existe")
            elif count == 0:
                all_ok = False
                issues.append("⚠️  No hay plantillas PDF importadas")

            if usuarios_count == 0:
                all_ok = False
                issues.append("⚠️  No hay usuarios registrados")

            if empresas_count == 0:
                all_ok = False
                issues.append("⚠️  No hay empresas registradas")

            if all_ok:
                print("\n✅ ¡TODO LISTO! El sistema de generación de PDFs está completamente configurado.")
                print("\n💡 SIGUIENTE PASO:")
                print("   1. Inicia el servidor: python src/dashboard/app.py")
                print("   2. Accede a: http://localhost:5000/formularios")
                print("   3. Selecciona una plantilla, empleado y empresa")
                print("   4. Click en 'Generar y Descargar PDF'")
            else:
                print("\n⚠️  PROBLEMAS DETECTADOS:")
                for issue in issues:
                    print(f"   {issue}")
                print("\n💡 Revisa las soluciones sugeridas arriba en cada sección.")
        else:
            print("❌ Error: No se pudo conectar a la base de datos")

except Exception as e:
    print(f"\n❌ Error durante el diagnóstico: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80 + "\n")
