# -*- coding: utf-8 -*-
"""
incapacidades.py - REFACTORIZADO con SQLAlchemy ORM
==================================================
Maneja la lógica para registrar y consultar incapacidades médicas.
"""
import os
from datetime import datetime
from flask import Blueprint, jsonify, request, session
from werkzeug.utils import secure_filename

from extensions import db
from models.orm_models import Incapacidad, Usuario, Empresa
from utils import login_required, USER_DATA_FOLDER, sanitize_and_save_file, validate_upload
from logger import logger

bp_incapacidades = Blueprint("bp_incapacidades", __name__, url_prefix="/api/incapacidades")

def _get_user_incapacidad_folder(numero_id):
    """Obtiene/crea la carpeta de incapacidades para un usuario."""
    try:
        user_folder_path = os.path.join(USER_DATA_FOLDER, str(numero_id), "INCAPACIDADES")
        os.makedirs(user_folder_path, exist_ok=True)
        return user_folder_path
    except Exception as e:
        logger.error(f"Error creando carpeta de incapacidad para {numero_id}: {e}", exc_info=True)
        raise

@bp_incapacidades.route("", methods=["GET"])
@login_required
def get_incapacidades():
    """Obtiene todos los registros de incapacidades usando ORM."""
    try:
        query = db.session.query(Incapacidad, Usuario, Empresa).join(Usuario, Incapacidad.usuario_id == Usuario.numeroId).join(Empresa, Usuario.empresa_nit == Empresa.nit)

        usuario_id = request.args.get("usuario_id")
        if usuario_id and usuario_id != "todos":
            query = query.filter(Incapacidad.usuario_id == usuario_id)

        empresa_nit = request.args.get("empresa_nit")
        if empresa_nit and empresa_nit != "todos":
            query = query.filter(Usuario.empresa_nit == empresa_nit)

        results = query.order_by(Incapacidad.fecha_inicio.desc()).all()

        incapacidades_list = []
        for incapacidad, usuario, empresa in results:
            inc_dict = incapacidad.to_dict()
            inc_dict['primerNombre'] = usuario.primerNombre
            inc_dict['primerApellido'] = usuario.primerApellido
            inc_dict['nombre_empresa'] = empresa.nombre_empresa
            incapacidades_list.append(inc_dict)
        
        logger.debug(f"Se consultaron {len(incapacidades_list)} incapacidades")
        return jsonify(incapacidades_list)

    except Exception as e:
        logger.error(f"Error obteniendo lista de incapacidades: {e}", exc_info=True)
        return jsonify({"error": "No se pudo obtener la lista de incapacidades."}), 500

@bp_incapacidades.route("", methods=["POST"])
@login_required
def add_incapacidad():
    """Añade un nuevo registro de incapacidad usando ORM."""
    numero_id = request.form.get("usuario_id")
    try:
        data = request.form
        required_fields = ["usuario_id", "diagnostico", "fecha_inicio", "fecha_fin"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Faltan campos obligatorios."}), 400

        if "archivos_info" not in request.files:
            return jsonify({"error": "No se incluyó el archivo PDF de soporte."}), 400

        file = request.files["archivos_info"]
        if file.filename == "":
            return jsonify({"error": "El archivo de soporte no tiene nombre."}), 400

        is_valid, error_msg = validate_upload(file, file_type="document")
        if not is_valid:
            return jsonify({"error": error_msg}), 400

        upload_path = _get_user_incapacidad_folder(numero_id)
        filepath = sanitize_and_save_file(file, upload_path)
        ruta_guardada = os.path.relpath(filepath, USER_DATA_FOLDER)

        # Crear nueva incapacidad con ORM
        nueva_incapacidad = Incapacidad(
            empresa_nit=data["empresa_nit"],
            usuario_id=numero_id,
            diagnostico=data["diagnostico"],
            fecha_inicio=data["fecha_inicio"],
            fecha_fin=data["fecha_fin"],
            estado="Registrada",
            archivos_info=ruta_guardada
        )

        db.session.add(nueva_incapacidad)
        db.session.commit()

        logger.info(f"Nueva incapacidad registrada con ID: {nueva_incapacidad.id} para usuario {numero_id}")
        return jsonify(nueva_incapacidad.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error general en add_incapacidad (Usuario: {numero_id}): {e}", exc_info=True)
        return jsonify({"error": f"Error inesperado en el servidor: {str(e)}"}), 500