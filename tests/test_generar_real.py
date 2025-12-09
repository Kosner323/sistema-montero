"""
Test del endpoint /generar con template real
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
print(" " * 15 + "TEST: GENERAR PDF CON TEMPLATE REAL (ID=3)")
print("=" * 80)
print()

with app.test_client() as client:
    # Test con template ID=3 (FORMULARIO EPS COOSALUD)
    print("Generando PDF:")
    print(f"  - Formulario ID: 3 (FORMULARIO EPS COOSALUD)")
    print(f"  - Usuario ID: 10 (yeison montero)")
    print(f"  - Empresa NIT: 999999999 (Montero Administradora)")
    print()
    
    response = client.post('/api/formularios/generar',
        data=json.dumps({
            'formulario_id': 3,
            'usuario_id': 10,
            'empresa_nit': '999999999'
        }),
        content_type='application/json'
    )
    
    print(f"Status: {response.status_code}")
    print()
    
    if response.status_code == 200:
        print(f"✓ PDF GENERADO EXITOSAMENTE")
        print(f"  Content-Type: {response.content_type}")
        print(f"  Tamaño: {len(response.data):,} bytes")
        
        # Guardar PDF de prueba
        output_path = os.path.join(os.path.dirname(__file__), "test_output.pdf")
        with open(output_path, 'wb') as f:
            f.write(response.data)
        print(f"  Guardado en: {output_path}")
    else:
        data = response.get_json()
        print(f"✗ ERROR: {data}")

print()
print("=" * 80)
print("TEST COMPLETADO")
print("=" * 80)
