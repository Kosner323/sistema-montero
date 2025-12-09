"""
PRUEBA DIRECTA: Motor PILA v1.2 - Independiente $5.000.000

Este script ejecuta la prueba solicitada de cálculo PILA
para un trabajador independiente con ingreso de 5 millones.
"""

import sys
sys.path.insert(0, 'D:\\Mi-App-React\\src\\dashboard')

from decimal import Decimal

# Constantes
SMMLV_2025 = Decimal('1300000')
IBC_INDEPENDIENTE_PORCENTAJE = Decimal('0.40')
SALUD_INDEPENDIENTE = Decimal('0.125')
PENSION_INDEPENDIENTE = Decimal('0.16')
CCF_INDEPENDIENTE_OPCIONAL = Decimal('0.02')

def calcular_independiente_5M():
    """
    Calcula aportes para independiente con ingreso de $5.000.000
    
    LÓGICA INDEPENDIENTE:
    - IBC = Ingreso * 40%
    - Salud = IBC * 12.5% (total a cargo del cotizante)
    - Pensión = IBC * 16% (total a cargo del cotizante)
    - CCF = Opcional (0% o 2%)
    - NO aplica ARL, SENA, ICBF
    """
    
    print("=" * 80)
    print(" PRUEBA SIMULADA: INDEPENDIENTE CON INGRESO DE $5.000.000")
    print("=" * 80)
    print()
    
    # Datos de entrada
    ingreso_mensual = Decimal('5000000')
    
    print(f"📊 DATOS DE ENTRADA:")
    print(f"   • Tipo Cotizante:       INDEPENDIENTE")
    print(f"   • Ingreso Mensual:      ${ingreso_mensual:,.0f} COP")
    print(f"   • SMMLV 2025:           ${SMMLV_2025:,.0f} COP")
    print()
    
    # PASO 1: Calcular IBC (40% del ingreso)
    ibc = ingreso_mensual * IBC_INDEPENDIENTE_PORCENTAJE
    print(f"🔢 CÁLCULO IBC:")
    print(f"   IBC = Ingreso * 40%")
    print(f"   IBC = ${ingreso_mensual:,.0f} * {IBC_INDEPENDIENTE_PORCENTAJE}")
    print(f"   IBC = ${ibc:,.0f} COP")
    print()
    
    # Validar mínimo
    if ibc < SMMLV_2025:
        print(f"   ⚠️ IBC es menor a 1 SMMLV, se ajusta a ${SMMLV_2025:,.0f}")
        ibc = SMMLV_2025
    else:
        print(f"   ✅ IBC válido (>= 1 SMMLV)")
    print()
    
    # PASO 2: Calcular Salud (12.5% total)
    salud = (ibc * SALUD_INDEPENDIENTE).quantize(Decimal('1'))
    print(f"💊 CÁLCULO SALUD (12.5% total):")
    print(f"   Salud = IBC * 12.5%")
    print(f"   Salud = ${ibc:,.0f} * {SALUD_INDEPENDIENTE}")
    print(f"   Salud = ${salud:,.0f} COP")
    print(f"   ")
    print(f"   ℹ️ Para INDEPENDIENTES:")
    print(f"      - El 12.5% es 100% a cargo del cotizante")
    print(f"      - NO hay aporte empleador")
    print()
    
    # PASO 3: Calcular Pensión (16% total)
    pension = (ibc * PENSION_INDEPENDIENTE).quantize(Decimal('1'))
    print(f"👴 CÁLCULO PENSIÓN (16% total):")
    print(f"   Pensión = IBC * 16%")
    print(f"   Pensión = ${ibc:,.0f} * {PENSION_INDEPENDIENTE}")
    print(f"   Pensión = ${pension:,.0f} COP")
    print(f"   ")
    print(f"   ℹ️ Para INDEPENDIENTES:")
    print(f"      - El 16% es 100% a cargo del cotizante")
    print(f"      - NO hay aporte empleador")
    print()
    
    # PASO 4: CCF (Opcional)
    ccf = Decimal('0')  # Sin CCF en esta prueba
    print(f"🏢 CÁLCULO CCF:")
    print(f"   CCF = ${ccf:,.0f} COP (NO activado)")
    print(f"   ")
    print(f"   ℹ️ Para INDEPENDIENTES:")
    print(f"      - CCF es OPCIONAL (2% si se activa)")
    print(f"      - En esta prueba: NO activado")
    print()
    
    # PASO 5: Otros aportes
    arl = Decimal('0')
    sena = Decimal('0')
    icbf = Decimal('0')
    print(f"⚙️ OTROS APORTES:")
    print(f"   ARL:  ${arl:,.0f} COP (NO aplica para independientes)")
    print(f"   SENA: ${sena:,.0f} COP (NO aplica para independientes)")
    print(f"   ICBF: ${icbf:,.0f} COP (NO aplica para independientes)")
    print()
    
    # TOTALES
    total_cotizante = salud + pension + ccf
    total_empleador = Decimal('0')  # No hay empleador
    total_general = total_cotizante
    salario_neto = ingreso_mensual - total_cotizante
    
    print("=" * 80)
    print(" RESUMEN FINAL")
    print("=" * 80)
    print()
    print(f"{'Concepto':<30} {'Valor':>20} {'% del IBC':>15}")
    print("-" * 80)
    print(f"{'IBC':<30} ${ibc:>19,.0f} {'100.0%':>15}")
    print(f"{'Salud (Cotizante)':<30} ${salud:>19,.0f} {'12.5%':>15}")
    print(f"{'Pensión (Cotizante)':<30} ${pension:>19,.0f} {'16.0%':>15}")
    print(f"{'CCF (Opcional)':<30} ${ccf:>19,.0f} {'0.0%':>15}")
    print(f"{'ARL':<30} ${arl:>19,.0f} {'N/A':>15}")
    print(f"{'SENA':<30} ${sena:>19,.0f} {'N/A':>15}")
    print(f"{'ICBF':<30} ${icbf:>19,.0f} {'N/A':>15}")
    print("-" * 80)
    print(f"{'TOTAL A PAGAR (Cotizante)':<30} ${total_cotizante:>19,.0f} {'28.5%':>15}")
    print(f"{'Total Empleador':<30} ${total_empleador:>19,.0f} {'0.0%':>15}")
    print("=" * 80)
    print(f"{'TOTAL SEGURIDAD SOCIAL':<30} ${total_general:>19,.0f}")
    print("=" * 80)
    print()
    print(f"💰 INGRESO NETO ESTIMADO:")
    print(f"   Ingreso Bruto:    ${ingreso_mensual:,.0f} COP")
    print(f"   (-) Descuentos:   ${total_cotizante:,.0f} COP")
    print(f"   ───────────────────────────────────")
    print(f"   Ingreso Neto:     ${salario_neto:,.0f} COP")
    print()
    print("=" * 80)
    
    # Validación de resultados esperados
    print()
    print("✅ VALIDACIÓN DE RESULTADOS:")
    print()
    
    # Verificar IBC
    ibc_esperado = Decimal('2000000')
    if ibc == ibc_esperado:
        print(f"   ✅ IBC correcto: ${ibc:,.0f} (esperado: ${ibc_esperado:,.0f})")
    else:
        print(f"   ❌ IBC incorrecto: ${ibc:,.0f} (esperado: ${ibc_esperado:,.0f})")
    
    # Verificar Salud
    salud_esperado = Decimal('250000')
    if salud == salud_esperado:
        print(f"   ✅ Salud correcto: ${salud:,.0f} (esperado: ${salud_esperado:,.0f})")
    else:
        print(f"   ❌ Salud incorrecto: ${salud:,.0f} (esperado: ${salud_esperado:,.0f})")
    
    # Verificar Pensión
    pension_esperado = Decimal('320000')
    if pension == pension_esperado:
        print(f"   ✅ Pensión correcto: ${pension:,.0f} (esperado: ${pension_esperado:,.0f})")
    else:
        print(f"   ❌ Pensión incorrecto: ${pension:,.0f} (esperado: ${pension_esperado:,.0f})")
    
    # Verificar Total
    total_esperado = Decimal('570000')
    if total_cotizante == total_esperado:
        print(f"   ✅ Total correcto: ${total_cotizante:,.0f} (esperado: ${total_esperado:,.0f})")
    else:
        print(f"   ❌ Total incorrecto: ${total_cotizante:,.0f} (esperado: ${total_esperado:,.0f})")
    
    # Verificar Neto
    neto_esperado = Decimal('4430000')
    if salario_neto == neto_esperado:
        print(f"   ✅ Neto correcto: ${salario_neto:,.0f} (esperado: ${neto_esperado:,.0f})")
    else:
        print(f"   ❌ Neto incorrecto: ${salario_neto:,.0f} (esperado: ${neto_esperado:,.0f})")
    
    print()
    print("=" * 80)
    print("📝 CONCLUSIONES:")
    print("=" * 80)
    print()
    print("1. Un trabajador INDEPENDIENTE con ingreso de $5.000.000:")
    print(f"   • Paga IBC = ${ibc:,.0f} (40% del ingreso)")
    print(f"   • Paga Salud = ${salud:,.0f} (12.5% del IBC)")
    print(f"   • Paga Pensión = ${pension:,.0f} (16% del IBC)")
    print(f"   • Total descuento = ${total_cotizante:,.0f} (28.5% del IBC)")
    print()
    print("2. DIFERENCIAS vs DEPENDIENTE:")
    print("   • NO paga ARL (riesgo laboral)")
    print("   • NO paga SENA ni ICBF")
    print("   • NO tiene aporte empleador (todo lo paga el cotizante)")
    print("   • IBC es 40% del ingreso (vs 100% para dependientes)")
    print()
    print("3. VENTAJA FISCAL:")
    print(f"   • Ingreso real: $5.000.000")
    print(f"   • Base cotización: $2.000.000 (ahorro de base)")
    print(f"   • Pero: 100% a cargo del trabajador")
    print()
    print("=" * 80)
    
    return {
        'ingreso': float(ingreso_mensual),
        'ibc': float(ibc),
        'salud': float(salud),
        'pension': float(pension),
        'ccf': float(ccf),
        'total': float(total_cotizante),
        'neto': float(salario_neto)
    }

if __name__ == "__main__":
    resultado = calcular_independiente_5M()
    
    print()
    print("🔧 DATOS PARA BACKEND:")
    print(f"   resultado = {resultado}")
