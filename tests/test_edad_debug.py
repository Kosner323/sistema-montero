#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script de debug para verificar el cálculo de edad"""

import sqlite3
from datetime import datetime

# Conectar a la base de datos
conn = sqlite3.connect('data/mi_sistema.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Obtener primeros 3 usuarios no admin
query = """
SELECT id, numeroId, primerNombre, primerApellido, fechaNacimiento 
FROM usuarios 
WHERE LOWER(role) NOT IN ('admin', 'superadmin', 'administrador', 'super')
LIMIT 5
"""

usuarios = cursor.fetchall()

print("=" * 80)
print("VERIFICACIÓN DE DATOS DE USUARIOS Y CÁLCULO DE EDAD")
print("=" * 80)

if not usuarios:
    print("\n⚠️ No hay usuarios en la base de datos (excluyendo administradores)")
else:
    print(f"\n✅ Se encontraron {len(usuarios)} usuarios\n")
    
    for usuario in usuarios:
        print(f"Usuario ID: {usuario['id']}")
        print(f"  Documento: {usuario['numeroId']}")
        print(f"  Nombre: {usuario['primerNombre']} {usuario['primerApellido']}")
        print(f"  Fecha Nacimiento: {usuario['fechaNacimiento']}")
        
        # Calcular edad
        fecha_nac = usuario['fechaNacimiento']
        if fecha_nac:
            try:
                # Probar diferentes formatos
                for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d']:
                    try:
                        nacimiento = datetime.strptime(fecha_nac, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    print(f"  ❌ Edad: No se pudo parsear la fecha '{fecha_nac}'")
                    print()
                    continue
                
                hoy = datetime.now()
                edad = hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))
                print(f"  ✅ Edad calculada: {edad} años")
            except Exception as e:
                print(f"  ❌ Error calculando edad: {e}")
        else:
            print(f"  ⚠️ Edad: N/A (sin fecha de nacimiento)")
        
        print()

conn.close()

print("=" * 80)
print("PRUEBA COMPLETADA")
print("=" * 80)
