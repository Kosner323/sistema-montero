# -*- coding: utf-8 -*-
"""
TEST DE SALUD DEL SISTEMA (HEALTH CHECK)
Verifica que todos los módulos estén conectados a la Base de Datos Única.
"""
import sys
import os
from flask import session

# Asegurar que podemos importar app.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
except ImportError as e:
    print(f"❌ Error Fatal: No se pudo importar la aplicación. {e}")
    sys.exit(1)

def ejecutar_diagnostico():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False # Desactivar CSRF para facilitar test

    print("\n🏥 INICIANDO DIAGNÓSTICO DE SIGNOS VITALES...")
    print("=============================================")

    with app.test_client() as client:
        # 1. SIMULAR LOGIN (Bypass de seguridad)
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Admin Diagnostico'
            sess['role'] = 'admin'
        
        modulos_a_probar = [
            # Nombre Módulo       | Ruta API                      | Tipo | Esperado
            ("🏠 Dashboard",       "/dashboard",                   "HTML", 200),
            ("🤖 Copiloto RPA",    "/copiloto/arl",                "HTML", 200),
            ("👥 Unif. Usuarios",  "/api/unificacion/master",      "JSON", "usuarios"),
            ("📢 Novedades",       "/api/novedades",               "JSON", "lista"),
            ("💰 Pagos",           "/api/pagos",                   "JSON", "lista"),
            ("⚖️ Tutelas",         "/api/tutelas",                 "JSON", "lista"),
            ("🏢 Empresas (API)",  "/api/empresas",                "JSON", "lista")
        ]

        score = 0
        total = len(modulos_a_probar)

        for nombre, ruta, tipo, esperado in modulos_a_probar:
            print(f"Testing {nombre}...", end=" ")
            try:
                res = client.get(ruta, follow_redirects=True)
                
                # Análisis de respuesta
                estado = "OK"
                detalle = ""

                if res.status_code != 200:
                    # Algunos módulos pueden dar 404 si no hay datos o ruta exacta, pero 500 es FATAL
                    if res.status_code == 500:
                        estado = "CRITICAL ERROR (500)"
                    elif res.status_code == 404:
                        estado = "WARNING (404 - Ruta no existe?)"
                    else:
                        estado = f"Code {res.status_code}"
                else:
                    # Si es JSON, verificamos contenido
                    if tipo == "JSON":
                        try:
                            json_data = res.get_json()
                            if json_data is None:
                                estado = "FAIL (No es JSON)"
                            elif isinstance(esperado, str) and esperado in ["lista", "usuarios"]:
                                # Verificar si es lista o tiene claves
                                if isinstance(json_data, list):
                                    detalle = f"({len(json_data)} registros)"
                                elif isinstance(json_data, dict):
                                    keys = list(json_data.keys())
                                    detalle = f"(Claves: {', '.join(keys[:3])}...)"
                        except:
                            estado = "FAIL (JSON Inválido)"
                
                # Imprimir resultado
                if "ERROR" in estado or "FAIL" in estado:
                    print(f"❌ {estado}")
                elif "WARNING" in estado:
                    print(f"⚠️  {estado}")
                    score += 0.5 # Medio punto
                else:
                    print(f"✅ VIVO {detalle}")
                    score += 1

            except Exception as e:
                print(f"💥 EXCEPCIÓN: {e}")

        print("=============================================")
        print(f"RESULTADO FINAL: {score}/{total} Módulos Operativos")
        
        if score == total:
            print("🏆 SISTEMA 100% SALUDABLE")
        elif score >= total - 2:
            print("👍 SISTEMA ESTABLE (Con advertencias menores)")
        else:
            print("🚑 REQUIERE ATENCIÓN INMEDIATA")

if __name__ == "__main__":
    ejecutar_diagnostico()
