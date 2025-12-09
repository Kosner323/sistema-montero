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


@bp_incapacidades.route("/<int:id>/transferir-cliente", methods=["PUT"])
@login_required
def transferir_a_cliente(id):
    """
    Registra el pago a cliente y cierra el caso de incapacidad.
    Estado requerido: "Pagada por EPS" -> Estado final: "Finalizada"
    """
    try:
        # Buscar la incapacidad
        incapacidad = db.session.query(Incapacidad).filter_by(id=id).first()
        
        if not incapacidad:
            return jsonify({"error": "Incapacidad no encontrada"}), 404
        
        # Validar estado
        if incapacidad.estado != "Pagada por EPS":
            return jsonify({
                "error": "Solo se pueden transferir incapacidades con estado 'Pagada por EPS'",
                "estado_actual": incapacidad.estado
            }), 400
        
        # Obtener datos del formulario
        monto_pagado = request.form.get("monto_pagado")
        fecha_pago = request.form.get("fecha_pago")
        observaciones = request.form.get("observaciones", "")
        
        # Validar campos obligatorios
        if not monto_pagado or not fecha_pago:
            return jsonify({"error": "Faltan campos obligatorios: monto_pagado, fecha_pago"}), 400
        
        # Validar y guardar archivo de comprobante
        if "comprobante" not in request.files:
            return jsonify({"error": "No se incluyó el comprobante de transferencia"}), 400
        
        file = request.files["comprobante"]
        if file.filename == "":
            return jsonify({"error": "El comprobante no tiene nombre"}), 400
        
        # Validar archivo
        is_valid, error_msg = validate_upload(file, file_type="document")
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        # Guardar comprobante en carpeta del usuario
        upload_path = _get_user_incapacidad_folder(incapacidad.usuario_id)
        comprobante_filename = f"comprobante_pago_{id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(upload_path, secure_filename(comprobante_filename))
        file.save(filepath)
        ruta_guardada = os.path.relpath(filepath, USER_DATA_FOLDER)
        
        # Actualizar incapacidad
        incapacidad.estado = "Finalizada"
        incapacidad.monto_pagado_cliente = float(monto_pagado)
        incapacidad.fecha_pago_cliente = fecha_pago
        incapacidad.observaciones_pago = observaciones
        incapacidad.comprobante_pago = ruta_guardada
        incapacidad.fecha_cierre = datetime.now().isoformat()
        
        db.session.commit()
        
        logger.info(f"Transferencia a cliente completada para incapacidad {id}. Estado: Finalizada")
        
        return jsonify({
            "success": True,
            "mensaje": "Pago a cliente registrado exitosamente",
            "incapacidad_id": id,
            "nuevo_estado": "Finalizada",
            "monto_pagado": float(monto_pagado),
            "fecha_cierre": incapacidad.fecha_cierre
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error en transferir_a_cliente para incapacidad {id}: {e}", exc_info=True)
        return jsonify({"error": f"Error al procesar transferencia: {str(e)}"}), 500