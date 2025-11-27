"""
envio_planillas.py - ACTUALIZADO con logging
====================================================
Maneja la lógica para registrar y consultar envíos de planillas.
"""
import os
import traceback
from datetime import datetime

from flask import Blueprint, jsonify, request, session, current_app

from logger import logger

# --- IMPORTACIÓN CENTRALIZADA ---
try:
    from ..utils import login_required
    from ..extensions import db
    from ..models.orm_models import EnvioPlanilla, Empresa
except (ImportError, ValueError):
    from utils import login_required
    from extensions import db
    from models.orm_models import EnvioPlanilla, Empresa
# -------------------------------

# ==================== DEFINICIÓN DEL BLUEPRINT ====================
bp_envio_planillas = Blueprint("bp_envio_planillas", __name__, url_prefix="/api/envios_planillas")

# ==================== ENDPOINTS DE ENVÍOS ====================


@bp_envio_planillas.route("", methods=["GET"])
@login_required
def get_envios():
    """Obtiene todos los registros de envíos de planillas."""
    try:
        # Filtros opcionales
        empresa_nit = request.args.get("empresa_nit")

        # Construir query ORM con filtros y JOIN
        query = db.session.query(EnvioPlanilla, Empresa.nombre_empresa).join(
            Empresa, EnvioPlanilla.empresa_nit == Empresa.nit, isouter=True
        )

        if empresa_nit and empresa_nit != "todos":
            query = query.filter(EnvioPlanilla.empresa_nit == empresa_nit)

        envios = query.order_by(EnvioPlanilla.fecha_envio.desc()).all()

        # Convertir resultados a diccionarios
        result = []
        for envio, nombre_empresa in envios:
            envio_dict = envio.to_dict()
            envio_dict['nombre_empresa'] = nombre_empresa
            result.append(envio_dict)

        logger.debug(f"Se consultaron {len(result)} registros de envíos")
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error obteniendo lista de envíos: {e}", exc_info=True)
        return jsonify({"error": "No se pudo obtener la lista de envíos."}), 500


@bp_envio_planillas.route("", methods=["POST"])
@login_required
def add_envio():
    """Añade un nuevo registro de envío de planilla."""
    data = request.get_json()
    nit = data.get("empresa_nit") if data else None
    
    try:
        # Validación básica - Ajustado a los campos del modelo EnvioPlanilla
        required_fields = ["empresa_nit", "periodo", "fecha_envio"]
        if not all(field in data for field in required_fields):
            logger.warning(f"Intento de agregar envío con campos faltantes. NIT: {nit}")
            return (
                jsonify({"error": "Faltan campos obligatorios (empresa_nit, periodo, fecha_envio)."}),
                400,
            )

        # Obtener nombre de empresa
        empresa = Empresa.query.filter_by(nit=data["empresa_nit"]).first()
        if not empresa:
            logger.warning(f"Intento de registro con NIT no encontrado: {nit}")
            return jsonify({"error": f"Empresa con NIT {nit} no encontrada."}), 404

        # Crear nuevo envío usando ORM
        nuevo_envio = EnvioPlanilla(
            empresa_nit=data["empresa_nit"],
            empresa_nombre=empresa.nombre_empresa,
            periodo=data["periodo"],
            tipo_id=data.get("tipo_id"),
            numero_id=data.get("numero_id"),
            documento=data.get("documento"),
            contacto=data.get("contacto"),
            telefono=data.get("telefono"),
            correo=data.get("correo"),
            canal=data.get("canal", "Correo"),
            mensaje=data.get("mensaje"),
            estado=data.get("estado", "Pendiente"),
            fecha_envio=data["fecha_envio"]
        )

        db.session.add(nuevo_envio)
        db.session.commit()

        logger.info(f"Nuevo envío de planilla registrado con ID: {nuevo_envio.id} para NIT: {data['empresa_nit']}")

        return jsonify(nuevo_envio.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error general al agregar envío (NIT: {nit}): {e}", exc_info=True)
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
