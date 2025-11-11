# -*- coding: utf-8 -*-
"""
tutelas.py - ACTUALIZADO con logging
====================================================
Maneja la lógica para registrar y consultar tutelas legales.
"""

from flask import Blueprint, request, jsonify, session
import sqlite3
import os
import traceback
from datetime import datetime
from werkzeug.utils import secure_filename
from functools import wraps  # Necesario para el fallback

# --- IMPORTAR UTILIDADES Y LOGGER ---
from logger import get_logger

logger = get_logger(__name__)

# --- INICIO BLOQUE DE IMPORTACIÓN ROBUSTA (Corregido el error de try/except) ---
try:
    from utils import (
        get_db_connection,
        login_required,
        validate_upload,
        sanitize_and_save_file,
        USER_DATA_FOLDER,
        log_file_upload,
    )
except ImportError as e:
    logger.error(f"Error importando utils en tutelas.py: {e}", exc_info=True)

    # --- Fallbacks para evitar la caída total ---
    def get_db_connection():
        return None

    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)

        return decorated_function

    def validate_upload(f, file_type):
        return False, "Error de importación"

    def sanitize_and_save_file(f, p, n):
        raise ImportError("Error de importación")

    USER_DATA_FOLDER = "."

    def log_file_upload(f, u, s, e=None):
        pass


# --- FIN BLOQUE DE IMPORTACIÓN ROBUSTA ---

# ==================== DEFINICIÓN DEL BLUEPRINT ====================
bp_tutelas = Blueprint("bp_tutelas", __name__, url_prefix="/api/tutelas")


# ==================== FUNCIONES AUXILIARES ====================
def _get_user_tutela_folder(numero_id):
    """Obtiene/crea la carpeta de tutelas para un usuario."""
    try:
        user_folder_path = os.path.join(USER_DATA_FOLDER, str(numero_id), "TUTELAS")
        os.makedirs(user_folder_path, exist_ok=True)
        return user_folder_path
    except Exception as e:
        logger.error(
            f"Error creando carpeta de tutela para {numero_id}: {e}", exc_info=True
        )
        raise


# ==================== ENDPOINTS DE TUTELAS ====================


@bp_tutelas.route("", methods=["GET"])
@login_required
def get_tutelas():
    """Obtiene todos los registros de tutelas."""
    conn = None
    try:
        # Filtros opcionales
        usuario_id = request.args.get("usuario_id")
        empresa_nit = request.args.get("empresa_nit")

        conn = get_db_connection()
        query = (
            "SELECT t.*, u.primerNombre, u.primerApellido, e.nombre_empresa FROM tutelas t "
            "LEFT JOIN usuarios u ON t.usuario_id = u.numeroId "
            "LEFT JOIN empresas e ON u.empresa_nit = e.nit"
        )

        conditions = []
        params = []

        if usuario_id and usuario_id != "todos":
            conditions.append("t.usuario_id = ?")
            params.append(usuario_id)

        if empresa_nit and empresa_nit != "todos":
            conditions.append("u.empresa_nit = ?")
            params.append(empresa_nit)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY t.fecha_inicio DESC"

        tutelas = conn.execute(query, tuple(params)).fetchall()

        logger.debug(f"Se consultaron {len(tutelas)} tutelas")
        return jsonify([dict(row) for row in tutelas])

    except Exception as e:
        logger.error(f"Error obteniendo lista de tutelas: {e}", exc_info=True)
        return jsonify({"error": "No se pudo obtener la lista de tutelas."}), 500
    finally:
        if conn:
            conn.close()


@bp_tutelas.route("", methods=["POST"])
@login_required
def add_tutela():
    """Añade un nuevo registro de tutela y sube el soporte."""
    conn = None
    numero_id = request.form.get("usuario_id")  # Para logging
    try:
        data = request.form

        # Validación de datos
        required_fields = ["usuario_id", "motivo", "fecha_inicio"]
        if not all(field in data for field in required_fields):
            logger.warning(
                f"Intento de agregar tutela con campos faltantes. Usuario: {numero_id}"
            )
            return (
                jsonify(
                    {
                        "error": "Faltan campos obligatorios (usuario_id, motivo, fecha_inicio)."
                    }
                ),
                400,
            )

        if "soporte_pdf" not in request.files:
            logger.warning(
                f"Intento de agregar tutela sin soporte PDF. Usuario: {numero_id}"
            )
            return jsonify({"error": "No se incluyó el archivo PDF de soporte."}), 400

        file = request.files["soporte_pdf"]
        if file.filename == "":
            return jsonify({"error": "El archivo de soporte no tiene nombre."}), 400

        # Validar el archivo PDF
        is_valid, error_msg = validate_upload(file, file_type="document")
        if not is_valid:
            logger.warning(f"Archivo de tutela inválido para {numero_id}: {error_msg}")
            return jsonify({"error": error_msg}), 400

        # Obtener ruta de guardado
        try:
            upload_path = _get_user_tutela_folder(numero_id)
        except Exception as folder_err:
            logger.error(
                f"No se pudo crear el directorio de tutela para {numero_id}: {folder_err}",
                exc_info=True,
            )
            return (
                jsonify(
                    {
                        "error": f"No se pudo crear el directorio del usuario: {folder_err}"
                    }
                ),
                500,
            )

        # Guardar el archivo PDF
        user_session_id = session.get("user_id", "unknown")
        try:
            ts = datetime.now().strftime("%Y%m%d")
            custom_name = (
                f"tutela_{data['motivo']}_{data['fecha_inicio']}_{ts}.pdf".replace(
                    " ", "_"
                )
            )

            filepath = sanitize_and_save_file(file, upload_path, custom_name)
            ruta_guardada = os.path.relpath(filepath, USER_DATA_FOLDER)
            log_file_upload(file.filename, user_session_id, success=True)

        except (ValueError, IOError) as e:
            logger.error(
                f"Error al guardar soporte de tutela para {numero_id}: {e}",
                exc_info=True,
            )
            log_file_upload(file.filename, user_session_id, success=False, error=str(e))
            return jsonify({"error": f"Error al guardar el archivo PDF: {str(e)}"}), 500

        # Guardar en base de datos
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO tutelas (
                    usuario_id, motivo, fecha_inicio, estado, 
                    descripcion, ruta_soporte_pdf
                ) VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    numero_id,
                    data["motivo"],
                    data["fecha_inicio"],
                    "Registrada",  # Estado inicial
                    data.get("descripcion"),
                    ruta_guardada,
                ),
            )
            conn.commit()

            nuevo_id = cur.lastrowid
            logger.info(
                f"Nueva tutela registrada con ID: {nuevo_id} para usuario {numero_id} por user_id: {user_session_id}"
            )

            nuevo_registro = conn.execute(
                "SELECT * FROM tutelas WHERE id = ?", (nuevo_id,)
            ).fetchone()
            return jsonify(dict(nuevo_registro)), 201

        except sqlite3.IntegrityError as ie:
            conn.rollback()
            logger.error(
                f"Error de integridad al guardar tutela para {numero_id}: {ie}",
                exc_info=True,
            )
            return (
                jsonify(
                    {
                        "error": "Error de integridad, verifique que el ID de usuario exista."
                    }
                ),
                409,
            )
        except Exception as db_err:
            conn.rollback()
            logger.error(
                f"Error de DB al guardar tutela para {numero_id}: {db_err}",
                exc_info=True,
            )
            return (
                jsonify({"error": f"Error al guardar en base de datos: {str(db_err)}"}),
                500,
            )
        finally:
            if conn:
                conn.close()

    except Exception as e:
        logger.error(
            f"Error general en add_tutela (Usuario: {numero_id}): {e}",
            exc_info=True,
        )
        return jsonify({"error": f"Error inesperado en el servidor: {str(e)}"}), 500


# --- INICIO DE BLOQUE AÑADIDO (PARA CORREGIR ERROR 404) ---

@bp_tutelas.route("/empresas_list", methods=["GET"])
@login_required
def get_empresas_list():
    """Obtiene una lista simple de todas las empresas (NIT y Nombre) para dropdowns."""
    conn = None
    try:
        conn = get_db_connection()
        # Seleccionamos las columnas que necesita el dropdown del frontend
        empresas = conn.execute(
            "SELECT nit, nombre_empresa FROM empresas ORDER BY nombre_empresa ASC"
        ).fetchall()
        
        logger.debug(f"Se consultaron {len(empresas)} empresas para la lista.")
        # Devolvemos la lista en un formato JSON que el frontend pueda consumir
        return jsonify([dict(row) for row in empresas])

    except Exception as e:
        logger.error(f"Error obteniendo lista de empresas: {e}", exc_info=True)
        return jsonify({"error": "No se pudo obtener la lista de empresas."}), 500
    finally:
        if conn:
            conn.close()

# --- FIN DE BLOQUE AÑADIDO ---


# --- INICIO DE BLOQUE AÑADIDO (PARA AUTOCOMPLETAR) ---

@bp_tutelas.route("/usuario_global/<string:numero_id>", methods=["GET"])
@login_required
def get_usuario_por_id(numero_id):
    """
    Busca un usuario en la tabla 'usuarios' por su numeroId.
    Optimizado para autocompletar en el modal de tutelas.
    """
    conn = None
    try:
        # Nota: Esta búsqueda es simple y no usa tipoId,
        # si necesitas que sea por tipoId Y numeroId, ajusta la consulta
        conn = get_db_connection()
        usuario = conn.execute(
            "SELECT primerNombre, primerApellido FROM usuarios WHERE numeroId = ?",
            (numero_id,),
        ).fetchone()

        if usuario:
            logger.debug(f"Usuario (para tutela) encontrado por ID: {numero_id}")
            return jsonify(dict(usuario))
        else:
            logger.warning(f"Usuario (para tutela) no encontrado por ID: {numero_id}")
            return jsonify({"error": "Usuario no encontrado"}), 404

    except Exception as e:
        logger.error(f"Error buscando usuario (para tutela): {e}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500
    finally:
        if conn:
            conn.close()

# --- FIN DE BLOQUE AÑADIDO ---