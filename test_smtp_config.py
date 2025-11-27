# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la configuración SMTP de Flask-Mail.
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Verificar que las variables SMTP estén configuradas
print("=" * 70)
print("VERIFICACIÓN DE CONFIGURACIÓN SMTP")
print("=" * 70)
print()

required_vars = {
    "MAIL_SERVER": os.getenv("MAIL_SERVER"),
    "MAIL_PORT": os.getenv("MAIL_PORT"),
    "MAIL_USERNAME": os.getenv("MAIL_USERNAME"),
    "MAIL_PASSWORD": os.getenv("MAIL_PASSWORD"),
    "MAIL_USE_TLS": os.getenv("MAIL_USE_TLS"),
}

print("Variables de entorno detectadas:")
print("-" * 70)
all_configured = True
for key, value in required_vars.items():
    if value:
        display_value = value if key != "MAIL_PASSWORD" else "***" + value[-4:] if len(value) > 4 else "***"
        print(f"✓ {key}: {display_value}")
    else:
        print(f"✗ {key}: NO CONFIGURADO")
        all_configured = False

print()

if not all_configured:
    print("⚠️  ERROR: Faltan variables de entorno")
    print()
    print("Por favor, configura las siguientes variables en tu archivo .env:")
    print()
    print("MAIL_SERVER=smtp.gmail.com")
    print("MAIL_PORT=587")
    print("MAIL_USE_TLS=True")
    print("MAIL_USERNAME=tu_email@gmail.com")
    print("MAIL_PASSWORD=tu_password_de_aplicacion")
    print()
    print("Para Gmail, necesitas una 'Contraseña de aplicación':")
    print("1. Ve a: https://myaccount.google.com/security")
    print("2. Activa la verificación en 2 pasos")
    print("3. Ve a: https://myaccount.google.com/apppasswords")
    print("4. Genera una contraseña de aplicación para 'Correo'")
    print()
    sys.exit(1)

print("=" * 70)
print("INICIALIZANDO APLICACIÓN FLASK")
print("=" * 70)
print()

try:
    from app import create_app
    from email_utils import send_test_email

    app = create_app()

    with app.app_context():
        print("Aplicación Flask inicializada correctamente")
        print()
        print("=" * 70)
        print("PRUEBA DE ENVÍO DE CORREO")
        print("=" * 70)
        print()

        recipient = input("Ingresa el correo de destino para la prueba: ").strip()

        if not recipient:
            print("❌ No se ingresó un correo de destino")
            sys.exit(1)

        print()
        print(f"Enviando correo de prueba a: {recipient}")
        print("Esto puede tardar unos segundos...")
        print()

        success = send_test_email(recipient)

        print()
        if success:
            print("✅ ¡Correo enviado exitosamente!")
            print()
            print(f"Revisa la bandeja de entrada de {recipient}")
            print("Si no lo ves, revisa la carpeta de spam/correo no deseado")
        else:
            print("❌ Error al enviar el correo")
            print()
            print("Posibles causas:")
            print("1. Contraseña incorrecta (asegúrate de usar la contraseña de aplicación)")
            print("2. Verificación en 2 pasos no activada en Gmail")
            print("3. Servidor SMTP bloqueado por firewall")
            print("4. Configuración incorrecta del servidor SMTP")
            print()
            print("Revisa los logs en la consola para más detalles")

except ImportError as e:
    print(f"❌ Error al importar módulos: {e}")
    print()
    print("Asegúrate de que Flask-Mail esté instalado:")
    print("pip install Flask-Mail")
except Exception as e:
    print(f"❌ Error inesperado: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print("PRUEBA COMPLETADA")
print("=" * 70)
