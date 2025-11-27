"""
routes/analytics.py
Blueprint de Analytics para métricas del dashboard
"""

from flask import Blueprint, jsonify, g
from datetime import datetime, timedelta
from utils import get_db_connection, login_required
import sqlite3

# Crear Blueprint
analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/metrics')


@analytics_bp.route('/overview', methods=['GET'])
@login_required
def get_overview():
    """
    Endpoint: GET /api/metrics/overview
    Retorna métricas generales del sistema:
    - Total de empresas
    - Total de usuarios
    - Pagos del mes actual
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Total de empresas
        cursor.execute("SELECT COUNT(*) as total FROM empresas")
        total_empresas = cursor.fetchone()['total']

        # Total de usuarios
        cursor.execute("SELECT COUNT(*) as total FROM usuarios")
        total_usuarios = cursor.fetchone()['total']

        # Pagos del mes actual
        # Asumiendo que existe una tabla 'pagos' con campo 'fecha_pago'
        fecha_inicio_mes = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT COUNT(*) as total, COALESCE(SUM(monto), 0) as monto_total
            FROM pagos
            WHERE fecha_pago >= ?
        """, (fecha_inicio_mes,))

        pagos_mes = cursor.fetchone()

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'total_empresas': total_empresas,
                'total_usuarios': total_usuarios,
                'pagos_mes': {
                    'cantidad': pagos_mes['total'],
                    'monto_total': float(pagos_mes['monto_total'])
                }
            }
        }), 200

    except sqlite3.Error as e:
        return jsonify({
            'success': False,
            'error': f'Error de base de datos: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }), 500


@analytics_bp.route('/pagos-trend', methods=['GET'])
@login_required
def get_pagos_trend():
    """
    Endpoint: GET /api/metrics/pagos-trend
    Retorna tendencia de pagos de los últimos 6 meses
    Formato: [{mes: 'YYYY-MM', cantidad: N, monto: M}, ...]
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Calcular fecha de hace 6 meses
        fecha_inicio = (datetime.now() - timedelta(days=180)).replace(day=1).strftime('%Y-%m-%d')

        # Query para obtener tendencia de pagos por mes
        cursor.execute("""
            SELECT
                strftime('%Y-%m', fecha_pago) as mes,
                COUNT(*) as cantidad,
                COALESCE(SUM(monto), 0) as monto_total
            FROM pagos
            WHERE fecha_pago >= ?
            GROUP BY strftime('%Y-%m', fecha_pago)
            ORDER BY mes ASC
        """, (fecha_inicio,))

        resultados = cursor.fetchall()
        conn.close()

        # Formatear resultados
        tendencia = []
        for row in resultados:
            tendencia.append({
                'mes': row['mes'],
                'cantidad': row['cantidad'],
                'monto': float(row['monto_total'])
            })

        return jsonify({
            'success': True,
            'data': tendencia
        }), 200

    except sqlite3.Error as e:
        return jsonify({
            'success': False,
            'error': f'Error de base de datos: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }), 500


@analytics_bp.route('/usuarios-trend', methods=['GET'])
@login_required
def get_usuarios_trend():
    """
    Endpoint: GET /api/metrics/usuarios-trend
    Retorna crecimiento de usuarios de los últimos 6 meses
    Formato: [{mes: 'YYYY-MM', nuevos_usuarios: N, total_acumulado: M}, ...]
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Calcular fecha de hace 6 meses
        fecha_inicio = (datetime.now() - timedelta(days=180)).replace(day=1).strftime('%Y-%m-%d')

        # Query para obtener nuevos usuarios por mes
        # Asumiendo que existe campo 'fecha_creacion' en tabla usuarios
        cursor.execute("""
            SELECT
                strftime('%Y-%m', fecha_creacion) as mes,
                COUNT(*) as nuevos_usuarios
            FROM usuarios
            WHERE fecha_creacion >= ?
            GROUP BY strftime('%Y-%m', fecha_creacion)
            ORDER BY mes ASC
        """, (fecha_inicio,))

        resultados = cursor.fetchall()

        # Calcular total acumulado
        tendencia = []
        acumulado = 0

        for row in resultados:
            acumulado += row['nuevos_usuarios']
            tendencia.append({
                'mes': row['mes'],
                'nuevos_usuarios': row['nuevos_usuarios'],
                'total_acumulado': acumulado
            })

        conn.close()

        return jsonify({
            'success': True,
            'data': tendencia
        }), 200

    except sqlite3.Error as e:
        return jsonify({
            'success': False,
            'error': f'Error de base de datos: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }), 500
