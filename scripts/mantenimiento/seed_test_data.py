#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
seed_test_data.py
=================
Seed database with minimal test data for impuestos automation testing
"""

import sqlite3
import sys
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = r"d:\Mi-App-React\data\mi_sistema.db"


def seed_test_data():
    """
    Seed database with minimal test data:
    - 1 Empresa de prueba
    - 1 Usuario asociado
    """
    print("\n" + "="*80)
    print("SEED: Creando datos de prueba para testing")
    print("="*80)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Verificar si ya existe empresa de prueba
        cursor.execute("SELECT nit, nombre_empresa FROM empresas WHERE nit = '900123456'")
        empresa_existente = cursor.fetchone()

        if empresa_existente:
            print(f"\n[OK] Empresa de prueba ya existe: {empresa_existente[1]} (NIT: {empresa_existente[0]})")
        else:
            # Crear empresa de prueba
            print("\n[CREANDO] Empresa de prueba...")
            cursor.execute("""
                INSERT INTO empresas (
                    nit, nombre_empresa, direccion_empresa, telefono_empresa, correo_empresa,
                    rep_legal_nombre, tipo_identificacion_empresa, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                '900123456',
                'EMPRESA PRUEBA LTDA',
                'Calle 123 #45-67',
                '3001234567',
                'prueba@empresa.com',
                'Juan Pérez',
                'NIT',
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            conn.commit()
            print(f"   [OK] Empresa creada: EMPRESA PRUEBA LTDA (NIT: 900123456)")

        # Verificar si ya existe usuario de prueba
        cursor.execute("SELECT numeroId, primerNombre, primerApellido FROM usuarios WHERE numeroId = '1234567890'")
        usuario_existente = cursor.fetchone()

        if usuario_existente:
            print(f"\n[OK] Usuario de prueba ya existe: {usuario_existente[1]} {usuario_existente[2]} (ID: {usuario_existente[0]})")
        else:
            # Crear usuario de prueba
            print("\n[CREANDO] Usuario de prueba...")
            cursor.execute("""
                INSERT INTO usuarios (
                    empresa_nit, tipoId, numeroId, primerNombre, primerApellido,
                    correoElectronico, telefonoCelular, administracion, fechaIngreso, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                '900123456',
                'CC',
                '1234567890',
                'Carlos',
                'Prueba',
                'carlos.prueba@empresa.com',
                '3009876543',
                'EMPRESA PRUEBA LTDA',
                datetime.now().strftime("%Y-%m-%d"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            conn.commit()
            print(f"   [OK] Usuario creado: Carlos Prueba (CC: 1234567890)")

        print("\n" + "="*80)
        print("[SUCCESS] Datos de prueba listos")
        print("="*80)
        print("\nDatos disponibles:")
        print("  - Empresa: EMPRESA PRUEBA LTDA (NIT: 900123456)")
        print("  - Usuario: Carlos Prueba (CC: 1234567890)")
        print("\nAhora puedes ejecutar los tests de automatizacion.")
        print("="*80 + "\n")

        return True

    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        conn.close()


if __name__ == "__main__":
    seed_test_data()
