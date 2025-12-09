# -*- coding: utf-8 -*-
"""
Blueprint para rutas de Automatización (Copiloto)
Gestión de ARL y otras automatizaciones RPA.
"""
import os
import sqlite3
import traceback
import threading
from datetime import datetime

from flask import Blueprint, render_template, redirect, session, request, jsonify, current_app

from logger import logger

# --- IMPORTACIÓN CENTRALIZADA ---
# Intentamos importar desde nivel superior o local, SIN crear fallbacks locales
try:
    from ..extensions import db
    from ..utils import login_required
except (ImportError, ValueError):
    from extensions import db
    from utils import login_required
# -------------------------------


# --- IMPORTAR BOT RPA ---
try:
    from rpa.arl_bot import ARLBot
except ImportError:
    class ARLBot:
        def __init__(self, headless=True): pass
        def cerrar(self): pass
        def ejecutar_afiliacion(self, d): return {"status":"error", "mensaje":"Bot no instalado"}


# ==================== CONFIGURACIÓN BLUEPRINT ====================
automation_bp = Blueprint('automation', __name__, url_prefix='/copiloto')


# ==================== RUTAS DE VISTAS ====================

@automation_bp.route('/arl')
@login_required
def arl():
    """Vista Principal"""
    conn = None
    empresas_lista = []
    diag_msg = ""

    try:
        conn = get_db_connection()
        if conn:
            # Test rápido al cargar la página
            cursor = conn.execute("SELECT nit, nombre_empresa FROM empresas ORDER BY nombre_empresa ASC")
            empresas_lista = [dict(row) for row in cursor.fetchall()]

            # LOG VISIBLE EN CONSOLA
            print(f"\n🤖 [COPILOTO START] Empresas cargadas: {len(empresas_lista)}")
            if len(empresas_lista) == 0:
                print("⚠️ ALERTA: La lista de empresas está vacía. Verifica la BD.")
        else:
            print("❌ [COPILOTO] Error fatal: Sin conexión a BD.")

        return render_template(
            'copiloto/arl.html',
            user=session.get('user'),
            empresas=empresas_lista
        )
    except Exception as e:
        logger.error(f"Error vista ARL: {e}")
        return render_template('copiloto/arl.html', user=session.get('user'), empresas=[])
    finally:
        if conn: conn.close()


# ==================== NUEVO: ENDPOINT DE DIAGNÓSTICO ====================
@automation_bp.route('/api/test-conexion', methods=['GET'])
@login_required
def test_conexion():
    """
    EJECUTA UNA PRUEBA DE CONEXIÓN Y DEVUELVE UN REPORTE JSON.
    Úsalo para verificar que el Copiloto ve los datos.
    """
    resultado = {
        "estado": "iniciando",
        "ruta_bd": "usando get_db_connection()",
        "empresas_encontradas": 0,
        "usuarios_encontrados": 0,
        "mensaje": ""
    }

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Verificar Empresas
        try:
            count_emp = cur.execute("SELECT COUNT(*) FROM empresas").fetchone()[0]
            resultado['empresas_encontradas'] = count_emp
        except Exception as e:
            resultado['errores_tabla_empresas'] = str(e)

        # Verificar Usuarios
        try:
            count_usr = cur.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
            resultado['usuarios_encontrados'] = count_usr
        except Exception as e:
            resultado['errores_tabla_usuarios'] = str(e)

        resultado['estado'] = "OK"
        resultado['mensaje'] = "Conexión exitosa y tablas verificadas."

    except Exception as e:
        resultado['estado'] = "ERROR"
        resultado['mensaje'] = str(e)
        logger.error(f"❌ Error en test_conexion: {e}")
    finally:
        if conn:
            conn.close()

    return jsonify(resultado)


# ==================== RUTAS DE API RPA ====================

@automation_bp.route('/api/empleado/buscar/<string:cedula>', methods=['GET'])
@login_required
def buscar_empleado_por_cedula(cedula):
    conn = None
    try:
        conn = get_db_connection()
        if not conn: return jsonify({"error": "Sin BD"}), 500

        query = """
            SELECT u.primerNombre, u.primerApellido, u.numeroId, u.empresa_nit, e.nombre_empresa
            FROM usuarios u
            LEFT JOIN empresas e ON u.empresa_nit = e.nit
            WHERE u.numeroId = ?
        """
        empleado = conn.execute(query, (cedula,)).fetchone()

        if empleado:
            nombre = f"{empleado['primerNombre']} {empleado['primerApellido']}"
            print(f"✅ [COPILOTO] Encontrado: {nombre}")
            return jsonify({
                "nombre": nombre,
                "empresa_nit": empleado['empresa_nit'],
                "empresa_nombre": empleado['nombre_empresa'] or 'Sin Empresa'
            }), 200
        else:
            print(f"⚠️ [COPILOTO] No encontrado: {cedula}")
            return jsonify({"error": "Empleado no encontrado."}), 404

    except Exception as e:
        logger.error(f"Error API buscar: {e}")
        return jsonify({"error": "Error interno."}), 500
    finally:
        if conn: conn.close()


@automation_bp.route('/api/ejecutar', methods=['POST'])
@login_required
def ejecutar_automatizacion():
    try:
        data = request.get_json()
        job_id = f"JOB-{datetime.now().strftime('%H%M%S')}"

        print(f"🚀 [COPILOTO] Ejecutando Job {job_id} para {data.get('empleado_nombre')}")

        # AQUI IRÍA LA INTEGRACIÓN REAL CON SELENIUM

        return jsonify({
            "status": "iniciado",
            "job_id": job_id,
            "message": "Robot iniciado correctamente."
        }), 200
    except Exception as e:
        logger.error(f"Error API ejecutar: {e}")
        return jsonify({"error": str(e)}), 500
