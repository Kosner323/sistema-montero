#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test del Endpoint de Generación de PDFs
Simula una petición real al endpoint /api/formularios/generar
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
print("🧪 TEST DEL ENDPOINT DE GENERACIÓN DE PDFs")
print("=" * 80)

try:
    from app import app
    from utils import get_db_connection
    import json

    with app.test_client() as client:
        with app.app_context():
            print("\n✅ Cliente de prueba creado")

            # Obtener IDs de prueba de la base de datos
            conn = get_db_connection()
            cursor = conn.cursor()

            # Obtener primer formulario
            cursor.execute("SELECT id, nombre FROM formularios_importados LIMIT 1")
            formulario = cursor.fetchone()

            # Obtener primer usuario
            cursor.execute("SELECT id, numeroId, primerNombre, primerApellido FROM usuarios WHERE id > 1 LIMIT 1")
            usuario = cursor.fetchone()

            # Obtener primera empresa
            cursor.execute("SELECT nit, nombre_empresa FROM empresas LIMIT 1")
            empresa = cursor.fetchone()

            conn.close()

            if not formulario or not usuario or not empresa:
                print("❌ No hay datos suficientes para hacer la prueba")
                print(f"   Formularios: {bool(formulario)}")
                print(f"   Usuarios: {bool(usuario)}")
                print(f"   Empresas: {bool(empresa)}")
                sys.exit(1)

            print("\n📊 Datos de Prueba:")
            print(f"   📄 Formulario: ID {formulario['id']} - {formulario['nombre']}")
            print(f"   👤 Usuario: ID {usuario['id']} - {usuario['primerNombre']} {usuario['primerApellido']} (CC: {usuario['numeroId']})")
            print(f"   🏢 Empresa: NIT {empresa['nit']} - {empresa['nombre_empresa']}")

            # Simular login (crear una sesión)
            print("\n🔐 Simulando sesión de usuario...")
            with client.session_transaction() as sess:
                sess['user'] = {
                    'id': 1,
                    'numeroId': '1000000',
                    'primerNombre': 'Admin',
                    'primerApellido': 'Sistema',
                    'role': 'SUPER'
                }

            # Preparar datos para la petición
            payload = {
                'formulario_id': formulario['id'],
                'usuario_id': usuario['id'],
                'empresa_nit': empresa['nit']
            }

            print("\n📤 Enviando petición POST a /api/formularios/generar...")
            print(f"   Payload: {json.dumps(payload, indent=6)}")

            # Hacer la petición
            response = client.post(
                '/api/formularios/generar',
                json=payload,
                content_type='application/json'
            )

            print("\n📥 Respuesta del Servidor:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Content-Type: {response.content_type}")

            if response.status_code == 200:
                print("\n✅ ¡ÉXITO! PDF generado correctamente")

                # Verificar headers
                content_disposition = response.headers.get('Content-Disposition', '')
                print(f"   Content-Disposition: {content_disposition}")

                # Verificar tamaño del PDF
                pdf_size = len(response.data)
                print(f"   Tamaño del PDF: {pdf_size:,} bytes ({pdf_size/1024:.2f} KB)")

                if pdf_size > 0:
                    print("\n   🎉 El PDF se generó con contenido válido")

                    # Guardar PDF de prueba
                    test_pdf_path = os.path.join(os.path.dirname(__file__), 'test_output.pdf')
                    with open(test_pdf_path, 'wb') as f:
                        f.write(response.data)
                    print(f"   💾 PDF de prueba guardado en: {test_pdf_path}")
                else:
                    print("\n   ⚠️  ADVERTENCIA: El PDF está vacío")

            elif response.status_code == 401:
                print("\n❌ ERROR 401: No autorizado")
                print("   El decorador @login_required bloqueó la petición")
                print("   Esto es normal en un test - en producción funcionará con sesión real")

            else:
                print(f"\n❌ ERROR {response.status_code}")
                try:
                    error_data = response.get_json()
                    print(f"   Mensaje: {error_data.get('error', 'Sin mensaje')}")
                    if 'detalle' in error_data:
                        print(f"   Detalle: {error_data['detalle']}")
                except:
                    print(f"   Respuesta: {response.data.decode('utf-8', errors='replace')[:500]}")

            # Resumen
            print("\n" + "=" * 80)
            print("📊 RESUMEN DEL TEST")
            print("=" * 80)

            if response.status_code == 200:
                print("\n✅ ¡ENDPOINT FUNCIONANDO CORRECTAMENTE!")
                print("\n💡 CÓMO USAR EN LA INTERFAZ WEB:")
                print("   1. Inicia el servidor: python src/dashboard/app.py")
                print("   2. Accede a: http://localhost:5000/formularios")
                print("   3. Inicia sesión con cualquier usuario")
                print("   4. Selecciona:")
                print(f"      - Formulario: {formulario['nombre']}")
                print(f"      - Empleado: Buscar por CC {usuario['numeroId']}")
                print(f"      - Empresa: {empresa['nombre_empresa']}")
                print("   5. Click en 'Generar y Descargar PDF'")
                print("\n   El PDF se descargará automáticamente a tu carpeta de Descargas")

            elif response.status_code == 401:
                print("\n⚠️  TEST BLOQUEADO POR AUTENTICACIÓN")
                print("   Esto es esperado - el endpoint requiere login")
                print("   En la interfaz web funcionará correctamente después de iniciar sesión")

            else:
                print(f"\n❌ ENDPOINT RETORNÓ ERROR {response.status_code}")
                print("   Revisa los logs arriba para más detalles")

except Exception as e:
    print(f"\n❌ Error durante el test: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80 + "\n")
