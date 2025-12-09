#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
logic/pila_engine.py
====================
Motor de Liquidación PILA Real - Seguridad Social Colombiana
Fase 11: Cálculos exactos según normativa vigente 2025

Autor: Senior Backend Developer & Data Scientist
Fecha: 2025-11-30
"""

from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional
from dataclasses import dataclass


class ConfiguracionPILA:
    """
    Configuración de valores legales para liquidación PILA 2025
    """
    # Valores base 2025
    SMMLV = Decimal('1300000')  # Salario Mínimo Mensual Legal Vigente
    AUX_TRANSPORTE = Decimal('162000')  # Auxilio de Transporte 2025
    UVT = Decimal('47065')  # Unidad de Valor Tributario 2025

    # Tarifas de aportes (porcentajes)
    SALUD_EMPLEADO = Decimal('4.0')  # 4%
    SALUD_EMPLEADOR = Decimal('8.5')  # 8.5%
    PENSION_EMPLEADO = Decimal('4.0')  # 4%
    PENSION_EMPLEADOR = Decimal('12.0')  # 12%

    # ARL - Riesgo I (mínimo)
    ARL_CLASE_1 = Decimal('0.522')  # 0.522%
    ARL_CLASE_2 = Decimal('1.044')
    ARL_CLASE_3 = Decimal('2.436')
    ARL_CLASE_4 = Decimal('4.350')
    ARL_CLASE_5 = Decimal('6.960')  # Máximo

    # CCF - Caja de Compensación Familiar
    CCF_EMPLEADOR = Decimal('4.0')  # 4%

    # SENA e ICBF (aplica para empresas con más de cierto límite)
    SENA = Decimal('2.0')  # 2%
    ICBF = Decimal('3.0')  # 3%

    # Topes para IBC
    IBC_MINIMO = SMMLV
    IBC_MAXIMO = SMMLV * 25  # 25 SMMLV

    # Días estándar por mes
    DIAS_MES_ESTANDAR = 30


class LiquidadorPILA:
    """
    Motor de Liquidación PILA con lógica real de seguridad social colombiana.

    Maneja:
    - Cálculo de IBC (Ingreso Base de Cotización)
    - Ajuste por días trabajados
    - Novedades (Ingreso, Retiro, Incapacidad, Licencia)
    - Validaciones legales
    - Cálculo de aportes exactos
    """

    def __init__(self, config: Optional[ConfiguracionPILA] = None):
        """
        Inicializa el liquidador con configuración PILA.

        Args:
            config: Configuración PILA (usa valores por defecto si no se provee)
        """
        self.config = config or ConfiguracionPILA()

    def calcular_linea(
        self,
        usuario: Dict,
        dias_trabajados: int = 30,
        novedades: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Calcula una línea completa de planilla PILA para un usuario.

        Args:
            usuario: Diccionario con datos del usuario
                {
                    'numeroId': str,
                    'primerNombre': str,
                    'primerApellido': str,
                    'ibc': float,  # Ingreso Base de Cotización
                    'salario': float,  # Salario mensual
                    'epsNombre': str,
                    'afpNombre': str,
                    'arlNombre': str,
                    'arlClase': int (1-5),
                    'tipoContrato': str  # 'Indefinido', 'Temporal', etc.
                }
            dias_trabajados: Días efectivos trabajados en el mes (1-30)
            novedades: Lista de novedades que afectan la liquidación
                [
                    {'tipo': 'Ingreso', 'fecha': '2025-01-15'},
                    {'tipo': 'Incapacidad', 'dias': 5, 'tipo_incapacidad': 'EG'},
                    {'tipo': 'Licencia', 'dias': 3, 'remunerada': True}
                ]

        Returns:
            Dict con la línea PILA completa
        """
        resultado = {
            'usuario_id': usuario.get('numeroId'),
            'nombre_completo': f"{usuario.get('primerNombre')} {usuario.get('primerApellido')}",
            'novedades_procesadas': [],
            'alertas': [],
            'marca_novedad': '',
            'validaciones': []
        }

        # PASO 1: PROCESAR NOVEDADES
        novedades = novedades or []
        dias_ajustados = dias_trabajados
        tiene_incapacidad = False
        tipo_incapacidad = None

        for novedad in novedades:
            tipo_nov = novedad.get('tipo', '').upper()

            if tipo_nov == 'INGRESO':
                fecha_ingreso = novedad.get('fecha')
                if fecha_ingreso:
                    dia_ingreso = int(fecha_ingreso.split('-')[-1])
                    dias_ajustados = self.config.DIAS_MES_ESTANDAR - dia_ingreso + 1
                    resultado['novedades_procesadas'].append(
                        f"INGRESO: Día {dia_ingreso}, cotiza {dias_ajustados} días"
                    )
                    resultado['marca_novedad'] = 'IGE'

            elif tipo_nov == 'RETIRO':
                fecha_retiro = novedad.get('fecha')
                if fecha_retiro:
                    dia_retiro = int(fecha_retiro.split('-')[-1])
                    dias_ajustados = dia_retiro
                    resultado['novedades_procesadas'].append(
                        f"RETIRO: Día {dia_retiro}, cotiza {dias_ajustados} días"
                    )
                    resultado['marca_novedad'] = 'RET'

            elif tipo_nov in ['INCAPACIDAD', 'INC']:
                tiene_incapacidad = True
                dias_inc = novedad.get('dias', 0)
                tipo_incapacidad = novedad.get('tipo_incapacidad', 'EG')

                if tipo_incapacidad == 'EG':
                    resultado['marca_novedad'] = 'LGE'
                    resultado['novedades_procesadas'].append(
                        f"INCAPACIDAD EG: {dias_inc} días (marca LGE)"
                    )

        # PASO 2: CALCULAR IBC
        ibc_base = Decimal(str(usuario.get('ibc', usuario.get('salario', 0))))

        if dias_ajustados < self.config.DIAS_MES_ESTANDAR:
            ibc_calculado = (ibc_base / self.config.DIAS_MES_ESTANDAR) * Decimal(str(dias_ajustados))
        else:
            ibc_calculado = ibc_base

        # VALIDACIÓN: IBC mínimo
        if ibc_calculado < self.config.IBC_MINIMO and dias_ajustados >= self.config.DIAS_MES_ESTANDAR:
            resultado['alertas'].append(
                f"IBC ${ibc_calculado:,.0f} menor al SMMLV"
            )
            ibc_calculado = self.config.IBC_MINIMO

        resultado['ibc_calculado'] = ibc_calculado
        resultado['dias_cotizados'] = dias_ajustados

        # PASO 3: CALCULAR APORTES
        salud_empleado = (ibc_calculado * self.config.SALUD_EMPLEADO / 100).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        salud_empleador = (ibc_calculado * self.config.SALUD_EMPLEADOR / 100).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        pension_empleado = (ibc_calculado * self.config.PENSION_EMPLEADO / 100).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        pension_empleador = (ibc_calculado * self.config.PENSION_EMPLEADOR / 100).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

        clase_arl = usuario.get('arlClase', 1)
        tarifa_arl_map = {
            1: self.config.ARL_CLASE_1,
            2: self.config.ARL_CLASE_2,
            3: self.config.ARL_CLASE_3,
            4: self.config.ARL_CLASE_4,
            5: self.config.ARL_CLASE_5
        }
        tarifa_arl = tarifa_arl_map.get(clase_arl, self.config.ARL_CLASE_1)
        arl = (ibc_calculado * tarifa_arl / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        ccf = (ibc_calculado * self.config.CCF_EMPLEADOR / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        total_empleado = salud_empleado + pension_empleado
        total_empleador = salud_empleador + pension_empleador + arl + ccf
        total_aportes = total_empleado + total_empleador

        resultado.update({
            'salud_empleado': float(salud_empleado),
            'salud_empleador': float(salud_empleador),
            'pension_empleado': float(pension_empleado),
            'pension_empleador': float(pension_empleador),
            'arl': float(arl),
            'arl_clase': clase_arl,
            'arl_tarifa': float(tarifa_arl),
            'ccf': float(ccf),
            'total_empleado': float(total_empleado),
            'total_empleador': float(total_empleador),
            'total_aportes': float(total_aportes),
            'ibc_calculado': float(ibc_calculado),
            'ibc_base': float(ibc_base)
        })

        if not resultado['alertas']:
            resultado['validaciones'].append("Liquidación correcta")

        return resultado

    def validar_planilla(self, lineas: List[Dict]) -> Dict:
        """Valida planilla completa"""
        errores = []
        advertencias = []
        total_aportes = Decimal('0')

        for i, linea in enumerate(lineas, start=1):
            ibc = Decimal(str(linea.get('ibc_calculado', 0)))
            if ibc < self.config.IBC_MINIMO:
                errores.append(f"Línea {i}: IBC menor al mínimo legal")

            dias = linea.get('dias_cotizados', 0)
            if dias < 1 or dias > 30:
                errores.append(f"Línea {i}: Días inválidos ({dias})")

            total_aportes += Decimal(str(linea.get('total_aportes', 0)))

        return {
            'valida': len(errores) == 0,
            'errores': errores,
            'advertencias': advertencias,
            'total_aportes': float(total_aportes),
            'total_empleados': len(lineas)
        }


if __name__ == "__main__":
    print("=" * 80)
    print("PRUEBA MOTOR PILA")
    print("=" * 80)

    liquidador = LiquidadorPILA()

    usuario_prueba = {
        'numeroId': '1234567890',
        'primerNombre': 'Juan',
        'primerApellido': 'Pérez',
        'ibc': 1500000,
        'salario': 1500000,
        'arlClase': 1
    }

    resultado = liquidador.calcular_linea(usuario_prueba, dias_trabajados=30)

    print(f"\nUsuario: {resultado['nombre_completo']}")
    print(f"IBC: ${resultado['ibc_calculado']:,.0f}")
    print(f"Días: {resultado['dias_cotizados']}")
    print(f"Total aportes: ${resultado['total_aportes']:,.0f}")
    print("=" * 80)


# ============================================================================
# CONSTANTES ADICIONALES PARA CalculadoraPILA - Seguridad Social 2025
# ============================================================================

# SALUD (12.5% total)
SALUD_TOTAL = Decimal('0.125')
SALUD_EMPLEADO = Decimal('0.04')      # 4% empleado
SALUD_EMPLEADOR = Decimal('0.085')    # 8.5% empleador (puede ser exonerado)

# PENSIÓN (16% total)
PENSION_TOTAL = Decimal('0.16')
PENSION_EMPLEADO = Decimal('0.04')    # 4% empleado
PENSION_EMPLEADOR = Decimal('0.12')   # 12% empleador

# ARL (Administradora de Riesgos Laborales) - Según nivel de riesgo
TABLA_ARL = {
    1: Decimal('0.00522'),   # Riesgo I (Mínimo): 0.522%
    2: Decimal('0.01044'),   # Riesgo II (Bajo): 1.044%
    3: Decimal('0.02436'),   # Riesgo III (Medio): 2.436%
    4: Decimal('0.04350'),   # Riesgo IV (Alto): 4.350%
    5: Decimal('0.06960')    # Riesgo V (Máximo): 6.960%
}

# PARAFISCALES
CCF_TASA = Decimal('0.04')
SENA_TASA = Decimal('0.02')
ICBF_TASA = Decimal('0.03')

# TOPES IBC
IBC_MAXIMO_SMMLV = 25  # Tope máximo de 25 SMMLV
IBC_MAXIMO = Decimal('1300000') * IBC_MAXIMO_SMMLV  # 32.5M
UMBRAL_SENA_ICBF = Decimal('1300000') * 10  # 10 SMMLV
UMBRAL_EXONERACION_SALUD = Decimal('1300000') * 10

# SALARIO INTEGRAL
PORCENTAJE_IBC_SALARIO_INTEGRAL = Decimal('0.70')  # 70% del salario base


# ============================================================================
# DATACLASS para resultado de CalculadoraPILA
# ============================================================================

@dataclass
class LiquidacionPILA:
    """
    Resultado completo de la liquidación de Seguridad Social
    Todos los valores en pesos colombianos (COP)
    """
    # Datos de entrada
    salario_base: Decimal
    ibc: Decimal
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
    ibc_limitado: bool
    advertencias: list


# ============================================================================
# CLASE CalculadoraPILA - Usada por routes/cotizaciones.py
# ============================================================================

class CalculadoraPILA:
    """
    Calculadora de Seguridad Social para Colombia - Versión 1.1
    
    Implementa la lógica pura de negocio para cálculo de aportes PILA.
    """
    
    def __init__(
        self,
        salario_base: float,
        nivel_riesgo_arl: int,
        es_empresa_exonerada: bool = True,
        es_salario_integral: bool = False
    ):
        self.salario_base = Decimal(str(salario_base))
        self.nivel_riesgo_arl = nivel_riesgo_arl
        self.es_empresa_exonerada = es_empresa_exonerada
        self.es_salario_integral = es_salario_integral
        self.advertencias = []
        self.salario_ajustado = False
        self.ibc_limitado = False
        
        self._validar_parametros()
        self.ibc = self._calcular_ibc()
        
    def _validar_parametros(self):
        """Valida los parámetros de entrada"""
        if self.nivel_riesgo_arl not in TABLA_ARL:
            raise ValueError(
                f"Nivel de riesgo ARL inválido: {self.nivel_riesgo_arl}. "
                f"Debe estar entre 1 y 5."
            )
        
        if self.salario_base <= 0:
            raise ValueError(
                f"El salario base debe ser mayor a cero. "
                f"Recibido: ${self.salario_base:,.2f}"
            )
        
        SMMLV = Decimal('1300000')
        if self.salario_base < SMMLV:
            self.salario_base = SMMLV
            self.salario_ajustado = True
    
    def _calcular_ibc(self) -> Decimal:
        """Calcula el IBC (Ingreso Base de Cotización)"""
        if self.es_salario_integral:
            ibc = self.salario_base * PORCENTAJE_IBC_SALARIO_INTEGRAL
            if ibc > IBC_MAXIMO:
                ibc = IBC_MAXIMO
                self.ibc_limitado = True
            return ibc
        
        if self.salario_base > IBC_MAXIMO:
            self.ibc_limitado = True
            return IBC_MAXIMO
        
        return self.salario_base
    
    def _redondear(self, valor: Decimal) -> Decimal:
        """Redondea un valor decimal al peso más cercano"""
        return valor.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    
    def _calcular_salud(self) -> Dict[str, Decimal]:
        """Calcula aportes de salud"""
        salud_empleado = self._redondear(self.ibc * SALUD_EMPLEADO)
        
        salud_empleador_exonerado = False
        if self.es_empresa_exonerada and self.salario_base < UMBRAL_EXONERACION_SALUD:
            salud_empleador = Decimal('0')
            salud_empleador_exonerado = True
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
        """Calcula aportes parafiscales"""
        ccf = self._redondear(self.ibc * CCF_TASA)
        
        aplica_sena_icbf = self.salario_base < UMBRAL_SENA_ICBF
        
        if aplica_sena_icbf:
            sena = self._redondear(self.ibc * SENA_TASA)
            icbf = self._redondear(self.ibc * ICBF_TASA)
        else:
            sena = Decimal('0')
            icbf = Decimal('0')
        
        return {
            'ccf': ccf,
            'sena': sena,
            'icbf': icbf,
            'total': ccf + sena + icbf,
            'aplica_sena_icbf': aplica_sena_icbf
        }
    
    def calcular(self) -> LiquidacionPILA:
        """Ejecuta el cálculo completo de Seguridad Social"""
        salud = self._calcular_salud()
        pension = self._calcular_pension()
        arl = self._calcular_arl()
        parafiscales = self._calcular_parafiscales()
        
        total_empleado = salud['empleado'] + pension['empleado']
        total_empleador = (
            salud['empleador'] +
            pension['empleador'] +
            arl['empleador'] +
            parafiscales['total']
        )
        total_general = total_empleado + total_empleador
        
        return LiquidacionPILA(
            salario_base=self.salario_base,
            ibc=self.ibc,
            nivel_riesgo_arl=self.nivel_riesgo_arl,
            es_salario_integral=self.es_salario_integral,
            es_empresa_exonerada=self.es_empresa_exonerada,
            salud_empleado=salud['empleado'],
            salud_empleador=salud['empleador'],
            salud_total=salud['total'],
            salud_empleador_exonerado=salud['exonerado'],
            pension_empleado=pension['empleado'],
            pension_empleador=pension['empleador'],
            pension_total=pension['total'],
            arl_empleador=arl['empleador'],
            tasa_arl=arl['tasa'],
            ccf=parafiscales['ccf'],
            sena=parafiscales['sena'],
            icbf=parafiscales['icbf'],
            parafiscales_total=parafiscales['total'],
            aplica_sena_icbf=parafiscales['aplica_sena_icbf'],
            total_empleado=total_empleado,
            total_empleador=total_empleador,
            total_general=total_general,
            fecha_calculo=datetime.now(),
            salario_ajustado=self.salario_ajustado,
            ibc_limitado=self.ibc_limitado,
            advertencias=self.advertencias.copy()
        )
