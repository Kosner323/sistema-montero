# -*- coding: utf-8 -*-
"""
tutelas.py - REFACTORIZADO con SQLAlchemy ORM
====================================================
Maneja la lógica para registrar y consultar tutelas legales.
"""
import os
from datetime import datetime
from flask import Blueprint, jsonify, request, session

from extensions import db
from models.orm_models import Tutela, Usuario, Empresa
from utils import login_required, USER_DATA_FOLDER, sanitize_and_save_file, validate_upload
from logger import logger

bp_tutelas = Blueprint("bp_tutelas", __name__, url_prefix="/api/tutelas")

def _get_user_tutela_folder(numero_id):
    """Obtiene/crea la carpeta de tutelas para un usuario."""
    try:
        user_folder_path = os.path.join(USER_DATA_FOLDER, str(numero_id), "TUTELAS")
        os.makedirs(user_folder_path, exist_ok=True)
        return user_folder_path
    except Exception as e:
        logger.error(f"Error creando carpeta de tutela para {numero_id}: {e}", exc_info=True)
        raise

@bp_tutelas.route("", methods=["GET"])
@login_required
def get_tutelas():
    """Obtiene todos los registros de tutelas usando ORM."""
    try:
        query = db.session.query(Tutela, Usuario, Empresa).join(Usuario, Tutela.usuario_id == Usuario.numeroId).join(Empresa, Tutela.empresa_nit == Empresa.nit)

        usuario_id = request.args.get("usuario_id")
        if usuario_id and usuario_id != "todos":
            query = query.filter(Tutela.usuario_id == usuario_id)

        empresa_nit = request.args.get("empresa_nit")
        if empresa_nit and empresa_nit != "todos":
            query = query.filter(Tutela.empresa_nit == empresa_nit)

        results = query.order_by(Tutela.fecha_radicacion.desc()).all()

        tutelas_list = []
        for tutela, usuario, empresa in results:
            tut_dict = tutela.to_dict()
            tut_dict['usuario_nombre'] = f"{usuario.primerNombre} {usuario.primerApellido}".strip()
            tut_dict['empresa_nombre'] = empresa.nombre_empresa
            tutelas_list.append(tut_dict)

        logger.debug(f"Se consultaron {len(tutelas_list)} tutelas")
        return jsonify(tutelas_list)

    except Exception as e:
        logger.error(f"Error obteniendo lista de tutelas: {e}", exc_info=True)
        return jsonify({"error": "No se pudo obtener la lista de tutelas."}), 500

@bp_tutelas.route("", methods=["POST"])
@login_required
def add_tutela():
    """Añade un nuevo registro de tutela usando ORM."""
    numero_id = request.form.get("usuario_id")
    try:
        data = request.form
        required_fields = ["empresa_nit", "usuario_id", "motivo", "fecha_radicacion"]
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

        upload_path = _get_user_tutela_folder(numero_id)
        filepath = sanitize_and_save_file(file, upload_path)
        ruta_guardada = os.path.relpath(filepath, USER_DATA_FOLDER)

        # Crear nueva tutela con ORM
        nueva_tutela = Tutela(
            empresa_nit=data["empresa_nit"],
            usuario_id=numero_id,
            motivo=data["motivo"],
            fecha_radicacion=datetime.strptime(data["fecha_radicacion"], '%Y-%m-%d'),
            estado="Registrada",
            archivos_info=ruta_guardada,
            # Campos adicionales del modelo que pueden venir del formulario
            empresa_nombre=data.get("empresa_nombre"),
            usuario_nombre=data.get("usuario_nombre")
        )

        db.session.add(nueva_tutela)
        db.session.commit()

        logger.info(f"Nueva tutela registrada con ID: {nueva_tutela.id} para usuario {numero_id}")
        return jsonify(nueva_tutela.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error general en add_tutela (Usuario: {numero_id}): {e}", exc_info=True)
        return jsonify({"error": f"Error inesperado en el servidor: {str(e)}"}), 500