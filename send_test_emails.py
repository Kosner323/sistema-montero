# -*- coding: utf-8 -*-
"""
Script para enviar correos de prueba a las direcciones especificadas.
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("=" * 70)
print("ENVIO DE CORREOS DE PRUEBA - SISTEMA MONTERO")
print("=" * 70)
print()

# Verificar configuración
mail_username = os.getenv("MAIL_USERNAME")
mail_password = os.getenv("MAIL_PASSWORD")

if not mail_username or mail_username == "tu_email@gmail.com":
    print("[ERROR] MAIL_USERNAME no esta configurado")
    print()
    print("Por favor, edita el archivo .env y configura:")
    print("MAIL_USERNAME=tu_email_real@gmail.com")
    print()
    sys.exit(1)

if not mail_password or mail_password == "tu_password_de_aplicacion_aqui":
    print("[ERROR] MAIL_PASSWORD no esta configurado")
    print()
    print("Necesitas generar una contrasena de aplicacion de Gmail:")
    print("1. Ve a: https://myaccount.google.com/security")
    print("2. Activa la verificacion en 2 pasos")
    print("3. Ve a: https://myaccount.google.com/apppasswords")
    print("4. Genera una contrasena para 'Correo'")
    print("5. Copia la contrasena de 16 caracteres")
    print("6. Edita .env y pon: MAIL_PASSWORD=xxxx xxxx xxxx xxxx")
    print()
    sys.exit(1)

print("[OK] Configuracion SMTP detectada")
print(f"  Servidor: {os.getenv('MAIL_SERVER')}")
print(f"  Usuario: {mail_username}")
print()

# Inicializar Flask
print("Inicializando aplicacion Flask...")
try:
    from app import create_app
    from email_utils import send_test_email, send_welcome_email

    app = create_app()

    with app.app_context():
        print("[OK] Aplicacion inicializada correctamente")
        print()
        print("=" * 70)
        print("ENVIANDO CORREOS DE PRUEBA")
        print("=" * 70)
        print()

        # Lista de destinatarios
        recipients = [
            "kevinlomasd@gmail.com",
            "monterojk2014@hotmail.com"
        ]

        success_count = 0
        failed_count = 0

        for i, recipient in enumerate(recipients, 1):
            print(f"[{i}/{len(recipients)}] Enviando correo a: {recipient}")
            print("    Esperando respuesta del servidor SMTP...")

            try:
                # Enviar correo de bienvenida con diseño profesional
                success = send_welcome_email(
                    recipient=recipient,
                    nombre="Usuario de Prueba",
                    fecha_registro=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    url_login="http://localhost:5000/login"
                )

                if success:
                    print(f"    [EXITO] Correo enviado exitosamente a {recipient}")
                    success_count += 1
                else:
                    print(f"    [ERROR] Error al enviar correo a {recipient}")
                    failed_count += 1

            except Exception as e:
                print(f"    [ERROR] Excepcion al enviar a {recipient}: {e}")
                failed_count += 1

            print()

        print("=" * 70)
        print("RESUMEN DE ENVIO")
        print("=" * 70)
        print(f"Total de correos: {len(recipients)}")
        print(f"[OK] Exitosos: {success_count}")
        print(f"[X] Fallidos: {failed_count}")
        print()

        if success_count > 0:
            print("CORREOS ENVIADOS!")
            print()
            print("Revisa las bandejas de entrada de:")
            for recipient in recipients:
                print(f"  - {recipient}")
            print()
            print("Si no los ves, revisa la carpeta de spam/correo no deseado")
        else:
            print("No se pudo enviar ningun correo")
            print()
            print("Posibles causas:")
            print("1. Contrasena de aplicacion incorrecta")
            print("2. Verificacion en 2 pasos no activada en Gmail")
            print("3. Puerto 587 bloqueado por firewall")
            print("4. Revisa los logs arriba para mas detalles")

except ImportError as e:
    print(f"[ERROR] Error al importar modulos: {e}")
    print()
    print("Asegurate de que Flask-Mail este instalado:")
    print("pip install Flask-Mail")
except Exception as e:
    print(f"[ERROR] Error inesperado: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
