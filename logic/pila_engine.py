"""
Motor de Cálculo de Seguridad Social (PILA) - Colombia
Sistema Montero - Lógica de Negocio Pura

VERSIÓN 1.1 - CORRECCIONES LEGALES
===================================
✓ CCF 4% se calcula SIEMPRE (sin umbral de 10 SMMLV)
✓ Exoneración de Salud Empleador para salarios < 10 SMMLV
✓ Tope IBC máximo de 25 SMMLV
✓ Soporte para Salario Integral (IBC = 70% del salario)

Este módulo implementa el cálculo exacto de aportes a Seguridad Social
según la legislación laboral colombiana vigente.

Autor: Sistema Montero
Fecha: 2025-11-26
Versión: 1.1.0
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
SALUD_EMPLEADOR = Decimal('0.085')    # 8.5% empleador (puede ser exonerado)

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

# PARAFISCALES
# CORRECCIÓN V1.1: CCF 4% SIEMPRE (sin umbral)
CCF_TASA = Decimal('0.04')

# SENA e ICBF solo para salarios < 10 SMMLV
SENA_TASA = Decimal('0.02')
ICBF_TASA = Decimal('0.03')
UMBRAL_SENA_ICBF = SMMLV_2025 * 10

# TOPES IBC
IBC_MAXIMO_SMMLV = 25  # Tope máximo de 25 SMMLV
IBC_MAXIMO = SMMLV_2025 * IBC_MAXIMO_SMMLV

# EXONERACIÓN DE SALUD
UMBRAL_EXONERACION_SALUD = SMMLV_2025 * 10  # Empresas con salarios < 10 SMMLV

# SALARIO INTEGRAL
PORCENTAJE_IBC_SALARIO_INTEGRAL = Decimal('0.70')  # 70% del salario base


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
    ibc: Decimal  # Ingreso Base de Cotización
    nivel_riesgo_arl: int
    es_salario_integral: bool
    es_empresa_exonerada: bool
    
    # Salud
    salud_empleado: Decimal
    salud_empleador: Decimal
    salud_total: Decimal
    salud_empleador_exonerado: bool
    
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
    aplica_sena_icbf: bool
    
    # Totales
    total_empleado: Decimal
    total_empleador: Decimal
    total_general: Decimal
    
    # Metadata
    fecha_calculo: datetime
    salario_ajustado: bool
    ibc_limitado: bool  # True si se aplicó tope de 25 SMMLV
    advertencias: list


# ============================================================================
# MOTOR DE CÁLCULO
# ============================================================================

class CalculadoraPILA:
    """
    Calculadora de Seguridad Social para Colombia - Versión 1.1
    
    MEJORAS EN VERSIÓN 1.1:
    - CCF 4% se calcula SIEMPRE (sin umbral)
    - Exoneración de Salud Empleador para salarios < 10 SMMLV
    - Tope IBC máximo de 25 SMMLV
    - Soporte para Salario Integral (IBC = 70%)
    
    Implementa la lógica pura de negocio sin dependencias de base de datos.
    Todos los cálculos se realizan con precisión Decimal para evitar
    errores de redondeo financiero.
    
    Ejemplo de uso:
        >>> calc = CalculadoraPILA(
        ...     salario_base=1300000,
        ...     nivel_riesgo_arl=1,
        ...     es_empresa_exonerada=True
        ... )
        >>> resultado = calc.calcular()
        >>> print(f"Total empleado: ${resultado.total_empleado:,.0f}")
        Total empleado: $104,000
    """
    
    def __init__(
        self,
        salario_base: float,
        nivel_riesgo_arl: int,
        es_empresa_exonerada: bool = True,
        es_salario_integral: bool = False
    ):
        """
        Inicializa la calculadora
        
        Args:
            salario_base: Salario mensual del empleado en COP
            nivel_riesgo_arl: Nivel de riesgo ARL (1=Mínimo a 5=Máximo)
            es_empresa_exonerada: Si aplica exoneración de Salud Empleador (default: True)
            es_salario_integral: Si el salario es integral (IBC = 70%)
        
        Raises:
            ValueError: Si los parámetros son inválidos
        """
        self.salario_base = Decimal(str(salario_base))
        self.nivel_riesgo_arl = nivel_riesgo_arl
        self.es_empresa_exonerada = es_empresa_exonerada
        self.es_salario_integral = es_salario_integral
        self.advertencias = []
        self.salario_ajustado = False
        self.ibc_limitado = False
        
        # Validaciones
        self._validar_parametros()
        
        # Calcular IBC
        self.ibc = self._calcular_ibc()
        
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
    
    def _calcular_ibc(self) -> Decimal:
        """
        Calcula el IBC (Ingreso Base de Cotización)
        
        CORRECCIÓN V1.1: Implementa:
        1. Salario Integral: IBC = 70% del salario
        2. Tope Máximo: IBC no puede superar 25 SMMLV
        3. Si no aplica ninguna excepción: IBC = salario base
        
        Returns:
            Decimal: IBC calculado
        """
        # REGLA 1: Salario Integral (IBC = 70%)
        if self.es_salario_integral:
            ibc = self.salario_base * PORCENTAJE_IBC_SALARIO_INTEGRAL
            self.advertencias.append(
                f"ℹ️ Salario Integral detectado: IBC = 70% de ${self.salario_base:,.0f} = ${ibc:,.0f}"
            )
            
            # Validar que el IBC integral no supere el tope de 25 SMMLV
            if ibc > IBC_MAXIMO:
                self.advertencias.append(
                    f"⚠️ IBC integral ${ibc:,.0f} supera el tope de 25 SMMLV. "
                    f"Limitado a ${IBC_MAXIMO:,.0f}"
                )
                ibc = IBC_MAXIMO
                self.ibc_limitado = True
            
            return ibc
        
        # REGLA 2: Tope Máximo de 25 SMMLV (para salarios ordinarios)
        if self.salario_base > IBC_MAXIMO:
            self.advertencias.append(
                f"ℹ️ Salario ${self.salario_base:,.0f} supera el tope de 25 SMMLV. "
                f"IBC limitado a ${IBC_MAXIMO:,.0f}"
            )
            self.ibc_limitado = True
            return IBC_MAXIMO
        
        # REGLA 3: IBC = Salario Base (caso normal)
        return self.salario_base
    
    def _redondear(self, valor: Decimal) -> Decimal:
        """
        Redondea un valor decimal al peso más cercano
        Usa redondeo bancario (ROUND_HALF_UP) según normas contables
        """
        return valor.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    
    def _calcular_salud(self) -> Dict[str, Decimal]:
        """
        Calcula aportes de salud
        
        CORRECCIÓN V1.1: Implementa exoneración de Salud Empleador
        Si es_empresa_exonerada=True y salario < 10 SMMLV:
            Salud Empleador = $0
        """
        salud_empleado = self._redondear(self.ibc * SALUD_EMPLEADO)
        
        # CORRECCIÓN V1.1: Exoneración de Salud Empleador
        salud_empleador_exonerado = False
        if self.es_empresa_exonerada and self.salario_base < UMBRAL_EXONERACION_SALUD:
            salud_empleador = Decimal('0')
            salud_empleador_exonerado = True
            self.advertencias.append(
                f"✓ Exoneración de Salud Empleador aplicada "
                f"(salario ${self.salario_base:,.0f} < 10 SMMLV)"
            )
        else:
            salud_empleador = self._redondear(self.ibc * SALUD_EMPLEADOR)
        
        return {
            'empleado': salud_empleado,
            'empleador': salud_empleador,
            'total': salud_empleado + salud_empleador,
            'exonerado': salud_empleador_exonerado
        }
    
    def _calcular_pension(self) -> Dict[str, Decimal]:
        """Calcula aportes de pensión"""
        pension_empleado = self._redondear(self.ibc * PENSION_EMPLEADO)
        pension_empleador = self._redondear(self.ibc * PENSION_EMPLEADOR)
        
        return {
            'empleado': pension_empleado,
            'empleador': pension_empleador,
            'total': pension_empleado + pension_empleador
        }
    
    def _calcular_arl(self) -> Dict[str, Decimal]:
        """Calcula aportes de ARL (100% empleador)"""
        tasa = TABLA_ARL[self.nivel_riesgo_arl]
        arl_empleador = self._redondear(self.ibc * tasa)
        
        return {
            'empleador': arl_empleador,
            'tasa': tasa
        }
    
    def _calcular_parafiscales(self) -> Dict[str, Decimal]:
        """
        Calcula aportes parafiscales
        
        CORRECCIÓN V1.1: CCF 4% SIEMPRE (sin umbral de 10 SMMLV)
        SENA e ICBF solo para salarios < 10 SMMLV
        """
        # CORRECCIÓN V1.1: CCF se calcula SIEMPRE
        ccf = self._redondear(self.ibc * CCF_TASA)
        
        # SENA e ICBF solo para salarios < 10 SMMLV
        aplica_sena_icbf = self.salario_base < UMBRAL_SENA_ICBF
        
        if aplica_sena_icbf:
            sena = self._redondear(self.ibc * SENA_TASA)
            icbf = self._redondear(self.ibc * ICBF_TASA)
        else:
            sena = Decimal('0')
            icbf = Decimal('0')
            self.advertencias.append(
                f"ℹ️ SENA e ICBF no aplicables (salario >= 10 SMMLV: ${UMBRAL_SENA_ICBF:,.0f})"
            )
        
        return {
            'ccf': ccf,
            'sena': sena,
            'icbf': icbf,
            'total': ccf + sena + icbf,
            'aplica_sena_icbf': aplica_sena_icbf
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
            ibc=self.ibc,
            nivel_riesgo_arl=self.nivel_riesgo_arl,
            es_salario_integral=self.es_salario_integral,
            es_empresa_exonerada=self.es_empresa_exonerada,
            
            # Salud
            salud_empleado=salud['empleado'],
            salud_empleador=salud['empleador'],
            salud_total=salud['total'],
            salud_empleador_exonerado=salud['exonerado'],
            
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
            aplica_sena_icbf=parafiscales['aplica_sena_icbf'],
            
            # Totales
            total_empleado=total_empleado,
            total_empleador=total_empleador,
            total_general=total_general,
            
            # Metadata
            fecha_calculo=datetime.now(),
            salario_ajustado=self.salario_ajustado,
            ibc_limitado=self.ibc_limitado,
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
                    Sistema Montero v1.1
{linea}

DATOS DEL EMPLEADO:
  • Salario Base:        ${resultado.salario_base:>15,.0f} COP
  • IBC (Base Cotiz.):   ${resultado.ibc:>15,.0f} COP
  • Nivel Riesgo ARL:    {resultado.nivel_riesgo_arl} ({self._nombre_riesgo()})
  • Tasa ARL:            {resultado.tasa_arl * 100:>15.3f}%
  • Salario Integral:    {'SÍ' if resultado.es_salario_integral else 'NO'}
  • Empresa Exonerada:   {'SÍ' if resultado.es_empresa_exonerada else 'NO'}
  
{linea}
CONCEPTOS DE LIQUIDACIÓN:
{linea}

1. SALUD (12.5% total)
   Empleado (4%):        ${resultado.salud_empleado:>15,.0f} COP
   Empleador (8.5%):     ${resultado.salud_empleador:>15,.0f} COP {'(EXONERADO)' if resultado.salud_empleador_exonerado else ''}
   ─────────────────────────────────────────
   Subtotal Salud:       ${resultado.salud_total:>15,.0f} COP

2. PENSIÓN (16% total)
   Empleado (4%):        ${resultado.pension_empleado:>15,.0f} COP
   Empleador (12%):      ${resultado.pension_empleador:>15,.0f} COP
   ─────────────────────────────────────────
   Subtotal Pensión:     ${resultado.pension_total:>15,.0f} COP

3. ARL (100% empleador)
   Empleador ({resultado.tasa_arl * 100:.3f}%):     ${resultado.arl_empleador:>15,.0f} COP

4. PARAFISCALES
   CCF (4%):             ${resultado.ccf:>15,.0f} COP [SIEMPRE]
   SENA (2%):            ${resultado.sena:>15,.0f} COP {'[< 10 SMMLV]' if resultado.aplica_sena_icbf else '[NO APLICA]'}
   ICBF (3%):            ${resultado.icbf:>15,.0f} COP {'[< 10 SMMLV]' if resultado.aplica_sena_icbf else '[NO APLICA]'}
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
            reporte += "\nADVERTENCIAS Y NOTAS:\n"
            for adv in resultado.advertencias:
                reporte += f"  {adv}\n"
            reporte += f"\n{linea}\n"
        
        reporte += f"\nFecha de Cálculo: {resultado.fecha_calculo.strftime('%Y-%m-%d %H:%M:%S')}\n"
        reporte += f"Versión Motor PILA: 1.1.0\n"
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

def calcular_pila_rapido(
    salario: float,
    riesgo_arl: int = 1,
    exonerada: bool = True,
    integral: bool = False
) -> Dict:
    """
    Función de conveniencia para cálculo rápido
    
    Args:
        salario: Salario mensual en COP
        riesgo_arl: Nivel de riesgo (1-5), default=1
        exonerada: Si aplica exoneración de salud, default=True
        integral: Si es salario integral, default=False
    
    Returns:
        dict: Diccionario con los valores calculados
    """
    calc = CalculadoraPILA(salario, riesgo_arl, exonerada, integral)
    resultado = calc.calcular()
    
    return {
        'salario_base': float(resultado.salario_base),
        'ibc': float(resultado.ibc),
        'total_empleado': float(resultado.total_empleado),
        'total_empleador': float(resultado.total_empleador),
        'total_general': float(resultado.total_general),
        'salud_empleado': float(resultado.salud_empleado),
        'pension_empleado': float(resultado.pension_empleado),
        'salario_neto': float(resultado.salario_base - resultado.total_empleado),
        'advertencias': resultado.advertencias
    }


def obtener_smmlv() -> float:
    """Retorna el SMMLV vigente"""
    return float(SMMLV_2025)


def obtener_tabla_arl() -> Dict[int, float]:
    """Retorna la tabla de tasas ARL"""
    return {k: float(v * 100) for k, v in TABLA_ARL.items()}  # Retorna en %


def obtener_tope_ibc() -> float:
    """Retorna el tope máximo de IBC (25 SMMLV)"""
    return float(IBC_MAXIMO)


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    print("\n🧮 MOTOR DE CÁLCULO PILA v1.1 - SISTEMA MONTERO\n")
    print("NUEVAS FUNCIONALIDADES:")
    print("  ✓ CCF 4% SIEMPRE (sin umbral)")
    print("  ✓ Exoneración de Salud Empleador < 10 SMMLV")
    print("  ✓ Tope IBC máximo 25 SMMLV")
    print("  ✓ Soporte Salario Integral (IBC = 70%)\n")
    
    # Ejemplo 1: Salario mínimo con exoneración
    print("=" * 70)
    print("EJEMPLO 1: Empleado con Salario Mínimo (CON Exoneración)")
    print("=" * 70)
    
    calc1 = CalculadoraPILA(
        salario_base=1300000,
        nivel_riesgo_arl=1,
        es_empresa_exonerada=True
    )
    print(calc1.generar_reporte())
    
    # Ejemplo 2: Salario alto sin exoneración
    print("\n" + "=" * 70)
    print("EJEMPLO 2: Empleado con Salario Alto (SIN Exoneración)")
    print("=" * 70)
    
    calc2 = CalculadoraPILA(
        salario_base=15000000,
        nivel_riesgo_arl=3,
        es_empresa_exonerada=False
    )
    print(calc2.generar_reporte())
    
    # Ejemplo 3: Salario integral
    print("\n" + "=" * 70)
    print("EJEMPLO 3: Salario Integral (IBC = 70%)")
    print("=" * 70)
    
    calc3 = CalculadoraPILA(
        salario_base=25000000,
        nivel_riesgo_arl=2,
        es_empresa_exonerada=False,
        es_salario_integral=True
    )
    print(calc3.generar_reporte())
    
    # Ejemplo 4: Salario que supera el tope de 25 SMMLV
    print("\n" + "=" * 70)
    print("EJEMPLO 4: Salario > 25 SMMLV (Tope IBC)")
    print("=" * 70)
    
    calc4 = CalculadoraPILA(
        salario_base=35000000,
        nivel_riesgo_arl=4,
        es_empresa_exonerada=False
    )
    print(calc4.generar_reporte())
