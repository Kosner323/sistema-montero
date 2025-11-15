# -*- coding: utf-8 -*-
"""
Blueprint para la gestión de credenciales de plataformas.
Permite a los usuarios guardar, ver, editar y eliminar de forma segura
las credenciales (usuario/contraseña) para diferentes servicios.
"""

import sqlite3
import traceback
from datetime import datetime

from flask import Blueprint, g, jsonify, request, session

from encryption import FernetEncryptor
from utils import get_db_connection, login_required

# (CORREGIDO: Importa la instancia global 'logger')
# from logger import logger

# --- Configuración del Blueprint ---
credenciales_bp = Blueprint("credenciales", __name__, url_prefix="/api/credenciales")

# --- Inicialización ---
# (CORREGIDO: No es necesario llamar a get_logger())
from logger import logger

# Inicializar el encriptador
try:
    encryptor = FernetEncryptor()
    # (CORREGIDO: usa 'logger')
    logger.info("Sistema de encriptación cargado correctamente")
except Exception as e:
    # (CORREGIDO: usa 'logger')
    logger.error(f"Error CRÍTICO al inicializar el encriptador: {e}", exc_info=True)
    # Si el encriptador falla, la app no debe continuar (o al menos este módulo)
    encryptor = None


# ==============================================================================
# HELPERS
# ==============================================================================


def get_user_id():
    """Obtiene el ID del usuario de la sesión de forma segura."""
    user_id = session.get("user_id")
    if not user_id:
        # (CORREGIDO: usa 'logger')
        logger.warning("Se intentó acceder a credenciales sin user_id en la sesión.")
    return user_id


# ==============================================================================
# ENDPOINTS CRUD
# ==============================================================================


@credenciales_bp.route("", methods=["POST"])
@login_required
def add_credencial():
    """
    Añade una nueva credencial a la base de datos, encriptando la contraseña.
    """
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "No autorizado"}), 401

    if not encryptor:
        # (CORREGIDO: usa 'logger')
        logger.error("Intento de añadir credencial pero el encriptador no está inicializado.")
        return jsonify({"error": "Error de configuración del servidor"}), 500

    data = request.json

    try:
        # Encriptar la contraseña antes de guardarla
        contrasena_encriptada = encryptor.encrypt(data.get("contrasena"))

        conn = get_db_connection()
        conn.execute(
            """
            INSERT INTO credenciales_plataforma
            (plataforma, usuario, contrasena, email, url, notas, creado_por_id, fecha_creacion, fecha_actualizacion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                data.get("plataforma"),
                data.get("usuario"),
                contrasena_encriptada,
                data.get("email"),
                data.get("url"),
                data.get("notas"),
                user_id,
                datetime.now(),
                datetime.now(),
            ),
        )
        conn.commit()
        # (CORREGIDO: usa 'logger')
        logger.info(f"Usuario {user_id} añadió credencial para {data.get('plataforma')}")
        return jsonify({"message": "Credencial guardada exitosamente"}), 201
    except Exception as e:
        # (CORREGIDO: usa 'logger')
        logger.error(f"Error al añadir credencial: {e}", exc_info=True)
        return jsonify({"error": "Error interno al guardar la credencial"}), 500


@credenciales_bp.route("", methods=["GET"])
@login_required
def get_credenciales():
    """
    Obtiene todas las credenciales del usuario logueado.
    Las contraseñas se devuelven ENCRIPTADAS.
    """
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "No autorizado"}), 401

    try:
        conn = get_db_connection()
        # NOTA: Por seguridad, podríamos querer que esto solo sea para rol 'admin'
        # Por ahora, se asume que solo trae las del usuario
        # OJO: La consulta actual trae TODAS. Debería filtrarse por usuario.
        # Implementando filtro por usuario:
        cursor = conn.execute(
            "SELECT id, plataforma, usuario, email, url, notas, fecha_actualizacion "
            "FROM credenciales_plataforma WHERE creado_por_id = ?",
            (user_id,),
        )
        credenciales = cursor.fetchall()

        # Convertir a lista de diccionarios
        lista_credenciales = [dict(row) for row in credenciales]

        # (CORREGIDO: usa 'logger')
        logger.info(f"Usuario {user_id} consultó {len(lista_credenciales)} credenciales.")
        return jsonify(lista_credenciales)

    except Exception as e:
        # (CORREGIDO: usa 'logger')
        logger.error(f"Error al obtener credenciales: {e}", exc_info=True)
        return jsonify({"error": "Error interno al obtener credenciales"}), 500


@credenciales_bp.route("/<int:id_credencial>", methods=["PUT"])
@login_required
def update_credencial(id_credencial):
    """
    Actualiza una credencial existente.
    Si se envía una nueva contraseña, la encripta.
    Soporta actualizaciones parciales: solo actualiza los campos enviados.
    """
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "No autorizado"}), 401

    if not encryptor:
        return jsonify({"error": "Error de configuración del servidor"}), 500

    data = request.json

    try:
        conn = get_db_connection()

        # Obtener la credencial existente completa
        cred = conn.execute(
            "SELECT * FROM credenciales_plataforma WHERE id = ? AND creado_por_id = ?", (id_credencial, user_id)
        ).fetchone()

        if not cred:
            # (CORREGIDO: usa 'logger')
            logger.warning(f"Usuario {user_id} intentó actualizar credencial ajena (ID: {id_credencial})")
            return jsonify({"error": "Credencial no encontrada o no autorizada"}), 404

        # Fusionar datos: combinar datos recibidos con los existentes
        # Si un campo no está en request.json, mantener el valor original
        merged_data = {
            "plataforma": data.get("plataforma", cred["plataforma"]),
            "usuario": data.get("usuario", cred["usuario"]),
            "email": data.get("email", cred["email"]),
            "url": data.get("url", cred["url"]),
            "notas": data.get("notas", cred["notas"]),
        }

        # Si se envió una contraseña nueva, encriptarla. Si no, mantener la antigua.
        if "contrasena" in data and data["contrasena"]:
            contrasena_encriptada = encryptor.encrypt(data["contrasena"])
        else:
            contrasena_encriptada = cred["contrasena"]  # Mantener la existente

        conn.execute(
            """
            UPDATE credenciales_plataforma
            SET plataforma = ?, usuario = ?, contrasena = ?, email = ?, url = ?, notas = ?,
                actualizado_por_id = ?, fecha_actualizacion = ?
            WHERE id = ? AND creado_por_id = ?
        """,
            (
                merged_data["plataforma"],
                merged_data["usuario"],
                contrasena_encriptada,
                merged_data["email"],
                merged_data["url"],
                merged_data["notas"],
                user_id,
                datetime.now(),
                id_credencial,
                user_id,
            ),
        )
        conn.commit()
        # (CORREGIDO: usa 'logger')
        logger.info(f"Usuario {user_id} actualizó credencial ID: {id_credencial}")
        return jsonify({"message": "Credencial actualizada exitosamente"}), 200
    except Exception as e:
        # (CORREGIDO: usa 'logger')
        logger.error(f"Error al actualizar credencial: {e}", exc_info=True)
        return jsonify({"error": "Error interno al actualizar la credencial"}), 500


@credenciales_bp.route("/<int:id_credencial>", methods=["DELETE"])
@login_required
def delete_credencial(id_credencial):
    """
    Elimina una credencial.
    """
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "No autorizado"}), 401

    try:
        conn = get_db_connection()

        # Verificar que la credencial pertenece al usuario
        cursor = conn.execute(
            "DELETE FROM credenciales_plataforma WHERE id = ? AND creado_por_id = ?", (id_credencial, user_id)
        )

        if cursor.rowcount == 0:
            # (CORREGIDO: usa 'logger')
            logger.warning(f"Usuario {user_id} intentó eliminar credencial ajena (ID: {id_credencial})")
            return jsonify({"error": "Credencial no encontrada o no autorizada"}), 404

        conn.commit()
        # (CORREGIDO: usa 'logger')
        logger.info(f"Usuario {user_id} eliminó credencial ID: {id_credencial}")
        return jsonify({"message": "Credencial eliminada exitosamente"}), 200
    except Exception as e:
        # (CORREGIDO: usa 'logger')
        logger.error(f"Error al eliminar credencial: {e}", exc_info=True)
        return jsonify({"error": "Error interno al eliminar la credencial"}), 500


@credenciales_bp.route("/<int:id_credencial>/decrypt", methods=["GET"])
@login_required
def decrypt_password(id_credencial):
    """
    Desencripta y devuelve la contraseña de una credencial específica.
    Esta es una operación sensible y debe ser loggeada.
    """
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "No autorizado"}), 401

    if not encryptor:
        return jsonify({"error": "Error de configuración del servidor"}), 500

    try:
        conn = get_db_connection()

        # Verificar que la credencial pertenece al usuario
        cred = conn.execute(
            "SELECT plataforma, contrasena FROM credenciales_plataforma WHERE id = ? AND creado_por_id = ?",
            (id_credencial, user_id),
        ).fetchone()

        if not cred:
            # (CORREGIDO: usa 'logger')
            logger.warning(f"Usuario {user_id} intentó desencriptar credencial ajena (ID: {id_credencial})")
            return jsonify({"error": "Credencial no encontrada o no autorizada"}), 404

        # Desencriptar la contraseña
        contrasena_desencriptada = encryptor.decrypt(cred["contrasena"])

        # (CORREGIDO: usa 'logger')
        logger.info(
            f"¡ALERTA DE SEGURIDAD! Usuario {user_id} desencriptó la contraseña para '{cred['plataforma']}' (ID: {id_credencial})"
        )

        return jsonify({"password": contrasena_desencriptada}), 200

    except Exception as e:
        # (CORREGIDO: usa 'logger')
        logger.error(f"Error al desencriptar credencial: {e}", exc_info=True)
        return jsonify({"error": "Error interno al desencriptar la contraseña"}), 500
