#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
routes/planillas.py
==================
Gestión de Planillas PILA con Auditoría IA (Jordy)
Fase 11: Validación inteligente antes de generar archivos planos

Autor: Senior Backend Developer & Data Scientist
Fecha: 2025-11-30
"""

import os
import json
from flask import Blueprint, request, jsonify, session
from functools import wraps
from datetime import datetime

# Importar motor PILA
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logic.pila_engine import LiquidadorPILA

# Logger
try:
    from logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Blueprint
bp_planillas = Blueprint('planillas', __name__, url_prefix='/api/planillas')


# =============================================================================
# DECORADOR: AUTENTICACIÓN
# =============================================================================

def login_required(f):
    """Decorador para requerir autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            logger.warning("Intento de acceso no autenticado a planillas")
            return jsonify({
                'success': False,
                'error': 'Debes iniciar sesión'
            }), 401
        return f(*args, **kwargs)
    return decorated_function


# =============================================================================
# ENDPOINT: POST /api/planillas/auditar
# =============================================================================

@bp_planillas.route('/auditar', methods=['POST'])
@login_required
def auditar_planilla():
    """
    FASE 11: Auditoría IA de Planilla PILA

    Jordy (Gemini AI) revisa el JSON de la planilla preliminar antes de
    generar el archivo plano. Busca errores de IBC, días incoherentes,
    tarifas erradas, etc.

    Request JSON:
        {
            "lineas": [
                {
                    "usuario_id": "1234567890",
                    "nombre_completo": "Juan Pérez",
                    "ibc_calculado": 1500000,
                    "dias_cotizados": 30,
                    "salud_empleado": 60000,
                    "pension_empleado": 60000,
                    ...
                }
            ],
            "mes": "2025-01",
            "empresa_nit": "900123456"
        }

    Response JSON:
        {
            "success": true,
            "auditoria": {
                "estado": "APROBADO" | "ERRORES_ENCONTRADOS",
                "errores": [...],
                "advertencias": [...],
                "sugerencias": [...],
                "resumen_ia": "Análisis de Jordy..."
            }
        }
    """
    try:
        data = request.get_json()

        if not data or 'lineas' not in data:
            return jsonify({
                'success': False,
                'error': 'Faltan datos de la planilla'
            }), 400

        lineas = data.get('lineas', [])
        mes = data.get('mes', datetime.now().strftime('%Y-%m'))
        empresa_nit = data.get('empresa_nit', 'SIN_NIT')

        if not lineas:
            return jsonify({
                'success': False,
                'error': 'La planilla no tiene líneas para auditar'
            }), 400

        logger.info(f"🔍 Auditando planilla: {len(lineas)} líneas, Mes: {mes}, Empresa: {empresa_nit}")

        # =====================================================================
        # PASO 1: VALIDACIÓN BÁSICA (PRE-IA)
        # =====================================================================

        liquidador = LiquidadorPILA()
        validacion_basica = liquidador.validar_planilla(lineas)

        errores_basicos = validacion_basica.get('errores', [])
        advertencias_basicas = validacion_basica.get('advertencias', [])

        # =====================================================================
        # PASO 2: PREPARAR DATOS PARA GEMINI
        # =====================================================================

        # Resumir datos para enviar a Gemini (no enviar todo el JSON)
        resumen_lineas = []
        for i, linea in enumerate(lineas[:10], start=1):  # Primeras 10 líneas
            resumen_lineas.append({
                "linea": i,
                "empleado": linea.get('nombre_completo', 'SIN NOMBRE'),
                "ibc": linea.get('ibc_calculado', 0),
                "dias": linea.get('dias_cotizados', 0),
                "total_aportes": linea.get('total_aportes', 0),
                "marca_novedad": linea.get('marca_novedad', '')
            })

        # Construir prompt para Gemini
        prompt_auditoria = f"""Actúa como Jordy, el auditor experto en PILA (seguridad social colombiana).

Revisa las siguientes líneas de una planilla PILA para el mes {mes}:

DATOS DE LA PLANILLA:
- Total empleados: {len(lineas)}
- Total aportes: ${validacion_basica.get('total_aportes', 0):,.0f}
- Empresa NIT: {empresa_nit}

PRIMERAS 10 LÍNEAS:
{json.dumps(resumen_lineas, indent=2, ensure_ascii=False)}

ERRORES DETECTADOS (validación básica):
{json.dumps(errores_basicos, indent=2, ensure_ascii=False) if errores_basicos else "Ninguno"}

TU MISIÓN:
1. Busca errores en IBC (debe ser >= $1,300,000 para 30 días)
2. Verifica coherencia de días cotizados (1-30)
3. Valida tarifas de aportes:
   - Salud empleado: 4% del IBC
   - Pensión empleado: 4% del IBC
   - ARL: 0.522% - 6.960% según clase de riesgo

4. Identifica inconsistencias en marcas de novedad (IGE, RET, LGE, etc.)

RESPONDE EN FORMATO JSON:
{{
    "estado": "APROBADO" o "ERRORES_ENCONTRADOS",
    "errores_criticos": ["error 1", "error 2"],
    "advertencias": ["advertencia 1"],
    "sugerencias": ["sugerencia 1"],
    "resumen": "Análisis breve (máximo 3 líneas)"
}}

Si todo está correcto, responde con estado "APROBADO" y resumen positivo."""

        # =====================================================================
        # PASO 3: LLAMAR A GEMINI AI
        # =====================================================================

        try:
            import google.generativeai as genai

            # Configurar Gemini (API key debe estar en variable de entorno)
            api_key = os.getenv('GEMINI_API_KEY')

            if not api_key:
                logger.warning("⚠️ GEMINI_API_KEY no configurada, usando validación básica solamente")

                return jsonify({
                    'success': True,
                    'auditoria': {
                        'estado': 'APROBADO' if not errores_basicos else 'ERRORES_ENCONTRADOS',
                        'errores': errores_basicos,
                        'advertencias': advertencias_basicas,
                        'sugerencias': [],
                        'resumen_ia': '⚠️ Auditoría IA no disponible (falta API key). Validación básica completada.',
                        'metodo': 'validacion_basica'
                    },
                    'validacion_basica': validacion_basica
                }), 200

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')

            logger.info("🤖 Enviando planilla a Gemini para auditoría...")

            response = model.generate_content(prompt_auditoria)
            respuesta_texto = response.text

            # Intentar parsear JSON de la respuesta
            try:
                # Limpiar markdown si viene con ```json
                if '```json' in respuesta_texto:
                    respuesta_texto = respuesta_texto.split('```json')[1].split('```')[0].strip()
                elif '```' in respuesta_texto:
                    respuesta_texto = respuesta_texto.split('```')[1].split('```')[0].strip()

                auditoria_ia = json.loads(respuesta_texto)

            except json.JSONDecodeError:
                logger.warning("⚠️ Respuesta de Gemini no es JSON válido, usando texto plano")
                auditoria_ia = {
                    'estado': 'ERRORES_ENCONTRADOS' if errores_basicos else 'APROBADO',
                    'errores_criticos': errores_basicos,
                    'advertencias': advertencias_basicas,
                    'sugerencias': [],
                    'resumen': respuesta_texto[:300]
                }

            logger.info(f"✅ Auditoría IA completada: {auditoria_ia.get('estado')}")

            return jsonify({
                'success': True,
                'auditoria': {
                    'estado': auditoria_ia.get('estado', 'APROBADO'),
                    'errores': auditoria_ia.get('errores_criticos', []),
                    'advertencias': auditoria_ia.get('advertencias', []),
                    'sugerencias': auditoria_ia.get('sugerencias', []),
                    'resumen_ia': auditoria_ia.get('resumen', 'Sin resumen'),
                    'metodo': 'gemini_ai'
                },
                'validacion_basica': validacion_basica
            }), 200

        except ImportError:
            logger.error("❌ Módulo google-generativeai no instalado")

            return jsonify({
                'success': True,
                'auditoria': {
                    'estado': 'APROBADO' if not errores_basicos else 'ERRORES_ENCONTRADOS',
                    'errores': errores_basicos,
                    'advertencias': advertencias_basicas + ['Gemini AI no disponible: ejecutar pip install google-generativeai'],
                    'sugerencias': [],
                    'resumen_ia': 'Validación básica completada. Para auditoría IA, instalar google-generativeai.',
                    'metodo': 'validacion_basica'
                },
                'validacion_basica': validacion_basica
            }), 200

        except Exception as gemini_error:
            logger.error(f"❌ Error en Gemini AI: {gemini_error}")

            return jsonify({
                'success': True,
                'auditoria': {
                    'estado': 'APROBADO' if not errores_basicos else 'ERRORES_ENCONTRADOS',
                    'errores': errores_basicos,
                    'advertencias': advertencias_basicas + [f'Error en Gemini: {str(gemini_error)}'],
                    'sugerencias': [],
                    'resumen_ia': 'Error en auditoría IA. Validación básica completada.',
                    'metodo': 'validacion_basica_fallback'
                },
                'validacion_basica': validacion_basica
            }), 200

    except Exception as e:
        logger.error(f"❌ Error auditando planilla: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Error al auditar planilla',
            'detalle': str(e)
        }), 500


# =============================================================================
# ENDPOINT: POST /api/planillas/calcular (HELPER)
# =============================================================================

@bp_planillas.route('/calcular', methods=['POST'])
@login_required
def calcular_planilla():
    """
    Calcula una planilla PILA usando el motor de liquidación.

    Request JSON:
        {
            "empleados": [
                {
                    "numeroId": "1234567890",
                    "primerNombre": "Juan",
                    "primerApellido": "Pérez",
                    "ibc": 1500000,
                    "arlClase": 1
                }
            ],
            "mes": "2025-01",
            "empresa_nit": "900123456"
        }

    Response JSON:
        {
            "success": true,
            "lineas": [...],
            "resumen": {
                "total_empleados": 10,
                "total_aportes": 5000000
            }
        }
    """
    try:
        data = request.get_json()
        empleados = data.get('empleados', [])

        if not empleados:
            return jsonify({
                'success': False,
                'error': 'No se recibieron empleados para calcular'
            }), 400

        liquidador = LiquidadorPILA()
        lineas = []

        for empleado in empleados:
            # Calcular línea PILA para cada empleado
            linea = liquidador.calcular_linea(
                usuario=empleado,
                dias_trabajados=empleado.get('dias_trabajados', 30),
                novedades=empleado.get('novedades', [])
            )
            lineas.append(linea)

        # Validar planilla completa
        validacion = liquidador.validar_planilla(lineas)

        return jsonify({
            'success': True,
            'lineas': lineas,
            'resumen': {
                'total_empleados': len(lineas),
                'total_aportes': validacion.get('total_aportes', 0),
                'valida': validacion.get('valida', False)
            },
            'validacion': validacion
        }), 200

    except Exception as e:
        logger.error(f"❌ Error calculando planilla: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Error al calcular planilla',
            'detalle': str(e)
        }), 500


if __name__ == "__main__":
    print("Módulo de planillas cargado correctamente")
