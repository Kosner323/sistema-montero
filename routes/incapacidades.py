# -*- coding: utf-8 -*-
"""
incapacidades.py - ACTUALIZADO con logging
==================================================
Maneja la lógica para registrar y consultar incapacidades médicas.
"""

import os
import sqlite3
from datetime import datetime

from flask import Blueprint, g, jsonify, request, session
from werkzeug.utils import secure_filename

# --- IMPORTAR UTILIDADES Y LOGGER ---
from logger import logger
from utils import USER_DATA_FOLDER, log_file_upload, login_required, sanitize_and_save_file, validate_upload

# ==================== DEFINICIÓN DEL BLUEPRINT ====================
bp_incapacidades = Blueprint("bp_incapacidades", __name__, url_prefix="/api/incapacidades")


# ==================== FUNCIONES AUXILIARES ====================
def _get_user_incapacidad_folder(numero_id):
    """Obtiene/crea la carpeta de incapacidades para un usuario."""
    try:
        user_folder_path = os.path.join(USER_DATA_FOLDER, str(numero_id), "INCAPACIDADES")
        os.makedirs(user_folder_path, exist_ok=True)
        return user_folder_path
    except Exception as e:
        logger.error(f"Error creando carpeta de incapacidad para {numero_id}: {e}", exc_info=True)
        raise


# ==================== ENDPOINTS DE INCAPACIDADES ====================


@bp_incapacidades.route("", methods=["GET"])
@login_required
def get_incapacidades():
    """Obtiene todos los registros de incapacidades."""
    try:
        # Filtros opcionales
        usuario_id = request.args.get("usuario_id")
        empresa_nit = request.args.get("empresa_nit")

        conn = g.db
        query = (
            "SELECT i.*, u.primerNombre, u.primerApellido, e.nombre_empresa FROM incapacidades i "
            "LEFT JOIN usuarios u ON i.usuario_id = u.numeroId "
            "LEFT JOIN empresas e ON u.empresa_nit = e.nit"
        )

        conditions = []
        params = []

        if usuario_id and usuario_id != "todos":
            conditions.append("i.usuario_id = ?")
            params.append(usuario_id)

        if empresa_nit and empresa_nit != "todos":
            conditions.append("u.empresa_nit = ?")
            params.append(empresa_nit)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY i.fecha_inicio DESC"

        incapacidades = conn.execute(query, tuple(params)).fetchall()

        logger.debug(f"Se consultaron {len(incapacidades)} incapacidades")
        return jsonify([dict(row) for row in incapacidades])

    except Exception as e:
        logger.error(f"Error obteniendo lista de incapacidades: {e}", exc_info=True)
        return jsonify({"error": "No se pudo obtener la lista de incapacidades."}), 500
    # g.db se cierra automáticamente por app.after_request


@bp_incapacidades.route("", methods=["POST"])
@login_required
def add_incapacidad():
    """Añade un nuevo registro de incapacidad y sube el soporte."""
    conn = None
    numero_id = request.form.get("usuario_id")  # Para logging
    try:
        data = request.form

        # Validación de datos
        required_fields = [
            "usuario_id",
            "tipo_incapacidad",
            "fecha_inicio",
            "dias_incapacidad",
        ]
        if not all(field in data for field in required_fields):
            logger.warning(f"Intento de agregar incapacidad con campos faltantes. Usuario: {numero_id}")
            return (
                jsonify({"error": "Faltan campos obligatorios (usuario_id, tipo, fecha_inicio, dias)."}),
                400,
            )

        if "soporte_pdf" not in request.files:
            logger.warning(f"Intento de agregar incapacidad sin soporte PDF. Usuario: {numero_id}")
            return jsonify({"error": "No se incluyó el archivo PDF de soporte."}), 400

        file = request.files["soporte_pdf"]
        if file.filename == "":
            return jsonify({"error": "El archivo de soporte no tiene nombre."}), 400

        # Validar el archivo PDF
        is_valid, error_msg = validate_upload(file, file_type="document")
        if not is_valid:
            logger.warning(f"Archivo de incapacidad inválido para {numero_id}: {error_msg}")
            return jsonify({"error": error_msg}), 400

        # Obtener ruta de guardado
        try:
            upload_path = _get_user_incapacidad_folder(numero_id)
        except Exception as folder_err:
            logger.error(
                f"No se pudo crear el directorio de incapacidad para {numero_id}: {folder_err}",
                exc_info=True,
            )
            return (
                jsonify({"error": f"No se pudo crear el directorio del usuario: {folder_err}"}),
                500,
            )

        # Guardar el archivo PDF
        user_session_id = session.get("user_id", "unknown")
        try:
            ts = datetime.now().strftime("%Y%m%d")
            custom_name = f"incapacidad_{data['tipo_incapacidad']}_{data['fecha_inicio']}_{ts}.pdf".replace(" ", "_")

            filepath = sanitize_and_save_file(file, upload_path, custom_name)
            ruta_guardada = os.path.relpath(filepath, USER_DATA_FOLDER)
            log_file_upload(file.filename, user_session_id, success=True)

        except (ValueError, IOError) as e:
            logger.error(
                f"Error al guardar soporte de incapacidad para {numero_id}: {e}",
                exc_info=True,
            )
            log_file_upload(file.filename, user_session_id, success=False, error=str(e))
            return jsonify({"error": f"Error al guardar el archivo PDF: {str(e)}"}), 500

        # Guardar en base de datos
        conn = g.db
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO incapacidades (
                    usuario_id, tipo_incapacidad, fecha_inicio, dias_incapacidad,
                    diagnostico, ruta_soporte_pdf, estado
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    numero_id,
                    data["tipo_incapacidad"],
                    data["fecha_inicio"],
                    int(data["dias_incapacidad"]),
                    data.get("diagnostico"),
                    ruta_guardada,
                    "Registrada",  # Estado inicial
                ),
            )
            conn.commit()

            nuevo_id = cur.lastrowid
            logger.info(
                f"Nueva incapacidad registrada con ID: {nuevo_id} para usuario {numero_id} por user_id: {user_session_id}"
            )

            nuevo_registro = conn.execute("SELECT * FROM incapacidades WHERE id = ?", (nuevo_id,)).fetchone()
            return jsonify(dict(nuevo_registro)), 201

        except sqlite3.IntegrityError as ie:
            conn.rollback()
            logger.error(
                f"Error de integridad al guardar incapacidad para {numero_id}: {ie}",
                exc_info=True,
            )
            return (
                jsonify({"error": "Error de integridad, verifique que el ID de usuario exista."}),
                409,
            )
        except Exception as db_err:
            conn.rollback()
            logger.error(
                f"Error de DB al guardar incapacidad para {numero_id}: {db_err}",
                exc_info=True,
            )
            return (
                jsonify({"error": f"Error al guardar en base de datos: {str(db_err)}"}),
                500,
            )
        # g.db se cierra automáticamente por app.after_request

    except Exception as e:
        logger.error(
            f"Error general en add_incapacidad (Usuario: {numero_id}): {e}",
            exc_info=True,
        )
        return jsonify({"error": f"Error inesperado en el servidor: {str(e)}"}), 500
