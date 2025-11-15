# -*- coding: utf-8 -*-
"""
Blueprint para la gestión de Empresas.
Permite el CRUD (Crear, Leer, Actualizar, Eliminar) de las entidades de empresa
en el sistema.
"""

import sqlite3
import traceback

from flask import Blueprint, current_app, g, jsonify, request, session
from pydantic import ValidationError

# (CORREGIDO: Importa la instancia global 'logger')
from logger import logger
from models.validation_models import EmpresaCreate, EmpresaUpdate
from utils import get_db_connection, login_required

# --- Configuración del Blueprint ---
# (CORREGIDO: No es necesario llamar a get_logger())
# logger = get_logger(__name__)

# El nombre del blueprint SÍ ES 'empresas_bp'
empresas_bp = Blueprint("empresas", __name__, url_prefix="/api/empresas")

# ==============================================================================
# ENDPOINTS CRUD
# ==============================================================================


@empresas_bp.route("", methods=["POST"])
@login_required
def add_empresa():
    """
    Crea una nueva empresa en la base de datos.
    Valida los datos de entrada usando Pydantic.
    """
    try:
        data = EmpresaCreate(**request.json)
    except ValidationError as e:
        # (CORREGIDO: usa 'logger')
        logger.warning(f"Validación fallida al crear empresa: {e.errors()}", extra={"data": request.json})
        # Solución: Serializar solo los mensajes de error
        error_details = [err["msg"] for err in e.errors()]
        return jsonify({"error": "Datos inválidos", "details": error_details}), 422
    except Exception as e:
        # (CORREGIDO: usa 'logger')
        logger.error(f"Error al parsear JSON de empresa: {e}", extra={"raw_data": request.data})
        return jsonify({"error": "Formato de solicitud inválido."}), 400

    from flask import g

    conn = None
    try:
        conn = g.db

        # Verificar si el NIT ya existe
        existe = conn.execute("SELECT id FROM empresas WHERE nit = ?", (data.nit,)).fetchone()

        if existe:
            # (CORREGIDO: usa 'logger')
            logger.warning(f"Intento de crear empresa con NIT duplicado: {data.nit}")
            return jsonify({"error": f"El NIT {data.nit} ya está registrado."}), 409  # 409 Conflict

        # Insertar la nueva empresa
        # Mapear campos del modelo Pydantic a campos de la BD
        cursor = conn.execute(
            """
            INSERT INTO empresas (
                nombre_empresa, nit, direccion_empresa,
                telefono_empresa, correo_empresa, ciudad_empresa,
                rep_legal_nombre
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (data.nombre_empresa, data.nit, data.direccion, data.telefono, data.email, data.ciudad, data.representante_legal),
        )
        conn.commit()

        nueva_empresa_id = cursor.lastrowid
        # (CORREGIDO: usa 'logger')
        logger.info(
            f"Nueva empresa creada: {data.nombre_empresa} (ID: {nueva_empresa_id}) por usuario {session.get('user_id')}"
        )

        return jsonify({"message": "Empresa creada exitosamente.", "id": nueva_empresa_id, "nit": data.nit}), 201

    except sqlite3.IntegrityError as e:
        # (CORREGIDO: usa 'logger')
        logger.error(f"Error de integridad al crear empresa (NIT duplicado?): {data.nit} - {e}", exc_info=True)
        return jsonify({"error": f"El NIT {data.nit} ya existe."}), 409
    except Exception as e:
        # (CORREGIDO: usa 'logger')
        logger.critical(f"Error inesperado al crear empresa: {e}", exc_info=True)
        if conn:
            conn.rollback()
        return jsonify({"error": "Error interno del servidor."}), 500


@empresas_bp.route("", methods=["GET"])
@login_required
def get_empresas():
    """
    Obtiene una lista paginada de todas las empresas.
    Acepta parámetros de query para paginación, búsqueda y orden.
    """
    # Parámetros de consulta
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    search_term = request.args.get("search", "", type=str)
    sort_by = request.args.get("sort_by", "nombre_empresa", type=str)
    sort_order = request.args.get("sort_order", "asc", type=str)

    # Validar parámetros de orden
    allowed_sort_by = ["nombre_empresa", "nit", "ciudad_empresa", "fecha_registro"]
    if sort_by not in allowed_sort_by:
        sort_by = "nombre_empresa"
    if sort_order.lower() not in ["asc", "desc"]:
        sort_order = "asc"

    offset = (page - 1) * per_page

    from flask import g

    conn = None
    try:
        conn = g.db

        # Construcción de la consulta
        base_query = "FROM empresas"
        count_query = "SELECT COUNT(id) "
        data_query = "SELECT * "

        where_clause = ""
        params = []

        if search_term:
            where_clause = "WHERE nombre_empresa LIKE ? OR nit LIKE ?"
            params.extend([f"%{search_term}%", f"%{search_term}%"])

        # Obtener conteo total
        total_rows_result = conn.execute(count_query + base_query + where_clause, params).fetchone()
        total_rows = total_rows_result[0] if total_rows_result else 0
        total_pages = (total_rows + per_page - 1) // per_page

        # Obtener datos paginados
        query = f"{data_query} {base_query} {where_clause} ORDER BY {sort_by} {sort_order} LIMIT ? OFFSET ?"
        params.extend([per_page, offset])

        empresas = conn.execute(query, params).fetchall()

        return jsonify(
            {
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages,
                "total_items": total_rows,
                "items": [dict(row) for row in empresas],
            }
        )

    except Exception as e:
        # (CORREGIDO: usa 'logger')
        logger.error(f"Error al obtener lista de empresas: {e}", exc_info=True)
        return jsonify({"error": "Error interno del servidor."}), 500


@empresas_bp.route("/<string:nit>", methods=["GET"])
@login_required
def get_empresa_by_nit(nit):
    """
    Obtiene los detalles de una empresa específica por su NIT.
    """
    from flask import g

    conn = None
    try:
        conn = g.db
        empresa = conn.execute("SELECT * FROM empresas WHERE nit = ?", (nit,)).fetchone()

        if empresa:
            return jsonify(dict(empresa))
        else:
            # (CORREGIDO: usa 'logger')
            logger.warning(f"Empresa no encontrada con NIT: {nit}")
            return jsonify({"error": "Empresa no encontrada"}), 404

    except Exception as e:
        # (CORREGIDO: usa 'logger')
        logger.error(f"Error al obtener empresa por NIT {nit}: {e}", exc_info=True)
        return jsonify({"error": "Error interno del servidor."}), 500


@empresas_bp.route("/<string:nit>", methods=["PUT"])
@login_required
def update_empresa(nit):
    """
    Actualiza los datos de una empresa existente.
    """
    try:
        data = EmpresaUpdate(**request.json)
    except ValidationError as e:
        # (CORREGIDO: usa 'logger')
        logger.warning(f"Validación fallida al actualizar empresa {nit}: {e.errors()}", extra={"data": request.json})
        # Solución: Serializar solo los mensajes de error
        error_details = [err["msg"] for err in e.errors()]
        return jsonify({"error": "Datos inválidos", "details": error_details}), 422

    from flask import g

    conn = None
    try:
        conn = g.db

        # Verificar que la empresa exista
        empresa_existente = conn.execute("SELECT id FROM empresas WHERE nit = ?", (nit,)).fetchone()

        if not empresa_existente:
            # (CORREGIDO: usa 'logger')
            logger.warning(f"Intento de actualizar empresa no existente. NIT: {nit}")
            return jsonify({"error": "Empresa no encontrada"}), 404

        # Verificar si el nuevo NIT ya está en uso por OTRA empresa
        if data.nit and data.nit != nit:
            nit_duplicado = conn.execute("SELECT id FROM empresas WHERE nit = ?", (data.nit,)).fetchone()
            if nit_duplicado:
                # (CORREGIDO: usa 'logger')
                logger.warning(f"Conflicto de NIT al actualizar. Nuevo NIT {data.nit} ya existe.")
                return jsonify({"error": f"El nuevo NIT {data.nit} ya está en uso."}), 409

        # Actualizar la empresa solo con campos proporcionados
        # Construir la consulta dinámicamente solo con campos no None
        update_fields = []
        update_values = []

        if data.nombre_empresa is not None:
            update_fields.append("nombre_empresa = ?")
            update_values.append(data.nombre_empresa)
        if data.nit is not None:
            update_fields.append("nit = ?")
            update_values.append(data.nit)
        if data.direccion is not None:
            update_fields.append("direccion_empresa = ?")
            update_values.append(data.direccion)
        if data.telefono is not None:
            update_fields.append("telefono_empresa = ?")
            update_values.append(data.telefono)
        if data.email is not None:
            update_fields.append("correo_empresa = ?")
            update_values.append(data.email)
        if data.ciudad is not None:
            update_fields.append("ciudad_empresa = ?")
            update_values.append(data.ciudad)
        if data.representante_legal is not None:
            update_fields.append("rep_legal_nombre = ?")
            update_values.append(data.representante_legal)

        if not update_fields:
            return jsonify({"error": "No se proporcionaron campos para actualizar"}), 400

        update_values.append(nit)  # Agregar NIT para la cláusula WHERE

        query = f"UPDATE empresas SET {', '.join(update_fields)} WHERE nit = ?"
        conn.execute(query, tuple(update_values))
        conn.commit()

        # (CORREGIDO: usa 'logger')
        logger.info(f"Empresa actualizada: {data.nombre_empresa} (NIT: {nit}) por usuario {session.get('user_id')}")

        return jsonify({"message": "Empresa actualizada exitosamente.", "nit": data.nit})

    except Exception as e:
        # (CORREGIDO: usa 'logger')
        logger.critical(f"Error inesperado al actualizar empresa {nit}: {e}", exc_info=True)
        if conn:
            conn.rollback()
        return jsonify({"error": "Error interno del servidor."}), 500


@empresas_bp.route("/<string:nit>", methods=["DELETE"])
@login_required
def delete_empresa(nit):
    """
    Elimina una empresa por su NIT.
    TODO: Añadir lógica para verificar dependencias (usuarios asociados, etc.)
    """
    from flask import g

    conn = None
    try:
        conn = g.db

        # Verificar si la empresa tiene usuarios asociados
        usuarios_asociados = conn.execute("SELECT COUNT(id) FROM usuarios WHERE empresa_nit = ?", (nit,)).fetchone()[0]

        if usuarios_asociados > 0:
            # (CORREGIDO: usa 'logger')
            logger.warning(f"Intento de eliminar empresa {nit} que tiene {usuarios_asociados} usuarios asociados.")
            return (
                jsonify(
                    {
                        "error": f"No se puede eliminar la empresa. Primero reasigne o elimine a los {usuarios_asociados} usuarios asociados."
                    }
                ),
                409,
            )  # Conflicto

        # Eliminar la empresa
        cursor = conn.execute("DELETE FROM empresas WHERE nit = ?", (nit,))

        if cursor.rowcount == 0:
            # (CORREGIDO: usa 'logger')
            logger.warning(f"Intento de eliminar empresa no existente. NIT: {nit}")
            return jsonify({"error": "Empresa no encontrada"}), 404

        conn.commit()
        # (CORREGIDO: usa 'logger')
        logger.info(f"Empresa eliminada (NIT: {nit}) por usuario {session.get('user_id')}")
        return jsonify({"message": "Empresa eliminada exitosamente."})

    except sqlite3.IntegrityError as e:
        # (CORREGIDO: usa 'logger')
        logger.error(f"Error de integridad al eliminar empresa {nit}: {e}", exc_info=True)
        return (
            jsonify({"error": "No se puede eliminar la empresa, tiene registros asociados (pagos, formularios, etc.)."}),
            409,
        )
    except Exception as e:
        # (CORREGIDO: usa 'logger')
        logger.critical(f"Error inesperado al eliminar empresa {nit}: {e}", exc_info=True)
        if conn:
            conn.rollback()
        return jsonify({"error": "Error interno del servidor."}), 500
