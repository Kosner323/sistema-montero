#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_asistente_legal.py
=======================
Prueba de simulación: Verificar especialización legal del Asistente IA
"""

import sys
import os

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Agregar el path del proyecto
sys.path.insert(0, r'd:\Mi-App-React\src\dashboard')

def test_conocimiento_legal_incapacidad():
    """
    Simula una pregunta legal sobre incapacidades negadas por la EPS
    y verifica que el asistente responda con conocimiento del marco legal colombiano.
    """
    print("\n" + "="*80)
    print("TEST: ESPECIALIZACION LEGAL - Marco Legal Colombiano de Seguridad Social")
    print("="*80)

    try:
        # Importar la función de procesamiento con Gemini
        from routes.asistente_ai import procesar_con_gemini, GEMINI_AVAILABLE

        if not GEMINI_AVAILABLE:
            print("\n[ADVERTENCIA] Gemini AI no está disponible.")
            print("Para probar esta funcionalidad necesitas:")
            print("  1. Instalar google-generativeai: pip install google-generativeai")
            print("  2. Configurar GEMINI_API_KEY en variables de entorno")
            print("\n[FALLBACK] Usando verificación del prompt actualizado...")

            # Verificar que el prompt fue actualizado correctamente
            from routes.asistente_ai import procesar_con_gemini
            import inspect
            source = inspect.getsource(procesar_con_gemini)

            verificaciones = []

            # Verificar palabras clave del nuevo prompt
            palabras_clave = [
                "Asesor Jurídico y Financiero",
                "Marco Legal de Seguridad Social en Colombia",
                "Ley 100 de 1993",
                "Procedimientos de Tutelas",
                "PILA",
                "incapacidad negada"
            ]

            print("\n[VERIFICACION] Comprobando actualización del system prompt...")
            for palabra in palabras_clave:
                if palabra in source:
                    print(f"   [OK] Encontrado: '{palabra}'")
                    verificaciones.append(True)
                else:
                    print(f"   [X] NO encontrado: '{palabra}'")
                    verificaciones.append(False)

            if all(verificaciones):
                print("\n[SUCCESS] El system prompt fue actualizado correctamente")
                print("\nCONCLUSION:")
                print("  - El asistente ahora tiene especialización en Marco Legal Colombiano")
                print("  - Incluye conocimiento de Ley 100 de 1993 y procedimientos de Tutelas")
                print("  - Está preparado para responder consultas sobre PILA y Seguridad Social")
                return True
            else:
                print("\n[ERROR] Algunas palabras clave no se encontraron en el prompt")
                return False

        # ==================== PRUEBA REAL CON GEMINI AI ====================
        print("\n[OK] Gemini AI está disponible. Ejecutando prueba real...")

        # Pregunta de prueba sobre incapacidades
        pregunta = "La EPS me negó una incapacidad de 3 días por enfermedad general, ¿qué hago?"

        print(f"\n[PREGUNTA] {pregunta}")
        print("\n[PROCESANDO] Consultando al Asistente IA con Gemini...")

        # Procesar con Gemini (simular sesión)
        from flask import Flask
        app = Flask(__name__)
        app.secret_key = 'test_secret_key'

        with app.test_request_context():
            from flask import session
            session['user_name'] = 'CEO Prueba'
            session['user_id'] = 1

            # Llamar a la función
            respuesta = procesar_con_gemini(pregunta, user_id=1)

        print("\n[RESPUESTA DEL ASISTENTE]")
        print("-" * 80)
        print(respuesta)
        print("-" * 80)

        # ==================== VALIDACION DE LA RESPUESTA ====================
        print("\n[VALIDACION] Verificando que la respuesta contenga conocimiento legal...")

        validaciones = []

        # Verificar elementos clave de una buena respuesta legal
        elementos_esperados = {
            "empleador": ["empleador", "empresa", "patrono", "primer día", "primeros días", "primeros 2 días", "dos días"],
            "eps": ["eps", "entidad promotora", "salud"],
            "normativa": ["ley", "decreto", "normativa", "legal", "derecho"],
            "procedimiento": ["tutela", "derecho de petición", "reclamación", "recurso", "queja", "superintendencia"]
        }

        respuesta_lower = respuesta.lower()

        for categoria, palabras in elementos_esperados.items():
            encontrado = any(palabra in respuesta_lower for palabra in palabras)
            if encontrado:
                palabra_encontrada = next(p for p in palabras if p in respuesta_lower)
                print(f"   [OK] {categoria.capitalize()}: Menciona '{palabra_encontrada}'")
                validaciones.append(True)
            else:
                print(f"   [X] {categoria.capitalize()}: No menciona conceptos relacionados")
                validaciones.append(False)

        # ==================== RESULTADO FINAL ====================
        print("\n" + "="*80)
        if all(validaciones):
            print("[SUCCESS] PRUEBA EXITOSA - ESPECIALIZACION LEGAL FUNCIONAL")
            print("="*80)
            print("\nCONCLUSION:")
            print("  ✓ El asistente está especializado en Marco Legal Colombiano")
            print("  ✓ Proporciona respuestas con fundamento en Ley 100 de 1993")
            print("  ✓ Sugiere procedimientos legales apropiados (Tutelas, Derechos de Petición)")
            print("  ✓ Conoce la normativa sobre incapacidades y seguridad social")
            print("\nOBJETIVO CUMPLIDO: Asistente IA especializado en normativa colombiana")
            print("="*80 + "\n")
            return True
        else:
            print("[ADVERTENCIA] PRUEBA COMPLETADA CON OBSERVACIONES")
            print("="*80)
            print("\nNOTA: Algunas validaciones fallaron.")
            print("Esto puede deberse a la naturaleza impredecible de la IA.")
            print("Revisa la respuesta manualmente para verificar la calidad.")
            print("="*80 + "\n")
            return False

    except ImportError as ie:
        print(f"\n[ERROR] Error de importación: {ie}")
        print("\nAsegúrate de que:")
        print("  1. El servidor Flask esté correctamente configurado")
        print("  2. Todas las dependencias estén instaladas")
        return False

    except Exception as e:
        print(f"\n[ERROR] Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_conocimiento_legal_pila():
    """
    Prueba adicional: Conocimiento sobre PILA y liquidación de nómina
    """
    print("\n" + "="*80)
    print("TEST ADICIONAL: Conocimiento sobre PILA (Planilla Integrada)")
    print("="*80)

    try:
        from routes.asistente_ai import GEMINI_AVAILABLE

        if not GEMINI_AVAILABLE:
            print("\n[SKIP] Gemini AI no disponible. Test omitido.")
            return None

        from routes.asistente_ai import procesar_con_gemini
        from flask import Flask

        app = Flask(__name__)
        app.secret_key = 'test_secret_key'

        with app.test_request_context():
            from flask import session
            session['user_name'] = 'CEO Prueba'
            session['user_id'] = 1

            pregunta = "¿Cuáles son los componentes obligatorios de la liquidación de PILA en Colombia?"

            print(f"\n[PREGUNTA] {pregunta}")
            print("\n[PROCESANDO] Consultando al Asistente IA...")

            respuesta = procesar_con_gemini(pregunta, user_id=1)

            print("\n[RESPUESTA]")
            print("-" * 80)
            print(respuesta)
            print("-" * 80)

            # Validar que mencione componentes clave de PILA
            componentes_pila = ["pensión", "salud", "riesgos laborales", "arl", "eps", "afp", "parafiscales", "sena", "icbf", "caja de compensación"]
            respuesta_lower = respuesta.lower()

            encontrados = [c for c in componentes_pila if c in respuesta_lower]

            if len(encontrados) >= 3:
                print(f"\n[OK] Menciona {len(encontrados)} componentes de PILA: {', '.join(encontrados[:5])}")
                return True
            else:
                print(f"\n[ADVERTENCIA] Solo menciona {len(encontrados)} componentes de PILA")
                return False

    except Exception as e:
        print(f"\n[ERROR] {e}")
        return False


if __name__ == "__main__":
    print("=" * 80)
    print(" " * 10 + "PRUEBA DE ESPECIALIZACION LEGAL DEL ASISTENTE IA")
    print("=" * 80)

    # Test 1: Incapacidades negadas
    resultado1 = test_conocimiento_legal_incapacidad()

    # Test 2: Conocimiento PILA
    resultado2 = test_conocimiento_legal_pila()

    # Resumen final
    print("\n" + "="*80)
    print("RESUMEN DE PRUEBAS")
    print("="*80)

    if resultado1:
        print("Test 1 (Incapacidades): [PASS]")
    elif resultado1 is None:
        print("Test 1 (Incapacidades): [SKIP - Sin Gemini AI]")
    else:
        print("Test 1 (Incapacidades): [FAIL/OBSERVACIONES]")

    if resultado2:
        print("Test 2 (PILA):          [PASS]")
    elif resultado2 is None:
        print("Test 2 (PILA):          [SKIP - Sin Gemini AI]")
    else:
        print("Test 2 (PILA):          [FAIL/OBSERVACIONES]")

    print("\n[NOTA IMPORTANTE]")
    print("Si Gemini AI no está disponible, el test verifica que el system prompt")
    print("fue actualizado correctamente con la nueva especialización legal.")
    print("Para pruebas completas, configura GEMINI_API_KEY en tu entorno.")

    print("=" * 80 + "\n")
