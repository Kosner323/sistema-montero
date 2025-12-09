"""
Test del endpoint /api/formularios/generar con datos reales
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from routes.formularios import bp_formularios
import json

app = Flask(__name__)
app.register_blueprint(bp_formularios)

print("=" * 80)
print(" " * 20 + "TEST: ENDPOINT /api/formularios/generar")
print("=" * 80)
print()

with app.test_client() as client:
    # Test 1: Usuario que existe (ID interno = 10, que corresponde a yeison montero)
    print("Test 1: Generar PDF con usuario ID=10 (yeison montero)")
    response = client.post('/api/formularios/generar',
        data=json.dumps({
            'usuario_id': 10,
            'empresa_nit': '999999999'
        }),
        content_type='application/json'
    )
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"   Content-Type: {response.content_type}")
        print(f"   Tamaño PDF: {len(response.data)} bytes")
        print(f"   ✓ PDF generado exitosamente")
    else:
        data = response.get_json()
        print(f"   Response: {data}")
        print(f"   ✗ FALLO")
    print()
    
    # Test 2: Usuario que NO existe
    print("Test 2: Generar PDF con usuario inexistente (ID=99999)")
    response = client.post('/api/formularios/generar',
        data=json.dumps({
            'usuario_id': 99999,
            'empresa_nit': '999999999'
        }),
        content_type='application/json'
    )
    print(f"   Status: {response.status_code}")
    data = response.get_json()
    print(f"   Response: {data}")
    print(f"   ✓ Validación correcta (404 esperado)" if response.status_code == 404 else "   ✗ FALLO")
    print()
    
    # Test 3: Empresa que NO existe
    print("Test 3: Generar PDF con empresa inexistente")
    response = client.post('/api/formularios/generar',
        data=json.dumps({
            'usuario_id': 10,
            'empresa_nit': '999999999999'
        }),
        content_type='application/json'
    )
    print(f"   Status: {response.status_code}")
    data = response.get_json()
    print(f"   Response: {data}")
    print(f"   ✓ Validación correcta (404 esperado)" if response.status_code == 404 else "   ✗ FALLO")
    print()

print("=" * 80)
print("TESTS COMPLETADOS")
print("=" * 80)
