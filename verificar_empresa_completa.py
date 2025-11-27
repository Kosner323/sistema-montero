# -*- coding: utf-8 -*-
import sqlite3
import json

conn = sqlite3.connect(r'D:\Mi-App-React\src\dashboard\montero.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Buscar la empresa con NIT 900123456
cursor.execute("SELECT * FROM empresas WHERE nit LIKE '900123456%'")
empresa = cursor.fetchone()

if empresa:
    print("EMPRESA ENCONTRADA:")
    print("="*70)

    # Convertir a diccionario para mejor visualización
    empresa_dict = dict(empresa)

    # Mostrar campos básicos
    print(f"\n[BASICOS]")
    print(f"  ID: {empresa_dict.get('id')}")
    print(f"  Nombre: {empresa_dict.get('nombre_empresa')}")
    print(f"  NIT: {empresa_dict.get('nit')}")
    print(f"  Direccion: {empresa_dict.get('direccion_empresa')}")
    print(f"  Telefono: {empresa_dict.get('telefono_empresa')}")
    print(f"  Correo: {empresa_dict.get('correo_empresa')}")
    print(f"  Ciudad: {empresa_dict.get('ciudad_empresa')}")
    print(f"  Departamento: {empresa_dict.get('departamento')}")

    # Información adicional
    print(f"\n[INFORMACION ADICIONAL]")
    print(f"  Tipo Empresa: {empresa_dict.get('tipo_empresa')}")
    print(f"  Sector: {empresa_dict.get('sector_economico')}")
    print(f"  Empleados: {empresa_dict.get('num_empleados')}")
    print(f"  Fecha Constitucion: {empresa_dict.get('fecha_constitucion')}")

    # Datos bancarios
    print(f"\n[BANCARIOS]")
    print(f"  Banco: {empresa_dict.get('banco')}")
    print(f"  Tipo Cuenta: {empresa_dict.get('tipo_cuenta')}")
    print(f"  Numero Cuenta: {empresa_dict.get('numero_cuenta')}")

    # Seguridad social
    print(f"\n[SEGURIDAD SOCIAL]")
    print(f"  ARL: {empresa_dict.get('arl')}")
    print(f"  CCF: {empresa_dict.get('ccf')}")
    print(f"  IBC: {empresa_dict.get('ibc_empresa')}")
    print(f"  AFP: {empresa_dict.get('afp_empresa')}")
    print(f"  ARL Empresa: {empresa_dict.get('arl_empresa')}")

    # Rep legal
    print(f"\n[REPRESENTANTE LEGAL]")
    print(f"  Nombre: {empresa_dict.get('rep_legal_nombre')}")
    print(f"  Tipo ID: {empresa_dict.get('rep_legal_tipo_id')}")
    print(f"  Numero ID: {empresa_dict.get('rep_legal_numero_id')}")
    print(f"  Telefono: {empresa_dict.get('rep_legal_telefono')}")
    print(f"  Correo: {empresa_dict.get('rep_legal_correo')}")

    # Contar campos con datos vs vacíos
    campos_con_datos = sum(1 for k, v in empresa_dict.items() if v is not None and v != '')
    campos_vacios = sum(1 for k, v in empresa_dict.items() if v is None or v == '')

    print(f"\n[RESUMEN]")
    print(f"  Campos con datos: {campos_con_datos}")
    print(f"  Campos vacios: {campos_vacios}")
    print(f"  Total campos: {len(empresa_dict)}")

else:
    print("NO SE ENCONTRO NINGUNA EMPRESA CON NIT 900123456*")
    print("\nListando todas las empresas en la BD:")
    cursor.execute("SELECT id, nit, nombre_empresa FROM empresas")
    empresas = cursor.fetchall()
    if empresas:
        for emp in empresas:
            print(f"  - ID: {emp['id']}, NIT: {emp['nit']}, Nombre: {emp['nombre_empresa']}")
    else:
        print("  [La base de datos esta vacia]")

conn.close()
