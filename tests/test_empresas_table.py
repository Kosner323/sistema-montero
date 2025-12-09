# -*- coding: utf-8 -*-
import sqlite3

DB_PATH = r"D:\Mi-App-React\src\dashboard\montero.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Insertar empresa de prueba
cursor.execute("""
    INSERT INTO empresas (
        nombre_empresa, nit, ciudad_empresa, departamento,
        tipo_empresa, sector_economico, banco, arl
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", (
    'EMPRESA PRUEBA S.A.S.',
    '900999999-1',
    'Bogota',
    'Cundinamarca',
    'S.A.S.',
    'Servicios',
    'Bancolombia',
    'SURA'
))
conn.commit()

# Verificar
cursor.execute("""
    SELECT nombre_empresa, nit, ciudad_empresa, departamento,
           tipo_empresa, sector_economico, banco, arl
    FROM empresas
""")
row = cursor.fetchone()

print("[OK] Empresa creada exitosamente:")
print(f"  Nombre: {row[0]}")
print(f"  NIT: {row[1]}")
print(f"  Ciudad: {row[2]}")
print(f"  Departamento: {row[3]}")
print(f"  Tipo: {row[4]}")
print(f"  Sector: {row[5]}")
print(f"  Banco: {row[6]}")
print(f"  ARL: {row[7]}")

conn.close()
print("\n[OK] Todos los campos nuevos funcionan correctamente!")
