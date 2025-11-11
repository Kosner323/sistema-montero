# -*- coding: utf-8 -*-
"""
empresas.py - ACTUALIZADO con validación de archivos y logging
====================================================
Este archivo maneja la lógica para el CRUD de empresas,
la validación de archivos y el logging profesional.
"""

from flask import Blueprint, request, jsonify, session
import sqlite3
import os
import traceback
import base64
from werkzeug.utils import secure_filename

# --- IMPORTAR UTILIDADES Y LOGGER ---
from logger import get_logger

logger = get_logger(__name__)

# --- INICIO DE CORRECCIÓN DE RUTA ---
try:
    from utils import (
        get_db_connection,
        login_required,
        format_key,
        # COMPANY_DATA_FOLDER, # <-- Eliminada de la importación
        # NUEVAS FUNCIONES DE VALIDACIÓN
        validate_upload,
        validate_multiple_uploads,
        sanitize_and_save_file,
        get_file_info,
        log_file_upload,
    )
    # Leer la variable del .env, con el fallback correcto
    COMPANY_DATA_FOLDER = os.getenv("COMPANY_DATA_FOLDER", "../../MONTERO_NEGOCIO/MONTERO_TOTAL/EMPRESAS")
except ImportError as e:
# --- FIN DE CORRECCIÓN DE RUTA ---
    logger.error(f"Error importando utils en empresas.py: {e}", exc_info=True)

    # Fallbacks si utils no se encuentra (no ideal)
    def get_db_connection():
        return None

    def login_required(f):
        return f

    def format_key(k):
        return k

    COMPANY_DATA_FOLDER = "." # Fallback de emergencia si utils falla

    def validate_upload(f, file_type):
        return False, "Error de importación"

    def sanitize_and_save_file(f, p, n):
        raise ImportError("Error de importación")

    def log_file_upload(f, u, s, e=None):
        pass


# ==================== DEFINICIÓN DEL BLUEPRINT ====================
bp_empresas = Blueprint("bp_empresas", __name__, url_prefix="/api/empresas")


# ==================== ENDPOINTS DE EMPRESAS ====================
@bp_empresas.route("", methods=["POST"])
@login_required
def add_empresa():
    conn = None
    try:
        data = request.form
        nombre_empresa = data.get("nombre_empresa")
        nit = data.get("nit")

        if not nombre_empresa or not nit:
            logger.warning(f"Intento de agregar empresa sin nombre o NIT. NIT: {nit}")
            return jsonify({"error": "Nombre y NIT obligatorios."}), 400

        # Crear carpeta de empresa
        sanitized_folder_name = secure_filename(f"{nit}_{nombre_empresa}")
        company_folder_path = os.path.join(COMPANY_DATA_FOLDER, sanitized_folder_name)
        os.makedirs(company_folder_path, exist_ok=True)
        logger.info(f"Carpeta creada para empresa: {company_folder_path}") # Log actualizado para verificar ruta

        # Crear subcarpetas estándar
        subfolders = [
            "USUARIOS Y CONTRASEÑAS",
            "PAGO DE IMPUESTOS",
            "EXTRACTOS BANCARIOS",
            "COTIZACIONES",
            "OTROS_ADJUNTOS",
        ]
        for folder in subfolders:
            os.makedirs(os.path.join(company_folder_path, folder), exist_ok=True)

        # Crear archivo de texto con datos
        txt_content = f"--- DATOS EMPRESA: {nombre_empresa} (NIT: {nit}) ---\n\n"
        for key, value in data.items():
            if (
                key != "firmaDigitalBase64"
                and key not in request.files
                and not key.startswith("otrosAdjuntos")
            ):
                txt_content += f"{format_key(key)}: {value}\n"

        with open(
            os.path.join(company_folder_path, "datos_empresa.txt"),
            "w",
            encoding="utf-8",
        ) as f:
            f.write(txt_content)

        # ==================== VALIDACIÓN Y GUARDADO DE ARCHIVOS ====================

        saved_files = {}
        upload_errors = []
        user_id = session.get("user_id", "unknown")  # Usar session, no request.session

        # 1. LOGO DE LA EMPRESA (debe ser imagen)
        if "logoEmpresa" in request.files:
            logo_file = request.files["logoEmpresa"]
            if logo_file and logo_file.filename:
                is_valid, error_msg = validate_upload(logo_file, file_type="image")

                if is_valid:
                    try:
                        _, extension = os.path.splitext(logo_file.filename)
                        custom_name = f"logo{extension}"
                        filepath = sanitize_and_save_file(
                            logo_file, company_folder_path, custom_name
                        )
                        saved_files["logo"] = os.path.basename(filepath)
                        log_file_upload(logo_file.filename, user_id, success=True)
                    except (ValueError, IOError) as e:
                        upload_errors.append(f"Logo: {str(e)}")
                        log_file_upload(
                            logo_file.filename, user_id, success=False, error=str(e)
                        )
                else:
                    upload_errors.append(f"Logo: {error_msg}")
                    log_file_upload(
                        logo_file.filename, user_id, success=False, error=error_msg
                    )

        # 2. DOCUMENTOS PDF (cédula, RUT, cámara de comercio, etc.)
        pdf_fields = {
            "cedulaRepresentante": "cedula_representante.pdf",
            "rut": "rut.pdf",
            "camaraComercio": "camara_comercio.pdf",
            "certificadoARL": "certificado_arl.pdf",
            "cuentaBancaria": "cuenta_bancaria.pdf",
            "carta": "carta.pdf",
        }

        for field_name, save_name in pdf_fields.items():
            if field_name in request.files:
                pdf_file = request.files[field_name]
                if pdf_file and pdf_file.filename:
                    is_valid, error_msg = validate_upload(
                        pdf_file, file_type="document"
                    )

                    if is_valid:
                        try:
                            filepath = sanitize_and_save_file(
                                pdf_file, company_folder_path, save_name
                            )
                            saved_files[field_name] = os.path.basename(filepath)
                            log_file_upload(pdf_file.filename, user_id, success=True)
                        except (ValueError, IOError) as e:
                            upload_errors.append(f"{format_key(field_name)}: {str(e)}")
                            log_file_upload(
                                pdf_file.filename, user_id, success=False, error=str(e)
                            )
                    else:
                        upload_errors.append(f"{format_key(field_name)}: {error_msg}")
                        log_file_upload(
                            pdf_file.filename, user_id, success=False, error=error_msg
                        )

        # 3. FIRMA DIGITAL (base64)
        firma_data_url = data.get("firmaDigitalBase64")
        if firma_data_url and "," in firma_data_url:
            try:
                header, encoded = firma_data_url.split(",", 1)
                firma_data = base64.b64decode(encoded)

                if len(firma_data) <= 2 * 1024 * 1024:  # Validar tamaño (máximo 2MB)
                    with open(
                        os.path.join(company_folder_path, "firma_representante.png"),
                        "wb",
                    ) as f:
                        f.write(firma_data)
                    saved_files["firma"] = "firma_representante.png"
                    log_file_upload("firma_representante.png", user_id, success=True)
                else:
                    upload_errors.append("Firma digital: Tamaño excedido (máximo 2MB)")
            except Exception as e:
                logger.error(f"Error procesando firma para {nit}: {e}", exc_info=True)
                upload_errors.append(f"Firma digital: Error al procesar ({str(e)})")

        # 4. OTROS ADJUNTOS (múltiples archivos)
        if "otrosAdjuntos" in request.files:
            otros_adjuntos_path = os.path.join(company_folder_path, "OTROS_ADJUNTOS")
            files = request.files.getlist("otrosAdjuntos")

            all_valid, file_errors = validate_multiple_uploads(files, file_type="all")

            if not all_valid:
                upload_errors.extend([f"Otros adjuntos: {err}" for err in file_errors])

            otros_saved = []
            for file in files:
                if file and file.filename:
                    is_valid, error_msg = validate_upload(file, file_type="all")
                    if is_valid:
                        try:
                            filepath = sanitize_and_save_file(file, otros_adjuntos_path)
                            otros_saved.append(os.path.basename(filepath))
                            log_file_upload(file.filename, user_id, success=True)
                        except (ValueError, IOError) as e:
                            upload_errors.append(f"Archivo {file.filename}: {str(e)}")
                            log_file_upload(
                                file.filename, user_id, success=False, error=str(e)
                            )

            if otros_saved:
                saved_files["otros_adjuntos"] = otros_saved

        # ==================== GUARDAR EN BASE DE DATOS ====================
        conn = get_db_connection()
        try:
            conn.execute(
                """
                INSERT INTO empresas (nombre_empresa, tipo_identificacion_empresa, nit, direccion_empresa, telefono_empresa, correo_empresa, departamento_empresa, ciudad_empresa, ibc_empresa, afp_empresa, arl_empresa, rep_legal_nombre, rep_legal_tipo_id, rep_legal_numero_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    nombre_empresa,
                    data.get("tipo_identificacion_empresa"),
                    nit,
                    data.get("direccion_empresa"),
                    data.get("telefono_empresa"),
                    data.get("correo_empresa"),
                    data.get("departamento_empresa"),
                    data.get("ciudad_empresa"),
                    data.get("ibc_empresa"),
                    data.get("afp_empresa"),
                    data.get("arl_empresa"),
                    data.get("rep_legal_nombre"),
                    data.get("rep_legal_tipo_id"),
                    data.get("rep_legal_numero_id"),
                ),
            )
            conn.commit()

            logger.info(
                f"Empresa '{nombre_empresa}' (NIT: {nit}) guardada exitosamente por user_id: {user_id}"
            )

            response_data = {
                "message": f"Empresa '{nombre_empresa}' guardada exitosamente.",
                "archivos_guardados": saved_files,
            }

            if upload_errors:
                response_data["advertencias"] = upload_errors
                response_data["mensaje_advertencia"] = (
                    f"La empresa fue creada pero {len(upload_errors)} archivo(s) no pudieron procesarse."
                )
                logger.warning(
                    f"Empresa {nit} creada con {len(upload_errors)} errores de carga: {upload_errors}"
                )

            return jsonify(response_data), 201

        except sqlite3.IntegrityError:
            conn.rollback()
            logger.warning(f"Intento de duplicar NIT: {nit}")
            return (
                jsonify({"error": "El NIT ingresado ya existe en la base de datos."}),
                409,
            )
        except Exception as db_err:
            conn.rollback()
            logger.error(
                f"Error al guardar empresa en DB (NIT: {nit}): {db_err}", exc_info=True
            )
            return (
                jsonify({"error": f"Error al guardar en base de datos: {str(db_err)}"}),
                500,
            )
        finally:
            if conn:
                conn.close()

    except Exception as e:
        logger.error(f"Error general en add_empresa: {e}", exc_info=True)
        return jsonify({"error": f"Error inesperado en el servidor: {str(e)}"}), 500


@bp_empresas.route("", methods=["GET"])
@login_required
def get_empresas():
    """Obtiene lista de empresas"""
    conn = None
    try:
        conn = get_db_connection()
        empresas = conn.execute(
            "SELECT * FROM empresas ORDER BY nombre_empresa"
        ).fetchall()
        logger.debug(f"Se consultaron {len(empresas)} empresas")
        return jsonify([dict(row) for row in empresas])
    except Exception as e:
        logger.error(f"Error obteniendo lista de empresas: {e}", exc_info=True)
        return jsonify({"error": "No se pudo obtener la lista de empresas."}), 500
    finally:
        if conn:
            conn.close()