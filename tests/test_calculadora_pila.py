"""
Suite de Pruebas Unitarias para el Motor PILA
Sistema Montero - Tests de Cálculo de Seguridad Social

Ejecutar con: pytest tests/test_calculadora_pila.py -v
O con: python -m pytest tests/test_calculadora_pila.py -v --cov=logic
"""

import pytest
import sys
from pathlib import Path
from decimal import Decimal

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from logic.pila_engine import (
    CalculadoraPILA,
    calcular_pila_rapido,
    obtener_smmlv,
    obtener_tabla_arl,
    SMMLV_2025,
    TABLA_ARL
)


class TestCalculadoraPILABasico:
    """Pruebas básicas de funcionalidad"""
    
    def test_salario_minimo_riesgo_1(self):
        """
        Prueba con salario mínimo y riesgo mínimo (I)
        Verificación exacta al peso de cada concepto
        """
        calc = CalculadoraPILA(salario_base=1300000, nivel_riesgo_arl=1)
        resultado = calc.calcular()
        
        # Verificar salario base
        assert resultado.salario_base == Decimal('1300000')
        assert resultado.nivel_riesgo_arl == 1
        
        # SALUD - Empleado 4%
        assert resultado.salud_empleado == Decimal('52000')  # 1,300,000 * 0.04
        
        # SALUD - Empleador 8.5%
        assert resultado.salud_empleador == Decimal('110500')  # 1,300,000 * 0.085
        
        # SALUD - Total 12.5%
        assert resultado.salud_total == Decimal('162500')  # 52,000 + 110,500
        
        # PENSIÓN - Empleado 4%
        assert resultado.pension_empleado == Decimal('52000')  # 1,300,000 * 0.04
        
        # PENSIÓN - Empleador 12%
        assert resultado.pension_empleador == Decimal('156000')  # 1,300,000 * 0.12
        
        # PENSIÓN - Total 16%
        assert resultado.pension_total == Decimal('208000')  # 52,000 + 156,000
        
        # ARL - Empleador (Riesgo I = 0.522%)
        assert resultado.arl_empleador == Decimal('6786')  # 1,300,000 * 0.00522
        assert resultado.tasa_arl == Decimal('0.00522')
        
        # PARAFISCALES - No aplican (salario < 10 SMMLV)
        assert resultado.aplica_parafiscales == False
        assert resultado.ccf == Decimal('0')
        assert resultado.sena == Decimal('0')
        assert resultado.icbf == Decimal('0')
        assert resultado.parafiscales_total == Decimal('0')
        
        # TOTALES
        assert resultado.total_empleado == Decimal('104000')  # 52,000 + 52,000
        assert resultado.total_empleador == Decimal('273286')  # 110,500 + 156,000 + 6,786
        assert resultado.total_general == Decimal('377286')  # 104,000 + 273,286
        
        # Metadata
        assert resultado.salario_ajustado == False
        assert len(resultado.advertencias) == 0
    
    def test_salario_minimo_riesgo_5(self):
        """
        Prueba con salario mínimo y riesgo máximo (V)
        """
        calc = CalculadoraPILA(salario_base=1300000, nivel_riesgo_arl=5)
        resultado = calc.calcular()
        
        # Salud y Pensión no cambian
        assert resultado.salud_empleado == Decimal('52000')
        assert resultado.pension_empleado == Decimal('52000')
        
        # ARL cambia según nivel de riesgo (Riesgo V = 6.960%)
        assert resultado.arl_empleador == Decimal('90480')  # 1,300,000 * 0.0696
        assert resultado.tasa_arl == Decimal('0.06960')
        
        # Total empleador aumenta por ARL
        assert resultado.total_empleador == Decimal('356980')  # 110,500 + 156,000 + 90,480
    
    def test_salario_alto_con_parafiscales(self):
        """
        Prueba con salario > 10 SMMLV (aplican parafiscales)
        """
        salario_alto = 15000000  # 15 millones (>10 SMMLV)
        calc = CalculadoraPILA(salario_base=salario_alto, nivel_riesgo_arl=3)
        resultado = calc.calcular()
        
        # Verificar que aplican parafiscales
        assert resultado.aplica_parafiscales == True
        
        # CCF = 4%
        assert resultado.ccf == Decimal('600000')  # 15,000,000 * 0.04
        
        # SENA = 2%
        assert resultado.sena == Decimal('300000')  # 15,000,000 * 0.02
        
        # ICBF = 3%
        assert resultado.icbf == Decimal('450000')  # 15,000,000 * 0.03
        
        # Total parafiscales = 9%
        assert resultado.parafiscales_total == Decimal('1350000')  # 600k + 300k + 450k
        
        # Verificar advertencia
        assert len(resultado.advertencias) > 0
        assert any('parafiscales' in adv.lower() for adv in resultado.advertencias)
    
    def test_todos_los_niveles_riesgo(self):
        """
        Verifica que todos los niveles de riesgo ARL calculen correctamente
        """
        salario = 2000000
        resultados_arl = {}
        
        for nivel in range(1, 6):
            calc = CalculadoraPILA(salario_base=salario, nivel_riesgo_arl=nivel)
            resultado = calc.calcular()
            resultados_arl[nivel] = resultado.arl_empleador
        
        # Verificar que cada nivel tiene un valor diferente y creciente
        assert resultados_arl[1] == Decimal('10440')   # 0.522%
        assert resultados_arl[2] == Decimal('20880')   # 1.044%
        assert resultados_arl[3] == Decimal('48720')   # 2.436%
        assert resultados_arl[4] == Decimal('87000')   # 4.350%
        assert resultados_arl[5] == Decimal('139200')  # 6.960%
        
        # Verificar que son crecientes
        assert resultados_arl[1] < resultados_arl[2] < resultados_arl[3] < resultados_arl[4] < resultados_arl[5]


class TestValidaciones:
    """Pruebas de validación de parámetros"""
    
    def test_salario_menor_al_minimo_autoajuste(self):
        """
        Verifica que salarios menores al mínimo se ajusten automáticamente
        """
        calc = CalculadoraPILA(salario_base=800000, nivel_riesgo_arl=1)
        resultado = calc.calcular()
        
        # Debe ajustarse al SMMLV
        assert resultado.salario_base == SMMLV_2025
        assert resultado.salario_ajustado == True
        
        # Debe tener advertencia
        assert len(resultado.advertencias) > 0
        assert any('menor al SMMLV' in adv for adv in resultado.advertencias)
    
    def test_salario_cero_error(self):
        """
        Verifica que salario cero lance error
        """
        with pytest.raises(ValueError, match="mayor a cero"):
            CalculadoraPILA(salario_base=0, nivel_riesgo_arl=1)
    
    def test_salario_negativo_error(self):
        """
        Verifica que salario negativo lance error
        """
        with pytest.raises(ValueError, match="mayor a cero"):
            CalculadoraPILA(salario_base=-1000, nivel_riesgo_arl=1)
    
    def test_nivel_riesgo_invalido_error(self):
        """
        Verifica que nivel de riesgo inválido lance error
        """
        with pytest.raises(ValueError, match="inválido"):
            CalculadoraPILA(salario_base=1300000, nivel_riesgo_arl=0)
        
        with pytest.raises(ValueError, match="inválido"):
            CalculadoraPILA(salario_base=1300000, nivel_riesgo_arl=6)
        
        with pytest.raises(ValueError, match="inválido"):
            CalculadoraPILA(salario_base=1300000, nivel_riesgo_arl=10)


class TestPrecisionDecimal:
    """Pruebas de precisión en cálculos financieros"""
    
    def test_redondeo_correcto(self):
        """
        Verifica que el redondeo sea correcto (al peso más cercano)
        """
        # Salario que genere decimales
        calc = CalculadoraPILA(salario_base=1234567, nivel_riesgo_arl=1)
        resultado = calc.calcular()
        
        # Ningún valor debe tener decimales
        assert resultado.salud_empleado % 1 == 0
        assert resultado.pension_empleado % 1 == 0
        assert resultado.arl_empleador % 1 == 0
        assert resultado.total_empleado % 1 == 0
        assert resultado.total_empleador % 1 == 0
    
    def test_suma_componentes_igual_total(self):
        """
        Verifica que la suma de componentes siempre sea igual al total
        (evita errores de redondeo)
        """
        calc = CalculadoraPILA(salario_base=3456789, nivel_riesgo_arl=4)
        resultado = calc.calcular()
        
        # Total empleado = salud + pensión
        assert resultado.total_empleado == (
            resultado.salud_empleado + resultado.pension_empleado
        )
        
        # Total empleador = salud + pensión + arl + parafiscales
        assert resultado.total_empleador == (
            resultado.salud_empleador +
            resultado.pension_empleador +
            resultado.arl_empleador +
            resultado.parafiscales_total
        )
        
        # Total general = total empleado + total empleador
        assert resultado.total_general == (
            resultado.total_empleado + resultado.total_empleador
        )


class TestFuncionesUtilidad:
    """Pruebas de funciones auxiliares"""
    
    def test_calcular_pila_rapido(self):
        """
        Verifica la función de conveniencia calcular_pila_rapido()
        """
        resultado = calcular_pila_rapido(salario=1300000, riesgo_arl=1)
        
        # Debe retornar dict con valores float
        assert isinstance(resultado, dict)
        assert isinstance(resultado['total_empleado'], float)
        assert resultado['total_empleado'] == 104000.0
        assert resultado['salario_neto'] == 1196000.0  # 1,300,000 - 104,000
    
    def test_obtener_smmlv(self):
        """
        Verifica que se pueda obtener el SMMLV vigente
        """
        smmlv = obtener_smmlv()
        assert smmlv == 1300000.0
        assert isinstance(smmlv, float)
    
    def test_obtener_tabla_arl(self):
        """
        Verifica que se pueda obtener la tabla de tasas ARL
        """
        tabla = obtener_tabla_arl()
        
        assert len(tabla) == 5
        assert tabla[1] == 0.00522
        assert tabla[5] == 0.06960
        assert all(isinstance(v, float) for v in tabla.values())


class TestCasosReales:
    """Pruebas con casos reales de nómina"""
    
    def test_empleado_administrativo(self):
        """
        Caso: Empleado administrativo (Riesgo I)
        Salario: $2,500,000
        """
        calc = CalculadoraPILA(salario_base=2500000, nivel_riesgo_arl=1)
        resultado = calc.calcular()
        
        assert resultado.salud_empleado == Decimal('100000')
        assert resultado.pension_empleado == Decimal('100000')
        assert resultado.total_empleado == Decimal('200000')
        
        # Salario neto
        salario_neto = resultado.salario_base - resultado.total_empleado
        assert salario_neto == Decimal('2300000')
    
    def test_empleado_construccion(self):
        """
        Caso: Empleado de construcción (Riesgo V)
        Salario: $1,800,000
        """
        calc = CalculadoraPILA(salario_base=1800000, nivel_riesgo_arl=5)
        resultado = calc.calcular()
        
        # ARL alto por riesgo
        assert resultado.arl_empleador == Decimal('125280')  # 6.96% de 1,800,000
        
        # Total empleador alto
        assert resultado.total_empleador > Decimal('400000')
    
    def test_gerente_alto_salario(self):
        """
        Caso: Gerente con salario alto (con parafiscales)
        Salario: $20,000,000
        """
        calc = CalculadoraPILA(salario_base=20000000, nivel_riesgo_arl=1)
        resultado = calc.calcular()
        
        # Parafiscales aplican
        assert resultado.aplica_parafiscales == True
        assert resultado.ccf == Decimal('800000')      # 4% de 20M
        assert resultado.sena == Decimal('400000')     # 2% de 20M
        assert resultado.icbf == Decimal('600000')     # 3% de 20M
        assert resultado.parafiscales_total == Decimal('1800000')  # 9% de 20M


class TestReporte:
    """Pruebas de generación de reportes"""
    
    def test_generar_reporte(self):
        """
        Verifica que se genere un reporte legible
        """
        calc = CalculadoraPILA(salario_base=1300000, nivel_riesgo_arl=1)
        reporte = calc.generar_reporte()
        
        # Debe contener secciones clave
        assert "LIQUIDACIÓN DE SEGURIDAD SOCIAL" in reporte
        assert "SALUD" in reporte
        assert "PENSIÓN" in reporte
        assert "ARL" in reporte
        assert "PARAFISCALES" in reporte
        assert "RESUMEN FINAL" in reporte
        
        # Debe mostrar valores
        assert "1,300,000" in reporte  # Salario
        assert "104,000" in reporte    # Total empleado
        assert "273,286" in reporte    # Total empleador
    
    def test_reporte_con_advertencias(self):
        """
        Verifica que las advertencias aparezcan en el reporte
        """
        calc = CalculadoraPILA(salario_base=900000, nivel_riesgo_arl=1)  # Menor al mínimo
        reporte = calc.generar_reporte()
        
        assert "ADVERTENCIAS" in reporte
        assert "menor al SMMLV" in reporte


# ============================================================================
# FIXTURES Y CONFIGURACIÓN DE PYTEST
# ============================================================================

@pytest.fixture
def calculadora_basica():
    """Fixture: Calculadora con valores estándar"""
    return CalculadoraPILA(salario_base=1300000, nivel_riesgo_arl=1)


@pytest.fixture
def calculadora_alto_salario():
    """Fixture: Calculadora con salario alto"""
    return CalculadoraPILA(salario_base=15000000, nivel_riesgo_arl=3)


# ============================================================================
# EJECUCIÓN DIRECTA
# ============================================================================

if __name__ == "__main__":
    print("🧪 EJECUTANDO SUITE DE PRUEBAS UNITARIAS - MOTOR PILA\n")
    pytest.main([__file__, "-v", "--tb=short"])
