# -*- coding: utf-8 -*-
"""
pagos.py - REFACTORIZADO CON ORM
==================================================
Maneja la lógica para registrar y consultar pagos usando SQLAlchemy ORM.
Elimina SQL manual y usa modelos ORM al 100%.
"""
import os
import traceback
from datetime import datetime
from flask import Blueprint, jsonify, request, session, current_app
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.utils import secure_filename

from logger import logger
from extensions import db
from models.orm_models import Pago, Empresa

# --- IMPORTACIÓN CENTRALIZADA ---
try:
    from ..utils import login_required, sanitize_and_save_file
except (ImportError, ValueError):
    from utils import login_required, sanitize_and_save_file
# -------------------------------


# ==================== DEFINICIÓN DEL BLUEPRINT ====================
bp_pagos = Blueprint("bp_pagos", __name__, url_prefix="/api/pagos")

# ==================== ENDPOINTS DE PAGOS ====================


@bp_pagos.route("", methods=["GET"])
@login_required
def get_pagos():
    """
    Obtiene todos los registros de pagos usando ORM con joins.

    Returns:
        JSON con lista de pagos ordenados por fecha, incluyendo datos del usuario y empresa
    """
    try:
        # ✅ Usando ORM con query compleja
        pagos = db.session.query(
            Pago,
            Usuario.primerNombre,
            Usuario.primerApellido,
            Usuario.empresa_nit,
            Empresa.nombre_empresa
        ).outerjoin(
            Usuario, Pago.usuario_id == Usuario.numeroId
        ).outerjoin(
            Empresa, Usuario.empresa_nit == Empresa.nit
        ).order_by(
            Pago.fecha_pago.desc()
        ).all()

        logger.debug(f"Se consultaron {len(pagos)} registros de pagos usando ORM")

        # Construir respuesta con datos combinados
        resultado = []
        for pago, primer_nombre, primer_apellido, empresa_nit, nombre_empresa in pagos:
            pago_dict = pago.to_dict()
            pago_dict['primerNombre'] = primer_nombre
            pago_dict['primerApellido'] = primer_apellido
            pago_dict['empresa_nit'] = empresa_nit
            pago_dict['nombre_empresa'] = nombre_empresa
            resultado.append(pago_dict)

        return jsonify(resultado)

    except SQLAlchemyError as e:
        logger.error(f"Error de SQLAlchemy obteniendo pagos: {e}", exc_info=True)
        return jsonify({"error": "No se pudo obtener la lista de pagos."}), 500
    except Exception as e:
        logger.error(f"Error inesperado obteniendo pagos: {e}", exc_info=True)
        return jsonify({"error": "Error interno del servidor."}), 500


@bp_pagos.route("", methods=["POST"])
@login_required
def add_pago():
    """
    Añade un nuevo registro de pago usando ORM.

    Request JSON:
        - usuario_id: ID del usuario que recibe el pago (requerido)
        - empresa_nit: NIT de la empresa que realiza el pago (requerido)
        - monto: Monto del pago (requerido)
        - tipo_pago: Tipo de pago (nomina, prima, etc.) (requerido)
        - fecha_pago: Fecha del pago (opcional, default: hoy)
        - referencia: Referencia o número de comprobante (opcional)

    Returns:
        JSON con el pago creado
    """
    try:
        data = request.get_json()

        # Validación básica
        required_fields = ["usuario_id", "empresa_nit", "monto", "tipo_pago"]
        if not all(field in data for field in required_fields):
            logger.warning("Intento de agregar pago con campos faltantes")
            return (
                jsonify({"error": "Faltan campos obligatorios (usuario_id, empresa_nit, monto, tipo_pago)."}),
                400,
            )

        # Validar monto
        try:
            monto = float(data["monto"])
            if monto <= 0:
                logger.warning(f"Intento de agregar pago con monto inválido: {monto}")
                return jsonify({"error": "El monto debe ser un valor positivo."}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "El monto debe ser un número válido."}), 400

        fecha_pago = data.get("fecha_pago", datetime.now().strftime("%Y-%m-%d"))

        # ✅ Crear nuevo pago usando ORM
        nuevo_pago = Pago(
            usuario_id=data["usuario_id"],
            empresa_nit=data["empresa_nit"],
            monto=monto,
            tipo_pago=data["tipo_pago"],
            fecha_pago=fecha_pago,
            referencia=data.get("referencia")
        )

        # ✅ Guardar en la base de datos
        db.session.add(nuevo_pago)
        db.session.commit()

        logger.info(f"Nuevo pago registrado con ID: {nuevo_pago.id} por un monto de {monto}")

        # Devolver el registro completo
        return jsonify(nuevo_pago.to_dict()), 201

    except IntegrityError as ie:
        db.session.rollback()
        logger.error(f"Error de integridad al agregar pago: {ie}", exc_info=True)
        return (
            jsonify({"error": "Error de integridad, verifique los datos (ej. NIT o ID de usuario no existen)."}),
            409,
        )
    except SQLAlchemyError as se:
        db.session.rollback()
        logger.error(f"Error de SQLAlchemy al agregar pago: {se}", exc_info=True)
        return jsonify({"error": "Error de base de datos al crear pago."}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error general al agregar pago: {e}", exc_info=True)
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500


@bp_pagos.route("/guardar-recibo", methods=["POST"])
@login_required
def guardar_recibo():
    """
    Guarda un recibo de pago en PDF junto con sus datos.

    Request Form Data:
        - reciboPdf: Archivo PDF del recibo (requerido)
        - empresa_nit: NIT de la empresa (requerido)
        - monto: Monto del pago (requerido)
        - fecha_pago: Fecha del pago (requerido)
        - concepto: Concepto/descripción del pago (opcional)
        - referencia: Número de referencia/comprobante (opcional)

    Returns:
        JSON con mensaje de éxito y ruta del archivo guardado
    """
    try:
        # Validar que se haya enviado un archivo
        if "reciboPdf" not in request.files:
            logger.warning("Intento de guardar recibo sin archivo PDF")
            return jsonify({"error": "No se incluyó el archivo PDF del recibo."}), 400

        file = request.files["reciboPdf"]
        if file.filename == "":
            return jsonify({"error": "El archivo no tiene nombre."}), 400

        # Obtener datos del formulario
        empresa_nit = request.form.get("empresa_nit")
        monto = request.form.get("monto")
        fecha_pago = request.form.get("fecha_pago")
        concepto = request.form.get("concepto", "Recibo de pago")
        referencia = request.form.get("referencia", "")

        # Validar campos requeridos
        if not empresa_nit or not monto or not fecha_pago:
            logger.warning("Intento de guardar recibo con campos faltantes")
            return jsonify({"error": "Faltan campos obligatorios (empresa_nit, monto, fecha_pago)."}), 400

        # Validar que la empresa exista
        empresa = Empresa.query.filter_by(nit=empresa_nit).first()
        if not empresa:
            logger.warning(f"Intento de guardar recibo con NIT no encontrado: {empresa_nit}")
            return jsonify({"error": f"Empresa con NIT {empresa_nit} no encontrada."}), 404

        nombre_empresa = empresa.nombre_empresa

        # Crear carpeta de destino organizada por empresa
        upload_base = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
        empresa_folder = os.path.join(upload_base, 'recibos', secure_filename(nombre_empresa))
        os.makedirs(empresa_folder, exist_ok=True)

        # Generar nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        custom_filename = f"recibo_{empresa_nit}_{timestamp}"

        # Guardar el archivo usando la utilidad centralizada
        try:
            filepath = sanitize_and_save_file(file, empresa_folder, custom_filename)
            logger.info(f"Recibo guardado exitosamente: {filepath}")
        except ValueError as ve:
            logger.error(f"Error de validación al guardar recibo: {ve}")
            return jsonify({"error": f"Archivo inválido: {str(ve)}"}), 400
        except Exception as save_err:
            logger.error(f"Error al guardar archivo de recibo: {save_err}", exc_info=True)
            return jsonify({"error": f"Error al guardar el archivo: {str(save_err)}"}), 500

        # Retornar respuesta exitosa
        return jsonify({
            "message": "Recibo guardado exitosamente",
            "archivo": os.path.basename(filepath),
            "empresa": nombre_empresa,
            "monto": monto,
            "fecha": fecha_pago,
            "concepto": concepto
        }), 201

    except SQLAlchemyError as se:
        logger.error(f"Error de base de datos al guardar recibo: {se}", exc_info=True)
        return jsonify({"error": "Error de base de datos al procesar el recibo."}), 500
    except Exception as e:
        logger.error(f"Error inesperado al guardar recibo: {e}", exc_info=True)
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
