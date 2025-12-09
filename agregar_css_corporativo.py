"""
Script para agregar corporate-redesign.css a todos los archivos HTML
que ya tienen style.css
"""
import os
import re

def agregar_css_corporativo(file_path):
    """Agrega el link del CSS corporativo después de style.css"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Verificar si ya tiene el CSS corporativo
        if 'corporate-redesign.css' in content:
            print(f"   [SKIP] Ya tiene CSS corporativo: {file_path}")
            return False

        # Verificar si tiene style.css
        if 'href="/assets/css/style.css"' not in content:
            print(f"   [WARN] No tiene style.css: {file_path}")
            return False

        # Patrón para encontrar la línea de style.css
        pattern = r'(<link rel="stylesheet" href="/assets/css/style\.css"[^>]*>)'

        # Replacement: agregar el CSS corporativo después
        replacement = r'\1\n    <!-- ✅ REDISEÑO CORPORATIVO ENTERPRISE -->\n    <link rel="stylesheet" href="/assets/css/corporate-redesign.css" />'

        # Reemplazar
        new_content = re.sub(pattern, replacement, content)

        # Verificar si se hizo el cambio
        if new_content == content:
            print(f"   [FAIL] No se pudo agregar CSS: {file_path}")
            return False

        # Guardar el archivo
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"   [OK] CSS agregado: {file_path}")
        return True

    except Exception as e:
        print(f"   [ERROR] Error en {file_path}: {str(e)}")
        return False

def main():
    """Procesar todos los archivos HTML en templates/"""
    templates_dir = 'd:\\Mi-App-React\\templates'

    print("Iniciando proceso de agregado de CSS corporativo...")
    print(f"Directorio: {templates_dir}\n")

    archivos_procesados = 0
    archivos_modificados = 0

    # Recorrer todos los archivos HTML
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html') or file.endswith('.HTML'):
                file_path = os.path.join(root, file)
                archivos_procesados += 1

                if agregar_css_corporativo(file_path):
                    archivos_modificados += 1

    print(f"\n{'='*60}")
    print(f"RESUMEN:")
    print(f"   - Archivos procesados: {archivos_procesados}")
    print(f"   - Archivos modificados: {archivos_modificados}")
    print(f"   - Archivos sin cambios: {archivos_procesados - archivos_modificados}")
    print(f"{'='*60}")
    print("Proceso completado exitosamente\n")

if __name__ == "__main__":
    main()
