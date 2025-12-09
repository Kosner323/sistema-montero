#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3

DB_PATH = r"d:\Mi-App-React\data\mi_sistema.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get table structure
cursor.execute("PRAGMA table_info(usuarios)")
columns = cursor.fetchall()

print("Estructura de la tabla usuarios:")
print("="*80)
for col in columns:
    print(f"{col[0]:3d}. {col[1]:30s} {col[2]:15s} NOT NULL={col[3]} DEFAULT={col[4]}")

print(f"\nTotal de columnas: {len(columns)}")

conn.close()
