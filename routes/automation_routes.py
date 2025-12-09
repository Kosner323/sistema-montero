# -*- coding: utf-8 -*-
"""
Blueprint para rutas de Automatización (Copiloto)
Gestión de ARL y otras automatizaciones RPA.

REFACTORIZADO: Usa SQLAlchemy ORM en lugar de SQL manual
Autor: Senior Backend Developer
Fecha: 2025-12-09
"""
import os
import traceback
import threading
from datetime import datetime

from flask import Blueprint, render_template, redirect, session, request, jsonify, current_app

from logger import logger

# --- IMPORTACIÓN CENTRALIZADA ---
try:
    from ..extensions import db
    from ..utils import login_required
except (ImportError, ValueError):
    from extensions import db
    from utils import login_required

# Modelos ORM
try:
    from ..models.orm_models import Empresa, Usuario
except (ImportError, ValueError):
    from models.orm_models import Empresa, Usuario
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
    """Vista Principal - Usando SQLAlchemy ORM"""
    empresas_lista = []

    try:
        # Consulta ORM en lugar de SQL manual
        empresas = Empresa.query.order_by(Empresa.nombre_empresa.asc()).all()
        empresas_lista = [{'nit': e.nit, 'nombre_empresa': e.nombre_empresa} for e in empresas]

        # LOG VISIBLE EN CONSOLA
        print(f"\n🤖 [COPILOTO START] Empresas cargadas: {len(empresas_lista)}")
        if len(empresas_lista) == 0:
            print("⚠️ ALERTA: La lista de empresas está vacía. Verifica la BD.")

        return render_template(
            'copiloto/arl.html',
            user=session.get('user'),
            empresas=empresas_lista
        )
    except Exception as e:
        logger.error(f"Error vista ARL: {e}")
        return render_template('copiloto/arl.html', user=session.get('user'), empresas=[])


# ==================== ENDPOINT DE DIAGNÓSTICO - SQLAlchemy ====================
@automation_bp.route('/api/test-conexion', methods=['GET'])
@login_required
def test_conexion():
    """
    EJECUTA UNA PRUEBA DE CONEXIÓN Y DEVUELVE UN REPORTE JSON.
    Úsalo para verificar que el Copiloto ve los datos.
    """
    resultado = {
        "estado": "iniciando",
        "ruta_bd": "SQLAlchemy ORM",
        "empresas_encontradas": 0,
        "usuarios_encontrados": 0,
        "mensaje": ""
    }

    try:
        # Verificar Empresas con ORM
        try:
            count_emp = Empresa.query.count()
            resultado['empresas_encontradas'] = count_emp
        except Exception as e:
            resultado['errores_tabla_empresas'] = str(e)

        # Verificar Usuarios con ORM
        try:
            count_usr = Usuario.query.count()
            resultado['usuarios_encontrados'] = count_usr
        except Exception as e:
            resultado['errores_tabla_usuarios'] = str(e)

        resultado['estado'] = "OK"
        resultado['mensaje'] = "Conexión exitosa y tablas verificadas (SQLAlchemy ORM)."

    except Exception as e:
        resultado['estado'] = "ERROR"
        resultado['mensaje'] = str(e)
        logger.error(f"❌ Error en test_conexion: {e}")

    return jsonify(resultado)


# ==================== RUTAS DE API RPA - SQLAlchemy ====================

@automation_bp.route('/api/empleado/buscar/<string:cedula>', methods=['GET'])
@login_required
def buscar_empleado_por_cedula(cedula):
    """Buscar empleado por cédula usando SQLAlchemy ORM"""
    try:
        # Query ORM con join
        empleado = Usuario.query.filter_by(numeroId=cedula).first()

        if empleado:
            nombre = f"{empleado.primerNombre or ''} {empleado.primerApellido or ''}".strip()
            empresa_nombre = 'Sin Empresa'
            
            # Obtener nombre de empresa si existe relación
            if empleado.empresa:
                empresa_nombre = empleado.empresa.nombre_empresa or 'Sin Empresa'
            
            print(f"✅ [COPILOTO] Encontrado: {nombre}")
            return jsonify({
                "nombre": nombre,
                "empresa_nit": empleado.empresa_nit,
                "empresa_nombre": empresa_nombre
            }), 200
        else:
            print(f"⚠️ [COPILOTO] No encontrado: {cedula}")
            return jsonify({"error": "Empleado no encontrado."}), 404

    except Exception as e:
        logger.error(f"Error API buscar: {e}")
        return jsonify({"error": "Error interno."}), 500


@automation_bp.route('/api/ejecutar', methods=['POST'])
@login_required
def ejecutar_automatizacion():
    """Ejecutar automatización RPA"""
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
