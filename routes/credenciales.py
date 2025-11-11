# -*- coding: utf-8 -*-
"""
credenciales.py
====================================================
Maneja la lógica de backend para gestionar las
credenciales de acceso a plataformas externas.
INCLUYE ENCRIPTACIÓN DE CREDENCIALES SENSIBLES
"""

from flask import Blueprint, request, jsonify
import sqlite3
import traceback
import os
from datetime import datetime
from werkzeug.utils import secure_filename

# --- IMPORTAR UTILIDADES ---
from logger import get_logger

logger = get_logger(__name__)

try:
    from utils import get_db_connection, login_required
except ImportError:
    logger.error("Error: No se pudo importar desde utils.py en credenciales.py")
    # --- Fallbacks simples ---
    from functools import wraps

    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)

        return decorated_function

    def get_db_connection():
        import os

        DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "mi_sistema.db")
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn


# --- Fin Fallbacks ---

# --- IMPORTAR SISTEMA DE ENCRIPTACIÓN ---
try:
    from encryption import get_encryption, encrypt_text, decrypt_text

    logger.info("Sistema de encriptación cargado correctamente")
except ImportError as e:
    logger.error(f"Error: No se pudo importar el módulo de encriptación: {e}")

    # Fallback sin encriptación (no recomendado para producción)
    def encrypt_text(text):
        return text

    def decrypt_text(text):
        return text

    logger.warning("ADVERTENCIA: Ejecutando sin encriptación. No usar en producción.")

# ==================== CONFIGURACIÓN DE RUTAS DE DOCUMENTOS ====================
# Directorio base para las carpetas de las empresas (según la solicitud del usuario)
# NOTA: Usamos getenv para hacerlo configurable, pero con el valor por defecto que indicaste.
BASE_EMPRESAS_DOCS = os.getenv(
    "BASE_EMPRESAS_DOCS", "D:\\Mi-App-React\\MONTERO_NEGOCIO\\MONTERO_TOTAL\\EMPRESAS"
)
SUBFOLDER_CREDENTIALS = "USUARIOS Y CONTRASEÑAS"
# ==============================================================================

# ==================== DEFINICIÓN DEL BLUEPRINT ====================
bp_credenciales = Blueprint("bp_credenciales", __name__, url_prefix="/api/credenciales")

# ==================== ENDPOINTS DE CREDENCIALES ====================


@bp_credenciales.route("", methods=["GET"])
@login_required
def get_credenciales():
    """Obtiene las credenciales, opcionalmente filtradas por empresa."""
    conn = None
    try:
        empresa_nit_filter = request.args.get("empresa_nit")

        conn = get_db_connection()
        # Se asegura de seleccionar la nueva columna ruta_documento_txt
        query = """
            SELECT c.*, e.nombre_empresa 
            FROM credenciales_plataforma c 
            LEFT JOIN empresas e ON c.empresa_nit = e.nit 
        """
        params = []

        if empresa_nit_filter and empresa_nit_filter != "todos":
            query += " WHERE c.empresa_nit = ?"
            params.append(empresa_nit_filter)

        query += " ORDER BY e.nombre_empresa, c.plataforma"

        credenciales = conn.execute(query, tuple(params)).fetchall()

        # Desencriptar las credenciales antes de devolverlas
        credenciales_desencriptadas = []
        for row in credenciales:
            credencial_dict = dict(row)
            try:
                # Desencriptar usuario y contraseña
                if credencial_dict.get("usuario"):
                    credencial_dict["usuario"] = decrypt_text(
                        credencial_dict["usuario"]
                    )
                if credencial_dict.get("contrasena"):
                    credencial_dict["contrasena"] = decrypt_text(
                        credencial_dict["contrasena"]
                    )
            except Exception as e:
                logger.warning(
                    f"Error desencriptando credencial {credencial_dict.get('id')}: {e}"
                )
                # Si falla la desencriptación, mantener los valores originales

            credenciales_desencriptadas.append(credencial_dict)

        return jsonify(credenciales_desencriptadas)

    except Exception as e:
        logger.error(f"Error obteniendo credenciales: {e}", exc_info=True)
        return jsonify({"error": "No se pudo obtener la lista de credenciales."}), 500
    finally:
        if conn:
            conn.close()


@bp_credenciales.route("", methods=["POST"])
@login_required
def add_credencial():
    """Crea un nuevo registro de credencial y genera un archivo .txt."""
    conn = None
    ruta_documento_txt = None

    try:
        data = request.get_json()
        required_fields = ["empresa_nit", "plataforma", "url", "usuario", "contrasena"]
        if not data or not all(field in data for field in required_fields):
            return (
                jsonify(
                    {
                        "error": "Faltan datos obligatorios (empresa_nit, plataforma, url, usuario, contrasena)."
                    }
                ),
                400,
            )

        conn = get_db_connection()
        cur = conn.cursor()

        # 1. Obtener el nombre de la empresa para la ruta de guardado
        empresa_row = conn.execute(
            "SELECT nombre_empresa FROM empresas WHERE nit = ?", (data["empresa_nit"],)
        ).fetchone()
        if not empresa_row:
            return jsonify({"error": "NIT de empresa no encontrado."}), 404

        # Formatear el nombre de la empresa para la carpeta (ej: COMERCIALIZADORA_AJK)
        nombre_empresa = empresa_row["nombre_empresa"].replace(" ", "_").upper()

        # 2. Construir la ruta de guardado y crear la carpeta
        # Ruta final: D:\Mi-App-React\...\EMPRESAS\<NOMBRE_EMPRESA>\USUARIOS Y CONTRASEÑAS
        empresa_dir = os.path.join(BASE_EMPRESAS_DOCS, nombre_empresa)
        target_dir = os.path.join(empresa_dir, SUBFOLDER_CREDENTIALS)

        os.makedirs(target_dir, exist_ok=True)

        # Nombre del archivo: [Plataforma_Segura]_[Fecha_Hora].txt
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_platform_name = secure_filename(data["plataforma"]).replace(".", "_")
        filename = f"{safe_platform_name}_{timestamp}.txt"
        file_path = os.path.join(target_dir, filename)

        # 3. Generar el contenido del archivo .txt (CON ADVERTENCIA DE ENCRIPTACIÓN)
        content = f"""====================================================
REGISTRO DE CREDENCIAL DE PLATAFORMA (ENCRIPTADO)
====================================================
EMPRESA: {empresa_row['nombre_empresa']} (NIT: {data['empresa_nit']})
FECHA DE REGISTRO: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
----------------------------------------------------
PLATAFORMA: {data['plataforma']}
URL: {data['url']}
USUARIO: {data['usuario']}
CONTRASEÑA: {data['contrasena']}
NOTAS: {data.get('notas') or 'N/A'}
----------------------------------------------------
ADVERTENCIA: Las credenciales en la base de datos 
están encriptadas. Este archivo contiene las 
credenciales en texto plano solo para respaldo.
===================================================="""

        # 4. Escribir el archivo .txt (EN TEXTO PLANO para respaldo)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        ruta_documento_txt = file_path

        # 5. ENCRIPTAR las credenciales antes de guardar en la base de datos
        usuario_encriptado = encrypt_text(data["usuario"])
        contrasena_encriptada = encrypt_text(data["contrasena"])

        logger.info(f"Encriptando credenciales para plataforma: {data['plataforma']}")

        # 6. Insertar el registro en la base de datos (CON DATOS ENCRIPTADOS)
        cur.execute(
            """
            INSERT INTO credenciales_plataforma (
                empresa_nit, plataforma, url, usuario, contrasena, notas, ruta_documento_txt
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                data["empresa_nit"],
                data["plataforma"],
                data["url"],
                usuario_encriptado,
                contrasena_encriptada,
                data.get("notas"),
                ruta_documento_txt,
            ),
        )
        conn.commit()

        nuevo_id = cur.lastrowid

        # 7. Devolver el registro recién creado (DESENCRIPTADO para el frontend)
        nuevo_registro = conn.execute(
            """
             SELECT c.*, e.nombre_empresa 
             FROM credenciales_plataforma c 
             LEFT JOIN empresas e ON c.empresa_nit = e.nit 
             WHERE c.id = ?
             """,
            (nuevo_id,),
        ).fetchone()

        # Desencriptar antes de devolver
        resultado_dict = dict(nuevo_registro)
        resultado_dict["usuario"] = decrypt_text(resultado_dict["usuario"])
        resultado_dict["contrasena"] = decrypt_text(resultado_dict["contrasena"])

        return jsonify(resultado_dict), 201

    except sqlite3.IntegrityError as ie:
        if conn:
            conn.rollback()
        logger.error(f"Error de integridad en credenciales: {ie}")
        return jsonify({"error": f"Error de integridad: {ie}"}), 409
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error creando credencial o archivo TXT: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "error": f"Error interno del servidor: {str(e)}. Ruta de archivo: {ruta_documento_txt}"
                }
            ),
            500,
        )
    finally:
        if conn:
            conn.close()


@bp_credenciales.route("/<int:credencial_id>", methods=["DELETE"])
@login_required
def delete_credencial(credencial_id):
    """Elimina un registro de credencial por su ID."""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Opcional: Obtener la ruta del archivo para eliminarlo
        credencial = conn.execute(
            "SELECT ruta_documento_txt FROM credenciales_plataforma WHERE id = ?",
            (credencial_id,),
        ).fetchone()

        # Eliminar el archivo físico si existe
        if credencial and credencial["ruta_documento_txt"]:
            try:
                if os.path.exists(credencial["ruta_documento_txt"]):
                    os.remove(credencial["ruta_documento_txt"])
                    logger.info(
                        f"Archivo de credencial eliminado: {credencial['ruta_documento_txt']}"
                    )
            except Exception as e:
                logger.warning(f"No se pudo eliminar el archivo físico: {e}")

        # Eliminar el registro de la base de datos
        cur.execute(
            "DELETE FROM credenciales_plataforma WHERE id = ?", (credencial_id,)
        )
        conn.commit()

        if cur.rowcount == 0:
            return jsonify({"error": "Credencial no encontrada."}), 404
        else:
            return jsonify({"message": "Credencial eliminada correctamente."}), 200

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error eliminando credencial {credencial_id}: {e}", exc_info=True)
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


@bp_credenciales.route("/<int:credencial_id>", methods=["PUT"])
@login_required
def update_credencial(credencial_id):
    """Actualiza un registro de credencial existente."""
    conn = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos para actualizar."}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Verificar que la credencial existe
        credencial_actual = conn.execute(
            "SELECT * FROM credenciales_plataforma WHERE id = ?", (credencial_id,)
        ).fetchone()

        if not credencial_actual:
            return jsonify({"error": "Credencial no encontrada."}), 404

        # Preparar los campos a actualizar
        campos_actualizar = []
        valores = []

        if "plataforma" in data:
            campos_actualizar.append("plataforma = ?")
            valores.append(data["plataforma"])

        if "url" in data:
            campos_actualizar.append("url = ?")
            valores.append(data["url"])

        if "usuario" in data:
            campos_actualizar.append("usuario = ?")
            # ENCRIPTAR el nuevo usuario
            valores.append(encrypt_text(data["usuario"]))

        if "contrasena" in data:
            campos_actualizar.append("contrasena = ?")
            # ENCRIPTAR la nueva contraseña
            valores.append(encrypt_text(data["contrasena"]))

        if "notas" in data:
            campos_actualizar.append("notas = ?")
            valores.append(data["notas"])

        if not campos_actualizar:
            return (
                jsonify({"error": "No se especificaron campos para actualizar."}),
                400,
            )

        # Actualizar en la base de datos
        valores.append(credencial_id)
        query = f"UPDATE credenciales_plataforma SET {', '.join(campos_actualizar)} WHERE id = ?"
        cur.execute(query, tuple(valores))
        conn.commit()

        logger.info(f"Credencial {credencial_id} actualizada correctamente")

        # Devolver el registro actualizado (desencriptado)
        registro_actualizado = conn.execute(
            """
             SELECT c.*, e.nombre_empresa 
             FROM credenciales_plataforma c 
             LEFT JOIN empresas e ON c.empresa_nit = e.nit 
             WHERE c.id = ?
             """,
            (credencial_id,),
        ).fetchone()

        resultado_dict = dict(registro_actualizado)
        resultado_dict["usuario"] = decrypt_text(resultado_dict["usuario"])
        resultado_dict["contrasena"] = decrypt_text(resultado_dict["contrasena"])

        return jsonify(resultado_dict), 200

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(
            f"Error actualizando credencial {credencial_id}: {e}", exc_info=True
        )
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()
