# -*- coding: utf-8 -*-
"""
Blueprint para el módulo de Marketing (Growth)
Gestiona redes sociales, campañas publicitarias y prospectos (CRM)
"""

from flask import Blueprint, render_template, request, jsonify
from utils import login_required, get_db_connection
from datetime import datetime

# Crear el Blueprint de marketing
bp_marketing = Blueprint("marketing", __name__, url_prefix="/marketing")


# =============================================================================
# RUTAS DE VISTAS (Render HTML)
# =============================================================================

@bp_marketing.route("/redes")
@login_required
def redes():
    """
    Muestra la página de gestión de redes sociales.
    """
    return render_template("marketing/redes.html")


@bp_marketing.route("/campanas")
@login_required
def campanas():
    """
    Muestra la página de gestión de campañas publicitarias.
    """
    return render_template("marketing/campanas.html")


@bp_marketing.route("/campanas/nueva")
@login_required
def nueva_campana():
    """
    Muestra el formulario para crear una nueva campaña.
    """
    return render_template("marketing/nueva_campana.html")


@bp_marketing.route("/campanas/crear")
@login_required
def crear_campana():
    """
    Muestra el formulario dedicado para crear una campaña (alias de nueva_campana).
    """
    return render_template("marketing/crear_campana.html")


@bp_marketing.route("/prospectos")
@login_required
def prospectos():
    """
    Muestra la página de gestión de prospectos (CRM de Leads).
    """
    return render_template("marketing/prospectos.html")


@bp_marketing.route("/prospectos/crear")
@login_required
def crear_prospecto():
    """
    Muestra el formulario dedicado para registrar un nuevo prospecto.
    """
    return render_template("marketing/crear_prospecto.html")


# =============================================================================
# API - REDES SOCIALES (CRUD)
# =============================================================================

@bp_marketing.route("/api/redes", methods=["GET"])
@login_required
def api_get_redes():
    """
    GET: Obtiene todas las redes sociales registradas.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, plataforma, url, seguidores, estado, descripcion, created_at
            FROM marketing_redes
            ORDER BY id DESC
        """)
        redes = cursor.fetchall()
        conn.close()
        
        return jsonify([dict(red) for red in redes]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp_marketing.route("/api/redes", methods=["POST"])
@login_required
def api_create_red():
    """
    POST: Crea una nueva red social.
    """
    try:
        data = request.get_json()
        
        # Validaciones
        if not data.get("plataforma") or not data.get("url"):
            return jsonify({"error": "Plataforma y URL son requeridos"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO marketing_redes (plataforma, url, seguidores, estado, descripcion)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data.get("plataforma"),
            data.get("url"),
            data.get("seguidores", 0),
            data.get("estado", "Activo"),
            data.get("descripcion", "")
        ))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        
        return jsonify({"message": "Red social creada exitosamente", "id": new_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp_marketing.route("/api/redes/<int:red_id>", methods=["PUT"])
@login_required
def api_update_red(red_id):
    """
    PUT: Actualiza una red social existente.
    """
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE marketing_redes
            SET seguidores = ?, estado = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (data.get("seguidores"), data.get("estado"), red_id))
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Red social actualizada exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =============================================================================
# API - CAMPAÑAS PUBLICITARIAS (CRUD)
# =============================================================================

@bp_marketing.route("/api/campanas", methods=["GET"])
@login_required
def api_get_campanas():
    """
    GET: Obtiene todas las campañas publicitarias.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nombre_campana, descripcion, fecha_inicio, fecha_fin, 
                   presupuesto, estado, objetivo, canal, metricas_alcance, metricas_conversiones
            FROM marketing_campanas
            ORDER BY fecha_inicio DESC
        """)
        campanas = cursor.fetchall()
        conn.close()
        
        return jsonify([dict(campana) for campana in campanas]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp_marketing.route("/api/campanas", methods=["POST"])
@login_required
def api_create_campana():
    """
    POST: Crea una nueva campaña publicitaria.
    """
    try:
        data = request.get_json()
        
        # Validaciones
        if not data.get("nombre_campana"):
            return jsonify({"error": "El nombre de la campaña es requerido"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO marketing_campanas 
            (nombre_campana, descripcion, fecha_inicio, fecha_fin, presupuesto, estado, objetivo, canal)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("nombre_campana"),
            data.get("descripcion", ""),
            data.get("fecha_inicio"),
            data.get("fecha_fin"),
            data.get("presupuesto", 0.0),
            data.get("estado", "Activa"),
            data.get("objetivo", ""),
            data.get("canal", "")
        ))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        
        return jsonify({"message": "Campaña creada exitosamente", "id": new_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp_marketing.route("/api/campanas/<int:campana_id>", methods=["PUT"])
@login_required
def api_update_campana(campana_id):
    """
    PUT: Actualiza el estado de una campaña.
    """
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE marketing_campanas
            SET estado = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (data.get("estado"), campana_id))
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Campaña actualizada exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =============================================================================
# API - PROSPECTOS / CRM DE LEADS (CRUD)
# =============================================================================

@bp_marketing.route("/api/prospectos", methods=["GET"])
@login_required
def api_get_prospectos():
    """
    GET: Obtiene todos los prospectos (leads).
    Soporta filtros por query params: ?estado=Nuevo&origen=Web
    """
    try:
        estado = request.args.get("estado")
        origen = request.args.get("origen")

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT id, nombre_empresa, nombre_contacto, telefono_contacto,
                   correo_contacto, origen, interes_servicio, estado, notas,
                   fecha_registro, fecha_contacto, valor_estimado
            FROM marketing_prospectos
            WHERE 1=1
        """
        params = []

        if estado:
            query += " AND estado = ?"
            params.append(estado)

        if origen:
            query += " AND origen = ?"
            params.append(origen)

        query += " ORDER BY fecha_registro DESC"

        cursor.execute(query, params)
        prospectos = cursor.fetchall()
        conn.close()

        return jsonify([dict(p) for p in prospectos]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp_marketing.route("/api/prospectos", methods=["POST"])
@login_required
def api_create_prospecto():
    """
    POST: Registra un nuevo prospecto (lead de empresa).
    """
    try:
        data = request.get_json()

        # Validaciones
        if not data.get("nombre_empresa"):
            return jsonify({"error": "El nombre de la empresa es requerido"}), 400
        if not data.get("nombre_contacto"):
            return jsonify({"error": "El nombre del contacto es requerido"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO marketing_prospectos
            (nombre_empresa, nombre_contacto, telefono_contacto, correo_contacto,
             origen, interes_servicio, estado, notas, valor_estimado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("nombre_empresa"),
            data.get("nombre_contacto"),
            data.get("telefono_contacto", ""),
            data.get("correo_contacto", ""),
            data.get("origen", "Web"),
            data.get("interes_servicio", ""),
            data.get("estado", "Nuevo"),
            data.get("notas", ""),
            data.get("valor_estimado", 0.0)
        ))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()

        return jsonify({"message": "Prospecto registrado exitosamente", "id": new_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp_marketing.route("/api/prospectos/<int:prospecto_id>", methods=["PUT"])
@login_required
def api_update_prospecto(prospecto_id):
    """
    PUT: Actualiza el estado o información de un prospecto.
    """
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Construir UPDATE dinámico
        campos = []
        valores = []
        
        if "estado" in data:
            campos.append("estado = ?")
            valores.append(data["estado"])
            
            # Si el estado cambia a Contactado, guardar fecha
            if data["estado"] == "Contactado":
                campos.append("fecha_contacto = ?")
                valores.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            # Si el estado cambia a Convertido, guardar fecha
            if data["estado"] == "Convertido":
                campos.append("fecha_conversion = ?")
                valores.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        if "notas" in data:
            campos.append("notas = ?")
            valores.append(data["notas"])
        
        campos.append("updated_at = CURRENT_TIMESTAMP")
        valores.append(prospecto_id)
        
        query = f"UPDATE marketing_prospectos SET {', '.join(campos)} WHERE id = ?"
        cursor.execute(query, valores)
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Prospecto actualizado exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp_marketing.route("/api/prospectos/<int:prospecto_id>", methods=["DELETE"])
@login_required
def api_delete_prospecto(prospecto_id):
    """
    DELETE: Elimina un prospecto.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM marketing_prospectos WHERE id = ?", (prospecto_id,))
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Prospecto eliminado exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =============================================================================
# API - ESTADÍSTICAS Y DASHBOARD
# =============================================================================

@bp_marketing.route("/api/stats", methods=["GET"])
@login_required
def api_get_stats():
    """
    GET: Obtiene estadísticas generales del módulo de marketing.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total de prospectos
        cursor.execute("SELECT COUNT(*) as total FROM marketing_prospectos")
        total_prospectos = cursor.fetchone()["total"]
        
        # Prospectos nuevos hoy
        cursor.execute("""
            SELECT COUNT(*) as nuevos_hoy 
            FROM marketing_prospectos 
            WHERE DATE(fecha_registro) = DATE('now')
        """)
        nuevos_hoy = cursor.fetchone()["nuevos_hoy"]
        
        # Campañas activas
        cursor.execute("""
            SELECT COUNT(*) as activas 
            FROM marketing_campanas 
            WHERE estado = 'Activa'
        """)
        campanas_activas = cursor.fetchone()["activas"]
        
        # Total seguidores en redes
        cursor.execute("SELECT SUM(seguidores) as total_seguidores FROM marketing_redes")
        total_seguidores = cursor.fetchone()["total_seguidores"] or 0
        
        conn.close()
        
        return jsonify({
            "total_prospectos": total_prospectos,
            "nuevos_hoy": nuevos_hoy,
            "campanas_activas": campanas_activas,
            "total_seguidores": total_seguidores
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

