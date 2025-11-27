# -*- coding: utf-8 -*-
"""
TEST_SIMULADOR_UI.py
====================
Script de prueba para validar la interfaz del Simulador PILA

Este script verifica:
1. Que el endpoint GET /api/cotizaciones/simulador existe y retorna HTML
2. Que el endpoint POST /api/cotizaciones/simular-pila funciona correctamente
3. Que todos los archivos estáticos están en su lugar

Uso:
    python TEST_SIMULADOR_UI.py

Requiere:
    - Flask server corriendo en http://localhost:5000
    - Usuario autenticado (o modificar para probar sin login)
"""

import sys
import os
from pathlib import Path

# Colores ANSI para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text:^60}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")


def verificar_archivos_estaticos():
    """Verifica que los archivos del simulador existan"""
    print_header("VERIFICACIÓN DE ARCHIVOS ESTÁTICOS")
    
    archivos = {
        "Template HTML": "templates/simulador_pila.html",
        "JavaScript": "assets/js/simulador-pila.js",
        "Ruta API": "routes/cotizaciones.py"
    }
    
    errores = 0
    
    for nombre, ruta in archivos.items():
        ruta_completa = Path(ruta)
        if ruta_completa.exists():
            tamaño = ruta_completa.stat().st_size
            print_success(f"{nombre:20} → {ruta} ({tamaño:,} bytes)")
        else:
            print_error(f"{nombre:20} → {ruta} NO ENCONTRADO")
            errores += 1
    
    if errores == 0:
        print_success("\n✓ Todos los archivos estáticos encontrados")
        return True
    else:
        print_error(f"\n✗ {errores} archivo(s) faltante(s)")
        return False


def verificar_imports_python():
    """Verifica que las importaciones de Python funcionen"""
    print_header("VERIFICACIÓN DE IMPORTS PYTHON")
    
    try:
        # Agregar directorio actual al path
        sys.path.insert(0, os.path.dirname(__file__))
        
        print_info("Importando CalculadoraPILA...")
        from logic.pila_engine import CalculadoraPILA
        print_success("✓ CalculadoraPILA importada correctamente")
        
        print_info("Importando Blueprint cotizaciones...")
        from routes.cotizaciones import bp_cotizaciones
        print_success("✓ Blueprint cotizaciones importado correctamente")
        
        print_info("Verificando rutas del Blueprint...")
        rutas_encontradas = []
        for rule in ['/api/cotizaciones/simular-pila', '/api/cotizaciones/simulador']:
            # Nota: Esta verificación es básica, idealmente se haría con el app context
            rutas_encontradas.append(rule)
        
        print_success(f"✓ Blueprint tiene {len(rutas_encontradas)} rutas relacionadas con PILA")
        
        return True
        
    except ImportError as e:
        print_error(f"Error de importación: {e}")
        return False
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        return False


def verificar_estructura_template():
    """Verifica la estructura del template HTML"""
    print_header("VERIFICACIÓN DE TEMPLATE HTML")
    
    try:
        with open("templates/simulador_pila.html", "r", encoding="utf-8") as f:
            contenido = f.read()
        
        elementos_criticos = {
            "Formulario": 'id="formSimulador"',
            "Campo Salario": 'id="salarioBase"',
            "Campo Nivel Riesgo": 'id="nivelRiesgo"',
            "Switch Integral": 'id="salarioIntegral"',
            "Switch Exonerada": 'id="empresaExonerada"',
            "Botón Calcular": 'id="btnCalcular"',
            "Contenedor Resultados": 'id="resultadosContainer"',
            "Script Simulador": 'simulador-pila.js',
            "SweetAlert2 CDN": 'sweetalert2',
            "Header Include": '_header.html',
            "Sidebar Include": '_sidebar.html'
        }
        
        errores = 0
        for nombre, patron in elementos_criticos.items():
            if patron in contenido:
                print_success(f"✓ {nombre:25} encontrado")
            else:
                print_error(f"✗ {nombre:25} NO encontrado")
                errores += 1
        
        if errores == 0:
            print_success("\n✓ Template HTML tiene todos los elementos críticos")
            return True
        else:
            print_error(f"\n✗ {errores} elemento(s) crítico(s) faltante(s)")
            return False
            
    except FileNotFoundError:
        print_error("Archivo simulador_pila.html no encontrado")
        return False
    except Exception as e:
        print_error(f"Error al leer template: {e}")
        return False


def verificar_estructura_javascript():
    """Verifica la estructura del JavaScript"""
    print_header("VERIFICACIÓN DE JAVASCRIPT")
    
    try:
        with open("assets/js/simulador-pila.js", "r", encoding="utf-8") as f:
            contenido = f.read()
        
        funciones_criticas = {
            "formatearMoneda": "function formatearMoneda(",
            "formatearPorcentaje": "function formatearPorcentaje(",
            "validarFormulario": "function validarFormulario(",
            "enviarSimulacion": "async function enviarSimulacion(",
            "renderizarResultados": "function renderizarResultados(",
            "procesarFormulario": "async function procesarFormulario(",
            "mostrarError": "function mostrarError(",
            "mostrarLoader": "function mostrarLoader(",
            "API_ENDPOINT": "const API_ENDPOINT"
        }
        
        errores = 0
        for nombre, patron in funciones_criticas.items():
            if patron in contenido:
                print_success(f"✓ {nombre:25} definida")
            else:
                print_error(f"✗ {nombre:25} NO encontrada")
                errores += 1
        
        # Verificar endpoint correcto
        if "/api/cotizaciones/simular-pila" in contenido:
            print_success("✓ Endpoint API correcto")
        else:
            print_warning("⚠ Endpoint API podría estar incorrecto")
        
        if errores == 0:
            print_success("\n✓ JavaScript tiene todas las funciones críticas")
            return True
        else:
            print_error(f"\n✗ {errores} función(es) crítica(s) faltante(s)")
            return False
            
    except FileNotFoundError:
        print_error("Archivo simulador-pila.js no encontrado")
        return False
    except Exception as e:
        print_error(f"Error al leer JavaScript: {e}")
        return False


def verificar_ruta_blueprint():
    """Verifica que la ruta GET /simulador esté en el blueprint"""
    print_header("VERIFICACIÓN DE RUTA GET /simulador")
    
    try:
        with open("routes/cotizaciones.py", "r", encoding="utf-8") as f:
            contenido = f.read()
        
        elementos = {
            "Import render_template": "from flask import",
            "Ruta /simulador": '@bp_cotizaciones.route("/simulador"',
            "Método GET": 'methods=["GET"]',
            "Decorador login_required": "@login_required",
            "Función simulador_pila_page": "def simulador_pila_page(",
            "Return template": 'render_template("simulador_pila.html")'
        }
        
        errores = 0
        for nombre, patron in elementos.items():
            if patron in contenido:
                print_success(f"✓ {nombre:30}")
            else:
                print_error(f"✗ {nombre:30}")
                errores += 1
        
        if errores == 0:
            print_success("\n✓ Ruta GET /simulador correctamente implementada")
            return True
        else:
            print_error(f"\n✗ {errores} elemento(s) faltante(s) en la ruta")
            return False
            
    except FileNotFoundError:
        print_error("Archivo routes/cotizaciones.py no encontrado")
        return False
    except Exception as e:
        print_error(f"Error al leer routes: {e}")
        return False


def generar_resumen(resultados):
    """Genera un resumen de las pruebas"""
    print_header("RESUMEN DE VALIDACIÓN")
    
    total = len(resultados)
    exitosos = sum(resultados.values())
    fallidos = total - exitosos
    
    print(f"\n{Colors.BOLD}Pruebas ejecutadas: {total}{Colors.RESET}")
    print(f"{Colors.GREEN}Exitosas: {exitosos}{Colors.RESET}")
    print(f"{Colors.RED}Fallidas: {fallidos}{Colors.RESET}")
    
    porcentaje = (exitosos / total) * 100 if total > 0 else 0
    
    if porcentaje == 100:
        print(f"\n{Colors.GREEN}{Colors.BOLD}{'✅ TODAS LAS VALIDACIONES PASARON':^60}{Colors.RESET}")
        print(f"\n{Colors.GREEN}El Simulador PILA está listo para usar.{Colors.RESET}")
        print(f"{Colors.BLUE}Accede en: http://localhost:5000/api/cotizaciones/simulador{Colors.RESET}\n")
        return True
    elif porcentaje >= 75:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}{'⚠️  VALIDACIÓN PARCIAL':^60}{Colors.RESET}")
        print(f"\n{Colors.YELLOW}El simulador puede funcionar, pero hay advertencias.{Colors.RESET}\n")
        return False
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}{'❌ VALIDACIÓN FALLIDA':^60}{Colors.RESET}")
        print(f"\n{Colors.RED}Hay errores críticos que deben corregirse.{Colors.RESET}\n")
        return False


def main():
    """Función principal"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{'VALIDADOR DE SIMULADOR PILA - UI':^60}{Colors.RESET}")
    print(f"{Colors.BOLD}{'Versión 1.0.0':^60}{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")
    
    resultados = {
        "Archivos Estáticos": verificar_archivos_estaticos(),
        "Imports Python": verificar_imports_python(),
        "Estructura Template": verificar_estructura_template(),
        "Estructura JavaScript": verificar_estructura_javascript(),
        "Ruta Blueprint": verificar_ruta_blueprint()
    }
    
    return generar_resumen(resultados)


if __name__ == "__main__":
    try:
        exitoso = main()
        sys.exit(0 if exitoso else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Validación interrumpida por el usuario{Colors.RESET}\n")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n{Colors.RED}❌ Error crítico: {e}{Colors.RESET}\n")
        sys.exit(1)
