"""
Script de validación para PILA v1.1
Ejecuta pruebas directas sin pytest para validar correcciones legales
"""

import sys
from pathlib import Path

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

from logic.pila_engine import (
    CalculadoraPILA,
    calcular_pila_rapido,
    SMMLV_2025,
    IBC_MAXIMO
)
from decimal import Decimal


def test_ccf_siempre():
    """✓ CCF 4% se calcula SIEMPRE (sin umbral de 10 SMMLV)"""
    print("\n" + "="*70)
    print("TEST 1: CCF 4% SIEMPRE (Corrección v1.1)")
    print("="*70)
    
    # Caso 1: Salario < 10 SMMLV
    calc1 = CalculadoraPILA(salario_base=5000000, nivel_riesgo_arl=1)
    resultado1 = calc1.calcular()
    esperado1 = Decimal('5000000') * Decimal('0.04')
    
    print(f"  Salario: $5,000,000 (< 10 SMMLV)")
    print(f"  CCF esperado: ${esperado1:,.0f}")
    print(f"  CCF obtenido: ${resultado1.ccf:,.0f}")
    assert resultado1.ccf == esperado1, "❌ CCF incorrecto para salario < 10 SMMLV"
    print("  ✓ CCF calculado correctamente")
    
    # Caso 2: Salario > 10 SMMLV (v1.0 fallaba aquí)
    calc2 = CalculadoraPILA(salario_base=20000000, nivel_riesgo_arl=1)
    resultado2 = calc2.calcular()
    ibc2 = Decimal('20000000')  # No supera 25 SMMLV
    esperado2 = ibc2 * Decimal('0.04')
    
    print(f"\n  Salario: $20,000,000 (> 10 SMMLV)")
    print(f"  CCF esperado: ${esperado2:,.0f}")
    print(f"  CCF obtenido: ${resultado2.ccf:,.0f}")
    assert resultado2.ccf == esperado2, "❌ CCF incorrecto para salario > 10 SMMLV"
    print("  ✓ CCF calculado correctamente (v1.0 fallaba aquí)")
    
    print("\n✅ TEST 1 PASADO: CCF 4% SIEMPRE")


def test_exoneracion_salud():
    """✓ Exoneración de Salud Empleador para salarios < 10 SMMLV"""
    print("\n" + "="*70)
    print("TEST 2: Exoneración Salud Empleador (Corrección v1.1)")
    print("="*70)
    
    # Caso 1: Empresa exonerada + salario < 10 SMMLV
    calc1 = CalculadoraPILA(
        salario_base=1300000,
        nivel_riesgo_arl=1,
        es_empresa_exonerada=True
    )
    resultado1 = calc1.calcular()
    
    print(f"  Salario: $1,300,000 (< 10 SMMLV)")
    print(f"  Empresa exonerada: SÍ")
    print(f"  Salud Empleador esperado: $0")
    print(f"  Salud Empleador obtenido: ${resultado1.salud_empleador:,.0f}")
    assert resultado1.salud_empleador == Decimal('0'), "❌ Exoneración no aplicada"
    assert resultado1.salud_empleador_exonerado, "❌ Flag exonerado no marcado"
    print("  ✓ Exoneración aplicada correctamente")
    
    # Caso 2: Empresa NO exonerada (debe pagar 8.5%)
    calc2 = CalculadoraPILA(
        salario_base=1300000,
        nivel_riesgo_arl=1,
        es_empresa_exonerada=False
    )
    resultado2 = calc2.calcular()
    esperado2 = Decimal('1300000') * Decimal('0.085')
    
    print(f"\n  Salario: $1,300,000 (< 10 SMMLV)")
    print(f"  Empresa exonerada: NO")
    print(f"  Salud Empleador esperado: ${esperado2:,.0f}")
    print(f"  Salud Empleador obtenido: ${resultado2.salud_empleador:,.0f}")
    assert resultado2.salud_empleador == esperado2, "❌ Debe pagar 8.5%"
    assert not resultado2.salud_empleador_exonerado, "❌ No debe estar exonerado"
    print("  ✓ Salud Empleador pagado correctamente")
    
    # Caso 3: Empresa exonerada pero salario > 10 SMMLV (no aplica exoneración)
    calc3 = CalculadoraPILA(
        salario_base=15000000,
        nivel_riesgo_arl=1,
        es_empresa_exonerada=True
    )
    resultado3 = calc3.calcular()
    esperado3 = Decimal('15000000') * Decimal('0.085')
    
    print(f"\n  Salario: $15,000,000 (> 10 SMMLV)")
    print(f"  Empresa exonerada: SÍ (pero NO aplica por salario alto)")
    print(f"  Salud Empleador esperado: ${esperado3:,.0f}")
    print(f"  Salud Empleador obtenido: ${resultado3.salud_empleador:,.0f}")
    assert resultado3.salud_empleador == esperado3, "❌ Debe pagar 8.5%"
    assert not resultado3.salud_empleador_exonerado, "❌ No debe estar exonerado"
    print("  ✓ Exoneración NO aplicada (salario > umbral)")
    
    print("\n✅ TEST 2 PASADO: Exoneración Salud Empleador")


def test_tope_ibc_25_smmlv():
    """✓ Tope IBC máximo de 25 SMMLV"""
    print("\n" + "="*70)
    print("TEST 3: Tope IBC Máximo 25 SMMLV (Corrección v1.1)")
    print("="*70)
    
    # Caso 1: Salario dentro del límite
    calc1 = CalculadoraPILA(salario_base=20000000, nivel_riesgo_arl=1)
    resultado1 = calc1.calcular()
    
    print(f"  Salario: $20,000,000 (< 25 SMMLV)")
    print(f"  IBC esperado: $20,000,000 (sin límite)")
    print(f"  IBC obtenido: ${resultado1.ibc:,.0f}")
    assert resultado1.ibc == Decimal('20000000'), "❌ IBC no debe limitarse"
    assert not resultado1.ibc_limitado, "❌ Flag limitado no debe estar activo"
    print("  ✓ IBC sin límite (dentro del rango)")
    
    # Caso 2: Salario que supera el tope
    calc2 = CalculadoraPILA(salario_base=35000000, nivel_riesgo_arl=1)
    resultado2 = calc2.calcular()
    
    print(f"\n  Salario: $35,000,000 (> 25 SMMLV)")
    print(f"  IBC esperado: ${IBC_MAXIMO:,.0f} (tope aplicado)")
    print(f"  IBC obtenido: ${resultado2.ibc:,.0f}")
    assert resultado2.ibc == IBC_MAXIMO, "❌ IBC debe limitarse a 25 SMMLV"
    assert resultado2.ibc_limitado, "❌ Flag limitado debe estar activo"
    print("  ✓ IBC limitado a 25 SMMLV correctamente")
    
    # Verificar que los cálculos usen el IBC limitado
    salud_esperada = IBC_MAXIMO * Decimal('0.04')
    print(f"\n  Salud empleado esperada (sobre IBC limitado): ${salud_esperada:,.0f}")
    print(f"  Salud empleado obtenida: ${resultado2.salud_empleado:,.0f}")
    assert resultado2.salud_empleado == salud_esperada, "❌ Salud debe usar IBC limitado"
    print("  ✓ Cálculos usan IBC limitado correctamente")
    
    print("\n✅ TEST 3 PASADO: Tope IBC 25 SMMLV")


def test_salario_integral():
    """✓ Soporte para Salario Integral (IBC = 70%)"""
    print("\n" + "="*70)
    print("TEST 4: Salario Integral IBC=70% (Corrección v1.1)")
    print("="*70)
    
    # Caso 1: Salario integral estándar
    calc1 = CalculadoraPILA(
        salario_base=25000000,
        nivel_riesgo_arl=2,
        es_salario_integral=True
    )
    resultado1 = calc1.calcular()
    ibc_esperado1 = Decimal('25000000') * Decimal('0.70')
    
    print(f"  Salario: $25,000,000")
    print(f"  Tipo: INTEGRAL")
    print(f"  IBC esperado: ${ibc_esperado1:,.0f} (70% del salario)")
    print(f"  IBC obtenido: ${resultado1.ibc:,.0f}")
    assert resultado1.ibc == ibc_esperado1, "❌ IBC debe ser 70% del salario"
    assert resultado1.es_salario_integral, "❌ Flag integral debe estar activo"
    print("  ✓ IBC = 70% del salario integral")
    
    # Caso 2: Salario integral que supera 25 SMMLV (tope se aplica sobre el 70%)
    calc2 = CalculadoraPILA(
        salario_base=50000000,
        nivel_riesgo_arl=2,
        es_salario_integral=True
    )
    resultado2 = calc2.calcular()
    ibc_70_porciento = Decimal('50000000') * Decimal('0.70')  # $35M
    ibc_esperado2 = IBC_MAXIMO  # $32.5M (tope aplicado)
    
    print(f"\n  Salario: $50,000,000")
    print(f"  Tipo: INTEGRAL")
    print(f"  IBC 70%: ${ibc_70_porciento:,.0f}")
    print(f"  IBC esperado: ${ibc_esperado2:,.0f} (tope aplicado)")
    print(f"  IBC obtenido: ${resultado2.ibc:,.0f}")
    assert resultado2.ibc == ibc_esperado2, "❌ Tope debe aplicarse sobre IBC integral"
    assert resultado2.ibc_limitado, "❌ Flag limitado debe estar activo"
    print("  ✓ Tope de 25 SMMLV aplicado sobre IBC integral")
    
    print("\n✅ TEST 4 PASADO: Salario Integral 70%")


def test_funciones_utilidad():
    """Validar funciones de utilidad"""
    print("\n" + "="*70)
    print("TEST 5: Funciones de Utilidad")
    print("="*70)
    
    resultado = calcular_pila_rapido(
        salario=1300000,
        riesgo_arl=1,
        exonerada=True,
        integral=False
    )
    
    print(f"  Salario: $1,300,000")
    print(f"  Total Empleado: ${resultado['total_empleado']:,.0f}")
    print(f"  Total Empleador: ${resultado['total_empleador']:,.0f}")
    print(f"  Salario Neto: ${resultado['salario_neto']:,.0f}")
    
    assert isinstance(resultado, dict), "❌ Debe retornar dict"
    assert 'total_empleado' in resultado, "❌ Falta campo total_empleado"
    assert 'advertencias' in resultado, "❌ Falta campo advertencias"
    
    print("  ✓ Función calcular_pila_rapido() funcional")
    print("\n✅ TEST 5 PASADO: Funciones de Utilidad")


def main():
    """Ejecuta todas las validaciones"""
    print("\n" + "="*70)
    print("VALIDACIÓN PILA v1.1 - CORRECCIONES LEGALES COLOMBIA")
    print("="*70)
    print(f"SMMLV 2025: ${SMMLV_2025:,.0f}")
    print(f"IBC Máximo (25 SMMLV): ${IBC_MAXIMO:,.0f}")
    
    try:
        test_ccf_siempre()
        test_exoneracion_salud()
        test_tope_ibc_25_smmlv()
        test_salario_integral()
        test_funciones_utilidad()
        
        print("\n" + "="*70)
        print("✅ TODOS LOS TESTS PASARON (5/5)")
        print("="*70)
        print("\n🎉 PILA v1.1 VALIDADO - Todas las correcciones legales funcionan")
        print("\nCorrecciones verificadas:")
        print("  ✓ CCF 4% SIEMPRE (sin umbral de 10 SMMLV)")
        print("  ✓ Exoneración de Salud Empleador < 10 SMMLV")
        print("  ✓ Tope IBC máximo de 25 SMMLV")
        print("  ✓ Soporte Salario Integral (IBC = 70%)")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ ERROR EN VALIDACIÓN: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
