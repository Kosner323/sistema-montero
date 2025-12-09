# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect(r'D:\Mi-App-React\src\dashboard\montero.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT nombre_empresa, nit, departamento, correo_empresa,
           rep_legal_telefono, rep_legal_correo, banco, tipo_empresa
    FROM empresas
    WHERE nit LIKE '900123456%'
""")

rows = cursor.fetchall()
if rows:
    print("Datos en BD para empresa 900123456:")
    for row in rows:
        print(f"  Nombre: {row[0]}")
        print(f"  NIT: {row[1]}")
        print(f"  Departamento: {row[2]}")
        print(f"  Correo: {row[3]}")
        print(f"  Tel Rep Legal: {row[4]}")
        print(f"  Correo Rep Legal: {row[5]}")
        print(f"  Banco: {row[6]}")
        print(f"  Tipo Empresa: {row[7]}")
else:
    print("No se encontro ninguna empresa con NIT 900123456*")

conn.close()
