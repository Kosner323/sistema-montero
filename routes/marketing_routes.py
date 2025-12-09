# -*- coding: utf-8 -*-
"""
Blueprint para el módulo de Marketing (Growth)
Gestiona redes sociales, campañas publicitarias y prospectos (CRM)

REFACTORIZADO: Usa SQLAlchemy ORM en lugar de SQL manual
Autor: Senior Backend Developer
Fecha: 2025-12-09
"""

from flask import Blueprint, render_template, request, jsonify
from datetime import datetime
from sqlalchemy import func, and_

# Extensions y modelos ORM
from extensions import db
from models.orm_models import Prospecto, RedSocial, CampanaMarketing

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


# Crear el Blueprint de marketing
bp_marketing = Blueprint("marketing", __name__, url_prefix="/marketing")


# =============================================================================
# RUTAS DE VISTAS (Render HTML)
# =============================================================================

@bp_marketing.route("/redes")
@login_required
def redes():
    """Muestra la página de gestión de redes sociales."""
    return render_template("marketing/redes.html")


@bp_marketing.route("/campanas")
@login_required
def campanas():
    """Muestra la página de gestión de campañas publicitarias."""
    return render_template("marketing/campanas.html")


@bp_marketing.route("/campanas/nueva")
@login_required
def nueva_campana():
    """Muestra el formulario para crear una nueva campaña."""
    return render_template("marketing/nueva_campana.html")


@bp_marketing.route("/campanas/crear")
@login_required
def crear_campana():
    """Muestra el formulario dedicado para crear una campaña."""
    return render_template("marketing/crear_campana.html")


@bp_marketing.route("/prospectos")
@login_required
def prospectos():
    """Muestra la página de gestión de prospectos (CRM de Leads)."""
    return render_template("marketing/prospectos.html")


@bp_marketing.route("/prospectos/crear")
@login_required
def crear_prospecto():
    """Muestra el formulario dedicado para registrar un nuevo prospecto."""
    return render_template("marketing/crear_prospecto.html")


# =============================================================================
# API - REDES SOCIALES (CRUD) - SQLAlchemy ORM
# =============================================================================

@bp_marketing.route("/api/redes", methods=["GET"])
@login_required
def api_get_redes():
    """GET: Obtiene todas las redes sociales registradas."""
    try:
        redes = RedSocial.query.order_by(RedSocial.id.desc()).all()
        return jsonify([r.to_dict() for r in redes]), 200
    except Exception as e:
        logger.error(f"Error al obtener redes sociales: {e}")
        return jsonify({"error": str(e)}), 500


@bp_marketing.route("/api/redes", methods=["POST"])
@login_required
def api_create_red():
    """POST: Crea una nueva red social."""
    try:
        data = request.get_json()
        
        if not data.get("plataforma") or not data.get("url"):
            return jsonify({"error": "Plataforma y URL son requeridos"}), 400
        
        nueva_red = RedSocial(
            plataforma=data.get("plataforma"),
            url=data.get("url"),
            seguidores=data.get("seguidores", 0),
            estado=data.get("estado", "Activo"),
            descripcion=data.get("descripcion", ""),
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        db.session.add(nueva_red)
        db.session.commit()
        
        logger.info(f"✅ Red social creada: {nueva_red.plataforma}")
        return jsonify({"message": "Red social creada exitosamente", "id": nueva_red.id}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear red social: {e}")
        return jsonify({"error": str(e)}), 500


@bp_marketing.route("/api/redes/<int:red_id>", methods=["PUT"])
@login_required
def api_update_red(red_id):
    """PUT: Actualiza una red social existente."""
    try:
        data = request.get_json()
        
        red = RedSocial.query.get(red_id)
        if not red:
            return jsonify({"error": "Red social no encontrada"}), 404
        
        if "seguidores" in data:
            red.seguidores = data["seguidores"]
        if "estado" in data:
            red.estado = data["estado"]
        if "url" in data:
            red.url = data["url"]
        if "descripcion" in data:
            red.descripcion = data["descripcion"]
        
        db.session.commit()
        
        logger.info(f"✅ Red social actualizada: {red.plataforma}")
        return jsonify({"message": "Red social actualizada exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al actualizar red social: {e}")
        return jsonify({"error": str(e)}), 500


@bp_marketing.route("/api/redes/<int:red_id>", methods=["DELETE"])
@login_required
def api_delete_red(red_id):
    """DELETE: Elimina una red social."""
    try:
        red = RedSocial.query.get(red_id)
        if not red:
            return jsonify({"error": "Red social no encontrada"}), 404
        
        db.session.delete(red)
        db.session.commit()
        
        logger.info(f"✅ Red social eliminada: ID {red_id}")
        return jsonify({"message": "Red social eliminada exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al eliminar red social: {e}")
        return jsonify({"error": str(e)}), 500


# =============================================================================
# API - CAMPAÑAS PUBLICITARIAS (CRUD) - SQLAlchemy ORM
# =============================================================================

@bp_marketing.route("/api/campanas", methods=["GET"])
@login_required
def api_get_campanas():
    """GET: Obtiene todas las campañas publicitarias."""
    try:
        campanas = CampanaMarketing.query.order_by(CampanaMarketing.fecha_inicio.desc()).all()
        return jsonify([c.to_dict() for c in campanas]), 200
    except Exception as e:
        logger.error(f"Error al obtener campañas: {e}")
        return jsonify({"error": str(e)}), 500


@bp_marketing.route("/api/campanas", methods=["POST"])
@login_required
def api_create_campana():
    """POST: Crea una nueva campaña publicitaria."""
    try:
        data = request.get_json()
        
        if not data.get("nombre_campana"):
            return jsonify({"error": "El nombre de la campaña es requerido"}), 400
        
        nueva_campana = CampanaMarketing(
            nombre_campana=data.get("nombre_campana"),
            descripcion=data.get("descripcion", ""),
            fecha_inicio=data.get("fecha_inicio"),
            fecha_fin=data.get("fecha_fin"),
            presupuesto=data.get("presupuesto", 0.0),
            estado=data.get("estado", "Activa"),
            objetivo=data.get("objetivo", ""),
            canal=data.get("canal", ""),
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        db.session.add(nueva_campana)
        db.session.commit()
        
        logger.info(f"✅ Campaña creada: {nueva_campana.nombre_campana}")
        return jsonify({"message": "Campaña creada exitosamente", "id": nueva_campana.id}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear campaña: {e}")
        return jsonify({"error": str(e)}), 500


@bp_marketing.route("/api/campanas/<int:campana_id>", methods=["PUT"])
@login_required
def api_update_campana(campana_id):
    """PUT: Actualiza el estado de una campaña."""
    try:
        data = request.get_json()
        
        campana = CampanaMarketing.query.get(campana_id)
        if not campana:
            return jsonify({"error": "Campaña no encontrada"}), 404
        
        if "estado" in data:
            campana.estado = data["estado"]
        if "descripcion" in data:
            campana.descripcion = data["descripcion"]
        if "presupuesto" in data:
            campana.presupuesto = data["presupuesto"]
        
        campana.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        db.session.commit()
        
        logger.info(f"✅ Campaña actualizada: {campana.nombre_campana}")
        return jsonify({"message": "Campaña actualizada exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al actualizar campaña: {e}")
        return jsonify({"error": str(e)}), 500


@bp_marketing.route("/api/campanas/<int:campana_id>", methods=["DELETE"])
@login_required
def api_delete_campana(campana_id):
    """DELETE: Elimina una campaña."""
    try:
        campana = CampanaMarketing.query.get(campana_id)
        if not campana:
            return jsonify({"error": "Campaña no encontrada"}), 404
        
        db.session.delete(campana)
        db.session.commit()
        
        logger.info(f"✅ Campaña eliminada: ID {campana_id}")
        return jsonify({"message": "Campaña eliminada exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al eliminar campaña: {e}")
        return jsonify({"error": str(e)}), 500


# =============================================================================
# API - PROSPECTOS / CRM DE LEADS (CRUD) - SQLAlchemy ORM
# =============================================================================

@bp_marketing.route("/api/prospectos", methods=["GET"])
@login_required
def api_get_prospectos():
    """GET: Obtiene todos los prospectos (leads)."""
    try:
        estado = request.args.get("estado")
        origen = request.args.get("origen")
        
        query = Prospecto.query
        
        if estado:
            query = query.filter(Prospecto.estado == estado)
        if origen:
            query = query.filter(Prospecto.origen == origen)
        
        prospectos = query.order_by(Prospecto.id.desc()).all()
        
        return jsonify([p.to_dict() for p in prospectos]), 200
    except Exception as e:
        logger.error(f"Error al obtener prospectos: {e}")
        return jsonify({"error": str(e)}), 500


@bp_marketing.route("/api/prospectos", methods=["POST"])
@login_required
def api_create_prospecto():
    """POST: Registra un nuevo prospecto (lead de empresa)."""
    try:
        data = request.get_json()
        
        if not data.get("nombre_empresa"):
            return jsonify({"error": "El nombre de la empresa es requerido"}), 400
        if not data.get("nombre_contacto"):
            return jsonify({"error": "El nombre del contacto es requerido"}), 400
        
        nuevo_prospecto = Prospecto(
            nombre_empresa=data.get("nombre_empresa"),
            nombre_contacto=data.get("nombre_contacto"),
            telefono_contacto=data.get("telefono_contacto", ""),
            correo_contacto=data.get("correo_contacto", ""),
            origen=data.get("origen", "Web"),
            interes_servicio=data.get("interes_servicio", ""),
            estado=data.get("estado", "Nuevo"),
            notas=data.get("notas", ""),
            valor_estimado=data.get("valor_estimado", 0.0),
            fecha_registro=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        db.session.add(nuevo_prospecto)
        db.session.commit()
        
        logger.info(f"✅ Prospecto creado: {nuevo_prospecto.nombre_empresa}")
        return jsonify({"message": "Prospecto registrado exitosamente", "id": nuevo_prospecto.id}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear prospecto: {e}")
        return jsonify({"error": str(e)}), 500


@bp_marketing.route("/api/prospectos/<int:prospecto_id>", methods=["PUT"])
@login_required
def api_update_prospecto(prospecto_id):
    """PUT: Actualiza el estado o información de un prospecto."""
    try:
        data = request.get_json()
        
        prospecto = Prospecto.query.get(prospecto_id)
        if not prospecto:
            return jsonify({"error": "Prospecto no encontrado"}), 404
        
        if "estado" in data:
            prospecto.estado = data["estado"]
            if data["estado"] == "Contactado":
                prospecto.fecha_contacto = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if "notas" in data:
            prospecto.notas = data["notas"]
        if "valor_estimado" in data:
            prospecto.valor_estimado = data["valor_estimado"]
        if "interes_servicio" in data:
            prospecto.interes_servicio = data["interes_servicio"]
        
        db.session.commit()
        
        logger.info(f"✅ Prospecto actualizado: {prospecto.nombre_empresa}")
        return jsonify({"message": "Prospecto actualizado exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al actualizar prospecto: {e}")
        return jsonify({"error": str(e)}), 500


@bp_marketing.route("/api/prospectos/<int:prospecto_id>", methods=["DELETE"])
@login_required
def api_delete_prospecto(prospecto_id):
    """DELETE: Elimina un prospecto."""
    try:
        prospecto = Prospecto.query.get(prospecto_id)
        if not prospecto:
            return jsonify({"error": "Prospecto no encontrado"}), 404
        
        db.session.delete(prospecto)
        db.session.commit()
        
        logger.info(f"✅ Prospecto eliminado: ID {prospecto_id}")
        return jsonify({"message": "Prospecto eliminado exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al eliminar prospecto: {e}")
        return jsonify({"error": str(e)}), 500


# =============================================================================
# API - ESTADÍSTICAS Y DASHBOARD - SQLAlchemy ORM
# =============================================================================

@bp_marketing.route("/api/stats", methods=["GET"])
@login_required
def api_get_stats():
    """GET: Obtiene estadísticas generales del módulo de marketing."""
    try:
        from datetime import date
        
        # Total de prospectos
        total_prospectos = Prospecto.query.count()
        
        # Prospectos nuevos hoy
        hoy = date.today().strftime("%Y-%m-%d")
        nuevos_hoy = Prospecto.query.filter(
            Prospecto.fecha_registro.like(f"{hoy}%")
        ).count()
        
        # Campañas activas
        campanas_activas = CampanaMarketing.query.filter(
            CampanaMarketing.estado == 'Activa'
        ).count()
        
        # Total seguidores en redes
        total_seguidores = db.session.query(
            func.coalesce(func.sum(RedSocial.seguidores), 0)
        ).scalar()
        
        return jsonify({
            "total_prospectos": total_prospectos,
            "nuevos_hoy": nuevos_hoy,
            "campanas_activas": campanas_activas,
            "total_seguidores": total_seguidores
        }), 200
    except Exception as e:
        logger.error(f"Error al obtener estadísticas de marketing: {e}")
        return jsonify({"error": str(e)}), 500
