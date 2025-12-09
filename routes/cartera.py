#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
routes/cartera.py
=================
Gestión de Cartera y Cobros
Fase 10.4: Endpoint para detección de morosos

Autor: Senior Backend Developer
Fecha: 2025-11-30
"""

from flask import Blueprint, jsonify, request, session
from datetime import datetime, date
from sqlalchemy import and_, or_

# Logger
try:
    from logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Extensions y modelos
from extensions import db
from models.orm_models import DeudaCartera, Empresa, Usuario

# Utils
try:
    from ..utils import login_required
except (ImportError, ValueError):
    from utils import login_required


# =============================================================================
# BLUEPRINT
# =============================================================================

bp_cartera = Blueprint('cartera', __name__, url_prefix='/api/cartera')


# =============================================================================
# ENDPOINT: GET /api/cartera/morosos (FASE 10.4)
# =============================================================================

@bp_cartera.route('/morosos', methods=['GET'])
@login_required
def obtener_morosos():
    """
    FASE 10.4: Obtiene lista de clientes morosos (deudas vencidas).

    Criterios:
        - Deudas con fecha_vencimiento < hoy
        - Estado != 'Pagado'

    Query Parameters:
        - dias_minimos: Filtrar deudas con al menos X días de mora (opcional)
        - entidad: Filtrar por entidad específica (EPS, ARL, etc.) (opcional)
        - empresa_nit: Filtrar por empresa específica (opcional)

    Response JSON:
        {
            "success": true,
            "total_morosos": 15,
            "monto_total_deuda": 45000000.00,
            "deudas": [
                {
                    "id": 1,
                    "usuario_id": "1234567890",
                    "nombre_usuario": "Juan Pérez",
                    "empresa_nit": "900123456",
                    "nombre_empresa": "Empresa ABC",
                    "entidad": "EPS",
                    "monto": 500000.00,
                    "dias_mora": 30,
                    "estado": "Vencido",
                    "fecha_vencimiento": "2024-10-15",
                    ...
                }
            ]
        }
    """
    try:
        # Parámetros de filtro
        dias_minimos = request.args.get('dias_minimos', type=int)
        entidad_filtro = request.args.get('entidad')
        empresa_nit_filtro = request.args.get('empresa_nit')

        # Fecha de hoy
        fecha_hoy = date.today().strftime("%Y-%m-%d")

        logger.info(f"📊 Consultando morosos con fecha límite: {fecha_hoy}")

        # ==================== CONSULTA BASE ====================
        # Deudas vencidas: fecha_vencimiento < hoy AND estado != 'Pagado'
        query = DeudaCartera.query.filter(
            and_(
                DeudaCartera.fecha_vencimiento.isnot(None),
                DeudaCartera.fecha_vencimiento < fecha_hoy,
                DeudaCartera.estado != 'Pagado'
            )
        )

        # ==================== FILTROS ADICIONALES ====================
        if dias_minimos is not None:
            query = query.filter(DeudaCartera.dias_mora >= dias_minimos)
            logger.info(f"   Filtro: días_mora >= {dias_minimos}")

        if entidad_filtro:
            query = query.filter(DeudaCartera.entidad == entidad_filtro)
            logger.info(f"   Filtro: entidad = {entidad_filtro}")

        if empresa_nit_filtro:
            query = query.filter(DeudaCartera.empresa_nit == empresa_nit_filtro)
            logger.info(f"   Filtro: empresa_nit = {empresa_nit_filtro}")

        # ==================== ORDENAMIENTO ====================
        # Ordenar por días de mora (mayor a menor) y luego por monto
        deudas_vencidas = query.order_by(
            DeudaCartera.dias_mora.desc(),
            DeudaCartera.monto.desc()
        ).all()

        # ==================== CÁLCULOS DE RESUMEN ====================
        total_morosos = len(deudas_vencidas)
        monto_total_deuda = sum(float(deuda.monto or 0) for deuda in deudas_vencidas)

        # Convertir a diccionarios
        deudas_list = []
        for deuda in deudas_vencidas:
            deuda_dict = deuda.to_dict()

            # Calcular días de mora si no están actualizados
            if deuda.fecha_vencimiento:
                try:
                    fecha_venc = datetime.strptime(deuda.fecha_vencimiento, "%Y-%m-%d").date()
                    dias_mora_calculados = (date.today() - fecha_venc).days
                    deuda_dict['dias_mora_calculados'] = dias_mora_calculados
                except:
                    deuda_dict['dias_mora_calculados'] = deuda.dias_mora or 0

            deudas_list.append(deuda_dict)

        logger.info(f"✅ Morosos encontrados: {total_morosos}, Monto total: ${monto_total_deuda:,.2f}")

        # ==================== ESTADÍSTICAS ADICIONALES ====================
        # Agrupar por entidad
        deudas_por_entidad = {}
        for deuda in deudas_vencidas:
            entidad = deuda.entidad or "Sin entidad"
            if entidad not in deudas_por_entidad:
                deudas_por_entidad[entidad] = {
                    'cantidad': 0,
                    'monto_total': 0.0
                }
            deudas_por_entidad[entidad]['cantidad'] += 1
            deudas_por_entidad[entidad]['monto_total'] += float(deuda.monto or 0)

        # Agrupar por empresa
        deudas_por_empresa = {}
        for deuda in deudas_vencidas:
            empresa = deuda.nombre_empresa or f"NIT {deuda.empresa_nit}"
            if empresa not in deudas_por_empresa:
                deudas_por_empresa[empresa] = {
                    'nit': deuda.empresa_nit,
                    'cantidad': 0,
                    'monto_total': 0.0
                }
            deudas_por_empresa[empresa]['cantidad'] += 1
            deudas_por_empresa[empresa]['monto_total'] += float(deuda.monto or 0)

        # ==================== RESPUESTA ====================
        return jsonify({
            'success': True,
            'fecha_consulta': fecha_hoy,
            'total_morosos': total_morosos,
            'monto_total_deuda': round(monto_total_deuda, 2),
            'deudas': deudas_list,
            'estadisticas': {
                'por_entidad': deudas_por_entidad,
                'por_empresa': deudas_por_empresa
            },
            'filtros_aplicados': {
                'dias_minimos': dias_minimos,
                'entidad': entidad_filtro,
                'empresa_nit': empresa_nit_filtro
            }
        }), 200

    except Exception as e:
        logger.error(f"❌ Error obteniendo morosos: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Error al obtener lista de morosos',
            'detalle': str(e)
        }), 500


# =============================================================================
# ENDPOINT: GET /api/cartera/resumen (BONUS)
# =============================================================================

@bp_cartera.route('/resumen', methods=['GET'])
@login_required
def obtener_resumen_cartera():
    """
    BONUS: Obtiene resumen general de cartera.

    Response JSON:
        {
            "success": true,
            "total_deudas": 50,
            "deudas_vigentes": 35,
            "deudas_vencidas": 15,
            "monto_total": 100000000.00,
            "monto_vigente": 55000000.00,
            "monto_vencido": 45000000.00
        }
    """
    try:
        fecha_hoy = date.today().strftime("%Y-%m-%d")

        # Total de deudas no pagadas
        total_deudas = DeudaCartera.query.filter(
            DeudaCartera.estado != 'Pagado'
        ).count()

        # Deudas vigentes (no vencidas)
        deudas_vigentes = DeudaCartera.query.filter(
            and_(
                DeudaCartera.estado != 'Pagado',
                or_(
                    DeudaCartera.fecha_vencimiento.is_(None),
                    DeudaCartera.fecha_vencimiento >= fecha_hoy
                )
            )
        ).all()

        # Deudas vencidas
        deudas_vencidas = DeudaCartera.query.filter(
            and_(
                DeudaCartera.estado != 'Pagado',
                DeudaCartera.fecha_vencimiento.isnot(None),
                DeudaCartera.fecha_vencimiento < fecha_hoy
            )
        ).all()

        # Calcular montos
        monto_vigente = sum(float(d.monto or 0) for d in deudas_vigentes)
        monto_vencido = sum(float(d.monto or 0) for d in deudas_vencidas)
        monto_total = monto_vigente + monto_vencido

        logger.info(f"📊 Resumen cartera: Total ${monto_total:,.2f} (Vigente: ${monto_vigente:,.2f}, Vencido: ${monto_vencido:,.2f})")

        return jsonify({
            'success': True,
            'fecha_consulta': fecha_hoy,
            'total_deudas': total_deudas,
            'deudas_vigentes': len(deudas_vigentes),
            'deudas_vencidas': len(deudas_vencidas),
            'monto_total': round(monto_total, 2),
            'monto_vigente': round(monto_vigente, 2),
            'monto_vencido': round(monto_vencido, 2),
            'porcentaje_mora': round((monto_vencido / monto_total * 100) if monto_total > 0 else 0, 2)
        }), 200

    except Exception as e:
        logger.error(f"❌ Error obteniendo resumen de cartera: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Error al obtener resumen de cartera',
            'detalle': str(e)
        }), 500


# =============================================================================
# ENDPOINT: PUT /api/cartera/programar-cobro (AGENDA PERSONALIZADA)
# =============================================================================

@bp_cartera.route('/programar-cobro', methods=['PUT'])
@login_required
def programar_recordatorio_cobro():
    """
    AGENDA DE COBROS: Programa una fecha de recordatorio para cobrar a un cliente.

    Request JSON:
        {
            "deuda_id": 123,                    # ID de la deuda en deudas_cartera
            "fecha_recordatorio": "2025-12-15"  # Fecha del recordatorio (YYYY-MM-DD)
        }

    Alternativa (si no hay ID de deuda):
        {
            "entidad_tipo": "empresa",          # "empresa" o "usuario"
            "entidad_id": "900123456",          # NIT o ID del usuario
            "fecha_recordatorio": "2025-12-15"
        }

    Response JSON:
        {
            "success": true,
            "mensaje": "Recordatorio programado para 2025-12-15",
            "deuda": {
                "id": 123,
                "nombre_usuario": "Juan Pérez",
                "monto": 500000.00,
                "fecha_recordatorio_cobro": "2025-12-15"
            }
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No se recibieron datos'
            }), 400

        # Validar fecha_recordatorio
        fecha_recordatorio = data.get('fecha_recordatorio')
        if not fecha_recordatorio:
            return jsonify({
                'success': False,
                'error': 'Falta el campo fecha_recordatorio'
            }), 400

        # Validar formato de fecha
        try:
            datetime.strptime(fecha_recordatorio, "%Y-%m-%d")
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
            }), 400

        # ==================== OPCIÓN 1: Actualizar por ID de deuda ====================
        deuda_id = data.get('deuda_id')

        if deuda_id:
            deuda = DeudaCartera.query.filter_by(id=deuda_id).first()

            if not deuda:
                return jsonify({
                    'success': False,
                    'error': f'Deuda con ID {deuda_id} no encontrada'
                }), 404

            # Actualizar fecha de recordatorio
            deuda.fecha_recordatorio_cobro = fecha_recordatorio
            db.session.commit()

            logger.info(f"⏰ Recordatorio programado para {fecha_recordatorio} - Deuda #{deuda_id} ({deuda.nombre_usuario})")

            return jsonify({
                'success': True,
                'mensaje': f'Recordatorio programado para {fecha_recordatorio}',
                'deuda': deuda.to_dict()
            }), 200

        # ==================== OPCIÓN 2: Actualizar por entidad ====================
        entidad_tipo = data.get('entidad_tipo')  # "empresa" o "usuario"
        entidad_id = data.get('entidad_id')      # NIT o ID del usuario

        if not entidad_tipo or not entidad_id:
            return jsonify({
                'success': False,
                'error': 'Debe proporcionar deuda_id O (entidad_tipo + entidad_id)'
            }), 400

        # Buscar deudas pendientes de la entidad
        if entidad_tipo.lower() == 'empresa':
            deudas = DeudaCartera.query.filter(
                and_(
                    DeudaCartera.empresa_nit == entidad_id,
                    DeudaCartera.estado != 'Pagado'
                )
            ).all()
        elif entidad_tipo.lower() == 'usuario':
            deudas = DeudaCartera.query.filter(
                and_(
                    DeudaCartera.usuario_id == entidad_id,
                    DeudaCartera.estado != 'Pagado'
                )
            ).all()
        else:
            return jsonify({
                'success': False,
                'error': 'entidad_tipo debe ser "empresa" o "usuario"'
            }), 400

        if not deudas:
            return jsonify({
                'success': False,
                'error': f'No se encontraron deudas pendientes para {entidad_tipo} {entidad_id}'
            }), 404

        # Actualizar todas las deudas de la entidad
        deudas_actualizadas = 0
        for deuda in deudas:
            deuda.fecha_recordatorio_cobro = fecha_recordatorio
            deudas_actualizadas += 1

        db.session.commit()

        logger.info(f"⏰ Recordatorio programado para {fecha_recordatorio} - {deudas_actualizadas} deudas de {entidad_tipo} {entidad_id}")

        return jsonify({
            'success': True,
            'mensaje': f'Recordatorio programado para {fecha_recordatorio}',
            'deudas_actualizadas': deudas_actualizadas,
            'deudas': [d.to_dict() for d in deudas]
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error programando recordatorio de cobro: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Error al programar recordatorio',
            'detalle': str(e)
        }), 500


if __name__ == "__main__":
    print("Módulo de gestión de cartera cargado correctamente")
