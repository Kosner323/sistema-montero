# -*- coding: utf-8 -*-
"""
SISTEMA DE DEPURACIONES MONTERO - VERSIÓN COMPLETA
Genera cartas de depuración personalizadas según 3 escenarios diferentes
"""

import os
import tempfile
from datetime import datetime
from io import BytesIO

from flask import Blueprint, g, jsonify, request, send_file, session
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from werkzeug.utils import secure_filename

from logger import logger

# --- IMPORTACIÓN CENTRALIZADA ---
# Intentamos importar desde nivel superior o local
try:
    from ..utils import get_db_connection, login_required
except (ImportError, ValueError):
    from utils import get_db_connection, login_required
# -------------------------------

# Definir el Blueprint
bp_depuraciones = Blueprint("bp_depuraciones", __name__, url_prefix="/api/depuraciones")

# Configuración de rutas
RUTA_BASE_USUARIOS = r"D:\Mi-App-React\MONTERO_NEGOCIO\MONTERO_TOTAL\USUARIOS"
RUTA_BASE_EMPRESAS = r"D:\Mi-App-React\MONTERO_NEGOCIO\MONTERO_TOTAL\EMPRESAS"
ALLOWED_EXTENSIONS = {"pdf"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp_depuraciones.route("/pendientes", methods=["GET"])
@login_required
def get_depuraciones_pendientes():
    """Obtiene todos los registros marcados como pendientes de depuración."""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(
            "SELECT id, entidad_nombre, causa, fecha_sugerida, estado FROM depuraciones_pendientes ORDER BY fecha_sugerida DESC"
        )
        pendientes = [dict(row) for row in c.fetchall()]
        return jsonify(pendientes), 200
    except Exception as e:
        logger.error("Error en operación", exc_info=True)
        return jsonify({"error": f"Error al consultar depuraciones: {str(e)}"}), 500
    # g.db se cierra automáticamente por app.after_request


@bp_depuraciones.route("/iniciar", methods=["POST"])
@login_required
def iniciar_proceso_depuracion():
    """
    Inicia la búsqueda de registros para depurar.
    Busca usuarios con +1 año de antigüedad.
    """
    try:
        conn = get_db_connection()
        c = conn.cursor()
        nuevos_pendientes_count = 0

        c.execute(
            """
            SELECT numeroId, primerNombre, primerApellido, fechaIngreso
            FROM usuarios
            WHERE julianday('now') - julianday(fechaIngreso) > 365
        """
        )
        usuarios_antiguos = c.fetchall()

        fecha_sugerida = datetime.now().strftime("%Y-%m-%d")
        causa = "Inactividad (+1 año)"

        for user in usuarios_antiguos:
            c.execute(
                "SELECT id FROM depuraciones_pendientes WHERE entidad_id = ? AND estado = 'Pendiente'",
                (user["numeroId"],),
            )
            if c.fetchone() is None:
                entidad_nombre = f"Empleado: {user['primerNombre']} {user['primerApellido']} (CC {user['numeroId']})"
                c.execute(
                    """
                    INSERT INTO depuraciones_pendientes (entidad_tipo, entidad_id, entidad_nombre, causa, estado, fecha_sugerida)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        "usuario",
                        user["numeroId"],
                        entidad_nombre,
                        causa,
                        "Pendiente",
                        fecha_sugerida,
                    ),
                )
                nuevos_pendientes_count += 1

        conn.commit()
        return (
            jsonify(
                {
                    "message": f"Se encontraron {nuevos_pendientes_count} nuevo(s) registro(s) para depurar.",
                    "nuevos_pendientes": nuevos_pendientes_count,
                }
            ),
            200,
        )

    except Exception as e:
        conn = get_db_connection()
        conn.rollback()
        logger.error("Error en operación", exc_info=True)
        return jsonify({"error": f"Error al iniciar depuración: {str(e)}"}), 500
    # g.db se cierra automáticamente por app.after_request


@bp_depuraciones.route("/<int:depuracion_id>/resolver", methods=["PUT"])
@login_required
def resolver_depuracion(depuracion_id):
    """
    Resuelve un item pendiente.
    'aprobar' = ELIMINA EL REGISTRO ORIGINAL.
    'rechazar' = Mantiene el registro original, pero lo quita de pendientes.
    """
    try:
        data = request.json
        accion = data.get("accion")

        if not accion:
            return jsonify({"error": "Falta la 'accion' (aprobar/rechazar)"}), 400

        conn = get_db_connection()
        c = conn.cursor()

        c.execute(
            "SELECT * FROM depuraciones_pendientes WHERE id = ? AND estado = 'Pendiente'",
            (depuracion_id,),
        )
        item = c.fetchone()

        if not item:
            return (
                jsonify({"error": "Registro pendiente no encontrado o ya resuelto"}),
                404,
            )

        message = ""

        if accion == "aprobar":
            if item["entidad_tipo"] == "usuario":
                c.execute("DELETE FROM usuarios WHERE numeroId = ?", (item["entidad_id"],))
                c.execute(
                    "UPDATE depuraciones_pendientes SET estado = 'Aprobada' WHERE id = ?",
                    (depuracion_id,),
                )
                message = f"Depuración Aprobada: El registro {item['entidad_nombre']} ha sido eliminado."

        elif accion == "rechazar":
            c.execute(
                "UPDATE depuraciones_pendientes SET estado = 'Rechazada' WHERE id = ?",
                (depuracion_id,),
            )
            message = f"Depuración Rechazada: El registro {item['entidad_nombre']} se conservará."

        else:
            return jsonify({"error": "Acción no válida"}), 400

        conn.commit()
        return jsonify({"success": True, "message": message}), 200

    except Exception as e:
        conn = get_db_connection()
        conn.rollback()
        logger.error("Error en operación", exc_info=True)
        return jsonify({"error": f"Error al resolver depuración: {str(e)}"}), 500
    # g.db se cierra automáticamente por app.after_request


@bp_depuraciones.route("/generar-carta", methods=["POST"])
@login_required
def generar_carta():
    """
    Genera la carta de depuración según el escenario y guarda el PDF combinado.
    """
    try:
        # Obtener datos del formulario
        tipo_escenario = request.form.get("tipo_escenario")
        empresa_nombre = request.form.get("empresa_nombre")
        empresa_numero_id = request.form.get("empresa_numero_id")
        usuario_numero_id = request.form.get("usuario_numero_id")
        usuario_nombre = request.form.get("usuario_nombre_completo")
        usuario_tipo_id = request.form.get("usuario_tipo_id")
        numero_planilla = request.form.get("numero_planilla")
        ciudad = request.form.get("ciudad")
        senores = request.form.get("senores")
        departamento_entidad = request.form.get("departamento_entidad")
        fecha_inicio = request.form.get("fecha_inicio")
        fecha_fin = request.form.get("fecha_fin")
        rep_legal_nombre = request.form.get("rep_legal_nombre")
        rep_legal_cargo = request.form.get("rep_legal_cargo")
        rep_legal_celular = request.form.get("rep_legal_celular")
        rep_legal_direccion = request.form.get("rep_legal_direccion")
        rep_legal_correo = request.form.get("rep_legal_correo")

        logger.info(f"Generando carta - Escenario: {tipo_escenario}")

        # Obtener archivos adjuntos
        archivos_adjuntos = []

        cedula = request.files.get("cedula")
        if cedula and allowed_file(cedula.filename):
            archivos_adjuntos.append(("cedula", cedula))

        afiliacion = request.files.get("afiliacion")
        if afiliacion and allowed_file(afiliacion.filename):
            archivos_adjuntos.append(("afiliacion", afiliacion))

        ingreso = request.files.get("ingreso")
        if ingreso and allowed_file(ingreso.filename):
            archivos_adjuntos.append(("ingreso", ingreso))

        retiro = request.files.get("retiro")
        if retiro and allowed_file(retiro.filename):
            archivos_adjuntos.append(("retiro", retiro))

        estado_cuenta = request.files.get("estado_cuenta")
        if estado_cuenta and allowed_file(estado_cuenta.filename):
            archivos_adjuntos.append(("estado_cuenta", estado_cuenta))

        # Normalizar nombre de empresa para buscar carpeta
        empresa_carpeta = empresa_nombre.replace(" ", "_").replace(".", "").upper()
        ruta_empresa = os.path.join(RUTA_BASE_EMPRESAS, empresa_carpeta)

        # Verificar que existe la carpeta de la empresa
        if not os.path.exists(ruta_empresa):
            logger.error(f"No se encuentra la carpeta de la empresa: {ruta_empresa}")
            return jsonify({"error": f"No se encuentra la carpeta de la empresa: {empresa_carpeta}"}), 404

        # Buscar PDF de carta base
        carta_base_path = os.path.join(ruta_empresa, "CARTA.pdf")
        if not os.path.exists(carta_base_path):
            logger.error(f"No se encuentra el PDF CARTA.pdf en: {ruta_empresa}")
            return jsonify({"error": "No se encuentra el archivo CARTA.pdf de la empresa"}), 404

        # Buscar firma
        firma_path = os.path.join(ruta_empresa, "firma_empresa.png")
        if not os.path.exists(firma_path):
            logger.error(f"No se encuentra la firma en: {ruta_empresa}")
            return jsonify({"error": "No se encuentra la firma_empresa.png"}), 404

        # Generar contenido según escenario
        fecha_actual = datetime.now().strftime("%d de %B de %Y")

        texto1 = f"{ciudad}, {fecha_actual}\n"
        texto1 += f"Señores:\n{senores}\n"
        texto1 += f"Departamento:\n{departamento_entidad}\n"
        texto1 += "Cordial saludo"

        if tipo_escenario in ["COMPLETO", "SIN_RETIRO"]:
            texto2 = f"El motivo de esta carta es para solicitarles la corrección de mora donde nos notifica de la siguiente persona {usuario_nombre} identificado con número de {usuario_tipo_id} {usuario_numero_id}, el cual laboró desde {fecha_inicio} hasta {fecha_fin}, por lo tanto anexamos estado de cuenta, planilla con número {numero_planilla} y afiliación para que nos colaboren con la corrección ya que nuestra intención como empresa es estar al día con todas nuestras obligaciones."

            anexos = ["Estado de cuenta", "Formulario de afiliación", "Planilla de ingreso"]

            if tipo_escenario == "COMPLETO":
                anexos.append("Planilla de retiro")

            if any(nombre == "cedula" for nombre, _ in archivos_adjuntos):
                anexos.append("Cédula")

        elif tipo_escenario == "BASICO":
            texto2 = f"El motivo de esta carta es para solicitarles la corrección de mora donde nos notifica de la siguiente persona {usuario_nombre} identificado con número de {usuario_tipo_id} {usuario_numero_id}, el cual evidenciamos que no se ha realizado la solicitud de afiliación, por lo tanto anexamos estado de cuenta para que nos colaboren con el comprobante de afiliación y en caso contrario de no haber dicho documento solicitamos la anulación del reporte del estado de cuenta, ya que nuestra intención como empresa es estar al día con todas nuestras obligaciones."

            anexos = ["Estado de cuenta"]
            if any(nombre == "cedula" for nombre, _ in archivos_adjuntos):
                anexos.append("Cédula")
        else:
            return jsonify({"error": "Escenario no reconocido"}), 400

        texto3 = "Anexamos:\n" + "\n".join([f"{i+1}. {anexo}" for i, anexo in enumerate(anexos)])
        texto3 += "\n\nMuchas gracias"

        texto4 = f"{rep_legal_nombre}\n"
        texto4 += f"{rep_legal_cargo}\n"
        texto4 += f"Celular: {rep_legal_celular}\n"
        texto4 += f"Dirección: {rep_legal_direccion}\n"
        texto4 += f"Correo: {rep_legal_correo}"

        # Rellenar PDF base con los textos
        pdf_rellenado = rellenar_pdf_carta(carta_base_path, firma_path, texto1, texto2, texto3, texto4)

        # Crear PDF combinado (carta + anexos)
        pdf_final = combinar_pdfs(pdf_rellenado, archivos_adjuntos, anexos)

        # Guardar en carpeta del usuario
        ruta_usuario = os.path.join(RUTA_BASE_USUARIOS, usuario_numero_id, "DEPURACIONES")
        os.makedirs(ruta_usuario, exist_ok=True)

        fecha_archivo = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"{empresa_carpeta}_{fecha_archivo}.pdf"
        ruta_final = os.path.join(ruta_usuario, nombre_archivo)

        with open(ruta_final, "wb") as f:
            f.write(pdf_final.getvalue())

        logger.info(f"✅ Carta generada exitosamente: {ruta_final}")

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Carta generada exitosamente",
                    "archivo": nombre_archivo,
                    "ruta": ruta_final,
                    "pdf_url": f"/api/depuraciones/descargar/{usuario_numero_id}/{nombre_archivo}",
                }
            ),
            200,
        )

    except Exception as e:
        logger.error("Error generando carta", exc_info=True)
        return jsonify({"error": f"Error al generar carta: {str(e)}"}), 500


def rellenar_pdf_carta(carta_base_path, firma_path, texto1, texto2, texto3, texto4):
    """
    Rellena el PDF base con los textos y la firma.
    Retorna un BytesIO con el PDF rellenado.
    """
    try:
        # Leer PDF base
        reader = PdfReader(carta_base_path)
        writer = PdfWriter()

        # Obtener primera página (asumiendo que la carta es de 1 página)
        page = reader.pages[0]

        # Crear un nuevo PDF con los textos superpuestos
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)

        # Configurar fuente
        can.setFont("Helvetica", 10)

        # TEXTO1 (cuerpo principal) - posición aproximada
        y_pos = 600
        for linea in texto1.split("\n"):
            can.drawString(72, y_pos, linea)
            y_pos -= 15

        # TEXTO2 (cuerpo) - justificado
        y_pos = 500
        max_width = 450
        words = texto2.split()
        line = ""

        for word in words:
            test_line = line + word + " "
            if can.stringWidth(test_line, "Helvetica", 10) < max_width:
                line = test_line
            else:
                can.drawString(72, y_pos, line)
                y_pos -= 15
                line = word + " "

        if line:
            can.drawString(72, y_pos, line)
            y_pos -= 30

        # TEXTO3 (anexos)
        for linea in texto3.split("\n"):
            can.drawString(72, y_pos, linea)
            y_pos -= 15

        y_pos -= 20

        # FIRMA (imagen)
        try:
            img = ImageReader(firma_path)
            can.drawImage(img, 72, y_pos - 60, width=150, height=60, preserveAspectRatio=True)
            y_pos -= 80
        except Exception as e:
            logger.warning(f"No se pudo insertar firma: {e}")
            can.drawString(72, y_pos, "[FIRMA DIGITAL]")
            y_pos -= 20

        # TEXTO4 (datos del representante)
        for linea in texto4.split("\n"):
            can.drawString(72, y_pos, linea)
            y_pos -= 12

        can.save()

        # Combinar el nuevo contenido con la página original
        packet.seek(0)
        new_pdf = PdfReader(packet)
        page.merge_page(new_pdf.pages[0])
        writer.add_page(page)

        # Copiar el resto de páginas si las hay
        for i in range(1, len(reader.pages)):
            writer.add_page(reader.pages[i])

        output = BytesIO()
        writer.write(output)
        output.seek(0)

        return output

    except Exception as e:
        logger.error(f"Error rellenando PDF: {e}", exc_info=True)
        raise


def combinar_pdfs(carta_pdf, archivos_adjuntos, orden_anexos):
    """
    Combina la carta con los archivos adjuntos en el orden especificado.
    """
    try:
        merger = PdfWriter()

        # Agregar carta primero
        merger.append(carta_pdf)

        # Mapeo de nombres de archivos
        mapeo = {
            "estado_cuenta": "Estado de cuenta",
            "afiliacion": "Formulario de afiliación",
            "ingreso": "Planilla de ingreso",
            "retiro": "Planilla de retiro",
            "cedula": "Cédula",
        }

        # Agregar anexos en el orden especificado
        for anexo_nombre in orden_anexos:
            # Buscar el archivo correspondiente
            for nombre_key, archivo in archivos_adjuntos:
                if mapeo.get(nombre_key) == anexo_nombre:
                    # Guardar temporalmente el archivo
                    temp_file = BytesIO(archivo.read())
                    temp_file.seek(0)
                    merger.append(temp_file)
                    break

        output = BytesIO()
        merger.write(output)
        merger.close()
        output.seek(0)

        return output

    except Exception as e:
        logger.error(f"Error combinando PDFs: {e}", exc_info=True)
        raise


@bp_depuraciones.route("/descargar/<usuario_id>/<archivo>", methods=["GET"])
@login_required
def descargar_carta(usuario_id, archivo):
    """
    Permite descargar una carta generada.
    """
    try:
        ruta_archivo = os.path.join(RUTA_BASE_USUARIOS, usuario_id, "DEPURACIONES", archivo)

        if not os.path.exists(ruta_archivo):
            return jsonify({"error": "Archivo no encontrado"}), 404

        return send_file(ruta_archivo, as_attachment=True, download_name=archivo)

    except Exception as e:
        logger.error(f"Error descargando carta: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


# ============================================
# ENDPOINTS AUXILIARES PARA BÚSQUEDA
# ============================================


@bp_depuraciones.route("/buscar-empresa", methods=["GET"])
@login_required
def buscar_empresa():
    """Busca una empresa por tipo y número de ID"""
    try:
        tipo = request.args.get("tipo")
        numero = request.args.get("numero")

        if not tipo or not numero:
            return jsonify({"error": "Faltan parámetros"}), 400

        conn = get_db_connection()
        c = conn.cursor()

        c.execute(
            """
            SELECT nombre_empresa, rep_legal_nombre, direccion_empresa,
                   correo_empresa, ciudad_empresa, telefono_empresa
            FROM empresas
            WHERE tipo_identificacion_empresa = ? AND nit = ?
            """,
            (tipo, numero),
        )

        empresa = c.fetchone()

        if not empresa:
            return jsonify({"error": "Empresa no encontrada"}), 404

        return jsonify(dict(empresa)), 200

    except Exception as e:
        logger.error(f"Error buscando empresa: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    # g.db se cierra automáticamente por app.after_request


@bp_depuraciones.route("/buscar-usuario", methods=["GET"])
@login_required
def buscar_usuario():
    """
    Busca un usuario por tipo y número de ID.

    Devuelve información completa del usuario para autocompletado,
    mapeando los nombres de la base de datos (ej. sexoIdentificacion)
    a los nombres que el script espera (ej. genero).
    """
    try:
        # Obtener parámetros de la petición
        tipo = request.args.get("tipo")
        numero = request.args.get("numero")

        # Validar que se proporcionen ambos parámetros
        if not tipo or not numero:
            return jsonify({"error": "Faltan parámetros"}), 400

        # Conectar a la base de datos
        conn = get_db_connection()
        c = conn.cursor()

        # --- CONSULTA SQL ACTUALIZADA ---
        # Mapea los nombres de la BD (ej. sexoIdentificacion)
        # a los nombres que el script espera (ej. genero) usando 'AS'
        c.execute(
            """
            SELECT
                primerNombre,
                segundoNombre,
                primerApellido,
                segundoApellido,
                telefonoCelular,
                correoElectronico,
                epsNombre,
                arlNombre,
                ccfNombre,
                afpNombre,
                ibc,
                nacionalidad,
                sexoIdentificacion AS genero,
                fechaNacimiento,
                departamentoNacimiento AS departamento,
                municipioNacimiento AS ciudad,
                direccion,
                comunaBarrio AS barrio
            FROM usuarios
            WHERE tipoId = ? AND numeroId = ?
            """,
            (tipo, numero),
        )

        # Obtener resultado
        usuario = c.fetchone()

        # Verificar si se encontró el usuario
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404

        # Convertir el resultado a diccionario y devolverlo
        # Los nombres de columna ya están renombrados por la consulta SQL
        return jsonify(dict(usuario)), 200

    except Exception as e:
        # Registrar error en el log
        logger.error(f"Error buscando usuario: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    # g.db se cierra automáticamente por app.after_request
