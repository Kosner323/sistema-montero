# -*- coding: utf-8 -*-
"""
usuarios.py - ACTUALIZADO con validación de archivos y logging
==================================================
Valida cédulas PDF, firma digital y usa logging profesional
"""

import base64
import os
import sqlite3
import traceback
from datetime import datetime

from flask import Blueprint, jsonify, request, session
from werkzeug.utils import secure_filename

# --- IMPORTAR UTILIDADES Y LOGGER ---
from logger import logger

# --- INICIO DE CORRECCIÓN DE RUTA ---
try:
    from utils import (  # USER_DATA_FOLDER, # <-- Eliminada de la importación; NUEVAS FUNCIONES DE VALIDACIÓN
        format_key,
        get_db_connection,
        log_file_upload,
        login_required,
        sanitize_and_save_file,
        validate_upload,
    )

    # Leer la variable del .env, con el fallback correcto
    USER_DATA_FOLDER = os.getenv("USER_DATA_FOLDER", "../../MONTERO_NEGOCIO/MONTERO_TOTAL/USUARIOS")
except ImportError as e:
    # --- FIN DE CORRECCIÓN DE RUTA ---
    logger.error(f"Error importando utils en usuarios.py: {e}", exc_info=True)

    # Fallbacks
    def get_db_connection():
        return None

    def login_required(f):
        return f

    def format_key(k):
        return k

    USER_DATA_FOLDER = "."  # Fallback de emergencia si utils falla

    def validate_upload(f, file_type):
        return False, "Error de importación"

    def sanitize_and_save_file(f, p, n):
        raise ImportError("Error de importación")

    def log_file_upload(f, u, s, e=None):
        pass


# ==================== DEFINICIÓN DEL BLUEPRINT ====================
usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/api/usuarios")


# ==================== ENDPOINTS DE USUARIOS ====================
@usuarios_bp.route("", methods=["POST"])
@login_required
def add_usuario():
    """
    Endpoint para agregar usuarios.
    Soporta dos modos:
    1. JSON (para API simple): campos nombre_completo, email, tipo_documento, numero_documento, etc.
    2. Form data (para formulario completo con archivos)
    """
    from typing import Optional

    from flask import g
    from pydantic import BaseModel, Field, ValidationError

    # Modelo Pydantic para validación de JSON
    class UsuarioCreate(BaseModel):
        nombre_completo: str = Field(..., min_length=1)
        email: Optional[str] = None
        tipo_documento: Optional[str] = None
        numero_documento: str = Field(..., min_length=1)
        telefono: Optional[str] = None
        cargo: Optional[str] = None
        empresa_nit: Optional[str] = None

    conn = None
    numero_documento = "desconocido"

    try:
        # Detectar si es JSON o Form data
        is_json = request.is_json

        if is_json:
            # ==================== MODO JSON (API SIMPLE) ====================
            try:
                # Validación con Pydantic
                usuario_data = UsuarioCreate(**request.get_json())
            except ValidationError as ve:
                logger.warning(f"Error de validación Pydantic: {ve}")
                return jsonify({"error": "Datos inválidos", "details": ve.errors()}), 422

            numero_documento = usuario_data.numero_documento

            if not numero_documento:
                logger.warning("Intento de agregar usuario sin Número de ID")
                return jsonify({"error": "Número de ID es obligatorio."}), 400

            # Guardar en base de datos (modo simple)
            conn = g.db
            try:
                conn.execute(
                    """
                    INSERT INTO usuarios (
                        nombre_completo, email, tipo_documento, numero_documento,
                        telefono, cargo, empresa_nit
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        usuario_data.nombre_completo,
                        usuario_data.email,
                        usuario_data.tipo_documento,
                        usuario_data.numero_documento,
                        usuario_data.telefono,
                        usuario_data.cargo,
                        usuario_data.empresa_nit,
                    ),
                )
                conn.commit()

                logger.info(f"Usuario {numero_documento} creado exitosamente (modo JSON)")
                return jsonify({"message": f"Usuario creado: {numero_documento}"}), 201

            except sqlite3.IntegrityError as ie:
                conn.rollback()
                if "UNIQUE constraint failed" in str(ie):
                    logger.warning(f"Intento de duplicar usuario. ID: {numero_documento}")
                    return jsonify({"error": "El usuario ya existe."}), 409
                else:
                    logger.error(f"Error de integridad: {ie}", exc_info=True)
                    return jsonify({"error": f"Error de integridad: {ie}"}), 409
            except Exception as db_err:
                conn.rollback()
                logger.error(f"Error al guardar usuario {numero_documento}: {db_err}", exc_info=True)
                return jsonify({"error": f"Error al guardar: {str(db_err)}"}), 500

        else:
            # ==================== MODO FORM DATA (FORMULARIO COMPLETO) ====================
            data = request.form
            numero_id = data.get("numeroId")
            if not numero_id:
                logger.warning("Intento de agregar usuario sin Número de ID")
                return jsonify({"error": "Número de ID es obligatorio."}), 400

            numero_documento = numero_id

            # Crear carpeta de usuario
            user_folder_path = os.path.join(USER_DATA_FOLDER, numero_id)
            os.makedirs(user_folder_path, exist_ok=True)
            logger.info(
                f"Carpeta creada para usuario: {numero_id} en {user_folder_path}"
            )  # Log actualizado para verificar ruta

            # Crear archivo de texto con datos
            txt_content = f"--- DATOS AFILIADO: {numero_id} ---\n\n"
            beneficiarios_content = ""
            beneficiario_count = 0
            beneficiario_keys = {}  # Para agrupar datos de beneficiarios por índice

            # Iterar sobre los datos del formulario
            for key, value in data.items():
                if key in ["firmaDigitalData", "documentoPdf"]:
                    continue

                if key.startswith(("nombreBeneficiario_", "parentesco_", "documentoBeneficiario_")):
                    parts = key.split("_")
                    if len(parts) == 2:
                        field_type, index = parts[0], parts[1]
                        if index not in beneficiario_keys:
                            beneficiario_keys[index] = {}
                        beneficiario_keys[index][field_type] = value
                else:
                    txt_content += f"{format_key(key)}: {value}\n"

            # Procesar y añadir beneficiarios al texto
            if beneficiario_keys:
                beneficiarios_content += "\n--- BENEFICIARIOS ---\n"

                # --- INICIO DE CORRECCIÓN 'X' ---
                # Filtrar solo claves que sean numéricas (ignora la 'X' de la plantilla)
                numeric_indices = [k for k in beneficiario_keys.keys() if k.isdigit()]
                sorted_indices = sorted(numeric_indices, key=int)
                # --- FIN DE CORRECCIÓN 'X' ---

                for index in sorted_indices:
                    b = beneficiario_keys[index]
                    nombre = b.get("nombreBeneficiario", "N/A")
                    parentesco = b.get("parentesco", "N/A")
                    documento = b.get("documentoBeneficiario", "N/A")
                    if nombre != "N/A":
                        beneficiario_count += 1
                        beneficiarios_content += f"\nBeneficiario #{beneficiario_count}:\n  Nombre: {nombre}\n  Parentesco: {parentesco}\n  Documento ID: {documento}\n"

            # Escribir el archivo de texto
            with open(os.path.join(user_folder_path, "datos_usuario.txt"), "w", encoding="utf-8") as f:
                f.write(txt_content + beneficiarios_content)

            # ==================== VALIDACIÓN Y GUARDADO DE ARCHIVOS ====================

            saved_files = {}
            upload_errors = []
            user_session_id = session.get("user_id", "unknown")

            # 1. FIRMA DIGITAL (base64)
            firma_data_url = data.get("firmaDigitalData")
            if firma_data_url and "," in firma_data_url:
                try:
                    _, encoded = firma_data_url.split(",", 1)
                    firma_data = base64.b64decode(encoded)

                    if len(firma_data) <= 2 * 1024 * 1024:  # Validar tamaño (máximo 2MB)
                        with open(os.path.join(user_folder_path, "firma_usuario.png"), "wb") as f:
                            f.write(firma_data)
                        saved_files["firma"] = "firma_usuario.png"
                        log_file_upload("firma_usuario.png", user_session_id, success=True)
                    else:
                        upload_errors.append("Firma digital: Tamaño excedido (máximo 2MB)")
                        log_file_upload(
                            "firma_usuario.png",
                            user_session_id,
                            success=False,
                            error="Tamaño excedido",
                        )
                except Exception as e:
                    logger.error(
                        f"Error decodificando o guardando firma para usuario {numero_id}: {e}",
                        exc_info=True,
                    )
                    upload_errors.append(f"Firma digital: Error al procesar ({str(e)})")
                    log_file_upload("firma_usuario.png", user_session_id, success=False, error=str(e))

            # 2. DOCUMENTO PDF (cédula) - VALIDACIÓN CRÍTICA
            if "documentoPdf" in request.files:
                pdf_file = request.files["documentoPdf"]
                if pdf_file and pdf_file.filename:
                    is_valid, error_msg = validate_upload(pdf_file, file_type="document")

                    if is_valid:
                        try:
                            custom_name = f"cedula_{numero_id}.pdf"
                            filepath = sanitize_and_save_file(pdf_file, user_folder_path, custom_name)
                            saved_files["cedula"] = os.path.basename(filepath)
                            log_file_upload(pdf_file.filename, user_session_id, success=True)

                        except (ValueError, IOError) as e:
                            upload_errors.append(f"Cédula PDF: {str(e)}")
                            log_file_upload(
                                pdf_file.filename,
                                user_session_id,
                                success=False,
                                error=str(e),
                            )
                    else:
                        upload_errors.append(f"Cédula PDF: {error_msg}")
                        log_file_upload(
                            pdf_file.filename,
                            user_session_id,
                            success=False,
                            error=error_msg,
                        )

            # Crear subcarpetas estándar
            subfolders = [
                "PLANILLAS",
                "MORAS",
                "EMPRESAS_AFILIADAS",
                "INCAPACIDADES",
                "BENEFICIARIOS",
                "NOVEDADES",
                "TUTELAS",
                "DEPURACIONES",
                "USUARIOS Y CONTRASEÑAS",
                "RECIBOS",
            ]
            for folder in subfolders:
                os.makedirs(os.path.join(user_folder_path, folder), exist_ok=True)

            os.makedirs(os.path.join(user_folder_path, "RECIBOS", "RECIBOS DE CAJA"), exist_ok=True)
            os.makedirs(
                os.path.join(user_folder_path, "RECIBOS", "COMPROBANTES DE CONSIGNACION"),
                exist_ok=True,
            )

            # ==================== GUARDAR EN BASE DE DATOS ====================
            conn = get_db_connection()
            try:
                empresa_nit = None
                if data.get("administracion"):
                    empresa = conn.execute(
                        "SELECT nit FROM empresas WHERE nombre_empresa = ?",
                        (data["administracion"],),
                    ).fetchone()
                    if empresa:
                        empresa_nit = empresa["nit"]
                    else:
                        logger.warning(
                            f"Advertencia: Empresa '{data['administracion']}' no encontrada en la tabla 'empresas' para el usuario {numero_id}."
                        )

                afp_costo = float(data.get("afpCosto")) if data.get("afpCosto") else None
                eps_costo = float(data.get("epsCosto")) if data.get("epsCosto") else None
                arl_costo = float(data.get("arlCosto")) if data.get("arlCosto") else None
                ccf_costo = float(data.get("ccfCosto")) if data.get("ccfCosto") else None
                ibc = float(data.get("ibc")) if data.get("ibc") else None

                conn.execute(
                    """
                    INSERT INTO usuarios (
                        empresa_nit, tipoId, numeroId, primerNombre, segundoNombre, primerApellido, segundoApellido,
                        sexoBiologico, sexoIdentificacion, nacionalidad, fechaNacimiento, paisNacimiento,
                        departamentoNacimiento, municipioNacimiento, direccion, telefonoCelular, telefonoFijo,
                        correoElectronico, comunaBarrio, afpNombre, afpCosto, epsNombre, epsCosto, arlNombre,
                        arlCosto, ccfNombre, ccfCosto, administracion, ibc, claseRiesgoARL, fechaIngreso
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        empresa_nit,
                        data.get("tipoId"),
                        numero_id,
                        data.get("primerNombre"),
                        data.get("segundoNombre"),
                        data.get("primerApellido"),
                        data.get("segundoApellido"),
                        data.get("sexoBiologico"),
                        data.get("sexoIdentificacion"),
                        data.get("nacionalidad"),
                        data.get("fechaNacimiento"),
                        data.get("paisNacimiento"),
                        data.get("departamentoNacimiento"),
                        data.get("municipioNacimiento"),
                        data.get("direccion"),
                        data.get("telefonoCelular"),
                        data.get("telefonoFijo"),
                        data.get("correoElectronico"),
                        data.get("comunaBarrio"),
                        data.get("afpNombre"),
                        afp_costo,
                        data.get("epsNombre"),
                        eps_costo,
                        data.get("arlNombre"),
                        arl_costo,
                        data.get("ccfNombre"),
                        ccf_costo,
                        data.get("administracion"),
                        ibc,
                        data.get("claseRiesgoARL"),
                        data.get("fechaIngreso"),
                    ),
                )
                conn.commit()

                logger.info(f"Usuario {numero_id} guardado exitosamente por user_id: {user_session_id}")

                response_data = {
                    "message": f"Usuario {numero_id} guardado exitosamente.",
                    "archivos_guardados": saved_files,
                }

                if upload_errors:
                    response_data["advertencias"] = upload_errors
                    response_data[
                        "mensaje_advertencia"
                    ] = f"Usuario creado pero {len(upload_errors)} archivo(s) no pudieron procesarse."
                    logger.warning(f"Usuario {numero_id} creado con {len(upload_errors)} errores de carga: {upload_errors}")

                return jsonify(response_data), 201

            except sqlite3.IntegrityError as ie:
                conn.rollback()
                # --- CORRECCIÓN: Detectar la restricción de constraint correcta ---
                # La restricción UNIQUE está en (tipoId, numeroId) según tu log anterior
                if "UNIQUE constraint failed: usuarios.tipoId, usuarios.numeroId" in str(ie):
                    logger.warning(f"Intento de duplicar usuario. ID: {numero_id}")
                    return jsonify({"error": "La combinación de Tipo de ID y Número de ID ya existe."}), 409
                # Fallback por si acaso
                elif "UNIQUE constraint failed: usuarios.numeroId" in str(ie):
                    logger.warning(f"Intento de duplicar usuario (solo numeroId). ID: {numero_id}")
                    return jsonify({"error": "El Número de ID ingresado ya existe."}), 409
                else:
                    logger.error(
                        f"Error de integridad al guardar usuario {numero_id}: {ie}",
                        exc_info=True,
                    )
                    return (
                        jsonify({"error": f"Error de integridad en base de datos: {ie}"}),
                        409,
                    )
            except Exception as db_err:
                conn.rollback()
                logger.error(
                    f"Error general al guardar usuario {numero_id} en DB: {db_err}",
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
        logger.error(f"Error general en add_usuario (ID: {numero_id}): {e}", exc_info=True)
        return jsonify({"error": f"Error inesperado en el servidor: {str(e)}"}), 500


@usuarios_bp.route("", methods=["GET"])
@login_required
def get_usuarios():
    """Obtiene lista de usuarios"""
    from flask import g

    conn = None
    try:
        empresa_nit = request.args.get("empresa_nit")
        conn = g.db

        # Intentar buscar por nombre_completo (tabla simple) o primerNombre (tabla compleja)
        try:
            if empresa_nit:
                usuarios = conn.execute(
                    "SELECT * FROM usuarios WHERE empresa_nit = ? ORDER BY nombre_completo",
                    (empresa_nit,),
                ).fetchall()
            else:
                usuarios = conn.execute("SELECT * FROM usuarios ORDER BY nombre_completo").fetchall()
        except sqlite3.OperationalError:
            # Si falla con nombre_completo, intentar con primerNombre
            if empresa_nit:
                usuarios = conn.execute(
                    "SELECT * FROM usuarios WHERE empresa_nit = ? ORDER BY primerNombre, primerApellido",
                    (empresa_nit,),
                ).fetchall()
            else:
                usuarios = conn.execute("SELECT * FROM usuarios ORDER BY primerNombre, primerApellido").fetchall()

        usuarios_list = [dict(row) for row in usuarios]
        logger.debug(f"Se consultaron {len(usuarios_list)} usuarios (filtro NIT: {empresa_nit})")

        # Formato esperado por los tests
        return jsonify({"items": usuarios_list, "total_items": len(usuarios_list)})
    except Exception as e:
        logger.error(f"Error obteniendo lista de usuarios: {e}", exc_info=True)
        return jsonify({"error": "No se pudo obtener la lista de usuarios."}), 500


# --- COPIAR Y PEGAR ESTE BLOQUE EN usuarios.py ---


@usuarios_bp.route("/buscar", methods=["GET"])
@login_required
def buscar_usuario():
    """
    Busca un usuario específico por tipo y número de ID.
    Optimizado para búsquedas rápidas desde el frontend.
    """
    conn = None
    try:
        tipo_id = request.args.get("tipoId")
        numero_id = request.args.get("numeroId")

        if not tipo_id or not numero_id:
            logger.warning(f"Búsqueda de usuario fallida: faltan parámetros (tipoId o numeroId)")
            return jsonify({"error": "Faltan tipoId y numeroId"}), 400

        conn = get_db_connection()
        usuario = conn.execute(
            "SELECT * FROM usuarios WHERE tipoId = ? AND numeroId = ?",
            (tipo_id, numero_id),
        ).fetchone()

        if usuario:
            logger.debug(f"Usuario encontrado por ID: {numero_id}")
            return jsonify(dict(usuario))  # Devolver el objeto de usuario único
        else:
            logger.warning(f"Usuario no encontrado por ID: {tipo_id} - {numero_id}")
            return jsonify({"error": "Usuario no encontrado"}), 404

    except Exception as e:
        logger.error(f"Error buscando usuario: {e}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500
    finally:
        if conn:
            conn.close()


# --- FIN DEL BLOQUE PARA COPIAR ---
