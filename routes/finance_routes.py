# -*- coding: utf-8 -*-
"""
Blueprint para rutas de Finanzas (Vistas Web + API Cartera)
Gestión de cartera, planillas, impuestos y otras vistas financieras

REFACTORIZADO: Usa SQLAlchemy ORM en lugar de SQL manual
Autor: Senior Backend Developer
Fecha: 2025-12-09
"""

from flask import Blueprint, render_template, redirect, session, request, jsonify
from datetime import datetime, date
from sqlalchemy import func, and_, or_

# Extensions y modelos ORM
from extensions import db
from models.orm_models import Empresa, CarteraCobrar, CarteraPagarSS

# Utils
try:
    from utils import login_required
except ImportError:
    from ..utils import login_required

# Logger
try:
    from logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


# Definimos el Blueprint para las Vistas de Finanzas
finance_bp = Blueprint('finance_bp_views', __name__)


# ==================== RUTAS DE PLANILLAS ====================

@finance_bp.route('/planillas/enviar')
def view_enviar_planillas():
    """Ruta para el menú 'Enviar Planillas'."""
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('planillas/enviar.html', user=session.get('user'))


# ==================== RUTAS DE PAGOS ====================

@finance_bp.route('/pagos/impuestos')
def view_pago_impuestos():
    """Ruta para el menú 'Pago de Impuestos'."""
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('pagos/impuestos.html', user=session.get('user'))


@finance_bp.route('/pagos/impuestos/crear')
def view_crear_impuesto():
    """Muestra el formulario para subir un nuevo formulario de impuestos."""
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('pagos/impuestos/crear.html', user=session.get('user'))


@finance_bp.route('/pagos/cartera')
def view_cartera():
    """Ruta para el menú 'Cartera'."""
    if 'user_id' not in session:
        return redirect('/login')
    try:
        return render_template('pagos/cartera.html', user=session.get('user'))
    except:
        return "Página en construcción (Falta archivo HTML)"


@finance_bp.route('/cartera/crear')
@login_required
def crear_cartera_vista():
    """Formulario para crear nueva cuenta por cobrar u obligación SS."""
    try:
        empresas = Empresa.query.order_by(Empresa.nombre_empresa).all()
        return render_template('pagos/crear_cartera.html', 
                             empresas=[e.to_dict() for e in empresas],
                             user=session.get('user'))
    except Exception as e:
        logger.error(f"Error al cargar empresas: {e}")
        return render_template('pagos/crear_cartera.html', 
                             empresas=[],
                             user=session.get('user'))


# ==================== RUTAS LEGACY (Compatibilidad) ====================

@finance_bp.route('/pagos/recaudo')
def recaudo():
    """Página de recaudo de pagos (ruta legacy)."""
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('pagos/recaudo.html', user=session.get('user'))


@finance_bp.route('/pagos/control')
def control():
    """Página de control de pagos - tabla (ruta legacy)."""
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('pagos/control_tabla.html', user=session.get('user'))


# =============================================================================
# API - CARTERA (Cuentas por Cobrar) - SQLAlchemy ORM
# =============================================================================

@finance_bp.route('/api/cartera/cobrar', methods=['GET'])
@login_required
def api_get_cartera_cobrar():
    """GET: Obtiene todas las cuentas por cobrar (lo que nos deben los clientes)."""
    try:
        cuentas = CarteraCobrar.query.order_by(CarteraCobrar.fecha_vencimiento.asc()).all()
        
        # Agregar nombre de empresa desde la relación
        result = []
        for cuenta in cuentas:
            data = cuenta.to_dict()
            if cuenta.empresa:
                data['nombre_empresa'] = cuenta.empresa.nombre_empresa
            result.append(data)
        
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error al obtener cartera por cobrar: {e}")
        return jsonify({"error": str(e)}), 500


@finance_bp.route('/api/cartera/pagar', methods=['GET'])
@login_required
def api_get_cartera_pagar():
    """GET: Obtiene todas las obligaciones de seguridad social pendientes."""
    try:
        obligaciones = CarteraPagarSS.query.order_by(CarteraPagarSS.fecha_limite.asc()).all()
        
        # Agregar nombre de empresa desde la relación
        result = []
        for ob in obligaciones:
            data = ob.to_dict()
            if ob.empresa:
                data['nombre_empresa'] = ob.empresa.nombre_empresa
            result.append(data)
        
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error al obtener obligaciones SS: {e}")
        return jsonify({"error": str(e)}), 500


@finance_bp.route('/api/cartera/cobrar', methods=['POST'])
@login_required
def api_create_cuenta_cobrar():
    """POST: Registra una nueva cuenta por cobrar (deuda de cliente)."""
    try:
        data = request.get_json()
        
        if not data.get('empresa_nit') or not data.get('concepto') or not data.get('monto'):
            return jsonify({"error": "Empresa, concepto y monto son requeridos"}), 400
        
        # Obtener nombre de empresa
        empresa = Empresa.query.filter_by(nit=data.get('empresa_nit')).first()
        
        nueva_cuenta = CarteraCobrar(
            empresa_nit=data.get('empresa_nit'),
            nombre_empresa=empresa.nombre_empresa if empresa else None,
            concepto=data.get('concepto'),
            monto=float(data.get('monto')),
            monto_pagado=0,
            fecha_emision=datetime.now().strftime("%Y-%m-%d"),
            fecha_vencimiento=data.get('fecha_vencimiento'),
            estado='Pendiente',
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        db.session.add(nueva_cuenta)
        db.session.commit()
        
        logger.info(f"✅ Cuenta por cobrar creada: {nueva_cuenta.concepto}")
        return jsonify({"message": "Cuenta por cobrar registrada exitosamente", "id": nueva_cuenta.id}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear cuenta por cobrar: {e}")
        return jsonify({"error": str(e)}), 500


@finance_bp.route('/api/cartera/pagar', methods=['POST'])
@login_required
def api_create_obligacion_ss():
    """POST: Registra una nueva obligación de seguridad social."""
    try:
        data = request.get_json()
        
        if not data.get('empresa_nit') or not data.get('tipo_entidad') or not data.get('monto'):
            return jsonify({"error": "Empresa, tipo de entidad y monto son requeridos"}), 400
        
        # Obtener nombre de empresa
        empresa = Empresa.query.filter_by(nit=data.get('empresa_nit')).first()
        
        nueva_obligacion = CarteraPagarSS(
            empresa_nit=data.get('empresa_nit'),
            nombre_empresa=empresa.nombre_empresa if empresa else None,
            tipo_entidad=data.get('tipo_entidad'),
            nombre_entidad=data.get('nombre_entidad', ''),
            periodo=data.get('periodo', datetime.now().strftime("%Y-%m")),
            monto=float(data.get('monto')),
            fecha_limite=data.get('fecha_limite'),
            estado='Pendiente',
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        db.session.add(nueva_obligacion)
        db.session.commit()
        
        logger.info(f"✅ Obligación SS creada: {nueva_obligacion.tipo_entidad}")
        return jsonify({"message": "Obligación registrada exitosamente", "id": nueva_obligacion.id}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear obligación SS: {e}")
        return jsonify({"error": str(e)}), 500


@finance_bp.route('/api/cartera/cobrar/<int:cuenta_id>/pagar', methods=['PUT'])
@login_required
def api_pagar_cuenta_cobrar(cuenta_id):
    """PUT: Marca una cuenta por cobrar como pagada."""
    try:
        data = request.get_json()
        monto_pagado = float(data.get('monto_pagado', 0))
        
        cuenta = CarteraCobrar.query.get(cuenta_id)
        if not cuenta:
            return jsonify({"error": "Cuenta no encontrada"}), 404
        
        # Determinar estado
        monto_total = float(cuenta.monto) if cuenta.monto else 0
        if monto_pagado >= monto_total:
            estado = 'Pagado'
        elif monto_pagado > 0:
            estado = 'Parcial'
        else:
            estado = 'Pendiente'
        
        cuenta.estado = estado
        cuenta.monto_pagado = monto_pagado
        
        db.session.commit()
        
        logger.info(f"✅ Cuenta por cobrar actualizada: ID {cuenta_id} -> {estado}")
        return jsonify({"message": "Cuenta actualizada exitosamente", "estado": estado}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al pagar cuenta: {e}")
        return jsonify({"error": str(e)}), 500


@finance_bp.route('/api/cartera/pagar/<int:obligacion_id>/pagar', methods=['PUT'])
@login_required
def api_pagar_obligacion_ss(obligacion_id):
    """PUT: Marca una obligación de seguridad social como pagada."""
    try:
        data = request.get_json()
        
        obligacion = CarteraPagarSS.query.get(obligacion_id)
        if not obligacion:
            return jsonify({"error": "Obligación no encontrada"}), 404
        
        obligacion.estado = 'Pagado'
        obligacion.fecha_pago = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        obligacion.numero_planilla = data.get('numero_planilla', '')
        
        db.session.commit()
        
        logger.info(f"✅ Obligación SS pagada: ID {obligacion_id}")
        return jsonify({"message": "Obligación marcada como pagada"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al pagar obligación: {e}")
        return jsonify({"error": str(e)}), 500


# =============================================================================
# API - ESTADÍSTICAS DE CARTERA - SQLAlchemy ORM
# =============================================================================

@finance_bp.route('/api/cartera/stats', methods=['GET'])
@login_required
def api_get_cartera_stats():
    """GET: Obtiene estadísticas de cartera (resúmenes financieros)."""
    try:
        hoy = date.today().strftime("%Y-%m-%d")
        
        # Total por cobrar (pendiente)
        total_cobrar_query = db.session.query(
            func.coalesce(
                func.sum(CarteraCobrar.monto - func.coalesce(CarteraCobrar.monto_pagado, 0)), 
                0
            )
        ).filter(CarteraCobrar.estado != 'Pagado')
        total_cobrar = total_cobrar_query.scalar() or 0
        
        # Cartera vencida
        cartera_vencida_query = db.session.query(
            func.coalesce(
                func.sum(CarteraCobrar.monto - func.coalesce(CarteraCobrar.monto_pagado, 0)), 
                0
            )
        ).filter(
            or_(
                CarteraCobrar.estado == 'Vencido',
                and_(
                    CarteraCobrar.estado == 'Pendiente',
                    CarteraCobrar.fecha_vencimiento < hoy
                )
            )
        )
        cartera_vencida = cartera_vencida_query.scalar() or 0
        
        # Total a pagar seguridad social
        total_pagar = db.session.query(
            func.coalesce(func.sum(CarteraPagarSS.monto), 0)
        ).filter(CarteraPagarSS.estado == 'Pendiente').scalar() or 0
        
        # Total a pagar por tipo
        por_tipo_query = db.session.query(
            CarteraPagarSS.tipo_entidad,
            func.coalesce(func.sum(CarteraPagarSS.monto), 0).label('monto_tipo')
        ).filter(
            CarteraPagarSS.estado == 'Pendiente'
        ).group_by(CarteraPagarSS.tipo_entidad).all()
        
        por_tipo = {row[0]: float(row[1]) for row in por_tipo_query}
        
        return jsonify({
            "total_cobrar": float(total_cobrar),
            "cartera_vencida": float(cartera_vencida),
            "total_pagar": float(total_pagar),
            "total_eps": por_tipo.get('EPS', 0),
            "total_arl": por_tipo.get('ARL', 0),
            "total_pension": por_tipo.get('Pensión', 0),
            "total_ccf": por_tipo.get('CCF', 0)
        }), 200
    except Exception as e:
        logger.error(f"Error al obtener estadísticas de cartera: {e}")
        return jsonify({"error": str(e)}), 500
