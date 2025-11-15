# -*- coding: utf-8 -*-
"""
unificacion.py - Módulo de Unificación de Usuarios y Empresas
==============================================================
Este módulo maneja la lógica para relacionar usuarios con empresas,
permitiendo asignar y desasignar empresas a usuarios de forma dinámica.

Funcionalidades:
- Listar usuarios con información de empresa asignada
- Listar empresas con conteo de usuarios asignados
- Asignar empresa a usuario
- Desasignar empresa de usuario
- Estadísticas de relaciones

Autor: Sistema Montero
Fecha: Noviembre 2025
"""

import sqlite3
import traceback

from flask import Blueprint, jsonify, request, session

# --- IMPORTAR UTILIDADES Y LOGGER ---
from logger import logger

try:
    from utils import get_db_connection, login_required
except ImportError as e:
    logger.error(f"Error importando utils en unificacion.py: {e}", exc_info=True)

    # Fallbacks básicos
    def get_db_connection():
        return None

    def login_required(f):
        return f


# ==================== DEFINICIÓN DEL BLUEPRINT ====================
bp_unificacion = Blueprint("bp_unificacion", __name__, url_prefix="/api/unificacion")

# ==================== ENDPOINTS DE UNIFICACIÓN ====================


@bp_unificacion.route("/usuarios", methods=["GET"])
@login_required
def get_usuarios_con_empresas():
    """
    Obtiene la lista de todos los usuarios con información de la empresa asignada.

    Returns:
        JSON con lista de usuarios incluyendo:
        - numeroId: Identificador del usuario
        - nombre: Nombre completo del usuario
        - empresa_nit: NIT de la empresa asignada (NULL si no tiene)
        - empresa_nombre: Nombre de la empresa asignada (NULL si no tiene)
    """
    conn = None
    try:
        logger.info("📋 Consultando lista de usuarios con empresas asignadas")
        conn = get_db_connection()

        if not conn:
            logger.error("❌ No se pudo conectar a la base de datos")
            return jsonify({"error": "Error de conexión a la base de datos"}), 500

        cursor = conn.cursor()

        # Query para obtener usuarios con información de empresa
        query = """
        SELECT
            u.numeroId,
            u.nombre,
            u.empresa_nit,
            e.nombre_empresa as empresa_nombre
        FROM usuarios u
        LEFT JOIN empresas e ON u.empresa_nit = e.nit
        ORDER BY
            CASE WHEN u.empresa_nit IS NULL THEN 1 ELSE 0 END,
            u.nombre ASC
        """

        cursor.execute(query)
        usuarios = cursor.fetchall()

        # Convertir a lista de diccionarios
        usuarios_list = []
        for usuario in usuarios:
            usuarios_list.append(
                {"numeroId": usuario[0], "nombre": usuario[1], "empresa_nit": usuario[2], "empresa_nombre": usuario[3]}
            )

        logger.info(f"✅ Se encontraron {len(usuarios_list)} usuarios")
        logger.info(f"   - {len([u for u in usuarios_list if u['empresa_nit']])} con empresa asignada")
        logger.info(f"   - {len([u for u in usuarios_list if not u['empresa_nit']])} sin empresa asignada")

        return jsonify(usuarios_list), 200

    except sqlite3.Error as db_error:
        logger.error(f"❌ Error de base de datos al obtener usuarios: {db_error}", exc_info=True)
        return jsonify({"error": f"Error de base de datos: {str(db_error)}"}), 500
    except Exception as e:
        logger.error(f"❌ Error inesperado al obtener usuarios: {e}", exc_info=True)
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@bp_unificacion.route("/empresas", methods=["GET"])
@login_required
def get_empresas_con_conteo():
    """
    Obtiene la lista de todas las empresas con el conteo de usuarios asignados.

    Returns:
        JSON con lista de empresas incluyendo:
        - nit: NIT de la empresa
        - nombre_empresa: Nombre de la empresa
        - total_usuarios: Cantidad de usuarios asignados a la empresa
    """
    conn = None
    try:
        logger.info("🏢 Consultando lista de empresas con conteo de usuarios")
        conn = get_db_connection()

        if not conn:
            logger.error("❌ No se pudo conectar a la base de datos")
            return jsonify({"error": "Error de conexión a la base de datos"}), 500

        cursor = conn.cursor()

        # Query para obtener empresas con conteo de usuarios
        query = """
        SELECT
            e.nit,
            e.nombre_empresa,
            COUNT(u.id) as total_usuarios
        FROM empresas e
        LEFT JOIN usuarios u ON e.nit = u.empresa_nit
        GROUP BY e.nit, e.nombre_empresa
        ORDER BY e.nombre_empresa ASC
        """

        cursor.execute(query)
        empresas = cursor.fetchall()

        # Convertir a lista de diccionarios
        empresas_list = []
        for empresa in empresas:
            empresas_list.append({"nit": empresa[0], "nombre_empresa": empresa[1], "total_usuarios": empresa[2]})

        logger.info(f"✅ Se encontraron {len(empresas_list)} empresas")
        total_asignaciones = sum([e["total_usuarios"] for e in empresas_list])
        logger.info(f"   - Total de asignaciones: {total_asignaciones}")

        return jsonify(empresas_list), 200

    except sqlite3.Error as db_error:
        logger.error(f"❌ Error de base de datos al obtener empresas: {db_error}", exc_info=True)
        return jsonify({"error": f"Error de base de datos: {str(db_error)}"}), 500
    except Exception as e:
        logger.error(f"❌ Error inesperado al obtener empresas: {e}", exc_info=True)
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@bp_unificacion.route("/asignar", methods=["POST"])
@login_required
def asignar_empresa_a_usuario():
    """
    Asigna una empresa a un usuario específico.

    Request Body (JSON):
        - usuario_id: Número de identificación del usuario
        - empresa_nit: NIT de la empresa a asignar

    Returns:
        JSON con mensaje de éxito o error
    """
    conn = None
    try:
        data = request.get_json()

        if not data:
            logger.warning("⚠️ Request sin datos JSON")
            return jsonify({"error": "Se requieren datos JSON"}), 400

        usuario_id = data.get("usuario_id")
        empresa_nit = data.get("empresa_nit")

        # Validaciones
        if not usuario_id or not empresa_nit:
            logger.warning(f"⚠️ Datos incompletos - Usuario: {usuario_id}, Empresa: {empresa_nit}")
            return jsonify({"error": "Se requieren usuario_id y empresa_nit"}), 400

        logger.info(f"🔗 Intentando asignar empresa {empresa_nit} al usuario {usuario_id}")

        conn = get_db_connection()
        if not conn:
            logger.error("❌ No se pudo conectar a la base de datos")
            return jsonify({"error": "Error de conexión a la base de datos"}), 500

        cursor = conn.cursor()

        # Verificar que el usuario existe
        cursor.execute("SELECT id, nombre FROM usuarios WHERE numeroId = ?", (usuario_id,))
        usuario = cursor.fetchone()

        if not usuario:
            logger.warning(f"⚠️ Usuario no encontrado: {usuario_id}")
            return jsonify({"error": f"Usuario con ID {usuario_id} no encontrado"}), 404

        # Verificar que la empresa existe
        cursor.execute("SELECT nit, nombre_empresa FROM empresas WHERE nit = ?", (empresa_nit,))
        empresa = cursor.fetchone()

        if not empresa:
            logger.warning(f"⚠️ Empresa no encontrada: {empresa_nit}")
            return jsonify({"error": f"Empresa con NIT {empresa_nit} no encontrada"}), 404

        # Actualizar la relación
        cursor.execute("UPDATE usuarios SET empresa_nit = ? WHERE numeroId = ?", (empresa_nit, usuario_id))

        conn.commit()

        usuario_nombre = usuario[1]
        empresa_nombre = empresa[1]

        logger.info(f"✅ Asignación exitosa:")
        logger.info(f"   - Usuario: {usuario_nombre} ({usuario_id})")
        logger.info(f"   - Empresa: {empresa_nombre} ({empresa_nit})")

        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Usuario {usuario_nombre} asignado exitosamente a {empresa_nombre}",
                    "usuario": {"id": usuario_id, "nombre": usuario_nombre},
                    "empresa": {"nit": empresa_nit, "nombre": empresa_nombre},
                }
            ),
            200,
        )

    except sqlite3.Error as db_error:
        if conn:
            conn.rollback()
        logger.error(f"❌ Error de base de datos al asignar empresa: {db_error}", exc_info=True)
        return jsonify({"error": f"Error de base de datos: {str(db_error)}"}), 500
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"❌ Error inesperado al asignar empresa: {e}", exc_info=True)
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@bp_unificacion.route("/desasignar", methods=["POST"])
@login_required
def desasignar_empresa_de_usuario():
    """
    Desasigna la empresa de un usuario específico (establece empresa_nit a NULL).

    Request Body (JSON):
        - usuario_id: Número de identificación del usuario

    Returns:
        JSON con mensaje de éxito o error
    """
    conn = None
    try:
        data = request.get_json()

        if not data:
            logger.warning("⚠️ Request sin datos JSON")
            return jsonify({"error": "Se requieren datos JSON"}), 400

        usuario_id = data.get("usuario_id")

        # Validación
        if not usuario_id:
            logger.warning("⚠️ Falta usuario_id en la solicitud")
            return jsonify({"error": "Se requiere usuario_id"}), 400

        logger.info(f"🔓 Intentando desasignar empresa del usuario {usuario_id}")

        conn = get_db_connection()
        if not conn:
            logger.error("❌ No se pudo conectar a la base de datos")
            return jsonify({"error": "Error de conexión a la base de datos"}), 500

        cursor = conn.cursor()

        # Verificar que el usuario existe y obtener info de empresa actual
        cursor.execute(
            """
            SELECT u.id, u.nombre, u.empresa_nit, e.nombre_empresa
            FROM usuarios u
            LEFT JOIN empresas e ON u.empresa_nit = e.nit
            WHERE u.numeroId = ?
        """,
            (usuario_id,),
        )
        usuario = cursor.fetchone()

        if not usuario:
            logger.warning(f"⚠️ Usuario no encontrado: {usuario_id}")
            return jsonify({"error": f"Usuario con ID {usuario_id} no encontrado"}), 404

        usuario_nombre = usuario[1]
        empresa_nit_actual = usuario[2]
        empresa_nombre_actual = usuario[3]

        if not empresa_nit_actual:
            logger.warning(f"⚠️ Usuario {usuario_id} no tiene empresa asignada")
            return jsonify({"error": f"Usuario {usuario_nombre} no tiene empresa asignada"}), 400

        # Desasignar la empresa (establecer a NULL)
        cursor.execute("UPDATE usuarios SET empresa_nit = NULL WHERE numeroId = ?", (usuario_id,))

        conn.commit()

        logger.info(f"✅ Desasignación exitosa:")
        logger.info(f"   - Usuario: {usuario_nombre} ({usuario_id})")
        logger.info(f"   - Empresa removida: {empresa_nombre_actual} ({empresa_nit_actual})")

        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Empresa {empresa_nombre_actual} desasignada exitosamente de {usuario_nombre}",
                    "usuario": {"id": usuario_id, "nombre": usuario_nombre},
                    "empresa_anterior": {"nit": empresa_nit_actual, "nombre": empresa_nombre_actual},
                }
            ),
            200,
        )

    except sqlite3.Error as db_error:
        if conn:
            conn.rollback()
        logger.error(f"❌ Error de base de datos al desasignar empresa: {db_error}", exc_info=True)
        return jsonify({"error": f"Error de base de datos: {str(db_error)}"}), 500
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"❌ Error inesperado al desasignar empresa: {e}", exc_info=True)
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@bp_unificacion.route("/estadisticas", methods=["GET"])
@login_required
def get_estadisticas():
    """
    Obtiene estadísticas generales de la unificación.

    Returns:
        JSON con estadísticas:
        - total_usuarios: Total de usuarios en el sistema
        - total_empresas: Total de empresas en el sistema
        - usuarios_asignados: Usuarios con empresa asignada
        - usuarios_sin_asignar: Usuarios sin empresa asignada
        - empresas_con_usuarios: Empresas que tienen al menos un usuario
        - empresas_sin_usuarios: Empresas sin usuarios asignados
    """
    conn = None
    try:
        logger.info("📊 Consultando estadísticas de unificación")
        conn = get_db_connection()

        if not conn:
            logger.error("❌ No se pudo conectar a la base de datos")
            return jsonify({"error": "Error de conexión a la base de datos"}), 500

        cursor = conn.cursor()

        # Estadísticas de usuarios
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        total_usuarios = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE empresa_nit IS NOT NULL")
        usuarios_asignados = cursor.fetchone()[0]

        usuarios_sin_asignar = total_usuarios - usuarios_asignados

        # Estadísticas de empresas
        cursor.execute("SELECT COUNT(*) FROM empresas")
        total_empresas = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(DISTINCT e.nit)
            FROM empresas e
            INNER JOIN usuarios u ON e.nit = u.empresa_nit
        """
        )
        empresas_con_usuarios = cursor.fetchone()[0]

        empresas_sin_usuarios = total_empresas - empresas_con_usuarios

        estadisticas = {
            "total_usuarios": total_usuarios,
            "total_empresas": total_empresas,
            "usuarios_asignados": usuarios_asignados,
            "usuarios_sin_asignar": usuarios_sin_asignar,
            "empresas_con_usuarios": empresas_con_usuarios,
            "empresas_sin_usuarios": empresas_sin_usuarios,
            "porcentaje_asignacion": round((usuarios_asignados / total_usuarios * 100) if total_usuarios > 0 else 0, 2),
        }

        logger.info("✅ Estadísticas obtenidas:")
        logger.info(
            f"   - Total usuarios: {total_usuarios} ({usuarios_asignados} asignados, {usuarios_sin_asignar} sin asignar)"
        )
        logger.info(
            f"   - Total empresas: {total_empresas} ({empresas_con_usuarios} con usuarios, {empresas_sin_usuarios} sin usuarios)"
        )
        logger.info(f"   - Porcentaje de asignación: {estadisticas['porcentaje_asignacion']}%")

        return jsonify(estadisticas), 200

    except sqlite3.Error as db_error:
        logger.error(f"❌ Error de base de datos al obtener estadísticas: {db_error}", exc_info=True)
        return jsonify({"error": f"Error de base de datos: {str(db_error)}"}), 500
    except Exception as e:
        logger.error(f"❌ Error inesperado al obtener estadísticas: {e}", exc_info=True)
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


# ==================== FUNCIONES DE UTILIDAD ====================


def validar_relacion_usuario_empresa(usuario_id, empresa_nit):
    """
    Valida que una relación usuario-empresa sea válida antes de aplicarla.

    Args:
        usuario_id: ID del usuario
        empresa_nit: NIT de la empresa

    Returns:
        tuple: (es_valido: bool, mensaje_error: str)
    """
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return False, "Error de conexión a la base de datos"

        cursor = conn.cursor()

        # Verificar usuario
        cursor.execute("SELECT id FROM usuarios WHERE numeroId = ?", (usuario_id,))
        if not cursor.fetchone():
            return False, f"Usuario {usuario_id} no existe"

        # Verificar empresa
        cursor.execute("SELECT nit FROM empresas WHERE nit = ?", (empresa_nit,))
        if not cursor.fetchone():
            return False, f"Empresa con NIT {empresa_nit} no existe"

        return True, ""

    except Exception as e:
        logger.error(f"Error en validación: {e}")
        return False, f"Error en validación: {str(e)}"
    finally:
        if conn:
            conn.close()


def get_relaciones_activas():
    """
    Obtiene todas las relaciones activas usuario-empresa.

    Returns:
        list: Lista de diccionarios con las relaciones activas
    """
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                u.numeroId,
                u.nombre,
                e.nit,
                e.nombre_empresa,
                u.created_at
            FROM usuarios u
            INNER JOIN empresas e ON u.empresa_nit = e.nit
            ORDER BY u.created_at DESC
        """
        )

        relaciones = []
        for row in cursor.fetchall():
            relaciones.append(
                {
                    "usuario_id": row[0],
                    "usuario_nombre": row[1],
                    "empresa_nit": row[2],
                    "empresa_nombre": row[3],
                    "fecha_asignacion": row[4],
                }
            )

        return relaciones

    except Exception as e:
        logger.error(f"Error obteniendo relaciones activas: {e}")
        return []
    finally:
        if conn:
            conn.close()


# ==================== INFORMACIÓN DEL MÓDULO ====================


def get_module_info():
    """
    Retorna información sobre el módulo de unificación.

    Returns:
        dict: Información del módulo
    """
    return {
        "nombre": "Módulo de Unificación",
        "version": "1.0.0",
        "descripcion": "Gestión de relaciones entre usuarios y empresas",
        "endpoints": [
            {
                "ruta": "/api/unificacion/usuarios",
                "metodo": "GET",
                "descripcion": "Obtiene lista de usuarios con empresas asignadas",
            },
            {
                "ruta": "/api/unificacion/empresas",
                "metodo": "GET",
                "descripcion": "Obtiene lista de empresas con conteo de usuarios",
            },
            {"ruta": "/api/unificacion/asignar", "metodo": "POST", "descripcion": "Asigna una empresa a un usuario"},
            {"ruta": "/api/unificacion/desasignar", "metodo": "POST", "descripcion": "Desasigna la empresa de un usuario"},
            {
                "ruta": "/api/unificacion/estadisticas",
                "metodo": "GET",
                "descripcion": "Obtiene estadísticas de la unificación",
            },
        ],
        "autor": "Sistema Montero",
        "fecha_creacion": "Noviembre 2025",
    }


if __name__ == "__main__":
    # Información del módulo cuando se ejecuta directamente
    info = get_module_info()
    print("=" * 70)
    print(f"📦 {info['nombre']} v{info['version']}")
    print("=" * 70)
    print(f"📝 {info['descripcion']}")
    print(f"\n🔗 Endpoints disponibles:")
    for endpoint in info["endpoints"]:
        print(f"   • [{endpoint['metodo']}] {endpoint['ruta']}")
        print(f"     {endpoint['descripcion']}")
    print("\n" + "=" * 70)
