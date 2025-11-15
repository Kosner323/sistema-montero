#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Verificación del Sistema Montero
Ejecutar desde: D:\Mi-App-React\src\dashboard
"""

import os
import sys
from pathlib import Path


def verificar_sistema():
    """Verifica la configuración completa del sistema"""

    print("=" * 80)
    print("🔍 VERIFICACIÓN DEL SISTEMA MONTERO")
    print("=" * 80)

    errores = []
    advertencias = []

    # 1. Verificar ubicación actual
    base_dir = Path.cwd()
    print(f"\n📁 Directorio actual: {base_dir}")

    # 2. Verificar app.py
    app_py = base_dir / "app.py"
    if app_py.exists():
        print("✅ app.py encontrado")
    else:
        errores.append("app.py no encontrado en el directorio actual")
        print("❌ app.py NO encontrado")

    # 3. Verificar carpeta assets
    print(f"\n📂 Verificando carpeta assets...")

    ubicaciones_assets = [
        base_dir / "assets",
        base_dir.parent / "assets",
    ]

    assets_dir = None
    for ubicacion in ubicaciones_assets:
        if ubicacion.exists():
            assets_dir = ubicacion
            print(f"✅ Assets encontrado en: {ubicacion}")
            break

    if not assets_dir:
        errores.append("Carpeta 'assets' no encontrada")
        print("❌ Carpeta 'assets' NO encontrada")
        print("   💡 Debes crearla en una de estas ubicaciones:")
        for loc in ubicaciones_assets:
            print(f"      - {loc}")
    else:
        # Verificar estructura de assets
        print(f"\n📂 Estructura de assets:")
        carpetas_requeridas = ["css", "js", "images", "fonts"]
        for carpeta in carpetas_requeridas:
            carpeta_path = assets_dir / carpeta
            if carpeta_path.exists():
                print(f"   ✅ {carpeta}/")
            else:
                advertencias.append(f"Carpeta 'assets/{carpeta}' no existe")
                print(f"   ⚠️  {carpeta}/ (no existe)")

        # Verificar archivos críticos
        print(f"\n📄 Archivos críticos:")
        archivos_criticos = [
            "css/style.css",
            "fonts/tabler-icons.min.css",
            "fonts/feather.css",
            "fonts/fontawesome.css",
        ]

        for archivo in archivos_criticos:
            archivo_path = assets_dir / archivo
            if archivo_path.exists():
                size = archivo_path.stat().st_size
                print(f"   ✅ {archivo} ({size:,} bytes)")
            else:
                advertencias.append(f"Archivo 'assets/{archivo}' no existe")
                print(f"   ⚠️  {archivo} (no existe)")

    # 4. Verificar archivos HTML
    print(f"\n📝 Verificando archivos HTML:")
    archivos_html = list(base_dir.glob("*.html"))
    print(f"   Total: {len(archivos_html)} archivos")

    # Verificar rutas en HTML
    html_con_error = []
    for html in archivos_html:
        try:
            with open(html, "r", encoding="utf-8") as f:
                contenido = f.read()
            if "../assets/" in contenido:
                html_con_error.append(html.name)
        except:
            pass

    if html_con_error:
        errores.append(f"{len(html_con_error)} archivos HTML con rutas incorrectas")
        print(f"   ❌ {len(html_con_error)} archivos con rutas '../assets/' (incorrecto)")
        for nombre in html_con_error[:5]:
            print(f"      - {nombre}")
    else:
        print(f"   ✅ Todos los archivos usan '/assets/' correctamente")

    # 5. Verificar base de datos
    print(f"\n💾 Base de datos:")
    db_path = base_dir / "data" / "mi_sistema.db"
    if db_path.exists():
        size = db_path.stat().st_size
        print(f"   ✅ Existe: {db_path} ({size:,} bytes)")
    else:
        print(f"   ⚠️  No existe (se creará al iniciar)")

    # 6. Verificar archivo .env
    print(f"\n🔐 Configuración:")
    env_path = base_dir / "_env"
    if env_path.exists():
        print(f"   ✅ Archivo _env encontrado")
    else:
        advertencias.append("Archivo '_env' no encontrado")
        print(f"   ⚠️  Archivo _env no encontrado")

    # 7. Verificar dependencias Python
    print(f"\n📦 Dependencias Python:")
    try:
        import flask

        print(f"   ✅ Flask {flask.__version__}")
    except ImportError:
        errores.append("Flask no instalado")
        print(f"   ❌ Flask no instalado")

    try:
        import cryptography

        print(f"   ✅ Cryptography instalado")
    except ImportError:
        advertencias.append("Cryptography no instalado")
        print(f"   ⚠️  Cryptography no instalado")

    # Resumen
    print("\n" + "=" * 80)
    print("📊 RESUMEN")
    print("=" * 80)

    if not errores and not advertencias:
        print("\n✅ ¡TODO PERFECTO! El sistema está listo para funcionar.")
        print("\n🚀 Para iniciar:")
        print("   python app.py")
        print("   o")
        print("   iniciar_sistema_corregido.bat")
    else:
        if errores:
            print(f"\n❌ ERRORES CRÍTICOS ({len(errores)}):")
            for i, error in enumerate(errores, 1):
                print(f"   {i}. {error}")

        if advertencias:
            print(f"\n⚠️  ADVERTENCIAS ({len(advertencias)}):")
            for i, adv in enumerate(advertencias, 1):
                print(f"   {i}. {adv}")

        print("\n💡 ACCIONES RECOMENDADAS:")

        if not assets_dir:
            print("\n   1. CREAR CARPETA ASSETS:")
            print(f"      mkdir {base_dir / 'assets'}")
            print(f"      mkdir {base_dir / 'assets' / 'css'}")
            print(f"      mkdir {base_dir / 'assets' / 'js'}")
            print(f"      mkdir {base_dir / 'assets' / 'images'}")
            print(f"      mkdir {base_dir / 'assets' / 'fonts'}")
            print("\n   2. COPIAR ARCHIVOS ASSETS REALES:")
            print(f"      Desde: D:\\Mi-App-React\\src\\assets")
            print(f"      Hacia: {base_dir / 'assets'}")

        if html_con_error:
            print("\n   3. CORREGIR RUTAS EN HTML:")
            print("      Ejecutar el script: corregir_rutas_assets.py")

    print("\n" + "=" * 80)

    return len(errores) == 0


if __name__ == "__main__":
    try:
        exito = verificar_sistema()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
