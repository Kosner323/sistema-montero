# -*- coding: utf-8 -*-
"""
pagos.py - ACTUALIZADO con logging
==================================================
Maneja la lógica para registrar y consultar pagos.
"""

from flask import Blueprint, request, jsonify
import sqlite3
import os
import traceback
from datetime import datetime
from functools import wraps  # Necesario para el fallback

# --- IMPORTAR UTILIDADES Y LOGGER ---
from logger import get_logger

logger = get_logger(__name__)

# --- INICIO BLOQUE DE IMPORTACIÓN ROBUSTA (Corregido SyntaxError) ---
try:
    from utils import get_db_connection, login_required
except ImportError as e:
    logger.error(f"Error importando utils en pagos.py: {e}", exc_info=True)

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
bp_pagos = Blueprint("bp_pagos", __name__, url_prefix="/api/pagos")

# ==================== ENDPOINTS DE PAGOS ====================


@bp_pagos.route("", methods=["GET"])
@login_required
def get_pagos():
    """Obtiene todos los registros de pagos."""
    conn = None
    try:
        conn = get_db_connection()
        pagos = conn.execute(
            """
            SELECT p.*, u.primerNombre, u.primerApellido, e.nombre_empresa 
            FROM pagos p
            LEFT JOIN usuarios u ON p.usuario_id = u.numeroId
            LEFT JOIN empresas e ON p.empresa_nit = e.nit
            ORDER BY p.fecha_pago DESC
        """
        ).fetchall()

        logger.debug(f"Se consultaron {len(pagos)} registros de pagos")
        return jsonify([dict(row) for row in pagos])

    except Exception as e:
        logger.error(f"Error obteniendo lista de pagos: {e}", exc_info=True)
        return jsonify({"error": "No se pudo obtener la lista de pagos."}), 500
    finally:
        if conn:
            conn.close()


@bp_pagos.route("", methods=["POST"])
@login_required
def add_pago():
    """Añade un nuevo registro de pago."""
    conn = None
    try:
        data = request.get_json()

        # Validación básica
        required_fields = ["usuario_id", "empresa_nit", "monto", "tipo_pago"]
        if not all(field in data for field in required_fields):
            logger.warning("Intento de agregar pago con campos faltantes")
            return (
                jsonify(
                    {
                        "error": "Faltan campos obligatorios (usuario_id, empresa_nit, monto, tipo_pago)."
                    }
                ),
                400,
            )

        monto = float(data["monto"])
        if monto <= 0:
            logger.warning(f"Intento de agregar pago con monto inválido: {monto}")
            return jsonify({"error": "El monto debe ser un valor positivo."}), 400

        fecha_pago = data.get("fecha_pago", datetime.now().strftime("%Y-%m-%d"))

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO pagos (usuario_id, empresa_nit, monto, tipo_pago, fecha_pago, referencia)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                data["usuario_id"],
                data["empresa_nit"],
                monto,
                data["tipo_pago"],
                fecha_pago,
                data.get("referencia"),
            ),
        )
        conn.commit()

        nuevo_id = cur.lastrowid
        logger.info(f"Nuevo pago registrado con ID: {nuevo_id} por un monto de {monto}")

        # Devolver el registro completo
        nuevo_pago = conn.execute(
            "SELECT * FROM pagos WHERE id = ?", (nuevo_id,)
        ).fetchone()

        return jsonify(dict(nuevo_pago)), 201

    except sqlite3.IntegrityError as ie:
        if conn:
            conn.rollback()
        logger.error(f"Error de integridad al agregar pago: {ie}", exc_info=True)
        return (
            jsonify(
                {
                    "error": "Error de integridad, verifique los datos (ej. NIT o ID de usuario no existen)."
                }
            ),
            409,
        )
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error general al agregar pago: {e}", exc_info=True)
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()
