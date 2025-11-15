# -*- coding: utf-8 -*-
"""
cotizaciones.py - ACTUALIZADO con logging
====================================================
Maneja la lógica para registrar y consultar cotizaciones.
"""

import os
import sqlite3
import traceback
from datetime import datetime
from functools import wraps  # Necesario para el fallback

from flask import Blueprint, jsonify, request

# --- IMPORTAR UTILIDADES Y LOGGER ---
from logger import logger

# --- INICIO BLOQUE DE IMPORTACIÓN ROBUSTA (Corregido IndentationError) ---
try:
    from utils import get_db_connection, login_required
except ImportError as e:
    logger.error(f"Error importando utils en cotizaciones.py: {e}", exc_info=True)

    # --- Fallbacks para evitar la caída total (IndentationError CORREGIDO) ---
    def get_db_connection():
        return None

    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)

        return decorated_function


# --- FIN BLOQUE DE IMPORTACIÓN ROBUSTA ---

# ==================== DEFINICIÓN DEL BLUEPRINT ====================
bp_cotizaciones = Blueprint("bp_cotizaciones", __name__, url_prefix="/api/cotizaciones")

# ==================== ENDPOINTS DE COTIZACIONES ====================


@bp_cotizaciones.route("", methods=["GET"])
@login_required
def get_cotizaciones():
    """Obtiene todos los registros de cotizaciones."""
    conn = None
    try:
        conn = get_db_connection()
        cotizaciones = conn.execute(
            """
            SELECT c.*, e.nombre_empresa
            FROM cotizaciones c
            LEFT JOIN empresas e ON c.empresa_nit = e.nit
            ORDER BY c.fecha_creacion DESC
        """
        ).fetchall()

        logger.debug(f"Se consultaron {len(cotizaciones)} registros de cotizaciones")
        return jsonify([dict(row) for row in cotizaciones])

    except Exception as e:
        logger.error(f"Error obteniendo lista de cotizaciones: {e}", exc_info=True)
        return jsonify({"error": "No se pudo obtener la lista de cotizaciones."}), 500
    finally:
        if conn:
            conn.close()


@bp_cotizaciones.route("", methods=["POST"])
@login_required
def add_cotizacion():
    """Añade un nuevo registro de cotización."""
    conn = None
    try:
        data = request.get_json()

        # Validación básica
        required_fields = ["empresa_nit", "monto", "servicio"]
        if not all(field in data for field in required_fields):
            logger.warning("Intento de agregar cotización con campos faltantes")
            return (
                jsonify({"error": "Faltan campos obligatorios (empresa_nit, monto, servicio)."}),
                400,
            )

        monto = float(data["monto"])
        if monto <= 0:
            logger.warning(f"Intento de agregar cotización con monto inválido: {monto}")
            return jsonify({"error": "El monto debe ser un valor positivo."}), 400

        fecha_cotizacion = data.get("fecha_cotizacion", datetime.now().strftime("%Y-%m-%d"))
        estado = data.get("estado", "Pendiente")

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO cotizaciones (empresa_nit, monto, servicio, fecha_creacion, estado, notas)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                data["empresa_nit"],
                monto,
                data["servicio"],
                fecha_cotizacion,
                estado,
                data.get("notas"),
            ),
        )
        conn.commit()

        nuevo_id = cur.lastrowid
        logger.info(f"Nueva cotización registrada con ID: {nuevo_id} para empresa {data['empresa_nit']}")

        # Devolver el registro completo
        nuevo_cotizacion = conn.execute("SELECT * FROM cotizaciones WHERE id = ?", (nuevo_id,)).fetchone()

        return jsonify(dict(nuevo_cotizacion)), 201

    except sqlite3.IntegrityError as ie:
        if conn:
            conn.rollback()
        logger.error(f"Error de integridad al agregar cotización: {ie}", exc_info=True)
        return (
            jsonify({"error": "Error de integridad, verifique que el NIT de la empresa exista."}),
            409,
        )
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error general al agregar cotización: {e}", exc_info=True)
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()
