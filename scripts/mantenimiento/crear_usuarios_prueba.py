#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para agregar usuarios de prueba con fechas de nacimiento"""

import sqlite3
from datetime import datetime, timedelta
import random

# Conectar a la base de datos
conn = sqlite3.connect('data/mi_sistema.db')
cursor = conn.cursor()

# Verificar si ya hay usuarios de prueba
cursor.execute("SELECT COUNT(*) as total FROM usuarios WHERE role = 'user' OR role = 'empleado'")
total_existente = cursor.fetchone()[0]

print("=" * 80)
print("CREACIÓN DE USUARIOS DE PRUEBA CON FECHAS DE NACIMIENTO")
print("=" * 80)
print(f"\nUsuarios existentes (no admin): {total_existente}")

if total_existente > 0:
    respuesta = input("\n¿Deseas agregar más usuarios de prueba? (s/n): ")
    if respuesta.lower() != 's':
        print("Operación cancelada.")
        conn.close()
        exit()

# Datos de prueba
nombres = [
    ("Juan", "Carlos", "Pérez", "Gómez", "1985-03-15"),
    ("María", "Fernanda", "López", "Martínez", "1990-07-22"),
    ("Carlos", "Alberto", "Rodríguez", "Silva", "1988-11-30"),
    ("Ana", "Sofía", "García", "Torres", "1992-05-18"),
    ("Luis", "Eduardo", "Hernández", "Ramírez", "1987-09-08"),
    ("Patricia", "Elena", "Morales", "Castro", "1995-02-14"),
    ("Jorge", "Andrés", "Vargas", "Díaz", "1983-12-25"),
    ("Diana", "Carolina", "Sánchez", "Ortiz", "1991-06-03"),
]

usuarios_creados = 0
print("\n🔄 Creando usuarios de prueba...\n")

for i, (primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, fecha_nac) in enumerate(nombres, 1):
    numero_doc = f"100{random.randint(1000000, 9999999)}"
    
    try:
        cursor.execute("""
            INSERT INTO usuarios (
                tipoId, numeroId, primerNombre, segundoNombre, 
                primerApellido, segundoApellido, fechaNacimiento,
                correoElectronico, role, estado,
                sexoBiologico, nacionalidad,
                telefonoCelular
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'CC', numero_doc, primer_nombre, segundo_nombre,
            primer_apellido, segundo_apellido, fecha_nac,
            f"{primer_nombre.lower()}.{primer_apellido.lower()}@test.com",
            'empleado', 'Activo',
            'M' if i % 2 == 0 else 'F', 'Colombiana',
            f"300{random.randint(1000000, 9999999)}"
        ))
        
        # Calcular edad para mostrar
        nacimiento = datetime.strptime(fecha_nac, '%Y-%m-%d')
        hoy = datetime.now()
        edad = hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))
        
        print(f"✅ Usuario {i}: {primer_nombre} {primer_apellido}")
        print(f"   Documento: {numero_doc}")
        print(f"   Fecha Nacimiento: {fecha_nac}")
        print(f"   Edad: {edad} años")
        print()
        
        usuarios_creados += 1
        
    except sqlite3.IntegrityError as e:
        print(f"⚠️ Usuario {i}: Ya existe o error de duplicado - {e}")
    except Exception as e:
        print(f"❌ Usuario {i}: Error - {e}")

conn.commit()
conn.close()

print("=" * 80)
print(f"✅ PROCESO COMPLETADO - {usuarios_creados} usuarios creados exitosamente")
print("=" * 80)
print("\n💡 Ahora puedes acceder a http://localhost:5000/unificacion")
print("   y verás la columna EDAD con los valores calculados.\n")
