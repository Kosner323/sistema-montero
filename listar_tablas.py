import sqlite3

conn = sqlite3.connect('data/mi_sistema.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()
print("\nTablas en mi_sistema.db:")
print("=" * 40)
for table in tables:
    print(f"  - {table[0]}")
print("=" * 40)
print(f"\nTotal: {len(tables)} tablas")
conn.close()
