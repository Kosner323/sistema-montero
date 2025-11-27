# -*- coding: utf-8 -*-
import json
from datetime import datetime

from flask import Blueprint, jsonify, request, session
from logger import logger

from extensions import db, mail
from models.orm_models import Novedad
from utils import login_required, USER_DATA_FOLDER

bp_novedades = Blueprint("bp_novedades", __name__, url_prefix="/api/novedades")

@bp_novedades.route("", methods=["GET"])
@login_required
def get_novedades():
    """Obtiene todas las novedades de la base de datos usando ORM."""
    try:
        novedades = Novedad.query.order_by(Novedad.updateDate.desc(), Novedad.creationDate.desc()).all()
        return jsonify([novedad.to_dict() for novedad in novedades])
    except Exception as e:
        logger.error(f"Error al obtener novedades: {e}", exc_info=True)
        return jsonify({"error": f"Error interno al obtener novedades: {str(e)}"}), 500

@bp_novedades.route("", methods=["POST"])
@login_required
def create_novedad():
    """Crea una nueva novedad en la base de datos usando ORM."""
    if not request.is_json:
        return jsonify({"error": "Se esperaba Content-Type: application/json"}), 415

    data = request.get_json()
    
    required_fields = ["client", "subject", "priority", "status", "description"]
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({"error": f"Faltan campos obligatorios: {', '.join(missing_fields)}."}), 400

    now_dt = datetime.now()
    now_str_datetime = now_dt.strftime("%Y-%m-%d %H:%M:%S")
    now_str_date = now_dt.strftime("%Y-%m-%d")

    user_name = session.get("user_name", "Usuario Desconocido")
    initial_history = [
        {
            "user": user_name,
            "timestamp": now_str_datetime,
            "action": "Creó el caso.",
            "comment": f"Estado inicial: {data['status']}, Prioridad: {data.get('priorityText', data['priority'])}.",
        }
    ]

    try:
        ibc_float = float(data.get("ibc")) if data.get("ibc") not in [None, ""] else None
    except (ValueError, TypeError):
        ibc_float = None

    new_novedad = Novedad(
        client=data.get("client"),
        subject=data.get("subject"),
        priority=data.get("priority"),
        status=data.get("status"),
        priorityText=data.get("priorityText", data.get("priority")),
        idType=data.get("idType"),
        idNumber=data.get("idNumber"),
        firstName=data.get("firstName"),
        lastName=data.get("lastName"),
        nationality=data.get("nationality"),
        gender=data.get("gender"),
        birthDate=data.get("birthDate"),
        phone=data.get("phone"),
        department=data.get("department"),
        city=data.get("city"),
        address=data.get("address"),
        neighborhood=data.get("neighborhood"),
        email=data.get("email"),
        beneficiaries=data.get("beneficiaries") or [],
        eps=data.get("eps"),
        arl=data.get("arl"),
        arlClass=data.get("arlClass"),
        ccf=data.get("ccf"),
        pensionFund=data.get("pensionFund"),
        ibc=ibc_float,
        description=data.get("description"),
        radicado=data.get("radicado"),
        solutionDescription=data.get("solutionDescription", ""),
        creationDate=now_str_date,
        updateDate=now_str_date,
        assignedTo=data.get("assignedTo", "Sistema"),
        history=initial_history,
    )

    try:
        db.session.add(new_novedad)
        db.session.commit()
        return jsonify(new_novedad.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error de base de datos al crear novedad: {e}", exc_info=True)
        return jsonify({"error": f"Error de base de datos: {str(e)}"}), 500

@bp_novedades.route("/<int:novedad_id>", methods=["PUT"])
@login_required
def update_novedad(novedad_id):
    """Actualiza una novedad existente usando ORM."""
    if not request.is_json:
        return jsonify({"error": "Se esperaba Content-Type: application/json"}), 415

    data = request.get_json()
    novedad = Novedad.query.get(novedad_id)

    if not novedad:
        return jsonify({"error": "Novedad no encontrada."}), 404

    now_dt = datetime.now()
    now_str_datetime = now_dt.strftime("%Y-%m-%d %H:%M:%S")
    now_str_date = now_dt.strftime("%Y-%m-%d")

    current_history = novedad.history or []
    user_name = session.get("user_name", "Usuario Desconocido")
    action_description_parts = []
    
    campos_actualizables = [
        "client", "subject", "priority", "status", "priorityText", "idType", "idNumber",
        "firstName", "lastName", "nationality", "gender", "birthDate", "phone",
        "department", "city", "address", "neighborhood", "email", "beneficiaries",
        "eps", "arl", "arlClass", "ccf", "pensionFund", "ibc", "description",
        "radicado", "solutionDescription", "assignedTo",
    ]

    updated = False
    for key in campos_actualizables:
        if key in data and data[key] != getattr(novedad, key):
            setattr(novedad, key, data[key])
            updated = True
            if key == "status":
                action_description_parts.append(f"Cambió estado a '{data[key]}'.")
            elif key == "priority":
                action_description_parts.append(f"Cambió prioridad a '{data.get('priorityText', data[key])}'.")

    new_comment = data.get("newComment", "").strip()
    if updated or new_comment:
        action_description = " ".join(action_description_parts) if action_description_parts else "Actualizó el caso."
        if not action_description_parts and new_comment:
            action_description = "Añadió comentario."

        history_entry = {
            "user": user_name,
            "timestamp": now_str_datetime,
            "action": action_description,
            "comment": new_comment,
        }
        current_history.append(history_entry)
        novedad.history = current_history
        novedad.updateDate = now_str_date
        
        try:
            db.session.commit()
            return jsonify(novedad.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error de base de datos al actualizar novedad {novedad_id}: {e}", exc_info=True)
            return jsonify({"error": f"Error de base de datos: {str(e)}"}), 500
    else:
        return jsonify({"message": "No se realizaron cambios."}), 200

@bp_novedades.route("/<int:novedad_id>", methods=["DELETE"])
@login_required
def delete_novedad(novedad_id):
    """Elimina una novedad usando ORM."""
    novedad = Novedad.query.get(novedad_id)
    if not novedad:
        return jsonify({"error": "Novedad no encontrada."}), 404

    try:
        db.session.delete(novedad)
        db.session.commit()
        user_name = session.get("user_name", "Usuario Desconocido")
        logger.info(f"Novedad {novedad_id} eliminada por {user_name} el {datetime.now()}")
        return jsonify({"message": f"Novedad {novedad_id} eliminada correctamente."}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error de base de datos al eliminar novedad {novedad_id}: {e}", exc_info=True)
        return jsonify({"error": f"Error de base de datos: {str(e)}"}), 500