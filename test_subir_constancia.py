"""
Test del endpoint /subir_constancia con la nueva nomenclatura
"""
import sys
import os
import io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from routes.formularios import bp_formularios

app = Flask(__name__)
app.register_blueprint(bp_formularios)

print("=" * 80)
print(" " * 15 + "TEST: ENDPOINT /api/formularios/subir_constancia")
print("=" * 80)
print()

with app.test_client() as client:
    # Test 1: Subir constancia ARL para usuario con empresa
    print("Test 1: Subir constancia ARL (nomenclatura: arl noviembre 2025.pdf)")
    print(f"  - Usuario ID: 10")
    print(f"  - Tipo: ARL")
    print()
    
    # Crear PDF fake
    fake_pdf = io.BytesIO(b'%PDF-1.4 contenido de prueba')
    fake_pdf.name = 'constancia_arl.pdf'
    
    response = client.post('/api/formularios/subir_constancia',
        data={
            'usuario_id': '10',
            'tipo_entidad': 'ARL',
            'archivo': (fake_pdf, 'constancia_arl.pdf', 'application/pdf')
        },
        content_type='multipart/form-data'
    )
    
    print(f"Status: {response.status_code}")
    data = response.get_json()
    print(f"Response:")
    for key, value in data.items():
        print(f"  {key}: {value}")
    
    if response.status_code == 201:
        print(f"\nOK: Constancia subida exitosamente")
        print(f"Nombre de archivo: {data.get('nombre_archivo')}")
        print(f"Mes/Anio: {data.get('mes_anio')}")
    else:
        print(f"\nERROR: {data.get('error')}")
    
    print()
    print("-" * 80)
    print()
    
    # Test 2: Usuario sin empresa (debe fallar)
    print("Test 2: Usuario sin empresa asignada (debe fallar con 400)")
    
    # Primero necesitamos un usuario sin empresa
    # Usaremos un ID que probablemente no tenga empresa
    
    fake_pdf2 = io.BytesIO(b'%PDF-1.4 otro contenido')
    fake_pdf2.name = 'constancia_eps.pdf'
    
    response = client.post('/api/formularios/subir_constancia',
        data={
            'usuario_id': '999',  # Usuario probablemente inexistente
            'tipo_entidad': 'EPS',
            'archivo': (fake_pdf2, 'constancia_eps.pdf', 'application/pdf')
        },
        content_type='multipart/form-data'
    )
    
    print(f"Status: {response.status_code}")
    data = response.get_json()
    print(f"Response: {data}")
    
    if response.status_code == 404:
        print(f"\nOK: Validacion correcta (404 esperado)")
    else:
        print(f"\nAVISO: Status inesperado")

print()
print("=" * 80)
print("TESTS COMPLETADOS")
print("=" * 80)
