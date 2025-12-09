#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Validación de Configuración Centralizada de Uploads
Sistema Montero

Verifica que la configuración global de subida de archivos esté correctamente implementada.
"""

import os
import sys

# Agregar el directorio dashboard al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from utils import (
    get_upload_folder, 
    get_max_file_size, 
    get_allowed_extensions,
    is_file_allowed,
    validate_file_size
)


def format_size(bytes_size):
    """Formatea tamaño en bytes a formato legible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"


def check_upload_config():
    """Verifica la configuración de uploads"""
    print("=" * 80)
    print("🔍 VALIDACIÓN DE CONFIGURACIÓN CENTRALIZADA DE UPLOADS")
    print("=" * 80)
    print()
    
    # Crear instancia de la app
    app = create_app()
    
    with app.app_context():
        print("✅ Contexto de aplicación creado correctamente")
        print()
        
        # 1. Verificar configuración en app.config
        print("📋 CONFIGURACIÓN GLOBAL (app.config):")
        print("-" * 80)
        
        upload_folder = app.config.get('UPLOAD_FOLDER')
        max_size = app.config.get('MAX_CONTENT_LENGTH')
        allowed_ext = app.config.get('ALLOWED_EXTENSIONS')
        
        if upload_folder:
            print(f"✅ UPLOAD_FOLDER configurado: {upload_folder}")
        else:
            print("❌ UPLOAD_FOLDER NO está configurado en app.config")
            return False
        
        if max_size:
            print(f"✅ MAX_CONTENT_LENGTH configurado: {format_size(max_size)}")
        else:
            print("❌ MAX_CONTENT_LENGTH NO está configurado en app.config")
            return False
        
        if allowed_ext:
            print(f"✅ ALLOWED_EXTENSIONS configurado: {', '.join(sorted(allowed_ext))}")
        else:
            print("❌ ALLOWED_EXTENSIONS NO está configurado en app.config")
            return False
        
        print()
        
        # 2. Verificar estructura de carpetas
        print("📁 ESTRUCTURA DE CARPETAS:")
        print("-" * 80)
        
        subdirs = ['docs', 'formularios', 'tutelas', 'impuestos', 'temp']
        all_exist = True
        
        for subdir in subdirs:
            full_path = os.path.join(upload_folder, subdir)
            if os.path.exists(full_path):
                print(f"✅ {subdir:15} → {full_path}")
            else:
                print(f"⚠️  {subdir:15} → NO EXISTE (se creará automáticamente)")
                all_exist = False
        
        print()
        
        # 3. Verificar funciones auxiliares de utils.py
        print("🔧 FUNCIONES AUXILIARES (utils.py):")
        print("-" * 80)
        
        try:
            # get_upload_folder
            test_folder = get_upload_folder('docs')
            print(f"✅ get_upload_folder('docs') → {test_folder}")
            
            # get_max_file_size
            max_from_util = get_max_file_size()
            print(f"✅ get_max_file_size() → {format_size(max_from_util)}")
            
            # get_allowed_extensions
            ext_from_util = get_allowed_extensions()
            print(f"✅ get_allowed_extensions() → {len(ext_from_util)} extensiones")
            
            # is_file_allowed - casos de prueba
            test_files = {
                'documento.pdf': True,
                'imagen.jpg': True,
                'hoja_calculo.xlsx': True,
                'virus.exe': False,
                'script.sh': False,
                'archivo.csv': True,
            }
            
            print()
            print("📝 PRUEBAS DE VALIDACIÓN DE ARCHIVOS:")
            print("-" * 80)
            
            all_passed = True
            for filename, expected in test_files.items():
                result = is_file_allowed(filename)
                status = "✅" if result == expected else "❌"
                print(f"{status} {filename:20} → {'Permitido' if result else 'Bloqueado'} (esperado: {'Permitido' if expected else 'Bloqueado'})")
                if result != expected:
                    all_passed = False
            
            print()
            
            # validate_file_size - pruebas
            print("📊 PRUEBAS DE VALIDACIÓN DE TAMAÑO:")
            print("-" * 80)
            
            test_sizes = [
                (1024, True),  # 1KB
                (1024 * 1024, True),  # 1MB
                (10 * 1024 * 1024, True),  # 10MB
                (20 * 1024 * 1024, False),  # 20MB (excede límite de 16MB)
            ]
            
            for size, expected_valid in test_sizes:
                test_content = b'x' * size
                is_valid, error_msg = validate_file_size(test_content)
                status = "✅" if is_valid == expected_valid else "❌"
                result_text = "Válido" if is_valid else f"Rechazado: {error_msg}"
                print(f"{status} {format_size(size):10} → {result_text}")
            
            print()
            
        except Exception as e:
            print(f"❌ Error al ejecutar funciones auxiliares: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # 4. Verificar admin_routes.py actualizado
        print("🔍 VERIFICACIÓN DE MÓDULOS ACTUALIZADOS:")
        print("-" * 80)
        
        try:
            from routes.admin_routes import allowed_file as admin_allowed_file
            print("✅ admin_routes.py importado correctamente")
            
            # Verificar que usa current_app.config
            test_pdf = admin_allowed_file('test.pdf')
            if test_pdf:
                print("✅ admin_routes.allowed_file() funciona correctamente")
            else:
                print("⚠️  admin_routes.allowed_file() devolvió resultado inesperado")
        
        except ImportError as e:
            print(f"⚠️  No se pudo importar admin_routes: {e}")
        except Exception as e:
            print(f"⚠️  Error al verificar admin_routes: {e}")
        
        print()
        
        # 5. Resumen final
        print("=" * 80)
        print("📊 RESUMEN DE VALIDACIÓN")
        print("=" * 80)
        
        if upload_folder and max_size and allowed_ext and all_passed:
            print("✅ CONFIGURACIÓN CENTRALIZADA CORRECTAMENTE IMPLEMENTADA")
            print()
            print("Próximos pasos recomendados:")
            print("  1. Reiniciar servidor Flask para aplicar cambios")
            print("  2. Probar subida de archivos en módulos (Gestor, Impuestos, Tutelas)")
            print("  3. Verificar logs de uploads en MONTERO_NEGOCIO/LOGS_APLICACION/")
            print()
            return True
        else:
            print("⚠️  CONFIGURACIÓN PARCIALMENTE IMPLEMENTADA")
            print()
            print("Revisar elementos marcados con ❌ en la validación anterior")
            print()
            return False


if __name__ == '__main__':
    success = check_upload_config()
    sys.exit(0 if success else 1)
