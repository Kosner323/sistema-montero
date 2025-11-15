# -*- coding: utf-8 -*-
import io
import os
import sqlite3
import traceback
from datetime import datetime

from flask import Blueprint, current_app, g, jsonify, request, send_file
from pypdf import PdfReader, PdfWriter
from PyPDF2.generic import NameObject, NumberObject
from werkzeug.utils import secure_filename

from logger import logger

# --- IMPORTAR UTILIDADES ---
# Importamos funciones y constantes necesarias desde utils.py
from utils import USER_DATA_FOLDER, login_required

# ==================== DEFINICIÓN DEL BLUEPRINT ====================
bp_formularios = Blueprint("bp_formularios", __name__, url_prefix="/api/formularios")
# Alias para compatibilidad con importaciones
formularios = bp_formularios

# ==================== ENDPOINTS DE FORMULARIOS ====================


@bp_formularios.route("/generar", methods=["POST"])
@login_required
def generar_formulario():
    """
    Genera un PDF rellenado basado en una plantilla, datos de usuario y empresa.
    Guarda una copia y devuelve el PDF para descarga.
    """
    try:
        data = request.get_json()
        fid = data.get("formulario_id")
        uid = data.get("usuario_id")  # Esperamos el ID de la tabla usuarios
        enit = data.get("empresa_nit")

        if not fid or not uid or not enit:
            return (
                jsonify({"error": "Faltan IDs (formulario, usuario o empresa)."}),
                400,
            )

        conn = g.db
        try:
            # Obtener info del formulario importado
            form_row = conn.execute(
                "SELECT nombre, nombre_archivo FROM formularios_importados WHERE id = ?",
                (fid,),
            ).fetchone()
            if not form_row:
                return jsonify({"error": "Plantilla de formulario no encontrada."}), 404

            # Obtener ruta de la plantilla desde la configuración de la app
            upload_folder = current_app.config["UPLOAD_FOLDER"]
            tpl_fname = form_row["nombre_archivo"]
            tpl_path = os.path.join(upload_folder, tpl_fname)

            if not os.path.exists(tpl_path):
                logger.error(f"Error crítico: Archivo de plantilla no hallado en disco: {tpl_path}")
                return (
                    jsonify({"error": f"Archivo de plantilla '{tpl_fname}' no hallado en el servidor."}),
                    404,
                )

            # Obtener datos del usuario (usando el ID numérico)
            user_data = conn.execute("SELECT * FROM usuarios WHERE id = ?", (uid,)).fetchone()
            if not user_data:
                return jsonify({"error": "Usuario no encontrado."}), 404
            ud = dict(user_data)  # Convertir a diccionario

            # Obtener datos de la empresa
            comp_data = conn.execute("SELECT * FROM empresas WHERE nit = ?", (enit,)).fetchone()
            if not comp_data:
                return (
                    jsonify({"error": f"Empresa con NIT '{enit}' no encontrada."}),
                    404,
                )
            cd = dict(comp_data)  # Convertir a diccionario

        except Exception as db_err:
            logger.error(f"Error consultando base de datos: {db_err}")
            # traceback.print_exc()  # MIGRADO: reemplazar por logger.error con exc_info=True
            return (
                jsonify({"error": f"Error al consultar base de datos: {str(db_err)}"}),
                500,
            )
        # finally: # La conexión se cierra más abajo

        # --- Mapeo de datos (Ajusta los nombres de campo del PDF según sea necesario) ---
        pdf_map = {
            # Datos del Usuario (ud)
            "tipo_id": ud.get("tipoId", ""),
            "numero_id": ud.get("numeroId", ""),
            "apellido1": ud.get("primerApellido", ""),
            "apellido2": ud.get("segundoApellido", ""),
            "nombre1": ud.get("primerNombre", ""),
            "nombre2": ud.get("segundoNombre", ""),
            "correo": ud.get("correoElectronico", ""),
            "direccion": ud.get("direccion", ""),
            "telefono_fijo": ud.get("telefonoFijo", ""),
            "telefono_celular": ud.get("telefonoCelular", ""),
            "barrio": ud.get("comunaBarrio", ""),
            "departamento_nac": ud.get("departamentoNacimiento", ""),
            "municipio_nac": ud.get("municipioNacimiento", ""),
            "pais_nac": ud.get("paisNacimiento", ""),
            "nacionalidad": ud.get("nacionalidad", ""),
            "municipio": ud.get("municipioNacimiento", ""),  # Puede ser repetido dependiendo del PDF
            "departamento": ud.get("departamentoNacimiento", ""),  # Puede ser repetido
            "fecha_nacimiento": ud.get("fechaNacimiento", ""),
            "afp_nombre": ud.get("afpNombre", ""),
            "fecha_ingreso": ud.get("fechaIngreso", ""),
            "ibc_usuario": str(ud.get("ibc", "")),  # Convertir a string
            # Checkboxes de Sexo (ajusta 'Yes'/'Off' según tu PDF)
            "sexo_M": "Yes" if ud.get("sexoBiologico") == "Masculino" else "Off",
            "sexo_F": "Yes" if ud.get("sexoBiologico") == "Femenino" else "Off",
            # Datos de la Empresa (cd)
            "nombre_empresa": cd.get("nombre_empresa", ""),
            "tipo_id_empresa": cd.get("tipo_identificacion_empresa", ""),
            "nit_empresa": cd.get("nit", ""),
            "direccion_empresa": cd.get("direccion_empresa", ""),
            "telefono_empresa": cd.get("telefono_empresa", ""),
            "correo_empresa": cd.get("correo_empresa", ""),
            "afp_empresa": cd.get("afp_empresa", ""),  # Podría ser diferente al del usuario
            "arl_empresa": cd.get("arl_empresa", ""),
            "ibc_empresa": str(cd.get("ibc_empresa", "")),  # Convertir a string
            "departamento_empresa": cd.get("departamento_empresa", ""),
            "ciudad_empresa": cd.get("ciudad_empresa", ""),
        }
        # --- Fin Mapeo ---

        packet = io.BytesIO()  # Contenedor en memoria para el PDF
        try:
            reader = PdfReader(tpl_path)
            writer = PdfWriter()
            fields = reader.get_fields()

            if not fields:
                print(f"Advertencia: La plantilla PDF '{tpl_fname}' no parece tener campos rellenables.")
                # Considerar devolver error o continuar con el PDF original

            # Copiar páginas de la plantilla al escritor
            for page in reader.pages:
                writer.add_page(page)

            # Rellenar campos si existen páginas y campos
            if writer.pages and fields:
                try:
                    # Intenta rellenar los campos en la primera página
                    writer.update_page_form_field_values(writer.pages[0], pdf_map)
                except Exception as update_err:
                    # Captura error específico si falla el relleno (ej. campo no existe)
                    logger.error(f"Error al actualizar campos del PDF {tpl_fname}: {update_err}")
                    # Decide si continuar o devolver error. Por ahora, continuamos.
                    pass
            elif not writer.pages:
                return (
                    jsonify({"error": "La plantilla PDF está vacía (sin páginas)."}),
                    400,
                )

            # Intentar aplanar el PDF (hacer campos no editables)
            try:
                for page in writer.pages:
                    if "/Annots" in page:
                        for ref in page["/Annots"]:
                            annot = ref.get_object()
                            # Buscar campos de formulario tipo Widget
                            if annot.get("/Subtype") == "/Widget":
                                flags = annot.get("/Ff", 0)  # Obtener flags existentes
                                # Añadir el flag 'ReadOnly' (bit 1)
                                annot.update({NameObject("/Ff"): NumberObject(flags | 1)})
            except Exception as flat_err:
                print(f"Advertencia: No se pudo aplanar el PDF {tpl_fname}: {flat_err}")
                # Continuar aunque no se pueda aplanar

            # Escribir el PDF modificado en memoria
            writer.write(packet)
            pdf_bytes = packet.getvalue()

            # --- Guardar una copia en la carpeta del usuario ---
            try:
                # Construir ruta de guardado según la estructura:
                # D:\Mi-App-React\MONTERO_NEGOCIO\MONTERO_TOTAL\USUARIOS\{ID_USUARIO}\EMPRESAS_AFILIADAS\{NOMBRE_EMPRESA}\{MES_AÑO}.pdf

                # Ruta base del negocio
                base_montero = os.path.join("D:", os.sep, "Mi-App-React", "MONTERO_NEGOCIO", "MONTERO_TOTAL", "USUARIOS")

                # Carpeta del usuario (usar numeroId o numero_documento)
                user_id = ud.get("numeroId") or ud.get("numero_documento", "USUARIO_SIN_ID")
                user_folder = os.path.join(base_montero, str(user_id))

                # Nombre seguro para la carpeta de la empresa (usar nombre_empresa)
                empresa_nombre = cd.get("nombre_empresa", "EMPRESA_SIN_NOMBRE")
                comp_folder_name = secure_filename(empresa_nombre).upper()

                # Ruta completa: USUARIOS/{ID}/EMPRESAS_AFILIADAS/{NOMBRE_EMPRESA}/
                save_path = os.path.join(user_folder, "EMPRESAS_AFILIADAS", comp_folder_name)
                os.makedirs(save_path, exist_ok=True)  # Crear todas las carpetas si no existen

                # Nombre del archivo: MES_AÑO.pdf (ej: "ENERO_2025.pdf")
                now = datetime.now()
                meses_nombres = [
                    "",
                    "ENERO",
                    "FEBRERO",
                    "MARZO",
                    "ABRIL",
                    "MAYO",
                    "JUNIO",
                    "JULIO",
                    "AGOSTO",
                    "SEPTIEMBRE",
                    "OCTUBRE",
                    "NOVIEMBRE",
                    "DICIEMBRE",
                ]
                save_fname = f"{meses_nombres[now.month]}_{now.year}.pdf"
                full_save_path = os.path.join(save_path, save_fname)

                # Escribir el archivo
                with open(full_save_path, "wb") as f:
                    f.write(pdf_bytes)
                logger.info(f"Copia de PDF guardada exitosamente en: {full_save_path}")
            except Exception as save_err:
                # Solo registrar error, no detener la descarga para el usuario
                logger.error(f"ERROR al guardar copia del PDF para usuario {user_id}: {save_err}", exc_info=True)
            # traceback.print_exc()  # MIGRADO: reemplazar por logger.error con exc_info=True
            # --- Fin Guardar Copia ---

            # Nombre del archivo para la descarga
            down_fname = secure_filename(f"{form_row['nombre']}_{ud['numeroId']}_{datetime.now().strftime('%Y%m%d')}.pdf")

            # Enviar el PDF generado como archivo adjunto para descarga
            return send_file(
                io.BytesIO(pdf_bytes),
                mimetype="application/pdf",
                as_attachment=True,
                download_name=down_fname,
            )

        except Exception as pdf_err:
            # Capturar errores durante el procesamiento del PDF
            logger.error(f"Error crítico procesando el PDF '{tpl_fname}': {pdf_err}")
            # traceback.print_exc()  # MIGRADO: reemplazar por logger.error con exc_info=True
            return (
                jsonify({"error": f"Error interno al procesar el PDF: {str(pdf_err)}"}),
                500,
            )

    except Exception as e:
        # Capturar cualquier otro error inesperado
        logger.error(f"Error general en generar_formulario: {e}")
        # traceback.print_exc()  # MIGRADO: reemplazar por logger.error con exc_info=True
        return jsonify({"error": f"Error general del servidor: {str(e)}"}), 500
    # g.db se cierra automáticamente por app.after_request


@bp_formularios.route("", methods=["GET"])
@login_required
def get_formularios():
    """Obtiene la lista de formularios PDF importados."""
    try:
        conn = g.db
        forms = conn.execute(
            "SELECT id, nombre, nombre_archivo, created_at FROM formularios_importados ORDER BY created_at DESC"
        ).fetchall()
        return jsonify([dict(row) for row in forms])
    except Exception as e:
        logger.error(f"Error obteniendo lista de formularios: {e}")
        # traceback.print_exc()  # MIGRADO: reemplazar por logger.error con exc_info=True
        return jsonify({"error": "No se pudo obtener la lista de formularios."}), 500
    # g.db se cierra automáticamente por app.after_request


@bp_formularios.route("/importar", methods=["POST"])
@login_required
def importar_formulario():
    """Importa un nuevo archivo PDF de plantilla al sistema."""
    fpath = None  # Ruta del archivo guardado temporalmente
    try:
        # Validar que los datos necesarios están presentes
        if "archivo" not in request.files or "nombre" not in request.form:
            return jsonify({"error": "Faltan datos (archivo o nombre)."}), 400

        file = request.files["archivo"]
        nombre = request.form["nombre"].strip()

        if not nombre:
            return (
                jsonify({"error": "El nombre del formulario no puede estar vacío."}),
                400,
            )
        if not file or file.filename == "":
            return jsonify({"error": "No se seleccionó ningún archivo."}), 400
        if not file.filename.lower().endswith(".pdf"):
            return jsonify({"error": "El archivo debe ser de tipo PDF."}), 400

        # Crear nombre seguro y ruta de guardado
        ts = datetime.now().strftime("%Y%m%d%H%M%S")  # Timestamp para nombre único
        base, ext = os.path.splitext(file.filename)
        safe_fname = secure_filename(f"{ts}_{base}{ext}")
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        fpath = os.path.join(upload_folder, safe_fname)

        # Guardar el archivo físico
        file.save(fpath)

        # Guardar registro en la base de datos
        conn = g.db
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO formularios_importados (nombre, nombre_archivo, ruta_archivo) VALUES (?, ?, ?)",
                (nombre, safe_fname, fpath),
            )
            conn.commit()
            fid = cur.lastrowid  # Obtener el ID del nuevo registro
            return (
                jsonify(
                    {
                        "message": f"Formulario '{nombre}' importado con éxito.",
                        "id": fid,
                        "nombre_guardado": safe_fname,
                    }
                ),
                201,
            )
        except Exception as db_err:
            conn.rollback()  # Revertir si falla la inserción en BD
            # Intentar eliminar el archivo físico si falló el guardado en BD
            if fpath and os.path.exists(fpath):
                try:
                    os.remove(fpath)
                except OSError as rm_err:
                    logger.error(f"Error eliminando archivo '{fpath}' tras fallo de BD: {rm_err}")
            logger.error(f"Error de base de datos al importar formulario: {db_err}")
            # traceback.print_exc()  # MIGRADO: reemplazar por logger.error con exc_info=True
            return (
                jsonify({"error": f"Error al guardar en base de datos: {str(db_err)}"}),
                500,
            )
        # finally se maneja fuera del try interno

    except Exception as e:
        # Intentar eliminar el archivo físico si falló el guardado del archivo
        if fpath and os.path.exists(fpath):
            try:
                os.remove(fpath)
            except OSError as rm_err:
                logger.error(f"Error eliminando archivo '{fpath}' tras fallo de guardado: {rm_err}")
        logger.error(f"Error al guardar archivo PDF: {e}")
        # traceback.print_exc()  # MIGRADO: reemplazar por logger.error con exc_info=True
        return jsonify({"error": f"Error al guardar el archivo PDF: {str(e)}"}), 500
    # g.db se cierra automáticamente por app.after_request


@bp_formularios.route("/<int:form_id>", methods=["DELETE"])
@login_required
def delete_formulario(form_id):
    """Elimina un formulario importado (registro BD y archivo físico)."""
    try:
        conn = g.db
        cur = conn.cursor()

        # Obtener la ruta del archivo antes de borrar el registro
        cur.execute("SELECT ruta_archivo FROM formularios_importados WHERE id = ?", (form_id,))
        row = cur.fetchone()

        # Eliminar el registro de la base de datos
        cur.execute("DELETE FROM formularios_importados WHERE id = ?", (form_id,))
        conn.commit()

        # Si el registro existía y tenía una ruta de archivo
        if cur.rowcount > 0:
            if row and row["ruta_archivo"]:
                fpath_del = row["ruta_archivo"]
                # Verificación de seguridad: asegurarse de que la ruta esté dentro de UPLOAD_FOLDER
                safe_upld = os.path.normpath(current_app.config["UPLOAD_FOLDER"])
                safe_fpath = os.path.normpath(fpath_del)
                if safe_fpath.startswith(safe_upld) and os.path.exists(safe_fpath):
                    try:
                        os.remove(safe_fpath)
                        print(f"Archivo físico eliminado: {safe_fpath}")
                    except OSError as e:
                        # Registrar error si no se puede borrar, pero continuar
                        logger.error(f"Error eliminando archivo físico {safe_fpath}: {e}")
                elif not safe_fpath.startswith(safe_upld):
                    print(f"Advertencia: Intento de eliminar archivo fuera de UPLOAD_FOLDER: {safe_fpath}")

            return jsonify({"message": "Formulario eliminado correctamente."}), 200
        else:
            # Si no se encontró el ID en la base de datos
            return jsonify({"error": "Formulario no encontrado."}), 404

    except Exception as e:
        if conn:
            conn.rollback()  # Revertir si hubo error en BD
        logger.error(f"Error eliminando formulario {form_id}: {e}")
        # traceback.print_exc()  # MIGRADO: reemplazar por logger.error con exc_info=True
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
    # g.db se cierra automáticamente por app.after_request
