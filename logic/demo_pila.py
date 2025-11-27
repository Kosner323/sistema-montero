"""
Script de Demostración del Motor PILA
Sistema Montero - Cálculo de Seguridad Social

Ejecutar desde la raíz del proyecto: python logic/demo_pila.py
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from logic.pila_engine import CalculadoraPILA, calcular_pila_rapido


def separador(titulo=""):
    """Imprime un separador visual"""
    print("\n" + "=" * 70)
    if titulo:
        print(f"  {titulo}")
        print("=" * 70)


def demo_basica():
    """Demostración básica: Salario mínimo"""
    separador("DEMO 1: EMPLEADO CON SALARIO MÍNIMO (Riesgo I)")
    
    calc = CalculadoraPILA(salario_base=1300000, nivel_riesgo_arl=1)
    print(calc.generar_reporte())


def demo_riesgos():
    """Demostración: Comparación de todos los niveles de riesgo"""
    separador("DEMO 2: COMPARACIÓN DE NIVELES DE RIESGO ARL")
    
    salario = 2000000
    print(f"\nSalario Base: ${salario:,.0f} COP\n")
    print(f"{'Nivel':<10} {'Descripción':<15} {'Tasa ARL':<12} {'Valor ARL':<15} {'Total Empleador':<15}")
    print("-" * 70)
    
    niveles = {
        1: "Mínimo",
        2: "Bajo",
        3: "Medio",
        4: "Alto",
        5: "Máximo"
    }
    
    for nivel, desc in niveles.items():
        calc = CalculadoraPILA(salario_base=salario, nivel_riesgo_arl=nivel)
        resultado = calc.calcular()
        
        print(f"Riesgo {nivel:<3} {desc:<15} {resultado.tasa_arl * 100:>8.3f}% "
              f"${resultado.arl_empleador:>12,.0f} ${resultado.total_empleador:>14,.0f}")


def demo_parafiscales():
    """Demostración: Salario alto con parafiscales"""
    separador("DEMO 3: SALARIO ALTO CON PARAFISCALES")
    
    calc = CalculadoraPILA(salario_base=15000000, nivel_riesgo_arl=3)
    print(calc.generar_reporte())


def demo_autoajuste():
    """Demostración: Salario menor al mínimo (auto-ajuste)"""
    separador("DEMO 4: AUTO-AJUSTE DE SALARIO MENOR AL MÍNIMO")
    
    print("\n⚠️  ADVERTENCIA: Intentando crear empleado con salario de $800,000")
    print("    (menor al SMMLV de $1,300,000)\n")
    
    calc = CalculadoraPILA(salario_base=800000, nivel_riesgo_arl=2)
    print(calc.generar_reporte())


def demo_funcion_rapida():
    """Demostración: Uso de función de conveniencia"""
    separador("DEMO 5: FUNCIÓN DE CÁLCULO RÁPIDO")
    
    print("\nUsando la función calcular_pila_rapido():\n")
    
    resultado = calcular_pila_rapido(salario=3000000, riesgo_arl=2)
    
    print(f"Salario Base:      ${resultado['salario_base']:>12,.0f} COP")
    print(f"Total Empleado:    ${resultado['total_empleado']:>12,.0f} COP")
    print(f"Total Empleador:   ${resultado['total_empleador']:>12,.0f} COP")
    print(f"Total General:     ${resultado['total_general']:>12,.0f} COP")
    print(f"─────────────────────────────────────────")
    print(f"Salario Neto:      ${resultado['salario_neto']:>12,.0f} COP")


def demo_casos_reales():
    """Demostración: Casos reales de nómina"""
    separador("DEMO 6: CASOS REALES DE NÓMINA")
    
    casos = [
        {"nombre": "Auxiliar Administrativo", "salario": 1600000, "riesgo": 1},
        {"nombre": "Operario de Construcción", "salario": 1800000, "riesgo": 5},
        {"nombre": "Contador Senior", "salario": 4500000, "riesgo": 1},
        {"nombre": "Gerente General", "salario": 20000000, "riesgo": 1},
    ]
    
    print(f"\n{'Cargo':<25} {'Salario':<15} {'Riesgo':<8} {'Empleado':<12} {'Empleador':<12} {'Salario Neto':<15}")
    print("-" * 100)
    
    for caso in casos:
        calc = CalculadoraPILA(salario_base=caso["salario"], nivel_riesgo_arl=caso["riesgo"])
        resultado = calc.calcular()
        
        salario_neto = resultado.salario_base - resultado.total_empleado
        
        print(f"{caso['nombre']:<25} ${caso['salario']:>12,.0f} {caso['riesgo']:<8} "
              f"${resultado.total_empleado:>10,.0f} ${resultado.total_empleador:>10,.0f} "
              f"${salario_neto:>13,.0f}")


def menu_interactivo():
    """Calculadora interactiva"""
    separador("DEMO 7: CALCULADORA INTERACTIVA")
    
    print("\n¡Calcula la Seguridad Social de cualquier empleado!\n")
    
    try:
        salario = float(input("Ingresa el salario mensual (COP): $"))
        
        print("\nNiveles de Riesgo ARL:")
        print("  1 = Mínimo (oficinas)")
        print("  2 = Bajo")
        print("  3 = Medio")
        print("  4 = Alto")
        print("  5 = Máximo (construcción, minería)")
        
        riesgo = int(input("\nIngresa el nivel de riesgo (1-5): "))
        
        calc = CalculadoraPILA(salario_base=salario, nivel_riesgo_arl=riesgo)
        print(calc.generar_reporte())
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")
    except KeyboardInterrupt:
        print("\n\n🚪 Saliendo del modo interactivo...")


def main():
    """Ejecuta todas las demostraciones"""
    
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║        🧮 MOTOR DE CÁLCULO PILA - SISTEMA MONTERO                ║
║           Demostración de Cálculo de Seguridad Social            ║
║                                                                   ║
║                          Versión 1.0.0                            ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # Ejecutar demos
    demo_basica()
    input("\nPresiona ENTER para continuar...")
    
    demo_riesgos()
    input("\nPresiona ENTER para continuar...")
    
    demo_parafiscales()
    input("\nPresiona ENTER para continuar...")
    
    demo_autoajuste()
    input("\nPresiona ENTER para continuar...")
    
    demo_funcion_rapida()
    input("\nPresiona ENTER para continuar...")
    
    demo_casos_reales()
    input("\nPresiona ENTER para continuar...")
    
    # Modo interactivo
    print("\n¿Deseas probar la calculadora interactiva? (s/n): ", end="")
    if input().lower() == 's':
        menu_interactivo()
    
    separador("FIN DE LA DEMOSTRACIÓN")
    print("\n✅ Todas las funcionalidades del Motor PILA han sido demostradas.\n")
    print("📚 Para más información, consulta:")
    print("   - Documentación: logic/pila_engine.py")
    print("   - Pruebas: tests/test_calculadora_pila.py")
    print("\n🧪 Ejecuta las pruebas con: pytest tests/test_calculadora_pila.py -v\n")


if __name__ == "__main__":
    main()
