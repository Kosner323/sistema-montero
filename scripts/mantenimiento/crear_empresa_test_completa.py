# -*- coding: utf-8 -*-
"""
Script para crear una empresa de prueba COMPLETA con todos los campos
"""
import sqlite3
from datetime import datetime

DB_PATH = r"D:\Mi-App-React\src\dashboard\montero.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 70)
print("CREANDO EMPRESA DE PRUEBA COMPLETA")
print("=" * 70)

# Datos completos de la empresa
empresa_test = {
    # Información básica
    "nombre_empresa": "EMPRESA DEMO S.A.S.",
    "tipo_identificacion_empresa": "NIT",
    "nit": "900123456-1",
    "direccion_empresa": "Calle 123 #45-67",
    "telefono_empresa": "3001234567",
    "correo_empresa": "contacto@empresademo.com",
    "ciudad_empresa": "Bogotá",

    # Ubicación
    "departamento": "Cundinamarca",

    # Información adicional
    "tipo_empresa": "S.A.S.",
    "sector_economico": "Servicios Tecnológicos",
    "num_empleados": 50,
    "fecha_constitucion": "2020-01-15",

    # Datos bancarios
    "banco": "Bancolombia",
    "tipo_cuenta": "Corriente",
    "numero_cuenta": "12345678901",

    # Seguridad social
    "arl": "III",
    "ccf": "Compensar",
    "ibc_empresa": "2500000",
    "afp_empresa": "Porvenir",
    "arl_empresa": "SURA",

    # Representante legal
    "rep_legal_nombre": "Juan Pérez García",
    "rep_legal_tipo_id": "CC",
    "rep_legal_numero_id": "1234567890",
    "rep_legal_telefono": "3109876543",
    "rep_legal_correo": "juan.perez@empresademo.com",
}

try:
    cursor.execute("""
        INSERT INTO empresas (
            nombre_empresa, tipo_identificacion_empresa, nit,
            direccion_empresa, telefono_empresa, correo_empresa,
            ciudad_empresa, departamento,
            tipo_empresa, sector_economico, num_empleados, fecha_constitucion,
            banco, tipo_cuenta, numero_cuenta,
            arl, ccf, ibc_empresa, afp_empresa, arl_empresa,
            rep_legal_nombre, rep_legal_tipo_id, rep_legal_numero_id,
            rep_legal_telefono, rep_legal_correo
        ) VALUES (
            ?, ?, ?,
            ?, ?, ?,
            ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?
        )
    """, (
        empresa_test["nombre_empresa"],
        empresa_test["tipo_identificacion_empresa"],
        empresa_test["nit"],
        empresa_test["direccion_empresa"],
        empresa_test["telefono_empresa"],
        empresa_test["correo_empresa"],
        empresa_test["ciudad_empresa"],
        empresa_test["departamento"],
        empresa_test["tipo_empresa"],
        empresa_test["sector_economico"],
        empresa_test["num_empleados"],
        empresa_test["fecha_constitucion"],
        empresa_test["banco"],
        empresa_test["tipo_cuenta"],
        empresa_test["numero_cuenta"],
        empresa_test["arl"],
        empresa_test["ccf"],
        empresa_test["ibc_empresa"],
        empresa_test["afp_empresa"],
        empresa_test["arl_empresa"],
        empresa_test["rep_legal_nombre"],
        empresa_test["rep_legal_tipo_id"],
        empresa_test["rep_legal_numero_id"],
        empresa_test["rep_legal_telefono"],
        empresa_test["rep_legal_correo"]
    ))

    conn.commit()
    empresa_id = cursor.lastrowid

    print(f"\n[OK] Empresa creada exitosamente con ID: {empresa_id}")
    print("\nDatos insertados:")
    print(f"  Nombre: {empresa_test['nombre_empresa']}")
    print(f"  NIT: {empresa_test['nit']}")
    print(f"  Dirección: {empresa_test['direccion_empresa']}")
    print(f"  Teléfono: {empresa_test['telefono_empresa']}")
    print(f"  Correo: {empresa_test['correo_empresa']}")
    print(f"  Ciudad: {empresa_test['ciudad_empresa']}")
    print(f"  Departamento: {empresa_test['departamento']}")
    print(f"  Tipo: {empresa_test['tipo_empresa']}")
    print(f"  Sector: {empresa_test['sector_economico']}")
    print(f"  Empleados: {empresa_test['num_empleados']}")
    print(f"  Fecha Constitución: {empresa_test['fecha_constitucion']}")
    print(f"  Banco: {empresa_test['banco']}")
    print(f"  Tipo Cuenta: {empresa_test['tipo_cuenta']}")
    print(f"  Número Cuenta: {empresa_test['numero_cuenta']}")
    print(f"  ARL: {empresa_test['arl']}")
    print(f"  CCF: {empresa_test['ccf']}")
    print(f"  IBC: {empresa_test['ibc_empresa']}")
    print(f"  AFP: {empresa_test['afp_empresa']}")
    print(f"  ARL Empresa: {empresa_test['arl_empresa']}")
    print(f"  Rep Legal: {empresa_test['rep_legal_nombre']}")
    print(f"  Rep Legal Tipo ID: {empresa_test['rep_legal_tipo_id']}")
    print(f"  Rep Legal Número ID: {empresa_test['rep_legal_numero_id']}")
    print(f"  Rep Legal Teléfono: {empresa_test['rep_legal_telefono']}")
    print(f"  Rep Legal Correo: {empresa_test['rep_legal_correo']}")

    print("\n" + "=" * 70)
    print("[OK] Ahora puedes editar esta empresa en:")
    print("http://localhost:5000/empresas/ingresar?edit_nit=900123456-1")
    print("=" * 70)

except Exception as e:
    print(f"\n[ERROR] Error al crear empresa: {e}")
    import traceback
    traceback.print_exc()
finally:
    conn.close()
