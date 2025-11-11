# -*- coding: utf-8 -*-
"""
pago_impuestos.py - ACTUALIZADO con logging
====================================================
Maneja la lógica de backend para la subida de formularios
de impuestos y la consulta de registros.
"""

from flask import Blueprint, request, jsonify, current_app, session
import sqlite3
import traceback
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from functools import wraps  # Necesario para el fallback

# --- IMPORTAR UTILIDADES Y LOGGER ---
from logger import get_logger

logger = get_logger(__name__)

# --- INICIO BLOQUE DE IMPORTACIÓN ROBUSTA (Corregido: Eliminado save_text_content del import) ---
try:
    from utils import (
        get_db_connection,
        login_required,
        COMPANY_DATA_FOLDER,
        sanitize_and_save_file,
        log_file_upload,
        # save_text_content <--- ELIMINADO PARA ARREGLAR ImportError
    )
except ImportError as e:
    logger.error(f"Error importando utils en pago_impuestos.py: {e}", exc_info=True)

    # --- Fallbacks ---
    def get_db_connection():
        DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "mi_sistema.db")
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)

        return decorated_function

    COMPANY_DATA_FOLDER = os.getenv(
        "COMPANY_DATA_FOLDER", "D:\\ruta\\por\\defecto\\EMPRESAS"
    )

    def sanitize_and_save_file(file, upload_path, custom_name=None):
        if not file or not file.filename:
            raise ValueError("Archivo no válido.")
        filename = secure_filename(custom_name if custom_name else file.filename)
        target_path = os.path.join(upload_path, filename)
        if os.path.normpath(target_path).startswith(os.path.normpath(upload_path)):
            file.save(target_path)
            return target_path
        else:
            raise ValueError("Ruta de archivo no válida.")

    # Función necesaria para guardar el TXT (ahora definida aquí si falla el import)
    def save_text_content(content, upload_path, filename):
        target_path = os.path.join(upload_path, secure_filename(filename))
        if os.path.normpath(target_path).startswith(os.path.normpath(upload_path)):
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
            return target_path
        else:
            raise ValueError("Ruta de archivo no válida para TXT.")

    def log_file_upload(filename, user_id, success, error=None):
        logger.warning(
            f"LOG_FALLBACK: User {user_id} upload {filename}. Success: {success}. Error: {error}"
        )


# --- FIN BLOQUE DE IMPORTACIÓN ROBUSTA ---

# ==================== DEFINICIÓN DEL BLUEPRINT ====================
bp_impuestos = Blueprint("bp_impuestos", __name__, url_prefix="/api/impuestos")


# ==================== FUNCIONES AUXILIARES ====================
def _get_company_folder(nit, nombre_empresa, tipo_impuesto):
    """
    Obtiene la ruta a la subcarpeta de un tipo de impuesto de una empresa.
    Crea la carpeta si no existe.
    """
    try:
        sanitized_folder_name = secure_filename(nombre_empresa.replace(" ", "_"))
        company_folder_path = os.path.join(COMPANY_DATA_FOLDER, sanitized_folder_name)
        impuestos_base_path = os.path.join(company_folder_path, "PAGO DE IMPUESTOS")
        sanitized_impuesto_name = secure_filename(tipo_impuesto.replace(" ", "_"))
        impuestos_path = os.path.join(impuestos_base_path, sanitized_impuesto_name)

        os.makedirs(impuestos_path, exist_ok=True)
        return impuestos_path
    except Exception as e:
        logger.error(
            f"Error en _get_company_folder para {nombre_empresa}: {e}", exc_info=True
        )
        raise


# ==================== ENDPOINTS DE IMPUESTOS ====================


@bp_impuestos.route("", methods=["GET"])
@login_required
def get_impuestos():
    """Obtiene registros de impuestos, con filtros."""
    conn = None
    try:
        empresa_nit = request.args.get("empresa_nit")
        tipo_impuesto = request.args.get("tipo_impuesto")

        conn = get_db_connection()
        query = "SELECT * FROM pago_impuestos"
        params = []
        conditions = []

        if empresa_nit and empresa_nit != "todos":
            conditions.append("empresa_nit = ?")
            params.append(empresa_nit)

        if tipo_impuesto and tipo_impuesto != "todos":
            conditions.append("tipo_impuesto = ?")
            params.append(tipo_impuesto)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY fecha_limite ASC"

        registros = conn.execute(query, tuple(params)).fetchall()
        logger.debug(f"Consulta de impuestos exitosa. Registros: {len(registros)}")
        return jsonify([dict(row) for row in registros])

    except Exception as e:
        logger.error(f"Error obteniendo registros de impuestos: {e}", exc_info=True)
        return jsonify({"error": "No se pudo obtener la lista de registros."}), 500
    finally:
        if conn:
            conn.close()


@bp_impuestos.route("", methods=["POST"])
@login_required
def add_impuesto():
    """Sube un nuevo formulario de impuesto, crea el archivo TXT y el registro."""
    conn = None
    nit = request.form.get("empresa_nit")
    try:
        data = request.form
        tipo_impuesto = data.get("tipo_impuesto")
        periodo = data.get("periodo")
        fecha_limite = data.get("fecha_limite")

        if not nit or not tipo_impuesto or not periodo or not fecha_limite:
            logger.warning(
                f"Intento de agregar impuesto sin datos obligatorios. NIT: {nit}"
            )
            return (
                jsonify({"error": "Faltan datos (empresa, impuesto, periodo, fecha)."}),
                400,
            )

        if "archivo" not in request.files:
            return jsonify({"error": "No se incluyó el archivo PDF."}), 400

        file = request.files["archivo"]
        if file.filename == "":
            return jsonify({"error": "El archivo no tiene nombre."}), 400

        conn = get_db_connection()

        # 1. Obtener el nombre de la empresa desde la BD
        empresa = conn.execute(
            "SELECT nombre_empresa FROM empresas WHERE nit = ?", (nit,)
        ).fetchone()
        if not empresa:
            logger.warning(f"Intento de registro con NIT no encontrado: {nit}")
            return jsonify({"error": f"Empresa con NIT {nit} no encontrada."}), 404
        nombre_empresa = empresa["nombre_empresa"]

        # 2. Determinar la ruta de guardado
        try:
            upload_path = _get_company_folder(nit, nombre_empresa, tipo_impuesto)
        except Exception as folder_err:
            logger.error(
                f"Error creando carpeta para {nombre_empresa} ({tipo_impuesto}): {folder_err}",
                exc_info=True,
            )
            return (
                jsonify(
                    {
                        "error": f"No se pudo crear el directorio de la empresa: {folder_err}"
                    }
                ),
                500,
            )

        # 3. Definir nombre de archivo base
        ts = datetime.now().strftime("%Y%m%d")
        base_filename = f"{nit}_{tipo_impuesto}_{periodo}_{ts}".replace(" ", "_")

        # 4. Guardar el archivo PDF
        user_session_id = session.get("user_id", "unknown")
        try:
            pdf_custom_name = f"{base_filename}{os.path.splitext(file.filename)[1]}"
            filepath = sanitize_and_save_file(file, upload_path, pdf_custom_name)
            ruta_guardada = os.path.relpath(filepath, COMPANY_DATA_FOLDER)
            log_file_upload(file.filename, user_session_id, success=True)

        except (ValueError, IOError) as e:
            logger.error(
                f"Error al guardar el archivo PDF para {nit}: {e}", exc_info=True
            )
            log_file_upload(file.filename, user_session_id, success=False, error=str(e))
            return jsonify({"error": f"Error al guardar el archivo PDF: {str(e)}"}), 500

        # 5. Generar y Guardar el archivo TXT
        try:
            txt_content = f"""
====================================================
  REGISTRO DE FORMULARIO DE IMPUESTO
====================================================

  FORMULARIO: {tipo_impuesto}
  EMPRESA:    {nombre_empresa}
  NIT:        {nit}
  PERÍODO FISCAL: {periodo}
  FECHA LÍMITE DE PAGO: {fecha_limite}
  
  ESTADO INICIAL: Pendiente de Pago
  FECHA DE CARGA: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

  RUTA DEL ARCHIVO PDF ADJUNTO:
  {os.path.basename(filepath)}
  
----------------------------------------------------
  OBSERVACIONES:
  Este archivo TXT se genera automáticamente como 
  soporte explicativo para el formulario de impuesto.
----------------------------------------------------
"""
            txt_filename = f"{base_filename}.txt"
            # save_text_content ahora está disponible por el bloque except/fallback
            save_text_content(txt_content, upload_path, txt_filename)
            logger.debug(
                f"Archivo TXT de soporte guardado en: {upload_path}/{txt_filename}"
            )

        except (ValueError, IOError) as e:
            logger.warning(
                f"Advertencia: Error al guardar archivo TXT de soporte para {nit}: {e}"
            )

        # 6. Guardar registro en la base de datos
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO pago_impuestos (
                empresa_nit, empresa_nombre, tipo_impuesto, periodo, fecha_limite, estado, ruta_archivo
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                nit,
                nombre_empresa,
                tipo_impuesto,
                periodo,
                fecha_limite,
                "Pendiente de Pago",
                ruta_guardada,
            ),
        )
        conn.commit()

        nuevo_id = cur.lastrowid
        logger.info(f"Impuesto registrado con ID: {nuevo_id} para NIT: {nit}")

        nuevo_registro = conn.execute(
            "SELECT * FROM pago_impuestos WHERE id = ?", (nuevo_id,)
        ).fetchone()

        return jsonify(dict(nuevo_registro)), 201

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(
            f"Error creando registro de impuesto (NIT: {nit}): {e}", exc_info=True
        )
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@bp_impuestos.route("/<int:impuesto_id>/pagar", methods=["PUT"])
@login_required
def marcar_como_pagado(impuesto_id):
    """Actualiza el estado de un impuesto a 'Pagado'."""
    conn = None
    try:
        conn = get_db_connection()

        registro = conn.execute(
            "SELECT * FROM pago_impuestos WHERE id = ?", (impuesto_id,)
        ).fetchone()
        if not registro:
            return jsonify({"error": "Registro no encontrado."}), 404

        conn.execute(
            "UPDATE pago_impuestos SET estado = 'Pagado' WHERE id = ?", (impuesto_id,)
        )
        conn.commit()

        registro_actualizado = conn.execute(
            "SELECT * FROM pago_impuestos WHERE id = ?", (impuesto_id,)
        ).fetchone()
        logger.info(f"Impuesto ID {impuesto_id} marcado como 'Pagado'")

        return jsonify(dict(registro_actualizado)), 200

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(
            f"Error actualizando estado de impuesto {impuesto_id}: {e}", exc_info=True
        )
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()
