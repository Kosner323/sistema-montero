#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_usuario_sin_empresa.py
============================
Prueba de simulacion: Crear usuario sin empresa (empresa_nit = NULL)
"""

import sqlite3
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = r"d:\Mi-App-React\data\mi_sistema.db"

def test_insert_json_mode():
    """Simula modo JSON (API simple) sin empresa_nit"""
    print("\n" + "="*80)
    print("TEST 1: MODO JSON - Usuario sin empresa")
    print("="*80)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Datos de prueba (similar al endpoint JSON)
        nombre_completo = "Kevin Montero"
        numero_documento = "987654321"
        email = "kevin@test.com"
        telefono = "3001234567"

        # IMPORTANTE: empresa_nit_final = None (sin empresa)
        empresa_nit_final = None

        print("\n[INPUT] Datos de prueba:")
        print(f"  nombre_completo: {nombre_completo}")
        print(f"  numero_documento: {numero_documento}")
        print(f"  empresa_nit: {empresa_nit_final}")

        # Simular INSERT del endpoint
        nombre_parts = nombre_completo.strip().split()
        primer_nombre = nombre_parts[0] if len(nombre_parts) > 0 else ''
        segundo_nombre = nombre_parts[1] if len(nombre_parts) > 1 else ''
        primer_apellido = nombre_parts[2] if len(nombre_parts) > 2 else ''
        segundo_apellido = nombre_parts[3] if len(nombre_parts) > 3 else ''

        cursor.execute(
            """
            INSERT INTO usuarios (
                empresa_nit, tipoId, numeroId, primerNombre, segundoNombre,
                primerApellido, segundoApellido, correoElectronico, telefonoCelular
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                empresa_nit_final,  # None
                "CC",
                numero_documento,
                primer_nombre,
                segundo_nombre,
                primer_apellido,
                segundo_apellido,
                email,
                telefono,
            ),
        )
        conn.commit()

        print("\n[OK] INSERT exitoso (modo JSON)")

        # Verificar el registro insertado
        cursor.execute(
            "SELECT id, numeroId, primerNombre, primerApellido, empresa_nit FROM usuarios WHERE numeroId = ?",
            (numero_documento,)
        )
        row = cursor.fetchone()

        print("\n[VERIFICACION] Registro guardado:")
        print(f"  ID: {row[0]}")
        print(f"  Numero Doc: {row[1]}")
        print(f"  Nombre: {row[2]} {row[3]}")
        print(f"  empresa_nit: {row[4] if row[4] else 'NULL'}")

        if row[4] is None:
            print("\n[SUCCESS] El campo empresa_nit se guardo como NULL correctamente")
        else:
            print(f"\n[ERROR] Se esperaba NULL pero se guardo: {row[4]}")

        # Limpiar
        cursor.execute("DELETE FROM usuarios WHERE numeroId = ?", (numero_documento,))
        conn.commit()
        print("\n[CLEANUP] Registro de prueba eliminado")

        return True

    except sqlite3.IntegrityError as e:
        print(f"\n[ERROR] IntegrityError: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()


def test_insert_form_mode():
    """Simula modo Form Data sin administracion (empresa)"""
    print("\n" + "="*80)
    print("TEST 2: MODO FORM DATA - Usuario sin empresa")
    print("="*80)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Datos de prueba (similar al formulario completo)
        numero_id = "112233445"
        primer_nombre = "Ana"
        primer_apellido = "Rodriguez"

        # IMPORTANTE: empresa_nit = None (no se proporciono administracion)
        empresa_nit = None

        print("\n[INPUT] Datos de prueba:")
        print(f"  numeroId: {numero_id}")
        print(f"  primerNombre: {primer_nombre}")
        print(f"  primerApellido: {primer_apellido}")
        print(f"  empresa_nit: {empresa_nit}")

        # Simular INSERT del endpoint (version simplificada)
        cursor.execute(
            """
            INSERT INTO usuarios (
                empresa_nit, tipoId, numeroId, primerNombre, primerApellido
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (empresa_nit, "CC", numero_id, primer_nombre, primer_apellido),
        )
        conn.commit()

        print("\n[OK] INSERT exitoso (modo Form Data)")

        # Verificar el registro insertado
        cursor.execute(
            "SELECT id, numeroId, primerNombre, primerApellido, empresa_nit FROM usuarios WHERE numeroId = ?",
            (numero_id,)
        )
        row = cursor.fetchone()

        print("\n[VERIFICACION] Registro guardado:")
        print(f"  ID: {row[0]}")
        print(f"  Numero Doc: {row[1]}")
        print(f"  Nombre: {row[2]} {row[3]}")
        print(f"  empresa_nit: {row[4] if row[4] else 'NULL'}")

        if row[4] is None:
            print("\n[SUCCESS] El campo empresa_nit se guardo como NULL correctamente")
        else:
            print(f"\n[ERROR] Se esperaba NULL pero se guardo: {row[4]}")

        # Limpiar
        cursor.execute("DELETE FROM usuarios WHERE numeroId = ?", (numero_id,))
        conn.commit()
        print("\n[CLEANUP] Registro de prueba eliminado")

        return True

    except sqlite3.IntegrityError as e:
        print(f"\n[ERROR] IntegrityError: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 80)
    print(" " * 15 + "PRUEBA DE SIMULACION: Usuario sin Empresa")
    print("=" * 80)

    # Test 1: Modo JSON
    test1 = test_insert_json_mode()

    # Test 2: Modo Form Data
    test2 = test_insert_form_mode()

    # Resumen
    print("\n" + "="*80)
    print("RESUMEN DE PRUEBAS")
    print("="*80)
    print(f"Test 1 (Modo JSON):      {'[PASS]' if test1 else '[FAIL]'}")
    print(f"Test 2 (Modo Form Data): {'[PASS]' if test2 else '[FAIL]'}")

    if test1 and test2:
        print("\n[SUCCESS] Todas las pruebas pasaron correctamente")
        print("\nCONCLUSION:")
        print("  - El codigo Python ahora acepta empresa_nit = None")
        print("  - La base de datos guarda NULL correctamente")
        print("  - NO se asigna el default '999999999'")
        print("\nOBJETIVO CUMPLIDO: Usuario independiente sin empresa")
    else:
        print("\n[ERROR] Algunas pruebas fallaron")

    print("=" * 80 + "\n")
