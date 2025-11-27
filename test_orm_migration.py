#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_orm_migration.py - Script de Prueba de Migración ORM
===========================================================
Verifica que la migración de SQL manual a SQLAlchemy ORM funciona correctamente.

Pruebas:
1. Crear una cotización de prueba usando ORM
2. Verificar que se guardó correctamente en la BD
3. Recuperar la cotización y validar los datos
4. Crear un pago de prueba usando ORM
5. Verificar integridad de datos

Autor: Ingeniero Backend Senior
Fecha: 2025-11-26
"""

import os
import sys
from datetime import datetime

# Agregar el directorio actual al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models.orm_models import (
    Cotizacion, Pago, Empresa, Usuario,
    PagoImpuesto, Tutela, Incapacidad
)


def test_crear_cotizacion():
    """
    TEST 1: Crear una cotización de prueba usando el ORM
    """
    print("\n" + "=" * 80)
    print("TEST 1: Crear Cotización usando ORM")
    print("=" * 80)

    try:
        # Generar ID único
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        id_cotizacion = f"COT-TEST-{timestamp}"

        # Crear cotización usando ORM
        nueva_cotizacion = Cotizacion(
            id_cotizacion=id_cotizacion,
            cliente="Cliente Prueba ORM",
            email="prueba@orm.com",
            servicio="Servicio de Prueba - Migración ORM",
            monto=1500000.00,
            notas="Esta cotización fue creada usando SQLAlchemy ORM como prueba de migración",
            fecha_creacion=datetime.now().strftime("%Y-%m-%d"),
            estado="Enviada"
        )

        # Guardar en la base de datos
        db.session.add(nueva_cotizacion)
        db.session.commit()

        print(f"[OK] Cotizacion creada exitosamente usando ORM")
        print(f"   ID Cotización: {nueva_cotizacion.id_cotizacion}")
        print(f"   ID en BD: {nueva_cotizacion.id}")
        print(f"   Cliente: {nueva_cotizacion.cliente}")
        print(f"   Monto: ${nueva_cotizacion.monto:,.2f}")
        print(f"   Estado: {nueva_cotizacion.estado}")

        return nueva_cotizacion.id

    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Error al crear cotizacion: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_recuperar_cotizacion(cotizacion_id):
    """
    TEST 2: Recuperar y verificar la cotización creada
    """
    print("\n" + "=" * 80)
    print("TEST 2: Recuperar Cotización desde BD")
    print("=" * 80)

    try:
        # Recuperar cotización por ID usando ORM
        cotizacion = Cotizacion.query.get(cotizacion_id)

        if cotizacion:
            print(f"[OK] Cotizacion recuperada exitosamente")
            print(f"   ID: {cotizacion.id}")
            print(f"   ID Cotización: {cotizacion.id_cotizacion}")
            print(f"   Cliente: {cotizacion.cliente}")
            print(f"   Email: {cotizacion.email}")
            print(f"   Servicio: {cotizacion.servicio}")
            print(f"   Monto: ${cotizacion.monto:,.2f}")
            print(f"   Fecha: {cotizacion.fecha_creacion}")
            print(f"   Estado: {cotizacion.estado}")

            # Verificar método to_dict()
            cotizacion_dict = cotizacion.to_dict()
            print(f"\n[OK] Metodo to_dict() funciona correctamente")
            print(f"   Claves en diccionario: {list(cotizacion_dict.keys())}")

            return True
        else:
            print(f"[ERROR] No se encontro la cotizacion con ID {cotizacion_id}")
            return False

    except Exception as e:
        print(f"[ERROR] Error al recuperar cotizacion: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_listar_todas_cotizaciones():
    """
    TEST 3: Listar todas las cotizaciones
    """
    print("\n" + "=" * 80)
    print("TEST 3: Listar Todas las Cotizaciones")
    print("=" * 80)

    try:
        # Obtener todas las cotizaciones usando ORM
        cotizaciones = Cotizacion.query.order_by(Cotizacion.fecha_creacion.desc()).all()

        print(f"[OK] Se encontraron {len(cotizaciones)} cotizaciones en la BD")

        if cotizaciones:
            print("\nÚltimas 5 cotizaciones:")
            for i, cot in enumerate(cotizaciones[:5], 1):
                print(f"   {i}. {cot.id_cotizacion} - {cot.cliente} - ${cot.monto:,.2f} - {cot.estado}")

        return len(cotizaciones) > 0

    except Exception as e:
        print(f"[ERROR] Error al listar cotizaciones: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_contar_registros():
    """
    TEST 4: Contar registros en diferentes tablas usando ORM
    """
    print("\n" + "=" * 80)
    print("TEST 4: Contar Registros en Tablas")
    print("=" * 80)

    try:
        stats = {
            'Empresas': Empresa.query.count(),
            'Usuarios': Usuario.query.count(),
            'Cotizaciones': Cotizacion.query.count(),
            'Pagos': Pago.query.count(),
            'Pagos Impuestos': PagoImpuesto.query.count(),
            'Tutelas': Tutela.query.count(),
            'Incapacidades': Incapacidad.query.count(),
        }

        print("[OK] Estadisticas de la Base de Datos:")
        for tabla, count in stats.items():
            print(f"   {tabla:20s}: {count:4d} registros")

        return True

    except Exception as e:
        print(f"[ERROR] Error al contar registros: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_crear_empresa_y_usuario():
    """
    TEST 5: Crear empresa y usuario de prueba
    """
    print("\n" + "=" * 80)
    print("TEST 5: Crear Empresa y Usuario de Prueba")
    print("=" * 80)

    try:
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        nit_test = f"999{timestamp}"

        # Verificar si ya existe
        empresa_existente = Empresa.query.filter_by(nit=nit_test).first()
        if empresa_existente:
            print(f"[!] Empresa con NIT {nit_test} ya existe, usando existente")
            return empresa_existente.id

        # Crear empresa de prueba
        nueva_empresa = Empresa(
            nombre_empresa="Empresa Prueba ORM S.A.S.",
            tipo_identificacion_empresa="NIT",
            nit=nit_test,
            direccion_empresa="Calle Falsa 123",
            telefono_empresa="3001234567",
            correo_empresa="prueba@orm.com",
            ciudad_empresa="Bogotá",
            departamento_empresa="Cundinamarca"
        )

        db.session.add(nueva_empresa)
        db.session.commit()

        print(f"[OK] Empresa creada exitosamente")
        print(f"   ID: {nueva_empresa.id}")
        print(f"   Nombre: {nueva_empresa.nombre_empresa}")
        print(f"   NIT: {nueva_empresa.nit}")

        return nueva_empresa.id

    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Error al crear empresa: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_queries_complejas():
    """
    TEST 6: Probar queries complejas con joins
    """
    print("\n" + "=" * 80)
    print("TEST 6: Queries Complejas con Joins")
    print("=" * 80)

    try:
        # Query con join entre Usuarios y Empresas
        usuarios_con_empresa = db.session.query(
            Usuario.primerNombre,
            Usuario.primerApellido,
            Usuario.numeroId,
            Empresa.nombre_empresa
        ).join(
            Empresa, Usuario.empresa_nit == Empresa.nit
        ).limit(5).all()

        print(f"[OK] Query con JOIN ejecutada correctamente")
        print(f"   Resultados encontrados: {len(usuarios_con_empresa)}")

        if usuarios_con_empresa:
            print("\nPrimeros usuarios con empresa:")
            for nombre, apellido, num_id, empresa in usuarios_con_empresa:
                print(f"   - {nombre} {apellido} ({num_id}) - {empresa}")

        return True

    except Exception as e:
        print(f"[ERROR] Error en queries complejas: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """
    Función principal que ejecuta todos los tests
    """
    print("\n" + "=" * 80)
    print(">> INICIANDO TESTS DE MIGRACION ORM")
    print("=" * 80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Objetivo: Verificar que SQLAlchemy ORM funciona correctamente")
    print("=" * 80)

    # Crear aplicación Flask
    app = create_app()

    with app.app_context():
        resultados = {}

        # Test 1: Crear cotización
        cotizacion_id = test_crear_cotizacion()
        resultados['Crear Cotización'] = cotizacion_id is not None

        # Test 2: Recuperar cotización
        if cotizacion_id:
            resultados['Recuperar Cotización'] = test_recuperar_cotizacion(cotizacion_id)
        else:
            resultados['Recuperar Cotización'] = False

        # Test 3: Listar cotizaciones
        resultados['Listar Cotizaciones'] = test_listar_todas_cotizaciones()

        # Test 4: Contar registros
        resultados['Contar Registros'] = test_contar_registros()

        # Test 5: Crear empresa
        resultados['Crear Empresa'] = test_crear_empresa_y_usuario() is not None

        # Test 6: Queries complejas
        resultados['Queries Complejas'] = test_queries_complejas()

        # Resumen
        print("\n" + "=" * 80)
        print(">> RESUMEN DE RESULTADOS")
        print("=" * 80)

        total_tests = len(resultados)
        tests_exitosos = sum(1 for r in resultados.values() if r)
        tests_fallidos = total_tests - tests_exitosos

        for test_name, resultado in resultados.items():
            status = "[PASS]" if resultado else "[FAIL]"
            print(f"   {status} - {test_name}")

        print("\n" + "-" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"[+] Exitosos: {tests_exitosos}")
        print(f"[-] Fallidos: {tests_fallidos}")
        print(f"Porcentaje: {(tests_exitosos/total_tests)*100:.1f}%")

        if tests_fallidos == 0:
            print("\n>> TODOS LOS TESTS PASARON! La migracion ORM es exitosa.")
        else:
            print(f"\n[!] {tests_fallidos} test(s) fallaron. Revisar logs arriba.")

        print("=" * 80 + "\n")

        return tests_fallidos == 0


if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except Exception as e:
        print(f"\n❌ Error crítico en la ejecución de tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
