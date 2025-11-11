#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir rutas de assets en archivos HTML
Convierte ../assets/ a /assets/ para compatibilidad con Flask.
Versión corregida para usar el directorio de ejecución (os.getcwd()).
"""

import os
import re
from pathlib import Path


def corregir_rutas_html(directorio_proyecto):
    """
    Corrige todas las referencias a ../assets/ en archivos HTML
    convirtiéndolas a /assets/
    """
    archivos_modificados = []
    # Patrón para encontrar ../assets/ (ignora mayúsculas/minúsculas)
    patron = re.compile(r"\.\.\/assets\/", re.IGNORECASE)

    # Buscar todos los archivos HTML recursivamente en el directorio
    # Nota: rglob busca en subcarpetas, si tuvieras HTML en ellas.
    for archivo_html in Path(directorio_proyecto).rglob("*.html"):
        try:
            # Abrir archivo para leer
            with open(archivo_html, "r", encoding="utf-8") as f:
                contenido_original = f.read()

            # Reemplazar ../assets/ por /assets/
            contenido_nuevo = patron.sub("/assets/", contenido_original)

            # Solo escribir si hubo cambios
            if contenido_original != contenido_nuevo:
                # Abrir archivo para escribir (sobrescribir)
                with open(archivo_html, "w", encoding="utf-8") as f:
                    f.write(contenido_nuevo)
                archivos_modificados.append(str(archivo_html))
                # Se imprime el nombre del archivo corregido para feedback
                print(f"✅ Corregido: {archivo_html.name}")

        except Exception as e:
            # Manejo de errores de lectura/escritura (ej. permisos)
            print(f"❌ Error en {archivo_html}: {e}")

    return archivos_modificados


def main():
    # **CORRECCIÓN APLICADA AQUÍ:** Usamos el directorio actual (D:\Mi-App-React\src\dashboard)
    directorio = os.getcwd()

    print("=" * 70)
    print("🔧 CORRECCIÓN DE RUTAS DE ASSETS EN HTML")
    print("=" * 70)
    print(
        f"📁 Directorio de Búsqueda: {directorio}\n"
    )  # Muestra la ruta real de Windows

    archivos = corregir_rutas_html(directorio)

    print("\n" + "=" * 70)
    print(f"✅ Proceso completado: {len(archivos)} archivos modificados")
    print("=" * 70)

    if archivos:
        print("\n📝 Archivos modificados:")
        for archivo in archivos:
            print(f"   - {Path(archivo).name}")
    else:
        print(
            "💡 No se encontraron archivos para modificar (posiblemente ya están corregidos)."
        )


if __name__ == "__main__":
    main()
