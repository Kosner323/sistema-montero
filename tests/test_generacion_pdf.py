"""
Script de Prueba: Sistema de Generación de PDFs con Firmas Digitales
Valida que las funciones auxiliares funcionen correctamente
"""

import os
import sys

# Agregar path del proyecto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'dashboard'))

from routes.formularios import buscar_firma_usuario, buscar_firma_empresa, BASE_MONTERO

def test_buscar_firma_usuario():
    """Prueba búsqueda de firma de usuario"""
    print("\n" + "="*80)
    print("TEST 1: BÚSQUEDA DE FIRMA DE USUARIO")
    print("="*80)
    
    # Caso 1: Usuario que no existe
    print("\n[TEST 1.1] Usuario inexistente: 999999999")
    resultado = buscar_firma_usuario("999999999")
    if resultado is None:
        print("✅ PASS: Retorna None cuando no existe")
    else:
        print(f"❌ FAIL: Debería retornar None, retornó: {resultado}")
    
    # Caso 2: Usuario que existe (reemplazar con ID real)
    print("\n[TEST 1.2] Usuario existente (si existe)")
    # Buscar primer usuario en la carpeta
    usuarios_path = os.path.join(BASE_MONTERO, "USUARIOS")
    if os.path.exists(usuarios_path):
        usuarios = [d for d in os.listdir(usuarios_path) if os.path.isdir(os.path.join(usuarios_path, d))]
        if usuarios:
            primer_usuario = usuarios[0]
            print(f"Probando con usuario: {primer_usuario}")
            resultado = buscar_firma_usuario(primer_usuario)
            
            if resultado and os.path.exists(resultado):
                print(f"✅ PASS: Firma encontrada en: {resultado}")
            else:
                print(f"⚠️  INFO: Usuario existe pero no tiene firma_usuario.png")
        else:
            print("⚠️  INFO: No hay usuarios en MONTERO_TOTAL/USUARIOS")
    else:
        print(f"⚠️  INFO: Carpeta USUARIOS no existe: {usuarios_path}")


def test_buscar_firma_empresa():
    """Prueba búsqueda de firma de empresa"""
    print("\n" + "="*80)
    print("TEST 2: BÚSQUEDA DE FIRMA DE EMPRESA")
    print("="*80)
    
    # Caso 1: Empresa que no existe
    print("\n[TEST 2.1] Empresa inexistente: NIT 999999999")
    resultado = buscar_firma_empresa("999999999")
    if resultado is None:
        print("✅ PASS: Retorna None cuando no existe")
    else:
        print(f"❌ FAIL: Debería retornar None, retornó: {resultado}")
    
    # Caso 2: Empresa que existe
    print("\n[TEST 2.2] Empresa existente (si existe)")
    empresas_path = os.path.join(BASE_MONTERO, "EMPRESAS")
    if os.path.exists(empresas_path):
        empresas = [d for d in os.listdir(empresas_path) if os.path.isdir(os.path.join(empresas_path, d))]
        if empresas:
            # Extraer NIT de la primera carpeta (formato: NIT_NombreEmpresa)
            primer_carpeta = empresas[0]
            if "_" in primer_carpeta:
                nit = primer_carpeta.split("_")[0]
                print(f"Probando con NIT: {nit} (carpeta: {primer_carpeta})")
                resultado = buscar_firma_empresa(nit)
                
                if resultado and os.path.exists(resultado):
                    print(f"✅ PASS: Firma encontrada en: {resultado}")
                else:
                    print(f"⚠️  INFO: Empresa existe pero no tiene firma_empresa.png")
            else:
                print(f"⚠️  INFO: Formato de carpeta inválido: {primer_carpeta}")
        else:
            print("⚠️  INFO: No hay empresas en MONTERO_TOTAL/EMPRESAS")
    else:
        print(f"⚠️  INFO: Carpeta EMPRESAS no existe: {empresas_path}")


def test_estructura_montero():
    """Valida que la estructura de carpetas MONTERO_TOTAL exista"""
    print("\n" + "="*80)
    print("TEST 3: VALIDACIÓN DE ESTRUCTURA MONTERO_TOTAL")
    print("="*80)
    
    print(f"\n[INFO] Ruta base: {BASE_MONTERO}")
    
    carpetas_esperadas = ["USUARIOS", "EMPRESAS"]
    
    for carpeta in carpetas_esperadas:
        ruta = os.path.join(BASE_MONTERO, carpeta)
        if os.path.exists(ruta):
            contenido = os.listdir(ruta)
            print(f"✅ {carpeta}/ existe ({len(contenido)} items)")
        else:
            print(f"❌ {carpeta}/ NO EXISTE")
            print(f"   Crear en: {ruta}")


def test_dependencias():
    """Valida que las dependencias estén instaladas"""
    print("\n" + "="*80)
    print("TEST 4: VALIDACIÓN DE DEPENDENCIAS")
    print("="*80)
    
    dependencias = [
        ("pdfrw", "pdfrw"),
        ("reportlab", "reportlab"),
        ("PIL", "pillow"),
        ("flask", "flask")
    ]
    
    for modulo, paquete in dependencias:
        try:
            __import__(modulo)
            print(f"✅ {paquete} instalado")
        except ImportError:
            print(f"❌ {paquete} NO INSTALADO")
            print(f"   Instalar con: pip install {paquete}")


def main():
    """Ejecutar todas las pruebas"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "PRUEBAS DEL SISTEMA DE PDFs" + " "*31 + "║")
    print("╚" + "="*78 + "╝")
    
    test_dependencias()
    test_estructura_montero()
    test_buscar_firma_usuario()
    test_buscar_firma_empresa()
    
    print("\n" + "="*80)
    print("PRUEBAS COMPLETADAS")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
