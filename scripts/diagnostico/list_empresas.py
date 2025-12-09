# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect(r'D:\Mi-App-React\src\dashboard\montero.db')
cursor = conn.cursor()

cursor.execute('SELECT nit, nombre_empresa FROM empresas')
rows = cursor.fetchall()

print(f'Total empresas en BD: {len(rows)}')
for row in rows:
    print(f'  NIT: {row[0]}, Nombre: {row[1]}')

conn.close()
