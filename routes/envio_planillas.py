# -*- coding: utf-8 -*-
"""
envio_planillas.py - ACTUALIZADO con logging
====================================================
Maneja la lógica para registrar y consultar envíos de planillas.
"""

import os
import sqlite3
import traceback
from datetime import datetime
from functools import wraps  # Necesario para el fallback

from flask import Blueprint, jsonify, request

# --- IMPORTAR UTILIDADES Y LOGGER ---
from logger import logger

# --- INICIO BLOQUE DE IMPORTACIÓN ROBUSTA (Corregido error de try/except) ---
try:
    from utils import get_db_connection, login_required
except ImportError as e:
    logger.error(f"Error importando utils en envio_planillas.py: {e}", exc_info=True)

    # --- Fallbacks ---
    def get_db_connection():
        return None

    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)

        return decorated_function


# --- FIN BLOQUE DE IMPORTACIÓN ROBUSTA ---

# ==================== DEFINICIÓN DEL BLUEPRINT ====================
bp_envio_planillas = Blueprint("bp_envio_planillas", __name__, url_prefix="/api/envios")

# ==================== ENDPOINTS DE ENVÍOS ====================


@bp_envio_planillas.route("", methods=["GET"])
@login_required
def get_envios():
    """Obtiene todos los registros de envíos de planillas."""
    conn = None
    try:
        # Filtros opcionales
        empresa_nit = request.args.get("empresa_nit")

        conn = get_db_connection()
        query = "SELECT e.*, emp.nombre_empresa FROM envios_planillas e LEFT JOIN empresas emp ON e.empresa_nit = emp.nit"
        params = []

        if empresa_nit and empresa_nit != "todos":
            query += " WHERE e.empresa_nit = ?"
            params.append(empresa_nit)

        query += " ORDER BY e.fecha_envio DESC"

        envios = conn.execute(query, tuple(params)).fetchall()

        logger.debug(f"Se consultaron {len(envios)} registros de envíos")
        return jsonify([dict(row) for row in envios])

    except Exception as e:
        logger.error(f"Error obteniendo lista de envíos: {e}", exc_info=True)
        return jsonify({"error": "No se pudo obtener la lista de envíos."}), 500
    finally:
        if conn:
            conn.close()


@bp_envio_planillas.route("", methods=["POST"])
@login_required
def add_envio():
    """Añade un nuevo registro de envío de planilla."""
    conn = None
    nit = request.get_json().get("empresa_nit")
    try:
        data = request.get_json()

        # Validación básica
        required_fields = ["empresa_nit", "fecha_envio", "plataforma", "estado"]
        if not all(field in data for field in required_fields):
            logger.warning(f"Intento de agregar envío con campos faltantes. NIT: {nit}")
            return (
                jsonify({"error": "Faltan campos obligatorios (empresa_nit, fecha_envio, plataforma, estado)."}),
                400,
            )

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO envios_planillas (empresa_nit, fecha_envio, plataforma, estado, notas, responsable)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                data["empresa_nit"],
                data["fecha_envio"],
                data["plataforma"],
                data["estado"],
                data.get("notas"),
                data.get("responsable"),
            ),
        )
        conn.commit()

        nuevo_id = cur.lastrowid
        logger.info(f"Nuevo envío de planilla registrado con ID: {nuevo_id} para NIT: {data['empresa_nit']}")

        nuevo_envio = conn.execute("SELECT * FROM envios_planillas WHERE id = ?", (nuevo_id,)).fetchone()

        return jsonify(dict(nuevo_envio)), 201

    except sqlite3.IntegrityError as ie:
        if conn:
            conn.rollback()
        logger.error(f"Error de integridad al agregar envío: {ie}", exc_info=True)
        return (
            jsonify({"error": "Error de integridad, verifique que el NIT de la empresa exista."}),
            409,
        )
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error general al agregar envío (NIT: {nit}): {e}", exc_info=True)
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()
