#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_pila_15_dias.py
===================
Prueba Simulada: FASE 11 - Liquidación PILA con 15 días trabajados
Verifica cálculo proporcional de IBC y aportes

Autor: Senior Backend Developer & Data Scientist
Fecha: 2025-11-30
"""

import sys
import os

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Agregar el directorio raíz al path para importar logic.pila_engine
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logic.pila_engine import LiquidadorPILA, ConfiguracionPILA
from decimal import Decimal


def test_liquidacion_15_dias():
    """
    Prueba simulada: Empleado que trabajó 15 días del mes (ingreso día 16).

    Escenario:
        - Empleado ingresa el 16 de enero
        - Salario mensual: $1,800,000
        - IBC: $1,800,000
        - Días trabajados: 15 (del 16 al 30)
        - ARL Clase 1 (oficina)

    Resultado esperado:
        - IBC proporcional: $900,000 (15/30 * $1,800,000)
        - Salud empleado: 4% de $900,000 = $36,000
        - Pensión empleado: 4% de $900,000 = $36,000
        - Total empleado: $72,000
    """
    print("\n" + "="*80)
    print("TEST: LIQUIDACIÓN PILA - EMPLEADO CON 15 DÍAS TRABAJADOS")
    print("="*80)

    try:
        # =====================================================================
        # PASO 1: CONFIGURACIÓN DEL MOTOR PILA
        # =====================================================================
        print("\n[PASO 1] Inicializando motor de liquidación PILA...")

        liquidador = LiquidadorPILA()
        print(f"   ✅ Motor inicializado")
        print(f"   ✅ SMMLV 2025: ${liquidador.config.SMMLV:,.0f}")
        print(f"   ✅ Días estándar: {liquidador.config.DIAS_MES_ESTANDAR}")

        # =====================================================================
        # PASO 2: DATOS DEL EMPLEADO
        # =====================================================================
        print("\n[PASO 2] Configurando datos del empleado...")

        empleado = {
            'numeroId': '1234567890',
            'primerNombre': 'Carlos',
            'primerApellido': 'Rodríguez',
            'ibc': 1800000,  # IBC base mensual
            'salario': 1800000,  # Salario mensual
            'epsNombre': 'Compensar EPS',
            'afpNombre': 'Protección',
            'arlNombre': 'Sura ARL',
            'arlClase': 1,  # Clase I - Riesgo mínimo
            'tipoContrato': 'Indefinido'
        }

        print(f"   ✅ Empleado: {empleado['primerNombre']} {empleado['primerApellido']}")
        print(f"   ✅ Identificación: {empleado['numeroId']}")
        print(f"   ✅ IBC base mensual: ${empleado['ibc']:,.0f}")
        print(f"   ✅ ARL Clase: {empleado['arlClase']}")

        # =====================================================================
        # PASO 3: NOVEDADES (Ingreso día 16)
        # =====================================================================
        print("\n[PASO 3] Configurando novedades...")

        novedades = [
            {
                'tipo': 'Ingreso',
                'fecha': '2025-01-16'  # Ingresó el 16 de enero
            }
        ]

        print(f"   ✅ Novedad registrada: INGRESO el 16 de enero")
        print(f"   ✅ Días a cotizar: 15 (del 16 al 30)")

        # =====================================================================
        # PASO 4: CALCULAR LÍNEA PILA
        # =====================================================================
        print("\n[PASO 4] Calculando liquidación PILA...")

        # Calcular con el motor (días se ajustarán automáticamente por la novedad)
        resultado = liquidador.calcular_linea(
            usuario=empleado,
            dias_trabajados=30,  # Se enviará 30, pero el motor ajustará por la novedad
            novedades=novedades
        )

        print(f"   ✅ Liquidación completada")

        # =====================================================================
        # PASO 5: VERIFICAR RESULTADOS
        # =====================================================================
        print("\n[PASO 5] Verificando resultados...")

        # IBC esperado (proporcional a 15 días)
        ibc_esperado = (Decimal('1800000') / 30) * 15
        ibc_calculado = Decimal(str(resultado['ibc_calculado']))

        print(f"\n   📊 IBC PROPORCIONAL:")
        print(f"      - IBC base mensual: ${empleado['ibc']:,.0f}")
        print(f"      - Días trabajados: {resultado['dias_cotizados']}")
        print(f"      - IBC proporcional esperado: ${float(ibc_esperado):,.0f}")
        print(f"      - IBC calculado: ${resultado['ibc_calculado']:,.0f}")

        # Validar IBC
        if abs(ibc_calculado - ibc_esperado) < Decimal('1'):
            print(f"      ✅ IBC correcto")
        else:
            print(f"      ❌ ERROR: IBC no coincide")
            return False

        # Aportes esperados
        salud_empleado_esperado = (ibc_esperado * Decimal('4.0') / 100)
        pension_empleado_esperado = (ibc_esperado * Decimal('4.0') / 100)
        total_empleado_esperado = salud_empleado_esperado + pension_empleado_esperado

        print(f"\n   📊 APORTES:")
        print(f"      - Salud empleado (4%): ${resultado['salud_empleado']:,.0f}")
        print(f"      - Salud empleador (8.5%): ${resultado['salud_empleador']:,.0f}")
        print(f"      - Pensión empleado (4%): ${resultado['pension_empleado']:,.0f}")
        print(f"      - Pensión empleador (12%): ${resultado['pension_empleador']:,.0f}")
        print(f"      - ARL Clase {resultado['arl_clase']} ({resultado['arl_tarifa']}%): ${resultado['arl']:,.0f}")
        print(f"      - CCF (4%): ${resultado['ccf']:,.0f}")

        print(f"\n   📊 TOTALES:")
        print(f"      - Total empleado: ${resultado['total_empleado']:,.0f}")
        print(f"      - Total empleador: ${resultado['total_empleador']:,.0f}")
        print(f"      - TOTAL APORTES: ${resultado['total_aportes']:,.0f}")

        # =====================================================================
        # PASO 6: VALIDACIONES
        # =====================================================================
        print("\n[PASO 6] Validaciones finales...")

        validaciones = []

        # Validar días cotizados
        if resultado['dias_cotizados'] == 15:
            validaciones.append(("✅", "Días cotizados: 15 (correcto)"))
        else:
            validaciones.append(("❌", f"Días cotizados: {resultado['dias_cotizados']} (esperado: 15)"))

        # Validar marca de novedad
        if resultado['marca_novedad'] == 'IGE':
            validaciones.append(("✅", "Marca novedad: IGE (Ingreso)"))
        else:
            validaciones.append(("❌", f"Marca novedad: {resultado['marca_novedad']} (esperado: IGE)"))

        # Validar IBC proporcional
        if abs(ibc_calculado - ibc_esperado) < Decimal('1'):
            validaciones.append(("✅", f"IBC proporcional: ${float(ibc_calculado):,.0f}"))
        else:
            validaciones.append(("❌", "IBC proporcional incorrecto"))

        # Validar total empleado
        total_emp_calc = Decimal(str(resultado['total_empleado']))
        if abs(total_emp_calc - total_empleado_esperado) < Decimal('1'):
            validaciones.append(("✅", f"Total empleado: ${resultado['total_empleado']:,.0f}"))
        else:
            validaciones.append(("❌", f"Total empleado: ${resultado['total_empleado']:,.0f} (esperado: ${float(total_empleado_esperado):,.0f})"))

        # Mostrar validaciones
        for simbolo, mensaje in validaciones:
            print(f"   {simbolo} {mensaje}")

        # Verificar si hay alertas
        if resultado['alertas']:
            print(f"\n   ⚠️  ALERTAS:")
            for alerta in resultado['alertas']:
                print(f"      - {alerta}")

        # Mostrar novedades procesadas
        if resultado['novedades_procesadas']:
            print(f"\n   📋 NOVEDADES PROCESADAS:")
            for novedad in resultado['novedades_procesadas']:
                print(f"      - {novedad}")

        # =====================================================================
        # PASO 7: COMPARACIÓN CON EMPLEADO DE 30 DÍAS
        # =====================================================================
        print("\n[PASO 7] Comparación con empleado de 30 días completos...")

        empleado_30dias = empleado.copy()
        resultado_30dias = liquidador.calcular_linea(
            usuario=empleado_30dias,
            dias_trabajados=30,
            novedades=[]
        )

        print(f"\n   📊 COMPARACIÓN:")
        print(f"      {'Concepto':<25} {'15 días':<20} {'30 días':<20}")
        print(f"      {'-'*65}")
        print(f"      {'IBC':<25} ${resultado['ibc_calculado']:>15,.0f}  ${resultado_30dias['ibc_calculado']:>15,.0f}")
        print(f"      {'Salud empleado':<25} ${resultado['salud_empleado']:>15,.0f}  ${resultado_30dias['salud_empleado']:>15,.0f}")
        print(f"      {'Pensión empleado':<25} ${resultado['pension_empleado']:>15,.0f}  ${resultado_30dias['pension_empleado']:>15,.0f}")
        print(f"      {'Total empleado':<25} ${resultado['total_empleado']:>15,.0f}  ${resultado_30dias['total_empleado']:>15,.0f}")
        print(f"      {'Total aportes':<25} ${resultado['total_aportes']:>15,.0f}  ${resultado_30dias['total_aportes']:>15,.0f}")

        # =====================================================================
        # RESULTADO FINAL
        # =====================================================================
        todas_ok = all(simbolo == "✅" for simbolo, _ in validaciones)

        if todas_ok:
            print("\n" + "="*80)
            print("[SUCCESS] TEST EXITOSO - LIQUIDACIÓN CORRECTA")
            print("="*80)
            print("\nCONCLUSIÓN:")
            print("  ✅ IBC proporcional calculado correctamente (15/30 días)")
            print("  ✅ Aportes calculados sobre IBC proporcional")
            print("  ✅ Marca de novedad 'IGE' aplicada")
            print("  ✅ Días cotizados: 15")
            print(f"  ✅ Total descuento empleado: ${resultado['total_empleado']:,.0f}")
            print("\nOBJETIVO CUMPLIDO: Motor PILA funciona correctamente con días parciales")
            print("="*80 + "\n")
            return True
        else:
            print("\n" + "="*80)
            print("[ADVERTENCIA] TEST COMPLETADO CON OBSERVACIONES")
            print("="*80 + "\n")
            return False

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("="*80)
    print(" "*20 + "FASE 11: PRUEBA MOTOR PILA")
    print("="*80)

    resultado = test_liquidacion_15_dias()

    if resultado:
        print("\n[RESULTADO FINAL] Motor PILA listo para producción")
    else:
        print("\n[RESULTADO FINAL] Revisar observaciones antes de usar en producción")

    print("="*80 + "\n")
