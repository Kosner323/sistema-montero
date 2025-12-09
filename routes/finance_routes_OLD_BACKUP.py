# -*- coding: utf-8 -*-
"""
Blueprint para rutas de Finanzas (Vistas Web + API Cartera)
Gestión de cartera, planillas, impuestos y otras vistas financieras
Nota: Las rutas de API de pagos están en pagos.py
"""

from flask import Blueprint, render_template, redirect, session, request, jsonify
from utils import login_required, get_db_connection
from datetime import datetime

# Definimos el Blueprint para las Vistas de Finanzas
# Nota: No usamos url_prefix aquí para tener flexibilidad en las rutas del menú
finance_bp = Blueprint('finance_bp_views', __name__)


# ==================== RUTAS DE PLANILLAS ====================

@finance_bp.route('/planillas/enviar')
def view_enviar_planillas():
    """
    Ruta para el menú "Enviar Planillas"
    Renderiza: planillas/enviar.html
    """
    # Verificar autenticación
    if 'user_id' not in session:
        return redirect('/login')

    return render_template('planillas/enviar.html', user=session.get('user'))


# ==================== RUTAS DE PAGOS ====================

@finance_bp.route('/pagos/impuestos')
def view_pago_impuestos():
    """
    Ruta para el menú "Pago de Impuestos"
    Renderiza: pagos/impuestos.html
    """
    # Verificar autenticación
    if 'user_id' not in session:
        return redirect('/login')

    return render_template('pagos/impuestos.html', user=session.get('user'))


@finance_bp.route('/pagos/impuestos/crear')
def view_crear_impuesto():
    """
    Muestra el formulario para subir un nuevo formulario de impuestos (página dedicada).
    """
    # Verificar autenticación
    if 'user_id' not in session:
        return redirect('/login')

    return render_template('pagos/impuestos/crear.html', user=session.get('user'))


@finance_bp.route('/pagos/cartera')
def view_cartera():
    """
    Ruta para el menú "Cartera" (si ya existe el HTML)
    Renderiza: pagos/cartera.html
    """
    # Verificar autenticación
    if 'user_id' not in session:
        return redirect('/login')

    try:
        return render_template('pagos/cartera.html', user=session.get('user'))
    except:
        return "Página en construcción (Falta archivo HTML)"


@finance_bp.route('/cartera/crear')
@login_required
def crear_cartera_vista():
    """
    Formulario para crear nueva cuenta por cobrar u obligación SS
    Renderiza: pagos/crear_cartera.html
    """
    # Obtener empresas para el dropdown
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nombre_empresa, nit FROM empresas ORDER BY nombre_empresa')
        empresas = cursor.fetchall()
        conn.close()
        
        return render_template('pagos/crear_cartera.html', 
                             empresas=empresas,
                             user=session.get('user'))
    except Exception as e:
        print(f"Error al cargar empresas: {e}")
        return render_template('pagos/crear_cartera.html', 
                             empresas=[],
                             user=session.get('user'))


# ==================== RUTAS LEGACY (Compatibilidad) ====================
# Estas rutas mantienen compatibilidad con enlaces antiguos

@finance_bp.route('/pagos/recaudo')
def recaudo():
    """
    Página de recaudo de pagos (ruta legacy)
    Renderiza: pagos/recaudo.html
    """
    # Verificar autenticación
    if 'user_id' not in session:
        return redirect('/login')

    return render_template('pagos/recaudo.html', user=session.get('user'))


@finance_bp.route('/pagos/control')
def control():
    """
    Página de control de pagos - tabla (ruta legacy)
    Renderiza: pagos/control_tabla.html
    """
    # Verificar autenticación
    if 'user_id' not in session:
        return redirect('/login')

    return render_template('pagos/control_tabla.html', user=session.get('user'))


# =============================================================================
# API - CARTERA (Cuentas por Cobrar y Obligaciones de Seguridad Social)
# =============================================================================

@finance_bp.route('/api/cartera/cobrar', methods=['GET'])
@login_required
def api_get_cartera_cobrar():
    """
    GET: Obtiene todas las cuentas por cobrar (lo que nos deben los clientes).
    Incluye JOIN con tabla empresas para mostrar nombres.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                cc.id,
                cc.empresa_nit,
                e.nombre_empresa,
                cc.concepto,
                cc.monto,
                cc.fecha_emision,
                cc.fecha_vencimiento,
                cc.estado,
                cc.monto_pagado,
                cc.fecha_pago,
                cc.notas
            FROM cartera_cobrar cc
            LEFT JOIN empresas e ON cc.empresa_nit = e.nit
            ORDER BY cc.fecha_vencimiento ASC
        """)
        
        cuentas = cursor.fetchall()
        conn.close()
        
        return jsonify([dict(cuenta) for cuenta in cuentas]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@finance_bp.route('/api/cartera/pagar', methods=['GET'])
@login_required
def api_get_cartera_pagar():
    """
    GET: Obtiene todas las obligaciones de seguridad social pendientes.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                cp.id,
                cp.empresa_nit,
                e.nombre_empresa,
                cp.tipo_entidad,
                cp.nombre_entidad,
                cp.periodo,
                cp.monto,
                cp.fecha_limite,
                cp.estado,
                cp.fecha_pago,
                cp.numero_planilla,
                cp.notas
            FROM cartera_pagar_ss cp
            LEFT JOIN empresas e ON cp.empresa_nit = e.nit
            ORDER BY cp.fecha_limite ASC
        """)
        
        obligaciones = cursor.fetchall()
        conn.close()
        
        return jsonify([dict(ob) for ob in obligaciones]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@finance_bp.route('/api/cartera/cobrar', methods=['POST'])
@login_required
def api_create_cuenta_cobrar():
    """
    POST: Registra una nueva cuenta por cobrar (deuda de cliente).
    """
    try:
        data = request.get_json()
        
        # Validaciones
        if not data.get('empresa_nit') or not data.get('concepto') or not data.get('monto'):
            return jsonify({"error": "Empresa, concepto y monto son requeridos"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO cartera_cobrar 
            (empresa_nit, concepto, monto, fecha_vencimiento, notas)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data.get('empresa_nit'),
            data.get('concepto'),
            float(data.get('monto')),
            data.get('fecha_vencimiento'),
            data.get('notas', '')
        ))
        
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        
        return jsonify({"message": "Cuenta por cobrar registrada exitosamente", "id": new_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@finance_bp.route('/api/cartera/cobrar/<int:cuenta_id>/pagar', methods=['PUT'])
@login_required
def api_pagar_cuenta_cobrar(cuenta_id):
    """
    PUT: Marca una cuenta por cobrar como pagada.
    """
    try:
        data = request.get_json()
        monto_pagado = data.get('monto_pagado', 0)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener monto total
        cursor.execute("SELECT monto FROM cartera_cobrar WHERE id = ?", (cuenta_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return jsonify({"error": "Cuenta no encontrada"}), 404
        
        monto_total = result['monto']
        
        # Determinar estado
        if monto_pagado >= monto_total:
            estado = 'Pagado'
        elif monto_pagado > 0:
            estado = 'Parcial'
        else:
            estado = 'Pendiente'
        
        cursor.execute("""
            UPDATE cartera_cobrar
            SET estado = ?,
                monto_pagado = ?,
                fecha_pago = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (estado, monto_pagado, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), cuenta_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Cuenta actualizada exitosamente", "estado": estado}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@finance_bp.route('/api/cartera/pagar/<int:obligacion_id>/pagar', methods=['PUT'])
@login_required
def api_pagar_obligacion_ss(obligacion_id):
    """
    PUT: Marca una obligación de seguridad social como pagada.
    """
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE cartera_pagar_ss
            SET estado = 'Pagado',
                fecha_pago = ?,
                numero_planilla = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data.get('numero_planilla', ''),
            obligacion_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Obligación marcada como pagada"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@finance_bp.route('/api/cartera/stats', methods=['GET'])
@login_required
def api_get_cartera_stats():
    """
    GET: Obtiene estadísticas de cartera (resúmenes financieros).
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total por cobrar
        cursor.execute("""
            SELECT COALESCE(SUM(monto - monto_pagado), 0) as total_cobrar
            FROM cartera_cobrar
            WHERE estado != 'Pagado'
        """)
        total_cobrar = cursor.fetchone()['total_cobrar']
        
        # Cartera vencida
        cursor.execute("""
            SELECT COALESCE(SUM(monto - monto_pagado), 0) as cartera_vencida
            FROM cartera_cobrar
            WHERE estado = 'Vencido' OR (estado = 'Pendiente' AND DATE(fecha_vencimiento) < DATE('now'))
        """)
        cartera_vencida = cursor.fetchone()['cartera_vencida']
        
        # Total a pagar seguridad social
        cursor.execute("""
            SELECT COALESCE(SUM(monto), 0) as total_pagar
            FROM cartera_pagar_ss
            WHERE estado = 'Pendiente'
        """)
        total_pagar = cursor.fetchone()['total_pagar']
        
        # Total a pagar por tipo
        cursor.execute("""
            SELECT tipo_entidad, COALESCE(SUM(monto), 0) as monto_tipo
            FROM cartera_pagar_ss
            WHERE estado = 'Pendiente'
            GROUP BY tipo_entidad
        """)
        por_tipo = {row['tipo_entidad']: row['monto_tipo'] for row in cursor.fetchall()}
        
        conn.close()
        
        return jsonify({
            "total_cobrar": total_cobrar,
            "cartera_vencida": cartera_vencida,
            "total_pagar": total_pagar,
            "total_eps": por_tipo.get('EPS', 0),
            "total_arl": por_tipo.get('ARL', 0),
            "total_pension": por_tipo.get('Pensión', 0),
            "total_ccf": por_tipo.get('CCF', 0)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
