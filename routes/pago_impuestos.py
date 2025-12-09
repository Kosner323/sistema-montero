# -*- coding: utf-8 -*-
"""
pago_impuestos.py - ACTUALIZADO con logging
====================================================
Maneja la lógica de backend para la subida de formularios
de impuestos y la consulta de registros.
"""
import os
import traceback
from datetime import datetime
from flask import Blueprint, jsonify, request, session
from werkzeug.utils import secure_filename
from logger import logger

# --- IMPORTACIÓN CENTRALIZADA ---
try:
    from ..utils import login_required, COMPANY_DATA_FOLDER, sanitize_and_save_file, log_file_upload
    from ..extensions import db
    from ..models.orm_models import PagoImpuesto, Empresa, Novedad
except (ImportError, ValueError):
    from utils import login_required, COMPANY_DATA_FOLDER, sanitize_and_save_file, log_file_upload
    from extensions import db
    from models.orm_models import PagoImpuesto, Empresa, Novedad
# -------------------------------

def save_text_content(content, upload_path, filename):
    """Guarda contenido de texto en un archivo."""
    target_path = os.path.join(upload_path, secure_filename(filename))
    if os.path.normpath(target_path).startswith(os.path.normpath(upload_path)):
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        return target_path
    else:
        raise ValueError("Ruta de archivo no válida para TXT.")

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
        logger.error(f"Error en _get_company_folder para {nombre_empresa}: {e}", exc_info=True)
        raise


# ==================== ENDPOINTS DE IMPUESTOS ====================


@bp_impuestos.route("", methods=["GET"])
@login_required
def get_impuestos():
    """Obtiene registros de impuestos, con filtros."""
    try:
        empresa_nit = request.args.get("empresa_nit")
        tipo_impuesto = request.args.get("tipo_impuesto")

        # Construir query ORM con filtros
        query = PagoImpuesto.query

        if empresa_nit and empresa_nit != "todos":
            query = query.filter_by(empresa_nit=empresa_nit)

        if tipo_impuesto and tipo_impuesto != "todos":
            query = query.filter_by(tipo_impuesto=tipo_impuesto)

        registros = query.order_by(PagoImpuesto.fecha_limite.asc()).all()
        logger.debug(f"Consulta de impuestos exitosa. Registros: {len(registros)}")
        return jsonify([registro.to_dict() for registro in registros])

    except Exception as e:
        logger.error(f"Error obteniendo registros de impuestos: {e}", exc_info=True)
        return jsonify({"error": "No se pudo obtener la lista de registros."}), 500


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
            logger.warning(f"Intento de agregar impuesto sin datos obligatorios. NIT: {nit}")
            return (
                jsonify({"error": "Faltan datos (empresa, impuesto, periodo, fecha)."}),
                400,
            )

        if "archivo" not in request.files:
            return jsonify({"error": "No se incluyó el archivo PDF."}), 400

        file = request.files["archivo"]
        if file.filename == "":
            return jsonify({"error": "El archivo no tiene nombre."}), 400

        # 1. Obtener el nombre de la empresa desde la BD usando ORM
        empresa = Empresa.query.filter_by(nit=nit).first()
        if not empresa:
            logger.warning(f"Intento de registro con NIT no encontrado: {nit}")
            return jsonify({"error": f"Empresa con NIT {nit} no encontrada."}), 404
        nombre_empresa = empresa.nombre_empresa

        # 2. Determinar la ruta de guardado
        try:
            upload_path = _get_company_folder(nit, nombre_empresa, tipo_impuesto)
        except Exception as folder_err:
            logger.error(
                f"Error creando carpeta para {nombre_empresa} ({tipo_impuesto}): {folder_err}",
                exc_info=True,
            )
            return (
                jsonify({"error": f"No se pudo crear el directorio de la empresa: {folder_err}"}),
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
            logger.error(f"Error al guardar el archivo PDF para {nit}: {e}", exc_info=True)
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
            logger.debug(f"Archivo TXT de soporte guardado en: {upload_path}/{txt_filename}")

        except (ValueError, IOError) as e:
            logger.warning(f"Advertencia: Error al guardar archivo TXT de soporte para {nit}: {e}")

        # 6. Guardar registro en la base de datos usando ORM
        nuevo_impuesto = PagoImpuesto(
            empresa_nit=nit,
            empresa_nombre=nombre_empresa,
            tipo_impuesto=tipo_impuesto,
            periodo=periodo,
            fecha_limite=fecha_limite,
            estado="Pendiente de Pago",
            ruta_archivo=ruta_guardada
        )

        db.session.add(nuevo_impuesto)
        db.session.commit()

        logger.info(f"Impuesto registrado con ID: {nuevo_impuesto.id} para NIT: {nit}")

        # ==================== AUTOMATIZACIÓN: NOTIFICAR A TESORERÍA ====================
        # REGLA DE NEGOCIO: Cuando se crea un impuesto, notificar automáticamente a Tesorería
        try:
            # Crear novedad automática para gestión de pago
            nueva_novedad = Novedad(
                subject=f"📋 IMPUESTO PENDIENTE: {tipo_impuesto}",
                description=f"Vence el {fecha_limite}. Empresa: {nombre_empresa} (NIT: {nit}). Período: {periodo}. Por favor gestionar pago.",
                status="Pendiente",
                priorityText="Alta",
                priority=3,  # Alta prioridad
                client=nombre_empresa,
                creationDate=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                assignedTo="Tesorería"
            )

            db.session.add(nueva_novedad)
            db.session.commit()

            logger.info(f"✅ Notificación automática creada (Novedad ID: {nueva_novedad.id}) para impuesto ID: {nuevo_impuesto.id}")

        except Exception as notif_error:
            # CRÍTICO: Si falla la notificación, NO fallar el registro del impuesto
            # El impuesto es prioridad, la notificación es secundaria
            db.session.rollback()  # Rollback solo de la novedad, el impuesto ya está committed
            logger.error(f"⚠️ ERROR al crear notificación automática para impuesto ID {nuevo_impuesto.id}: {notif_error}", exc_info=True)
            logger.warning(f"⚠️ El impuesto fue registrado exitosamente pero la notificación falló. Revisar manualmente.")

        # =================================================================================

        return jsonify(nuevo_impuesto.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creando registro de impuesto (NIT: {nit}): {e}", exc_info=True)
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500


@bp_impuestos.route("/<int:impuesto_id>/pagar", methods=["POST", "PUT"])
@login_required
def marcar_como_pagado(impuesto_id):
    """
    Actualiza el estado de un impuesto a 'Pagado' con comprobante de pago.

    Request (multipart/form-data):
        - comprobante: Archivo PDF/Imagen del comprobante (opcional)
        - fecha_pago: Fecha en que se realizó el pago (opcional)

    Returns:
        JSON con el registro actualizado
    """
    try:
        # Obtener el registro del impuesto
        registro = PagoImpuesto.query.get(impuesto_id)
        if not registro:
            logger.warning(f"Intento de marcar como pagado impuesto inexistente ID: {impuesto_id}")
            return jsonify({"error": "Registro de impuesto no encontrado."}), 404

        # Obtener datos de la empresa
        empresa = Empresa.query.filter_by(nit=registro.empresa_nit).first()
        if not empresa:
            logger.error(f"Empresa con NIT {registro.empresa_nit} no encontrada para impuesto ID {impuesto_id}")
            return jsonify({"error": "Empresa asociada no encontrada."}), 404

        nombre_empresa = empresa.nombre_empresa
        comprobante_guardado = False
        ruta_comprobante = None

        # Si se envió un archivo de comprobante, guardarlo
        if "comprobante" in request.files:
            file = request.files["comprobante"]

            if file and file.filename != "":
                try:
                    # Crear estructura de carpetas: EMPRESAS/{nombre}/IMPUESTOS/{tipo}/PAGOS/
                    sanitized_empresa = secure_filename(nombre_empresa.replace(" ", "_"))
                    sanitized_tipo = secure_filename(registro.tipo_impuesto.replace(" ", "_"))

                    pagos_folder = os.path.join(
                        COMPANY_DATA_FOLDER,
                        sanitized_empresa,
                        "PAGO DE IMPUESTOS",
                        sanitized_tipo,
                        "PAGOS"
                    )
                    os.makedirs(pagos_folder, exist_ok=True)

                    # Nombre del archivo: ComprobantePago_{NIT}_{Tipo}_{Periodo}_{Fecha}
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    ext = os.path.splitext(file.filename)[1]
                    custom_filename = f"ComprobantePago_{registro.empresa_nit}_{sanitized_tipo}_{registro.periodo}_{timestamp}{ext}"

                    # Guardar el archivo
                    filepath = sanitize_and_save_file(file, pagos_folder, custom_filename)

                    # Guardar ruta relativa
                    ruta_comprobante = os.path.relpath(filepath, COMPANY_DATA_FOLDER)
                    comprobante_guardado = True

                    logger.info(f"Comprobante de pago guardado: {ruta_comprobante}")

                    # Log de carga exitosa
                    user_session_id = session.get("user_id", "unknown")
                    log_file_upload(file.filename, user_session_id, success=True)

                except (ValueError, IOError) as file_error:
                    logger.error(f"Error al guardar comprobante para impuesto ID {impuesto_id}: {file_error}", exc_info=True)
                    user_session_id = session.get("user_id", "unknown")
                    log_file_upload(file.filename, user_session_id, success=False, error=str(file_error))
                    return jsonify({"error": f"Error al guardar el comprobante: {str(file_error)}"}), 500

        # Actualizar el registro del impuesto
        registro.estado = 'Pagado'

        # Si se guardó el comprobante, actualizar la ruta (si el modelo tiene el campo)
        if comprobante_guardado and ruta_comprobante:
            # Verificar si el modelo tiene el atributo ruta_soporte_pago
            if hasattr(registro, 'ruta_soporte_pago'):
                registro.ruta_soporte_pago = ruta_comprobante
            else:
                logger.warning(f"El modelo PagoImpuesto no tiene campo 'ruta_soporte_pago'. Comprobante guardado en: {ruta_comprobante}")

        # Fecha de pago (si se proporciona)
        fecha_pago = request.form.get("fecha_pago")
        if fecha_pago and hasattr(registro, 'fecha_pago'):
            registro.fecha_pago = fecha_pago

        db.session.commit()

        logger.info(f"Impuesto ID {impuesto_id} marcado como 'Pagado' {' con comprobante' if comprobante_guardado else ''}")

        # ==================== OPCIONAL: ACTUALIZAR NOVEDAD ASOCIADA ====================
        # Buscar la novedad relacionada con este impuesto y marcarla como Resuelta
        try:
            # Buscar novedad que mencione este tipo de impuesto y empresa
            novedad_relacionada = Novedad.query.filter(
                Novedad.subject.like(f"%{registro.tipo_impuesto}%"),
                Novedad.client == nombre_empresa,
                Novedad.status == "Pendiente"
            ).first()

            if novedad_relacionada:
                novedad_relacionada.status = "Resuelta"
                novedad_relacionada.solutionDescription = f"Impuesto pagado el {fecha_pago or datetime.now().strftime('%Y-%m-%d')}. Comprobante archivado."
                db.session.commit()
                logger.info(f"✅ Novedad ID {novedad_relacionada.id} marcada como Resuelta para impuesto ID {impuesto_id}")
            else:
                logger.debug(f"No se encontró novedad pendiente asociada para impuesto ID {impuesto_id}")

        except Exception as novedad_error:
            logger.warning(f"⚠️ Error al actualizar novedad asociada para impuesto ID {impuesto_id}: {novedad_error}")
            # No fallar el pago por error en actualización de novedad
        # ===============================================================================

        # Preparar respuesta
        response_data = registro.to_dict()
        if comprobante_guardado:
            response_data['comprobante_guardado'] = True
            response_data['ruta_comprobante'] = ruta_comprobante

        return jsonify(response_data), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error actualizando estado de impuesto {impuesto_id}: {e}", exc_info=True)
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500


@bp_impuestos.route("/balance", methods=["GET"])
@login_required
def get_balance_impuestos():
    """
    Genera un reporte de balance de impuestos filtrado por empresa y año.

    Query Parameters:
        - empresa_nit: NIT de la empresa (requerido)
        - anio: Año fiscal (ej: 2025) (requerido)

    Returns:
        JSON con balance detallado de impuestos del año
    """
    try:
        # Obtener parámetros
        empresa_nit = request.args.get("empresa_nit")
        anio = request.args.get("anio")

        # Validación de parámetros
        if not empresa_nit or not anio:
            logger.warning("Intento de consultar balance sin empresa_nit o anio")
            return jsonify({"error": "Parámetros requeridos: empresa_nit y anio"}), 400

        # Validar que el año sea numérico
        try:
            anio_int = int(anio)
        except ValueError:
            return jsonify({"error": "El parámetro 'anio' debe ser un número"}), 400

        # Verificar que la empresa existe
        empresa = Empresa.query.filter_by(nit=empresa_nit).first()
        if not empresa:
            logger.warning(f"Intento de consultar balance para NIT no encontrado: {empresa_nit}")
            return jsonify({"error": f"Empresa con NIT {empresa_nit} no encontrada"}), 404

        # Consultar impuestos del año especificado
        # Filtrar por año en el campo fecha_limite (formato YYYY-MM-DD)
        impuestos = PagoImpuesto.query.filter(
            PagoImpuesto.empresa_nit == empresa_nit,
            PagoImpuesto.fecha_limite.like(f"{anio}%")
        ).order_by(PagoImpuesto.fecha_limite.asc()).all()

        logger.debug(f"Balance consultado para {empresa_nit} año {anio}: {len(impuestos)} registros")

        # Construir estadísticas
        total_impuestos = len(impuestos)
        impuestos_pagados = len([i for i in impuestos if i.estado == 'Pagado'])
        impuestos_pendientes = len([i for i in impuestos if i.estado == 'Pendiente de Pago'])
        impuestos_vencidos = len([i for i in impuestos if i.estado == 'Vencido'])

        # Calcular totales (si existe campo valor en el modelo, si no, usar 0)
        total_pagado = 0.0
        total_pendiente = 0.0

        # Preparar lista detallada de impuestos
        impuestos_detalle = []
        for impuesto in impuestos:
            impuesto_dict = impuesto.to_dict()

            # Agregar enlace al comprobante si existe
            if hasattr(impuesto, 'ruta_soporte_pago') and impuesto.ruta_soporte_pago:
                impuesto_dict['tiene_comprobante'] = True
                impuesto_dict['url_comprobante'] = f"/static/empresas/{impuesto.ruta_soporte_pago}"
            else:
                impuesto_dict['tiene_comprobante'] = False

            # Calcular días hasta vencimiento o desde vencimiento
            try:
                fecha_limite_dt = datetime.strptime(impuesto.fecha_limite, "%Y-%m-%d")
                dias_diferencia = (fecha_limite_dt - datetime.now()).days

                if impuesto.estado == 'Pendiente de Pago':
                    if dias_diferencia > 0:
                        impuesto_dict['dias_hasta_vencimiento'] = dias_diferencia
                        impuesto_dict['estado_alerta'] = 'Normal' if dias_diferencia > 15 else 'Próximo a Vencer'
                    else:
                        impuesto_dict['dias_desde_vencimiento'] = abs(dias_diferencia)
                        impuesto_dict['estado_alerta'] = 'Vencido'
            except ValueError:
                impuesto_dict['dias_hasta_vencimiento'] = None

            impuestos_detalle.append(impuesto_dict)

        # Preparar respuesta
        response = {
            "empresa": {
                "nit": empresa_nit,
                "nombre": empresa.nombre_empresa
            },
            "periodo": {
                "anio": anio_int,
                "fecha_consulta": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "resumen": {
                "total_impuestos": total_impuestos,
                "pagados": impuestos_pagados,
                "pendientes": impuestos_pendientes,
                "vencidos": impuestos_vencidos,
                "porcentaje_cumplimiento": round((impuestos_pagados / total_impuestos * 100), 2) if total_impuestos > 0 else 0
            },
            "totales_financieros": {
                "total_pagado": total_pagado,
                "total_pendiente": total_pendiente,
                "nota": "Los valores financieros dependen de la estructura del modelo PagoImpuesto"
            },
            "impuestos": impuestos_detalle
        }

        logger.info(f"Balance generado para {empresa.nombre_empresa} año {anio}: {total_impuestos} impuestos, {impuestos_pagados} pagados")

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error generando balance de impuestos: {e}", exc_info=True)
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
