#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Validación de ENCRYPTION_KEY
Sistema Montero - Validación rápida
"""

import os
import sys


def validar_env_file():
    """Valida que el archivo _env exista y tenga ENCRYPTION_KEY"""
    print("📁 Verificando archivo _env...")

    if not os.path.exists("_env"):
        print("❌ ERROR: Archivo _env no encontrado")
        return False

    with open("_env", "r", encoding="utf-8") as f:
        contenido = f.read()

    if "ENCRYPTION_KEY=" not in contenido:
        print("❌ ERROR: ENCRYPTION_KEY no encontrada en _env")
        return False

    # Buscar la línea de ENCRYPTION_KEY
    for linea in contenido.split("\n"):
        if linea.startswith("ENCRYPTION_KEY="):
            clave = linea.split("=", 1)[1].strip()
            if not clave or clave == "":
                print("❌ ERROR: ENCRYPTION_KEY está vacía")
                return False
            print(f"✅ ENCRYPTION_KEY encontrada: {clave[:20]}...")
            return True

    print("❌ ERROR: ENCRYPTION_KEY no encontrada")
    return False


def validar_cryptography():
    """Valida que cryptography esté instalado"""
    print("\n🔐 Verificando módulo cryptography...")

    try:
        import cryptography

        print(f"✅ cryptography instalado - versión: {cryptography.__version__}")
        return True
    except ImportError:
        print("❌ ERROR: cryptography no está instalado")
        print("   Ejecuta: pip install cryptography --break-system-packages")
        return False


def validar_encryption():
    """Valida que el sistema de encriptación funcione"""
    print("\n🔒 Probando sistema de encriptación...")

    try:
        # Importar el sistema de encriptación
        from encryption import encrypt_text, decrypt_text

        # Texto de prueba
        texto_prueba = "Hola Montero - Prueba de encriptación 123"
        print(f"   Texto original: {texto_prueba}")

        # Encriptar
        texto_encriptado = encrypt_text(texto_prueba)
        print(f"   Texto encriptado: {texto_encriptado[:50]}...")

        # Desencriptar
        texto_desencriptado = decrypt_text(texto_encriptado)
        print(f"   Texto desencriptado: {texto_desencriptado}")

        # Verificar que sean iguales
        if texto_prueba == texto_desencriptado:
            print("✅ Encriptación/Desencriptación funcionan correctamente")
            return True
        else:
            print("❌ ERROR: El texto desencriptado no coincide con el original")
            return False

    except Exception as e:
        print(f"❌ ERROR al probar encriptación: {str(e)}")
        return False


def main():
    """Función principal de validación"""
    print("\n" + "=" * 60)
    print("  VALIDACIÓN DE ENCRYPTION_KEY - Sistema Montero")
    print("=" * 60 + "\n")

    # Validaciones
    validaciones = [
        ("Archivo _env", validar_env_file),
        ("Módulo cryptography", validar_cryptography),
        ("Sistema de encriptación", validar_encryption),
    ]

    resultados = []
    for nombre, funcion in validaciones:
        try:
            resultado = funcion()
            resultados.append(resultado)
        except Exception as e:
            print(f"❌ ERROR en {nombre}: {str(e)}")
            resultados.append(False)

    # Resumen
    print("\n" + "=" * 60)
    print("  RESUMEN DE VALIDACIÓN")
    print("=" * 60)

    exitosas = sum(resultados)
    totales = len(resultados)

    for i, (nombre, _) in enumerate(validaciones):
        estado = "✅ PASS" if resultados[i] else "❌ FAIL"
        print(f"  {estado} - {nombre}")

    print(f"\nResultado: {exitosas}/{totales} validaciones exitosas")

    if all(resultados):
        print("\n🎉 ¡TODO FUNCIONA CORRECTAMENTE!")
        print("   El sistema de encriptación está operativo.")
        return 0
    else:
        print("\n⚠️  HAY PROBLEMAS QUE RESOLVER")
        print("   Revisa los errores anteriores.")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Validación interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
