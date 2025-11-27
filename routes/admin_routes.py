# -*- coding: utf-8 -*-
"""
admin_routes.py - Módulo de Administración (Gestor de Archivos y Auditoría)
==============================================================================
Gestión de documentos centralizados y registro de auditoría del sistema
"""
import os
import sqlite3
import traceback
import hashlib
import mimetypes
from datetime import datetime
from werkzeug.utils import secure_filename

from flask import (
    Blueprint,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
)

from logger import logger

# --- IMPORTACIÓN CENTRALIZADA ---
#from extensions import db, mail
try:
    from ..models.orm_models import Usuario, Empresa, Pago, Incapacidad, Tutela, Cotizacion
    from ..utils import get_db_connection, login_required, USER_DATA_FOLDER
except (ImportError, ValueError):
    from models.orm_models import Usuario, Empresa, Pago, Incapacidad, Tutela, Cotizacion
    from utils import get_db_connection, login_required, USER_DATA_FOLDER
# -------------------------------


# ==================== CONFIGURACIÓN DE ARCHIVOS ====================
# Nota: UPLOAD_FOLDER ahora se obtiene de app.config (configuración centralizada)
# La carpeta específica para documentos del gestor es: app.config['UPLOAD_FOLDER']/docs

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB (legacy, usar app.config['MAX_CONTENT_LENGTH'])


def allowed_file(filename):
    """Verifica si la extensión del archivo está permitida"""
    from flask import current_app
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx', 'xls', 'xlsx', 'txt'})
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def get_file_hash(file_content):
    """Genera un hash SHA256 del contenido del archivo"""
    return hashlib.sha256(file_content).hexdigest()


# ==================== DEFINICIÓN DEL BLUEPRINT ====================
admin_bp = Blueprint("admin", __name__)


# ==================== FUNCIÓN HELPER: REGISTRAR LOG ====================
def registrar_log(
    accion, detalle="", resultado="exito", usuario_id=None, usuario_nombre=None
):
    """
    Función helper para registrar actividad en auditoría.
    Puede ser importada y usada desde otros módulos.

    Args:
        accion (str): Tipo de acción (ej: "Login", "Subir Archivo", "Eliminar Usuario")
        detalle (str): Información adicional
        resultado (str): 'exito', 'error', 'advertencia'
        usuario_id (int): ID del usuario (opcional, se toma de session si no se provee)
        usuario_nombre (str): Nombre del usuario (opcional)
    """
    conn = None
    try:
        # Obtener datos de sesión si no se proporcionan
        if usuario_id is None:
            usuario_id = session.get("user_id")

        if usuario_nombre is None:
            usuario_nombre = session.get("user_name", "Sistema")

        # Obtener contexto de la petición
        ip_address = request.remote_addr if request else None
        user_agent = request.headers.get("User-Agent", "")[:200] if request else ""
        metodo_http = request.method if request else ""
        ruta = request.path if request else ""

        conn = get_db_connection()
        conn.execute(
            """
            INSERT INTO auditoria_logs (
                usuario_id, usuario_nombre, accion, detalle, resultado,
                ip_address, user_agent, metodo_http, ruta
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                usuario_id,
                usuario_nombre,
                accion,
                detalle,
                resultado,
                ip_address,
                user_agent,
                metodo_http,
                ruta,
            ),
        )
        conn.commit()
        logger.debug(f"Log de auditoría registrado: {accion} - {resultado}")

    except Exception as e:
        logger.error(f"Error al registrar log de auditoría: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()


# ==================== RUTAS DE VISTAS ====================


@admin_bp.route("/gestor-archivos")
@login_required
def gestor_archivos():
    """Página del gestor de archivos centralizado"""
    logger.debug(f"Usuario {session.get('user_id')} accediendo a gestor de archivos")
    return render_template("archivos/gestor.html", user=session.get("user"))


@admin_bp.route("/auditoria")
@login_required
def auditoria():
    """Página de auditoría de logs del sistema"""
    # Verificar si el usuario es admin (recomendado)
    if session.get("role") != "admin":
        logger.warning(
            f"Usuario no admin {session.get('user_id')} intentó acceder a auditoría"
        )
        registrar_log(
            "Acceso Denegado a Auditoría",
            f"Usuario sin permisos intentó acceder",
            resultado="advertencia",
        )
        return redirect("/dashboard")

    logger.debug(f"Admin {session.get('user_id')} accediendo a auditoría")
    return render_template("auditoria/logs.html", user=session.get("user"))


# ==================== RUTAS API: GESTOR DE ARCHIVOS ====================


@admin_bp.route("/api/archivos", methods=["GET"])
@login_required
def get_archivos():
    """Obtiene la lista de archivos del gestor"""
    conn = None
    try:
        categoria = request.args.get("categoria", "todos")

        conn = get_db_connection()
        query = """
            SELECT
                id, nombre_archivo, nombre_interno, ruta, categoria,
                tipo_mime, tamano_bytes, fecha_subida,
                subido_por, subido_por_nombre, descripcion
            FROM documentos_gestor
        """
        params = []

        if categoria and categoria != "todos":
            query += " WHERE categoria = ?"
            params.append(categoria)

        query += " ORDER BY fecha_subida DESC"

        archivos = conn.execute(query, tuple(params)).fetchall()
        logger.debug(f"Consultados {len(archivos)} archivos del gestor")

        return jsonify([dict(row) for row in archivos])

    except Exception as e:
        logger.error(f"Error obteniendo lista de archivos: {e}", exc_info=True)
        return jsonify({"error": "No se pudo obtener la lista de archivos."}), 500
    finally:
        if conn:
            conn.close()


@admin_bp.route("/api/archivos/subir", methods=["POST"])
@login_required
def subir_archivo():
    """Sube un nuevo archivo al gestor documental"""
    conn = None
    try:
        # Validar que haya archivo
        if "archivo" not in request.files:
            return jsonify({"error": "No se incluyó ningún archivo."}), 400

        file = request.files["archivo"]
        if file.filename == "":
            return jsonify({"error": "El archivo no tiene nombre."}), 400

        # Obtener datos del formulario
        categoria = request.form.get("categoria", "Otro")
        descripcion = request.form.get("descripcion", "")

        # Validar categoría
        categorias_validas = ["Legal", "Contable", "RRHH", "Operativo", "Otro"]
        if categoria not in categorias_validas:
            return jsonify({"error": "Categoría no válida."}), 400

        # Validar extensión
        if not allowed_file(file.filename):
            return (
                jsonify(
                    {
                        "error": f"Tipo de archivo no permitido. Permitidos: {', '.join(ALLOWED_EXTENSIONS)}"
                    }
                ),
                400,
            )

        # Leer contenido del archivo
        file_content = file.read()

        # Validar tamaño
        if len(file_content) > MAX_FILE_SIZE:
            return (
                jsonify(
                    {
                        "error": f"El archivo excede el tamaño máximo permitido ({MAX_FILE_SIZE // (1024*1024)} MB)."
                    }
                ),
                400,
            )

        # Generar nombre interno (hash + timestamp para evitar colisiones)
        file_hash = get_file_hash(file_content)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = file.filename.rsplit(".", 1)[1].lower()
        nombre_interno = f"{file_hash[:16]}_{timestamp}.{extension}"

        # Guardar archivo en disco (usando configuración centralizada)
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'docs')
        os.makedirs(upload_folder, exist_ok=True)  # Asegurar que existe la carpeta
        filepath = os.path.join(upload_folder, nombre_interno)
        with open(filepath, "wb") as f:
            f.write(file_content)

        # Obtener tipo MIME
        tipo_mime = mimetypes.guess_type(file.filename)[0] or "application/octet-stream"

        # Guardar registro en base de datos
        conn = get_db_connection()
        user_id = session.get("user_id")
        user_name = session.get("user_name", "Usuario Desconocido")

        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO documentos_gestor (
                nombre_archivo, nombre_interno, ruta, categoria,
                tipo_mime, tamano_bytes, subido_por, subido_por_nombre, descripcion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                secure_filename(file.filename),
                nombre_interno,
                filepath,
                categoria,
                tipo_mime,
                len(file_content),
                user_id,
                user_name,
                descripcion,
            ),
        )
        conn.commit()

        nuevo_id = cur.lastrowid
        logger.info(
            f"Archivo '{file.filename}' subido exitosamente con ID: {nuevo_id} por usuario {user_id}"
        )

        # Registrar en auditoría
        registrar_log(
            "Subir Archivo",
            f"Archivo: {file.filename}, Categoría: {categoria}, Tamaño: {len(file_content)} bytes",
            resultado="exito",
        )

        # Retornar registro completo
        nuevo_archivo = conn.execute(
            "SELECT * FROM documentos_gestor WHERE id = ?", (nuevo_id,)
        ).fetchone()

        return jsonify(dict(nuevo_archivo)), 201

    except Exception as e:
        if conn:
            conn.rollback()

        logger.error(f"Error al subir archivo: {e}", exc_info=True)
        registrar_log(
            "Error al Subir Archivo", f"Error: {str(e)}", resultado="error"
        )
        return jsonify({"error": f"Error al subir el archivo: {str(e)}"}), 500

    finally:
        if conn:
            conn.close()


@admin_bp.route("/api/archivos/<int:archivo_id>", methods=["DELETE"])
@login_required
def eliminar_archivo(archivo_id):
    """Elimina un archivo del gestor (solo Admin)"""
    conn = None
    try:
        # Verificar permisos de admin
        if session.get("role") != "admin":
            logger.warning(
                f"Usuario no admin {session.get('user_id')} intentó eliminar archivo {archivo_id}"
            )
            registrar_log(
                "Intento de Eliminación Denegada",
                f"Archivo ID: {archivo_id}",
                resultado="advertencia",
            )
            return (
                jsonify(
                    {"error": "No tienes permisos para eliminar archivos."}
                ),
                403,
            )

        conn = get_db_connection()

        # Obtener información del archivo
        archivo = conn.execute(
            "SELECT * FROM documentos_gestor WHERE id = ?", (archivo_id,)
        ).fetchone()

        if not archivo:
            return jsonify({"error": "Archivo no encontrado."}), 404

        # Eliminar archivo físico del disco
        try:
            if os.path.exists(archivo["ruta"]):
                os.remove(archivo["ruta"])
                logger.debug(f"Archivo físico eliminado: {archivo['ruta']}")
        except OSError as e:
            logger.error(f"Error al eliminar archivo físico: {e}")
            # Continuar eliminando el registro de la BD aunque falle el borrado físico

        # Eliminar registro de la base de datos
        conn.execute("DELETE FROM documentos_gestor WHERE id = ?", (archivo_id,))
        conn.commit()

        logger.info(
            f"Archivo ID {archivo_id} ('{archivo['nombre_archivo']}') eliminado por usuario {session.get('user_id')}"
        )

        # Registrar en auditoría
        registrar_log(
            "Eliminar Archivo",
            f"Archivo: {archivo['nombre_archivo']}, Categoría: {archivo['categoria']}",
            resultado="exito",
        )

        return jsonify({"message": "Archivo eliminado exitosamente."}), 200

    except Exception as e:
        if conn:
            conn.rollback()

        logger.error(f"Error al eliminar archivo {archivo_id}: {e}", exc_info=True)
        registrar_log(
            "Error al Eliminar Archivo",
            f"Archivo ID: {archivo_id}, Error: {str(e)}",
            resultado="error",
        )
        return jsonify({"error": f"Error al eliminar el archivo: {str(e)}"}), 500

    finally:
        if conn:
            conn.close()


@admin_bp.route("/api/archivos/<int:archivo_id>/descargar", methods=["GET"])
@login_required
def descargar_archivo(archivo_id):
    """Descarga un archivo del gestor"""
    conn = None
    try:
        conn = get_db_connection()

        archivo = conn.execute(
            "SELECT * FROM documentos_gestor WHERE id = ?", (archivo_id,)
        ).fetchone()

        if not archivo:
            return jsonify({"error": "Archivo no encontrado."}), 404

        # Verificar que el archivo existe en disco
        if not os.path.exists(archivo["ruta"]):
            logger.error(f"Archivo físico no encontrado: {archivo['ruta']}")
            return (
                jsonify({"error": "El archivo físico no se encuentra en el servidor."}),
                404,
            )

        # Registrar descarga en auditoría
        registrar_log(
            "Descargar Archivo",
            f"Archivo: {archivo['nombre_archivo']}",
            resultado="exito",
        )

        # Enviar archivo
        directory = os.path.dirname(archivo["ruta"])
        filename = os.path.basename(archivo["ruta"])

        return send_from_directory(
            directory, filename, as_attachment=True, download_name=archivo["nombre_archivo"]
        )

    except Exception as e:
        logger.error(f"Error al descargar archivo {archivo_id}: {e}", exc_info=True)
        return jsonify({"error": "Error al descargar el archivo."}), 500

    finally:
        if conn:
            conn.close()


# ==================== RUTAS API: AUDITORÍA ====================


@admin_bp.route("/api/auditoria", methods=["GET"])
@login_required
def get_auditoria_logs():
    """Obtiene los últimos logs de auditoría (solo Admin)"""
    conn = None
    try:
        # Verificar permisos de admin
        if session.get("role") != "admin":
            logger.warning(
                f"Usuario no admin {session.get('user_id')} intentó acceder a logs de auditoría"
            )
            return jsonify({"error": "No tienes permisos para ver los logs."}), 403

        # Parámetros de consulta
        limit = int(request.args.get("limit", 100))
        accion = request.args.get("accion")
        usuario = request.args.get("usuario")

        conn = get_db_connection()
        query = """
            SELECT
                id, usuario_id, usuario_nombre, accion, detalle, resultado,
                ip_address, user_agent, metodo_http, ruta, fecha_hora
            FROM auditoria_logs
        """
        params = []
        conditions = []

        if accion:
            conditions.append("accion LIKE ?")
            params.append(f"%{accion}%")

        if usuario:
            conditions.append("usuario_nombre LIKE ?")
            params.append(f"%{usuario}%")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY fecha_hora DESC LIMIT ?"
        params.append(limit)

        logs = conn.execute(query, tuple(params)).fetchall()
        logger.debug(f"Consultados {len(logs)} logs de auditoría")

        return jsonify([dict(row) for row in logs])

    except Exception as e:
        logger.error(f"Error obteniendo logs de auditoría: {e}", exc_info=True)
        return jsonify({"error": "No se pudieron obtener los logs."}), 500

    finally:
        if conn:
            conn.close()
