"""
Blueprint de Tareas Personal (Fase 11.2)
=========================================
API REST para gestión de tareas To-Do List por usuario

Endpoints:
    GET    /api/tareas           - Lista tareas del usuario
    POST   /api/tareas           - Crea nueva tarea
    PUT    /api/tareas/<id>/toggle - Marca completada/pendiente
    DELETE /api/tareas/<id>      - Elimina tarea

Autor: Senior Backend Developer
Fecha: 30 de Noviembre de 2024
"""

from flask import Blueprint, request, jsonify, session
from datetime import datetime
from extensions import db
from models.orm_models import TareaUsuario
from functools import wraps

# Crear Blueprint
tareas_bp = Blueprint('tareas', __name__, url_prefix='/api/tareas')


# =============================================================================
# DECORADOR DE AUTENTICACIÓN
# =============================================================================

def require_auth(f):
    """Decorador para verificar que el usuario esté logueado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'No autenticado. Inicia sesión primero.'
            }), 401
        return f(*args, **kwargs)
    return decorated_function


# =============================================================================
# ENDPOINTS
# =============================================================================

@tareas_bp.route('', methods=['GET'])
@require_auth
def listar_tareas():
    """
    GET /api/tareas
    
    Retorna todas las tareas del usuario logueado.
    Parámetros opcionales:
        - estado: 'pendientes' | 'completadas' | 'todas' (default: 'pendientes')
    
    Response:
        {
            "success": true,
            "tareas": [
                {
                    "id": 1,
                    "descripcion": "Revisar planillas",
                    "completada": false,
                    "created_at": "2025-11-30 10:00:00"
                }
            ],
            "total": 5,
            "pendientes": 3,
            "completadas": 2
        }
    """
    try:
        user_id = session.get('user_id')
        estado = request.args.get('estado', 'pendientes')
        
        # Query base
        query = TareaUsuario.query.filter_by(user_id=user_id)
        
        # Filtrar por estado
        if estado == 'pendientes':
            query = query.filter_by(completada=0)
        elif estado == 'completadas':
            query = query.filter_by(completada=1)
        # 'todas' no filtra
        
        # Ordenar: pendientes primero, luego por fecha descendente
        tareas = query.order_by(TareaUsuario.completada.asc(), TareaUsuario.created_at.desc()).all()
        
        # Estadísticas
        total_pendientes = TareaUsuario.query.filter_by(user_id=user_id, completada=0).count()
        total_completadas = TareaUsuario.query.filter_by(user_id=user_id, completada=1).count()
        
        return jsonify({
            'success': True,
            'tareas': [tarea.to_dict() for tarea in tareas],
            'total': len(tareas),
            'pendientes': total_pendientes,
            'completadas': total_completadas
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al listar tareas: {str(e)}'
        }), 500


@tareas_bp.route('', methods=['POST'])
@require_auth
def crear_tarea():
    """
    POST /api/tareas
    
    Crea una nueva tarea para el usuario logueado.
    
    Request Body:
        {
            "descripcion": "Texto de la tarea"
        }
    
    Response:
        {
            "success": true,
            "tarea": {
                "id": 4,
                "descripcion": "Nueva tarea",
                "completada": false,
                "created_at": "2025-11-30 10:30:00"
            },
            "message": "Tarea creada exitosamente"
        }
    """
    try:
        data = request.get_json()
        
        # Validar datos
        if not data or 'descripcion' not in data:
            return jsonify({
                'success': False,
                'error': 'El campo "descripcion" es obligatorio'
            }), 400
        
        descripcion = data.get('descripcion', '').strip()
        
        if not descripcion:
            return jsonify({
                'success': False,
                'error': 'La descripción no puede estar vacía'
            }), 400
        
        if len(descripcion) > 500:
            return jsonify({
                'success': False,
                'error': 'La descripción no puede superar 500 caracteres'
            }), 400
        
        # Crear nueva tarea
        user_id = session.get('user_id')
        
        nueva_tarea = TareaUsuario(
            user_id=user_id,
            descripcion=descripcion,
            completada=0,
            created_at=datetime.utcnow()
        )
        
        db.session.add(nueva_tarea)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'tarea': nueva_tarea.to_dict(),
            'message': 'Tarea creada exitosamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Error al crear tarea: {str(e)}'
        }), 500


@tareas_bp.route('/<int:tarea_id>/toggle', methods=['PUT'])
@require_auth
def toggle_tarea(tarea_id):
    """
    PUT /api/tareas/<id>/toggle
    
    Marca una tarea como completada/pendiente (toggle estado).
    
    Response:
        {
            "success": true,
            "tarea": {
                "id": 1,
                "descripcion": "Revisar planillas",
                "completada": true,
                "created_at": "2025-11-30 10:00:00"
            },
            "message": "Tarea marcada como completada"
        }
    """
    try:
        user_id = session.get('user_id')
        
        # Buscar tarea (solo del usuario actual)
        tarea = TareaUsuario.query.filter_by(id=tarea_id, user_id=user_id).first()
        
        if not tarea:
            return jsonify({
                'success': False,
                'error': 'Tarea no encontrada o no pertenece al usuario'
            }), 404
        
        # Toggle estado
        tarea.completada = 1 if tarea.completada == 0 else 0
        db.session.commit()
        
        estado_texto = "completada" if tarea.completada else "pendiente"
        
        return jsonify({
            'success': True,
            'tarea': tarea.to_dict(),
            'message': f'Tarea marcada como {estado_texto}'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Error al actualizar tarea: {str(e)}'
        }), 500


@tareas_bp.route('/<int:tarea_id>', methods=['DELETE'])
@require_auth
def eliminar_tarea(tarea_id):
    """
    DELETE /api/tareas/<id>
    
    Elimina una tarea del usuario logueado.
    
    Response:
        {
            "success": true,
            "message": "Tarea eliminada exitosamente",
            "tarea_id": 1
        }
    """
    try:
        user_id = session.get('user_id')
        
        # Buscar tarea (solo del usuario actual)
        tarea = TareaUsuario.query.filter_by(id=tarea_id, user_id=user_id).first()
        
        if not tarea:
            return jsonify({
                'success': False,
                'error': 'Tarea no encontrada o no pertenece al usuario'
            }), 404
        
        # Guardar descripción antes de eliminar (para log)
        descripcion = tarea.descripcion
        
        # Eliminar tarea
        db.session.delete(tarea)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tarea eliminada exitosamente',
            'tarea_id': tarea_id,
            'descripcion': descripcion
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Error al eliminar tarea: {str(e)}'
        }), 500


# =============================================================================
# ENDPOINT DE ESTADÍSTICAS (BONUS)
# =============================================================================

@tareas_bp.route('/stats', methods=['GET'])
@require_auth
def estadisticas_tareas():
    """
    GET /api/tareas/stats
    
    Retorna estadísticas de tareas del usuario.
    
    Response:
        {
            "success": true,
            "stats": {
                "total": 10,
                "pendientes": 7,
                "completadas": 3,
                "porcentaje_completadas": 30.0
            }
        }
    """
    try:
        user_id = session.get('user_id')
        
        total = TareaUsuario.query.filter_by(user_id=user_id).count()
        pendientes = TareaUsuario.query.filter_by(user_id=user_id, completada=0).count()
        completadas = TareaUsuario.query.filter_by(user_id=user_id, completada=1).count()
        
        porcentaje = (completadas / total * 100) if total > 0 else 0.0
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total,
                'pendientes': pendientes,
                'completadas': completadas,
                'porcentaje_completadas': round(porcentaje, 2)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al obtener estadísticas: {str(e)}'
        }), 500
