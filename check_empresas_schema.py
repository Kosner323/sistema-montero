#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check empresas table schema"""

import sqlite3

DB_PATH = r"d:\Mi-App-React\data\mi_sistema.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get table info
cursor.execute("PRAGMA table_info(empresas)")
columns = cursor.fetchall()

print("\nEstructura de la tabla 'empresas':")
print("="*60)
for col in columns:
    print(f"{col[1]:30} {col[2]:15} {'NOT NULL' if col[3] else 'NULL'}")
print("="*60 + "\n")

conn.close()
