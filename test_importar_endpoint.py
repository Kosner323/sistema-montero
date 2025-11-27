"""
Test del endpoint /api/formularios/importar
"""
import sys
import os
import io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from routes.formularios import bp_formularios
from werkzeug.datastructures import FileStorage

app = Flask(__name__)
app.register_blueprint(bp_formularios)

print("=" * 80)
print(" " * 20 + "TEST: ENDPOINT /api/formularios/importar")
print("=" * 80)
print()

with app.test_client() as client:
    # Test 1: Sin archivo
    print("Test 1: Enviar sin archivo")
    response = client.post('/api/formularios/importar', data={
        'nombre': 'Test Formulario'
    })
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.get_json()}")
    print(f"   ✓ Esperado: 400 BAD REQUEST" if response.status_code == 400 else "   ✗ FALLO")
    print()
    
    # Test 2: Sin nombre
    print("Test 2: Enviar archivo sin nombre")
    fake_pdf = io.BytesIO(b'%PDF-1.4 fake content')
    fake_pdf.name = 'test.pdf'
    response = client.post('/api/formularios/importar', data={
        'archivo': (fake_pdf, 'test.pdf', 'application/pdf')
    })
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.get_json()}")
    print(f"   ✓ Esperado: 400 BAD REQUEST" if response.status_code == 400 else "   ✗ FALLO")
    print()
    
    # Test 3: Con campo 'archivo' (del frontend)
    print("Test 3: Enviar con campo 'archivo' (nombre del frontend)")
    fake_pdf = io.BytesIO(b'%PDF-1.4 fake content')
    fake_pdf.name = 'test_frontend.pdf'
    response = client.post('/api/formularios/importar', data={
        'nombre': 'Test Frontend',
        'descripcion': 'Enviado con campo archivo',
        'archivo': (fake_pdf, 'test_frontend.pdf', 'application/pdf')
    })
    print(f"   Status: {response.status_code}")
    data = response.get_json()
    print(f"   Response: {data}")
    print(f"   ✓ Esperado: 201 CREATED" if response.status_code == 201 else "   ✗ FALLO")
    print()
    
    # Test 4: Con campo 'file' (estándar)
    print("Test 4: Enviar con campo 'file' (estándar)")
    fake_pdf = io.BytesIO(b'%PDF-1.4 fake content')
    fake_pdf.name = 'test_standard.pdf'
    response = client.post('/api/formularios/importar', data={
        'nombre': 'Test Standard',
        'descripcion': 'Enviado con campo file',
        'file': (fake_pdf, 'test_standard.pdf', 'application/pdf')
    })
    print(f"   Status: {response.status_code}")
    data = response.get_json()
    print(f"   Response: {data}")
    print(f"   ✓ Esperado: 201 CREATED" if response.status_code == 201 else "   ✗ FALLO")
    print()

print("=" * 80)
print("TESTS COMPLETADOS")
print("=" * 80)
