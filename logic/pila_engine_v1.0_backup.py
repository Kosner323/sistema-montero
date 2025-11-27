"""
Motor de Cálculo de Seguridad Social (PILA) - Colombia
Sistema Montero - Lógica de Negocio Pura

Este módulo implementa el cálculo exacto de aportes a Seguridad Social
según la legislación laboral colombiana vigente.

Autor: Sistema Montero
Fecha: 2025-11-26
Versión: 1.0.0
"""

from typing import Dict, Optional
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from datetime import datetime


# ============================================================================
# CONSTANTES COLOMBIA - SEGURIDAD SOCIAL 2025
# ============================================================================

# Salario Mínimo Mensual Legal Vigente
SMMLV_2025 = Decimal('1300000')  # $1.300.000 COP

# SALUD (12.5% total)
SALUD_TOTAL = Decimal('0.125')
SALUD_EMPLEADO = Decimal('0.04')      # 4% empleado
SALUD_EMPLEADOR = Decimal('0.085')    # 8.5% empleador

# PENSIÓN (16% total)
PENSION_TOTAL = Decimal('0.16')
PENSION_EMPLEADO = Decimal('0.04')    # 4% empleado
PENSION_EMPLEADOR = Decimal('0.12')   # 12% empleador

# ARL (Administradora de Riesgos Laborales) - Según nivel de riesgo
# Fuente: Decreto 1772 de 1994 y actualizaciones
TABLA_ARL = {
    1: Decimal('0.00522'),   # Riesgo I (Mínimo): 0.522%
    2: Decimal('0.01044'),   # Riesgo II (Bajo): 1.044%
    3: Decimal('0.02436'),   # Riesgo III (Medio): 2.436%
    4: Decimal('0.04350'),   # Riesgo IV (Alto): 4.350%
    5: Decimal('0.06960')    # Riesgo V (Máximo): 6.960%
}

# PARAFISCALES (Solo para salarios > 10 SMMLV)
UMBRAL_PARAFISCALES = SMMLV_2025 * 10

# Caja de Compensación Familiar (4% empleador)
CCF_TASA = Decimal('0.04')

# SENA (2% empleador)
SENA_TASA = Decimal('0.02')

# ICBF (3% empleador)
ICBF_TASA = Decimal('0.03')


# ============================================================================
# CLASES DE DATOS
# ============================================================================

@dataclass
class LiquidacionPILA:
    """
    Resultado completo de la liquidación de Seguridad Social
    Todos los valores en pesos colombianos (COP)
    """
    # Datos de entrada
    salario_base: Decimal
    nivel_riesgo_arl: int
    
    # Salud
    salud_empleado: Decimal
    salud_empleador: Decimal
    salud_total: Decimal
    
    # Pensión
    pension_empleado: Decimal
    pension_empleador: Decimal
    pension_total: Decimal
    
    # ARL
    arl_empleador: Decimal
    tasa_arl: Decimal
    
    # Parafiscales
    ccf: Decimal
    sena: Decimal
    icbf: Decimal
    parafiscales_total: Decimal
    aplica_parafiscales: bool
    
    # Totales
    total_empleado: Decimal
    total_empleador: Decimal
    total_general: Decimal
    
    # Metadata
    fecha_calculo: datetime
    salario_ajustado: bool  # True si se ajustó al mínimo
    advertencias: list


# ============================================================================
# MOTOR DE CÁLCULO
# ============================================================================

class CalculadoraPILA:
    """
    Calculadora de Seguridad Social para Colombia
    
    Implementa la lógica pura de negocio sin dependencias de base de datos.
    Todos los cálculos se realizan con precisión Decimal para evitar
    errores de redondeo financiero.
    
    Ejemplo de uso:
        >>> calc = CalculadoraPILA(salario_base=1300000, nivel_riesgo_arl=1)
        >>> resultado = calc.calcular()
        >>> print(f"Total empleado: ${resultado.total_empleado:,.0f}")
        Total empleado: $104,000
    """
    
    def __init__(self, salario_base: float, nivel_riesgo_arl: int):
        """
        Inicializa la calculadora
        
        Args:
            salario_base: Salario mensual del empleado en COP
            nivel_riesgo_arl: Nivel de riesgo ARL (1=Mínimo a 5=Máximo)
        
        Raises:
            ValueError: Si los parámetros son inválidos
        """
        self.salario_base = Decimal(str(salario_base))
        self.nivel_riesgo_arl = nivel_riesgo_arl
        self.advertencias = []
        self.salario_ajustado = False
        
        # Validaciones
        self._validar_parametros()
        
    def _validar_parametros(self):
        """Valida los parámetros de entrada"""
        
        # Validar nivel de riesgo ARL
        if self.nivel_riesgo_arl not in TABLA_ARL:
            raise ValueError(
                f"Nivel de riesgo ARL inválido: {self.nivel_riesgo_arl}. "
                f"Debe estar entre 1 y 5."
            )
        
        # Validar salario positivo
        if self.salario_base <= 0:
            raise ValueError(
                f"El salario base debe ser mayor a cero. "
                f"Recibido: ${self.salario_base:,.2f}"
            )
        
        # Ajustar al mínimo si es menor
        if self.salario_base < SMMLV_2025:
            self.advertencias.append(
                f"⚠️ Salario ${self.salario_base:,.0f} es menor al SMMLV "
                f"(${SMMLV_2025:,.0f}). Se ajustará automáticamente al mínimo legal."
            )
            self.salario_base = SMMLV_2025
            self.salario_ajustado = True
    
    def _redondear(self, valor: Decimal) -> Decimal:
        """
        Redondea un valor decimal al peso más cercano
        Usa redondeo bancario (ROUND_HALF_UP) según normas contables
        """
        return valor.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    
    def _calcular_salud(self) -> Dict[str, Decimal]:
        """Calcula aportes de salud"""
        salud_empleado = self._redondear(self.salario_base * SALUD_EMPLEADO)
        salud_empleador = self._redondear(self.salario_base * SALUD_EMPLEADOR)
        
        return {
            'empleado': salud_empleado,
            'empleador': salud_empleador,
            'total': salud_empleado + salud_empleador
        }
    
    def _calcular_pension(self) -> Dict[str, Decimal]:
        """Calcula aportes de pensión"""
        pension_empleado = self._redondear(self.salario_base * PENSION_EMPLEADO)
        pension_empleador = self._redondear(self.salario_base * PENSION_EMPLEADOR)
        
        return {
            'empleado': pension_empleado,
            'empleador': pension_empleador,
            'total': pension_empleado + pension_empleador
        }
    
    def _calcular_arl(self) -> Dict[str, Decimal]:
        """Calcula aportes de ARL (100% empleador)"""
        tasa = TABLA_ARL[self.nivel_riesgo_arl]
        arl_empleador = self._redondear(self.salario_base * tasa)
        
        return {
            'empleador': arl_empleador,
            'tasa': tasa
        }
    
    def _calcular_parafiscales(self) -> Dict[str, Decimal]:
        """
        Calcula aportes parafiscales
        
        Nota: Según Ley 1607 de 2012, los parafiscales NO aplican
        para salarios menores o iguales a 10 SMMLV
        """
        aplica = self.salario_base > UMBRAL_PARAFISCALES
        
        if not aplica:
            return {
                'ccf': Decimal('0'),
                'sena': Decimal('0'),
                'icbf': Decimal('0'),
                'total': Decimal('0'),
                'aplica': False
            }
        
        ccf = self._redondear(self.salario_base * CCF_TASA)
        sena = self._redondear(self.salario_base * SENA_TASA)
        icbf = self._redondear(self.salario_base * ICBF_TASA)
        
        self.advertencias.append(
            f"ℹ️ Salario superior a 10 SMMLV (${UMBRAL_PARAFISCALES:,.0f}). "
            f"Se aplican parafiscales completos."
        )
        
        return {
            'ccf': ccf,
            'sena': sena,
            'icbf': icbf,
            'total': ccf + sena + icbf,
            'aplica': True
        }
    
    def calcular(self) -> LiquidacionPILA:
        """
        Ejecuta el cálculo completo de Seguridad Social
        
        Returns:
            LiquidacionPILA: Objeto con todos los valores calculados
        """
        
        # Calcular componentes
        salud = self._calcular_salud()
        pension = self._calcular_pension()
        arl = self._calcular_arl()
        parafiscales = self._calcular_parafiscales()
        
        # Calcular totales
        total_empleado = salud['empleado'] + pension['empleado']
        
        total_empleador = (
            salud['empleador'] +
            pension['empleador'] +
            arl['empleador'] +
            parafiscales['total']
        )
        
        total_general = total_empleado + total_empleador
        
        # Construir resultado
        return LiquidacionPILA(
            # Entrada
            salario_base=self.salario_base,
            nivel_riesgo_arl=self.nivel_riesgo_arl,
            
            # Salud
            salud_empleado=salud['empleado'],
            salud_empleador=salud['empleador'],
            salud_total=salud['total'],
            
            # Pensión
            pension_empleado=pension['empleado'],
            pension_empleador=pension['empleador'],
            pension_total=pension['total'],
            
            # ARL
            arl_empleador=arl['empleador'],
            tasa_arl=arl['tasa'],
            
            # Parafiscales
            ccf=parafiscales['ccf'],
            sena=parafiscales['sena'],
            icbf=parafiscales['icbf'],
            parafiscales_total=parafiscales['total'],
            aplica_parafiscales=parafiscales['aplica'],
            
            # Totales
            total_empleado=total_empleado,
            total_empleador=total_empleador,
            total_general=total_general,
            
            # Metadata
            fecha_calculo=datetime.now(),
            salario_ajustado=self.salario_ajustado,
            advertencias=self.advertencias.copy()
        )
    
    def generar_reporte(self) -> str:
        """
        Genera un reporte legible en texto de la liquidación
        
        Returns:
            str: Reporte formateado para imprimir
        """
        resultado = self.calcular()
        
        linea = "=" * 70
        
        reporte = f"""
{linea}
        LIQUIDACIÓN DE SEGURIDAD SOCIAL - COLOMBIA
                    Sistema Montero v1.0
{linea}

DATOS DEL EMPLEADO:
  • Salario Base:        ${resultado.salario_base:>15,.0f} COP
  • Nivel Riesgo ARL:    {resultado.nivel_riesgo_arl} ({self._nombre_riesgo()})
  • Tasa ARL:            {resultado.tasa_arl * 100:>15.3f}%
  
{linea}
CONCEPTOS DE LIQUIDACIÓN:
{linea}

1. SALUD (12.5% total)
   Empleado (4%):        ${resultado.salud_empleado:>15,.0f} COP
   Empleador (8.5%):     ${resultado.salud_empleador:>15,.0f} COP
   ─────────────────────────────────────────
   Subtotal Salud:       ${resultado.salud_total:>15,.0f} COP

2. PENSIÓN (16% total)
   Empleado (4%):        ${resultado.pension_empleado:>15,.0f} COP
   Empleador (12%):      ${resultado.pension_empleador:>15,.0f} COP
   ─────────────────────────────────────────
   Subtotal Pensión:     ${resultado.pension_total:>15,.0f} COP

3. ARL (100% empleador)
   Empleador ({resultado.tasa_arl * 100:.3f}%):     ${resultado.arl_empleador:>15,.0f} COP

4. PARAFISCALES (Solo si salario > 10 SMMLV)
   Aplica:               {'SÍ' if resultado.aplica_parafiscales else 'NO'}
   CCF (4%):             ${resultado.ccf:>15,.0f} COP
   SENA (2%):            ${resultado.sena:>15,.0f} COP
   ICBF (3%):            ${resultado.icbf:>15,.0f} COP
   ─────────────────────────────────────────
   Subtotal Parafiscales:${resultado.parafiscales_total:>15,.0f} COP

{linea}
RESUMEN FINAL:
{linea}

  Total Empleado:        ${resultado.total_empleado:>15,.0f} COP
  Total Empleador:       ${resultado.total_empleador:>15,.0f} COP
  ═════════════════════════════════════════
  TOTAL GENERAL:         ${resultado.total_general:>15,.0f} COP

  Salario Neto (estimado): ${resultado.salario_base - resultado.total_empleado:>11,.0f} COP

{linea}
"""
        
        # Agregar advertencias si existen
        if resultado.advertencias:
            reporte += "\nADVERTENCIAS:\n"
            for adv in resultado.advertencias:
                reporte += f"  {adv}\n"
            reporte += f"\n{linea}\n"
        
        reporte += f"\nFecha de Cálculo: {resultado.fecha_calculo.strftime('%Y-%m-%d %H:%M:%S')}\n"
        reporte += f"{linea}\n"
        
        return reporte
    
    def _nombre_riesgo(self) -> str:
        """Retorna el nombre descriptivo del nivel de riesgo"""
        nombres = {
            1: "Mínimo",
            2: "Bajo",
            3: "Medio",
            4: "Alto",
            5: "Máximo"
        }
        return nombres.get(self.nivel_riesgo_arl, "Desconocido")


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def calcular_pila_rapido(salario: float, riesgo_arl: int = 1) -> Dict:
    """
    Función de conveniencia para cálculo rápido
    
    Args:
        salario: Salario mensual en COP
        riesgo_arl: Nivel de riesgo (1-5), default=1
    
    Returns:
        dict: Diccionario con los valores calculados
    """
    calc = CalculadoraPILA(salario, riesgo_arl)
    resultado = calc.calcular()
    
    return {
        'salario_base': float(resultado.salario_base),
        'total_empleado': float(resultado.total_empleado),
        'total_empleador': float(resultado.total_empleador),
        'total_general': float(resultado.total_general),
        'salud_empleado': float(resultado.salud_empleado),
        'pension_empleado': float(resultado.pension_empleado),
        'salario_neto': float(resultado.salario_base - resultado.total_empleado)
    }


def obtener_smmlv() -> float:
    """Retorna el SMMLV vigente"""
    return float(SMMLV_2025)


def obtener_tabla_arl() -> Dict[int, float]:
    """Retorna la tabla de tasas ARL"""
    return {k: float(v) for k, v in TABLA_ARL.items()}


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    print("\n🧮 MOTOR DE CÁLCULO PILA - SISTEMA MONTERO\n")
    
    # Ejemplo 1: Salario mínimo, riesgo bajo
    print("=" * 70)
    print("EJEMPLO 1: Empleado con Salario Mínimo")
    print("=" * 70)
    
    calc1 = CalculadoraPILA(salario_base=1300000, nivel_riesgo_arl=1)
    print(calc1.generar_reporte())
    
    # Ejemplo 2: Salario alto con parafiscales
    print("\n" + "=" * 70)
    print("EJEMPLO 2: Empleado con Salario Alto (aplica parafiscales)")
    print("=" * 70)
    
    calc2 = CalculadoraPILA(salario_base=15000000, nivel_riesgo_arl=3)
    print(calc2.generar_reporte())
    
    # Ejemplo 3: Salario menor al mínimo (auto-ajuste)
    print("\n" + "=" * 70)
    print("EJEMPLO 3: Salario Menor al Mínimo (auto-ajuste)")
    print("=" * 70)
    
    calc3 = CalculadoraPILA(salario_base=800000, nivel_riesgo_arl=2)
    print(calc3.generar_reporte())
