"""
Script de prueba para los endpoints del módulo de formularios.
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routes.formularios import bp_formularios
from flask import Flask

app = Flask(__name__)
app.register_blueprint(bp_formularios)

print("=" * 80)
print(" " * 25 + "VERIFICACIÓN DE RUTAS - MÓDULO FORMULARIOS")
print("=" * 80)
print()

# Obtener todas las rutas del blueprint
rutas = []
for rule in app.url_map.iter_rules():
    if rule.endpoint.startswith('bp_formularios'):
        rutas.append({
            'ruta': rule.rule,
            'metodos': ', '.join(rule.methods - {'HEAD', 'OPTIONS'}),
            'endpoint': rule.endpoint
        })

# Ordenar por ruta
rutas.sort(key=lambda x: x['ruta'])

print(f"Total de rutas registradas: {len(rutas)}")
print()
print("-" * 80)
print(f"{'RUTA':<50} {'MÉTODOS':<15} {'ENDPOINT'}")
print("-" * 80)

for ruta in rutas:
    print(f"{ruta['ruta']:<50} {ruta['metodos']:<15} {ruta['endpoint']}")

print("-" * 80)
print()

# Verificar endpoints críticos
endpoints_requeridos = [
    ('GET', '/api/formularios'),
    ('POST', '/api/formularios/generar'),
    ('POST', '/api/formularios/importar'),
    ('DELETE', '/api/formularios/<int:formulario_id>'),
    ('GET', '/api/formularios/diagnostico'),
]

print("VERIFICACIÓN DE ENDPOINTS CRÍTICOS:")
print()

for metodo, ruta_esperada in endpoints_requeridos:
    encontrado = False
    for ruta in rutas:
        if ruta_esperada in ruta['ruta'] or ruta['ruta'] in ruta_esperada:
            if metodo in ruta['metodos']:
                print(f"✓ {metodo:7} {ruta_esperada:50} - OK")
                encontrado = True
                break
    
    if not encontrado:
        print(f"✗ {metodo:7} {ruta_esperada:50} - FALTA")

print()
print("=" * 80)
print("DIAGNÓSTICO COMPLETADO")
print("=" * 80)
