# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                   MÓDULO DE GENERACIÓN DE FORMULARIOS PDF                 ║
║                                                                           ║
║  Autor: Sistema Montero - Claude (Anthropic)                            ║
║  Fecha: 24 de Noviembre de 2025                                          ║
║  Descripción: Generación de PDFs con datos dinámicos, checkboxes y      ║
║               firmas digitales estampadas usando pdfrw + reportlab       ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import io
import os
import glob
from datetime import datetime
from flask import Blueprint, jsonify, request, send_file, render_template
from werkzeug.utils import secure_filename
from pdfrw import PdfReader, PdfWriter, PdfDict, PdfName, PdfObject, PageMerge
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from PIL import Image

from logger import logger

# ==================== IMPORTACIÓN DE UTILIDADES ====================
try:
    from ..utils import get_db_connection, login_required
except (ImportError, ValueError):
    from utils import get_db_connection, login_required

# ==================== BLUEPRINTS ====================
# Blueprint para vistas HTML (sin prefijo /api)
bp_formularios_pages = Blueprint("bp_formularios_pages", __name__, url_prefix="/formularios")

# Blueprint para API (con prefijo /api)
bp_formularios = Blueprint("bp_formularios", __name__, url_prefix="/api/formularios")
formularios = bp_formularios  # Alias para compatibilidad


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                       RUTAS DE VISTAS HTML                                ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

@bp_formularios_pages.route("/")
@login_required
def index():
    """
    Ruta principal: Gestor de Afiliaciones (Dashboard)
    Muestra la interfaz para gestionar documentos de EPS, ARL, Pensión y Caja.
    """
    return render_template("formularios/index.html")


@bp_formularios_pages.route("/generador")
@login_required
def generador():
    """
    Ruta del Generador de PDF Rellenable
    Muestra la interfaz antigua de generación de formularios PDF.
    Se abre en nueva pestaña desde el dashboard.
    """
    return render_template("formularios/generador.html")

# ==================== CONFIGURACIÓN ====================
BASE_MONTERO = r"D:\Mi-App-React\MONTERO_NEGOCIO\MONTERO_TOTAL"
TEMPLATE_PDF = os.path.join(os.path.dirname(__file__), "..", "assets", "templates", "formulario_afiliacion.pdf")
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), "..", "static", "uploads", "temp")

# Crear carpeta de salida si no existe
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                          HELPERS DE VALIDACIÓN                            ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

def val(v):
    """
    Valida y convierte valores a string seguro.
    
    Args:
        v: Valor a validar (puede ser None, int, str, etc.)
        
    Returns:
        str: String del valor o cadena vacía si es None
        
    Examples:
        >>> val(None)
        ''
        >>> val(123)
        '123'
        >>> val('Texto')
        'Texto'
    """
    return str(v) if v is not None else ""


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                    HELPERS DE BÚSQUEDA DE FIRMAS                          ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

def buscar_ruta_firma(tipo, id_o_nit):
    """
    Busca la ruta de la firma digital (imagen PNG) según el tipo.
    
    Args:
        tipo (str): 'usuario' o 'empresa'
        id_o_nit (str): Número de identificación del usuario o NIT de la empresa
        
    Returns:
        str or None: Ruta absoluta al archivo PNG de la firma, o None si no existe
        
    Examples:
        >>> buscar_ruta_firma('usuario', '123456789')
        'D:\\Mi-App-React\\MONTERO_NEGOCIO\\MONTERO_TOTAL\\USUARIOS\\123456789\\firma_usuario.png'

        >>> buscar_ruta_firma('empresa', '900123456')
        'D:\\Mi-App-React\\MONTERO_NEGOCIO\\MONTERO_TOTAL\\EMPRESAS\\900123456_MiEmpresa\\firma_representante.png'
    """
    try:
        if tipo.lower() == 'usuario':
            # Búsqueda en carpeta de usuario: USUARIOS/<id>/firma_usuario.png
            ruta_usuario = os.path.join(BASE_MONTERO, "USUARIOS", str(id_o_nit))
            ruta_firma = os.path.join(ruta_usuario, "firma_usuario.png")
            
            if os.path.exists(ruta_firma):
                logger.info(f"✅ Firma de usuario encontrada: {ruta_firma}")
                return ruta_firma
            else:
                logger.warning(f"⚠️ No se encontró firma_usuario.png en: {ruta_usuario}")
                return None
                
        elif tipo.lower() == 'empresa':
            # Búsqueda en carpeta de empresa: EMPRESAS/<nit>_*/firma_representante.png
            carpeta_empresas = os.path.join(BASE_MONTERO, "EMPRESAS")
            patron = os.path.join(carpeta_empresas, f"{id_o_nit}_*")
            carpetas_encontradas = glob.glob(patron)

            if not carpetas_encontradas:
                logger.warning(f"⚠️ No se encontró carpeta de empresa con NIT {id_o_nit}")
                return None

            # Usar la primera carpeta encontrada
            carpeta_empresa = carpetas_encontradas[0]
            ruta_firma = os.path.join(carpeta_empresa, "firma_representante.png")

            if os.path.exists(ruta_firma):
                logger.info(f"✅ Firma de empresa encontrada: {ruta_firma}")
                return ruta_firma
            else:
                logger.warning(f"⚠️ No se encontró firma_representante.png en: {carpeta_empresa}")
                return None
        else:
            logger.error(f"❌ Tipo de firma inválido: {tipo}. Use 'usuario' o 'empresa'")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error buscando firma {tipo} con ID/NIT {id_o_nit}: {e}", exc_info=True)
        return None


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                    HELPERS DE PROCESAMIENTO PDF                           ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

def obtener_coordenadas_campo(pdf_template, nombre_campo):
    """
    Extrae las coordenadas del campo especificado en el PDF.
    
    Args:
        pdf_template (PdfReader): PDF template leído con pdfrw
        nombre_campo (str): Nombre del campo a buscar (ej: 'firma_usuario')
        
    Returns:
        dict or None: {'x': float, 'y': float, 'width': float, 'height': float} o None
    """
    try:
        for page in pdf_template.pages:
            annotations = page.get('/Annots')
            if annotations is None:
                continue
                
            for annotation in annotations:
                field_name = annotation.get('/T')
                if field_name and field_name.strip('()') == nombre_campo:
                    rect = annotation.get('/Rect')
                    if rect:
                        # /Rect es [x1, y1, x2, y2]
                        x1, y1, x2, y2 = [float(r) for r in rect]
                        return {
                            'x': x1,
                            'y': y1,
                            'width': x2 - x1,
                            'height': y2 - y1
                        }
        
        logger.warning(f"⚠️ No se encontró el campo '{nombre_campo}' en el PDF")
        return None
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo coordenadas del campo '{nombre_campo}': {e}", exc_info=True)
        return None


def estampar_firma_en_overlay(c, imagen_path, coords, page_height):
    """
    Dibuja una imagen de firma en el canvas de reportlab.
    
    Args:
        c (canvas.Canvas): Canvas de reportlab
        imagen_path (str): Ruta a la imagen PNG
        coords (dict): Coordenadas {'x', 'y', 'width', 'height'}
        page_height (float): Altura total de la página (para conversión de coordenadas)
    """
    try:
        if not imagen_path or not os.path.exists(imagen_path):
            logger.warning(f"⚠️ Imagen no encontrada: {imagen_path}")
            return
            
        # Abrir imagen con PIL para obtener dimensiones
        img = Image.open(imagen_path)
        img_width, img_height = img.size
        
        # Calcular aspect ratio
        aspect_ratio = img_width / img_height
        
        # Ajustar tamaño al 90% del campo para dejar margen
        campo_width = coords['width'] * 0.9
        campo_height = coords['height'] * 0.9
        
        # Calcular dimensiones manteniendo aspect ratio
        if (campo_width / campo_height) > aspect_ratio:
            # Limitado por altura
            new_height = campo_height
            new_width = campo_height * aspect_ratio
        else:
            # Limitado por ancho
            new_width = campo_width
            new_height = campo_width / aspect_ratio
        
        # Centrar la imagen en el campo
        offset_x = (coords['width'] - new_width) / 2
        offset_y = (coords['height'] - new_height) / 2
        
        # Convertir coordenadas PDF a coordenadas reportlab
        # PDF: origen abajo-izquierda, reportlab: igual
        x = coords['x'] + offset_x
        y = coords['y'] + offset_y
        
        # Dibujar imagen
        c.drawImage(
            imagen_path,
            x, y,
            width=new_width,
            height=new_height,
            preserveAspectRatio=True,
            mask='auto'
        )
        
        logger.info(f"✅ Firma estampada en ({x:.2f}, {y:.2f}) con tamaño {new_width:.2f}x{new_height:.2f}")
        
    except Exception as e:
        logger.error(f"❌ Error estampando firma: {e}", exc_info=True)


def crear_overlay_firmas(pdf_template, firma_usuario_path, firma_empresa_path):
    """
    Crea un PDF overlay con las firmas digitales usando reportlab.
    
    Args:
        pdf_template (PdfReader): Template PDF leído con pdfrw
        firma_usuario_path (str or None): Ruta a firma del usuario
        firma_empresa_path (str or None): Ruta a firma de la empresa
        
    Returns:
        io.BytesIO or None: Buffer con el PDF overlay, o None si no hay firmas
    """
    try:
        # Verificar si hay al menos una firma
        if not firma_usuario_path and not firma_empresa_path:
            logger.info("ℹ️ No hay firmas para estampar")
            return None
        
        # Obtener dimensiones de la página
        page = pdf_template.pages[0]
        media_box = page.get('/MediaBox')
        if media_box:
            page_width = float(media_box[2]) - float(media_box[0])
            page_height = float(media_box[3]) - float(media_box[1])
        else:
            # Usar Letter como fallback
            page_width, page_height = letter
        
        logger.info(f"📄 Dimensiones de página: {page_width}x{page_height}")
        
        # Crear buffer en memoria
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=(page_width, page_height))
        
        # Estampar firma de usuario
        if firma_usuario_path:
            coords_usuario = obtener_coordenadas_campo(pdf_template, 'firma_usuario')
            if coords_usuario:
                logger.info(f"📍 Coordenadas firma_usuario: {coords_usuario}")
                estampar_firma_en_overlay(c, firma_usuario_path, coords_usuario, page_height)
            else:
                logger.warning("⚠️ No se encontraron coordenadas para 'firma_usuario'")
        
        # Estampar firma de empresa
        if firma_empresa_path:
            coords_empresa = obtener_coordenadas_campo(pdf_template, 'firma_empleador')
            if coords_empresa:
                logger.info(f"📍 Coordenadas firma_empleador: {coords_empresa}")
                estampar_firma_en_overlay(c, firma_empresa_path, coords_empresa, page_height)
            else:
                logger.warning("⚠️ No se encontraron coordenadas para 'firma_empleador'")
        
        # Finalizar canvas
        c.save()
        buffer.seek(0)
        
        logger.info("✅ Overlay de firmas creado exitosamente")
        return buffer
        
    except Exception as e:
        logger.error(f"❌ Error creando overlay de firmas: {e}", exc_info=True)
        return None


def fusionar_overlay_con_pdf(pdf_original, overlay_buffer):
    """
    Fusiona el overlay de firmas con el PDF original usando pdfrw.
    
    Args:
        pdf_original (PdfReader): PDF original con campos rellenados
        overlay_buffer (io.BytesIO): Buffer con el overlay de reportlab
        
    Returns:
        PdfReader: PDF fusionado
    """
    try:
        # Leer overlay
        overlay_pdf = PdfReader(overlay_buffer)
        overlay_page = overlay_pdf.pages[0]
        
        # Fusionar con la primera página del original
        merger = PageMerge(pdf_original.pages[0])
        merger.add(overlay_page).render()
        
        logger.info("✅ Overlay fusionado con PDF original")
        return pdf_original
        
    except Exception as e:
        logger.error(f"❌ Error fusionando overlay: {e}", exc_info=True)
        return pdf_original


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                    RUTAS DE GESTIÓN DE FORMULARIOS                        ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

@bp_formularios.route("", methods=["GET"])
@bp_formularios.route("/", methods=["GET"])
def listar_formularios():
    """
    Lista todos los formularios PDF disponibles en la base de datos.
    
    Returns:
        200: Lista de formularios en formato JSON
        500: Error interno del servidor
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, nombre, descripcion, ruta_archivo, created_at, updated_at
            FROM formularios
            ORDER BY created_at DESC
        """)
        
        formularios = []
        for row in cursor.fetchall():
            formularios.append({
                'id': row[0],
                'nombre': row[1],
                'descripcion': row[2],
                'ruta_archivo': row[3],
                'created_at': row[4],
                'updated_at': row[5]
            })
        
        conn.close()
        
        logger.info(f"✅ Se listaron {len(formularios)} formularios")
        return jsonify(formularios), 200
        
    except Exception as e:
        logger.error(f"❌ Error listando formularios: {e}", exc_info=True)
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@bp_formularios.route("/importar", methods=["POST"])
def importar_formulario():
    """
    Importa un nuevo template PDF a la base de datos.
    
    Form Data esperado:
        - file o archivo: Archivo PDF
        - nombre: Nombre del formulario
        - descripcion: Descripción opcional
        
    Returns:
        201: Formulario importado exitosamente
        400: Error en validación
        500: Error interno del servidor
    """
    try:
        # Validar archivo (aceptar 'file' o 'archivo')
        file = request.files.get('file') or request.files.get('archivo')
        
        if not file:
            return jsonify({"error": "No se recibió ningún archivo"}), 400
        
        if file.filename == '':
            return jsonify({"error": "Archivo vacío"}), 400
        
        if not file.filename.endswith('.pdf'):
            return jsonify({"error": "Solo se permiten archivos PDF"}), 400
        
        # Validar datos
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        
        if not nombre:
            return jsonify({"error": "Se requiere un nombre para el formulario"}), 400
        
        # Guardar archivo
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_final = f"{timestamp}_{filename}"
        
        templates_folder = os.path.join(os.path.dirname(__file__), "..", "assets", "templates")
        os.makedirs(templates_folder, exist_ok=True)
        
        file_path = os.path.join(templates_folder, filename_final)
        file.save(file_path)
        
        logger.info(f"✅ Archivo guardado en: {file_path}")
        
        # Guardar en base de datos
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO formularios (nombre, descripcion, ruta_archivo, created_at, updated_at)
            VALUES (?, ?, ?, datetime('now'), datetime('now'))
        """, (nombre, descripcion, file_path))
        
        formulario_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Formulario importado con ID: {formulario_id}")
        
        return jsonify({
            "message": "Formulario importado exitosamente",
            "id": formulario_id,
            "nombre": nombre,
            "ruta_archivo": file_path
        }), 201
        
    except Exception as e:
        logger.error(f"❌ Error importando formulario: {e}", exc_info=True)
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@bp_formularios.route("/<int:formulario_id>", methods=["DELETE"])
def eliminar_formulario(formulario_id):
    """
    Elimina un formulario de la base de datos.
    
    Args:
        formulario_id (int): ID del formulario a eliminar
        
    Returns:
        200: Formulario eliminado exitosamente
        404: Formulario no encontrado
        500: Error interno del servidor
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que existe
        cursor.execute("SELECT ruta_archivo FROM formularios WHERE id = ?", (formulario_id,))
        formulario = cursor.fetchone()
        
        if not formulario:
            conn.close()
            return jsonify({"error": f"Formulario {formulario_id} no encontrado"}), 404
        
        # Eliminar archivo físico si existe
        ruta_archivo = formulario[0]
        if ruta_archivo and os.path.exists(ruta_archivo):
            try:
                os.remove(ruta_archivo)
                logger.info(f"✅ Archivo eliminado: {ruta_archivo}")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo eliminar el archivo: {e}")
        
        # Eliminar de BD
        cursor.execute("DELETE FROM formularios WHERE id = ?", (formulario_id,))
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Formulario {formulario_id} eliminado de BD")
        
        return jsonify({"message": "Formulario eliminado exitosamente"}), 200
        
    except Exception as e:
        logger.error(f"❌ Error eliminando formulario: {e}", exc_info=True)
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                    RUTA: SUBIR CONSTANCIA EXTERNA                         ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

@bp_formularios.route("/subir_constancia", methods=["POST"])
def subir_constancia():
    """
    Sube una constancia de afiliación (ARL, EPS, CAJA, PENSIÓN) para un usuario.
    
    Form Data esperado:
        - usuario_id: ID del usuario
        - tipo_entidad: 'EPS', 'ARL', 'PENSION', 'CAJA'
        - archivo: Archivo PDF de la constancia
        
    Returns:
        201: Constancia subida exitosamente
        400: Error en validación o usuario sin empresa
        404: Usuario no encontrado
        500: Error interno del servidor
    """
    try:
        # ═══════════════════════════════════════════════════════════════════
        # DICCIONARIO DE MESES EN ESPAÑOL (para nomenclatura del archivo)
        # ═══════════════════════════════════════════════════════════════════
        MESES = {
            1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
            5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
            9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
        }
        
        # ═══════════════════════════════════════════════════════════════════
        # FASE 1: VALIDACIÓN DE DATOS
        # ═══════════════════════════════════════════════════════════════════
        
        # Validar usuario_id
        usuario_id = request.form.get('usuario_id')
        if not usuario_id:
            return jsonify({"error": "Se requiere usuario_id"}), 400
        
        try:
            usuario_id = int(usuario_id)
        except ValueError:
            return jsonify({"error": "usuario_id debe ser un número"}), 400
        
        # Validar tipo_entidad
        tipo_entidad = request.form.get('tipo_entidad', '').strip().upper()
        entidades_validas = ['EPS', 'ARL', 'PENSION', 'CAJA']
        
        if tipo_entidad not in entidades_validas:
            return jsonify({
                "error": f"tipo_entidad debe ser uno de: {', '.join(entidades_validas)}"
            }), 400
        
        # Validar archivo
        archivo = request.files.get('archivo')
        
        if not archivo:
            return jsonify({"error": "No se recibió ningún archivo"}), 400
        
        if archivo.filename == '':
            return jsonify({"error": "Archivo vacío"}), 400
        
        if not archivo.filename.lower().endswith('.pdf'):
            return jsonify({"error": "Solo se permiten archivos PDF"}), 400
        
        logger.info(f"📤 Subiendo constancia {tipo_entidad} para usuario {usuario_id}")
        
        # ═══════════════════════════════════════════════════════════════════
        # FASE 2: BUSCAR USUARIO Y OBTENER numeroId + empresa_nit
        # ═══════════════════════════════════════════════════════════════════
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT numeroId, empresa_nit 
            FROM usuarios 
            WHERE id = ?
        """, (usuario_id,))
        usuario = cursor.fetchone()
        
        if not usuario:
            conn.close()
            return jsonify({"error": f"Usuario {usuario_id} no encontrado"}), 404
        
        numero_id = usuario[0]
        empresa_nit = usuario[1]
        
        # VALIDACIÓN: Usuario debe tener empresa asignada
        if not empresa_nit:
            conn.close()
            return jsonify({
                "error": "El usuario no tiene empresa asignada. Asigne una empresa antes de subir constancias."
            }), 400
        
        logger.info(f"✅ Usuario encontrado: numeroId={numero_id}, empresa_nit={empresa_nit}")
        
        # Obtener nombre de la empresa
        cursor.execute("SELECT nombre_empresa FROM empresas WHERE nit = ?", (empresa_nit,))
        empresa = cursor.fetchone()
        
        if not empresa:
            conn.close()
            return jsonify({"error": f"Empresa con NIT {empresa_nit} no encontrada"}), 404
        
        nombre_empresa = empresa[0]
        logger.info(f"✅ Empresa encontrada: {nombre_empresa}")
        
        # ═══════════════════════════════════════════════════════════════════
        # FASE 3: CONSTRUCCIÓN DE RUTA DE GUARDADO
        # ═══════════════════════════════════════════════════════════════════
        
        # Ruta base absoluta
        BASE_DIR = r"D:\Mi-App-React\MONTERO_NEGOCIO\MONTERO_TOTAL\USUARIOS"
        
        # Sanitizar nombre de empresa (reemplazar caracteres especiales)
        nombre_empresa_sanitizado = nombre_empresa.replace(' ', '_').replace('.', '').replace('/', '_')
        nombre_empresa_sanitizado = ''.join(c for c in nombre_empresa_sanitizado if c.isalnum() or c == '_')
        
        # Estructura: BASE / <numeroId> / EMPRESAS_AFILIADAS / <nombre_empresa_sanitizado> /
        carpeta_destino = os.path.join(
            BASE_DIR,
            str(numero_id),
            "EMPRESAS_AFILIADAS",
            nombre_empresa_sanitizado
        )
        
        # Crear carpetas si no existen
        os.makedirs(carpeta_destino, exist_ok=True)
        logger.info(f"📁 Carpeta creada/verificada: {carpeta_destino}")
        
        # ═══════════════════════════════════════════════════════════════════
        # FASE 4: NOMBRE DEL ARCHIVO (Nomenclatura)
        # ═══════════════════════════════════════════════════════════════════
        
        # Obtener mes y año actual
        fecha_actual = datetime.now()
        mes_numero = fecha_actual.month
        anio = fecha_actual.year
        
        # Obtener nombre del mes en español
        nombre_mes = MESES.get(mes_numero, 'mes')
        
        # Formato: [tipo_entidad] [nombre_mes] [año].pdf
        # Ejemplo: arl noviembre 2025.pdf
        nombre_archivo = f"{tipo_entidad.lower()} {nombre_mes} {anio}.pdf"
        ruta_completa = os.path.join(carpeta_destino, nombre_archivo)
        
        # Para BD: "noviembre 2025"
        mes_anio = f"{nombre_mes} {anio}"
        
        logger.info(f"📄 Nombre de archivo: {nombre_archivo}")
        
        # ═══════════════════════════════════════════════════════════════════
        # FASE 5: GUARDAR ARCHIVO FÍSICO
        # ═══════════════════════════════════════════════════════════════════
        archivo.save(ruta_completa)
        logger.info(f"💾 Archivo guardado en: {ruta_completa}")
        
        # ═══════════════════════════════════════════════════════════════════
        # FASE 6: INSERTAR EN BASE DE DATOS (afiliaciones)
        # ═══════════════════════════════════════════════════════════════════
        
        # Verificar si ya existe un registro para este mes/año
        cursor.execute("""
            SELECT id FROM afiliaciones 
            WHERE usuario_id = ? 
            AND tipo_entidad = ? 
            AND mes_anio = ?
        """, (usuario_id, tipo_entidad, mes_anio))
        
        registro_existente = cursor.fetchone()
        
        if registro_existente:
            # UPDATE: Actualizar registro existente
            cursor.execute("""
                UPDATE afiliaciones 
                SET estado = 'COMPLETADO',
                    ruta_archivo = ?,
                    empresa_nit = ?,
                    fecha_actualizacion = datetime('now')
                WHERE usuario_id = ? 
                AND tipo_entidad = ?
                AND mes_anio = ?
            """, (ruta_completa, empresa_nit, usuario_id, tipo_entidad, mes_anio))
            
            logger.info(f"🔄 Registro actualizado en afiliaciones")
        else:
            # INSERT: Crear nuevo registro
            cursor.execute("""
                INSERT INTO afiliaciones (
                    usuario_id, 
                    tipo_entidad, 
                    empresa_nit, 
                    mes_anio, 
                    ruta_archivo, 
                    estado
                )
                VALUES (?, ?, ?, ?, ?, 'COMPLETADO')
            """, (usuario_id, tipo_entidad, empresa_nit, mes_anio, ruta_completa))
            
            logger.info(f"➕ Nuevo registro creado en afiliaciones")
        
        conn.commit()
        conn.close()
        
        # ═══════════════════════════════════════════════════════════════════
        # FASE 7: RESPUESTA EXITOSA
        # ═══════════════════════════════════════════════════════════════════
        return jsonify({
            "message": f"Constancia de {tipo_entidad} subida exitosamente",
            "usuario_id": usuario_id,
            "tipo_entidad": tipo_entidad,
            "empresa_nit": empresa_nit,
            "empresa_nombre": nombre_empresa,
            "mes_anio": mes_anio,
            "estado": "COMPLETADO",
            "ruta_archivo": ruta_completa,
            "nombre_archivo": nombre_archivo
        }), 201
        
    except Exception as e:
        logger.error(f"❌ Error subiendo constancia: {e}", exc_info=True)
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


@bp_formularios.route("/estado_afiliaciones/<int:usuario_id>", methods=["GET"])
def obtener_estado_afiliaciones(usuario_id):
    """
    Obtiene el estado de todas las afiliaciones de un usuario.
    
    Args:
        usuario_id (int): ID del usuario
        
    Returns:
        200: Estado de afiliaciones en formato JSON
        404: Usuario no encontrado
        500: Error interno del servidor
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que el usuario existe
        cursor.execute("SELECT id FROM usuarios WHERE id = ?", (usuario_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": f"Usuario {usuario_id} no encontrado"}), 404
        
        # Obtener todas las afiliaciones
        cursor.execute("""
            SELECT tipo_entidad, estado, ruta_archivo, fecha_actualizacion
            FROM afiliaciones
            WHERE usuario_id = ?
            ORDER BY tipo_entidad
        """, (usuario_id,))
        
        afiliaciones = []
        for row in cursor.fetchall():
            afiliaciones.append({
                'tipo_entidad': row[0],
                'estado': row[1],
                'ruta_archivo': row[2],
                'fecha_actualizacion': row[3],
                'tiene_documento': row[2] is not None and os.path.exists(row[2]) if row[2] else False
            })
        
        conn.close()
        
        # Crear estructura completa con todas las entidades
        entidades = ['EPS', 'ARL', 'PENSION', 'CAJA']
        resultado = {}
        
        for entidad in entidades:
            afiliacion = next((a for a in afiliaciones if a['tipo_entidad'] == entidad), None)
            if afiliacion:
                resultado[entidad] = afiliacion
            else:
                resultado[entidad] = {
                    'tipo_entidad': entidad,
                    'estado': 'PENDIENTE',
                    'ruta_archivo': None,
                    'fecha_actualizacion': None,
                    'tiene_documento': False
                }
        
        logger.info(f"✅ Estado de afiliaciones obtenido para usuario {usuario_id}")
        return jsonify(resultado), 200
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo estado de afiliaciones: {e}", exc_info=True)
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                       RUTA PRINCIPAL: /generar                            ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

@bp_formularios.route("/generar", methods=["POST"])
def generar_formulario():
    """
    Genera un PDF de formulario de afiliación con datos del usuario, empresa y firmas.
    
    Body JSON esperado:
        {
            "formulario_id": 1,  # ID del template en la BD (opcional, usa el primero si no se especifica)
            "usuario_id": 10,    # ID interno del usuario
            "empresa_nit": "900123456"
        }
        
    Returns:
        200: Archivo PDF generado
        400: Error en validación de datos
        404: Usuario, empresa o formulario no encontrados
        500: Error interno del servidor
    """
    try:
        # ═══════════════════════════════════════════════════════════════════
        # FASE 1: VALIDACIÓN DE REQUEST
        # ═══════════════════════════════════════════════════════════════════
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400
        
        formulario_id = data.get("formulario_id")
        formulario_id = data.get("formulario_id")
        usuario_id = data.get("usuario_id")
        empresa_nit = data.get("empresa_nit")
        
        if not usuario_id or not empresa_nit:
            return jsonify({"error": "Se requieren usuario_id y empresa_nit"}), 400
        
        logger.info(f"🔄 Generando formulario para Usuario: {usuario_id}, Empresa: {empresa_nit}")
        
        # ═══════════════════════════════════════════════════════════════════
        # FASE 2: CONSULTA A BASE DE DATOS
        # ═══════════════════════════════════════════════════════════════════
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener ruta del template PDF
        if formulario_id:
            cursor.execute("SELECT ruta_archivo FROM formularios WHERE id = ?", (formulario_id,))
            formulario = cursor.fetchone()
            if not formulario:
                conn.close()
                return jsonify({"error": f"Formulario {formulario_id} no encontrado"}), 404
            template_pdf = formulario[0]
        else:
            # Si no se especifica, usar el primero disponible
            cursor.execute("SELECT ruta_archivo FROM formularios ORDER BY id LIMIT 1")
            formulario = cursor.fetchone()
            if not formulario:
                conn.close()
                return jsonify({"error": "No hay templates PDF disponibles. Importe uno primero."}), 404
            template_pdf = formulario[0]
        
        logger.info(f"📄 Template seleccionado: {template_pdf}")
        
        # Consultar datos del usuario (por ID interno de la tabla)
        cursor.execute("""
            SELECT 
                tipoId, numeroId, primerNombre, segundoNombre, 
                primerApellido, segundoApellido, correoElectronico,
                direccion, telefonoFijo, telefonoCelular, comunaBarrio,
                municipioNacimiento, departamentoNacimiento, fechaNacimiento,
                nacionalidad, paisNacimiento, afpNombre, sexoBiologico,
                sexoIdentificacion, fechaIngreso
            FROM usuarios
            WHERE id = ?
        """, (usuario_id,))
        
        usuario = cursor.fetchone()
        
        if not usuario:
            conn.close()
            return jsonify({"error": f"Usuario {usuario_id} no encontrado"}), 404
        
        # Consultar datos de la empresa
        cursor.execute("""
            SELECT 
                nombre_empresa, nit, tipo_identificacion_empresa,
                direccion_empresa, telefono_empresa, correo_empresa,
                afp_empresa, arl_empresa, ibc_empresa,
                departamento_empresa, ciudad_empresa
            FROM empresas
            WHERE nit = ?
        """, (empresa_nit,))
        
        empresa = cursor.fetchone()
        conn.close()
        
        if not empresa:
            return jsonify({"error": f"Empresa {empresa_nit} no encontrada"}), 404
        
        logger.info("✅ Datos de usuario y empresa obtenidos de BD")
        
        # Extraer numeroId para búsqueda de firma
        numero_id = usuario[1]  # numeroId está en la posición 1 del SELECT
        
        # ═══════════════════════════════════════════════════════════════════
        # FASE 3: BÚSQUEDA DE FIRMAS DIGITALES
        # ═══════════════════════════════════════════════════════════════════
        firma_usuario = buscar_ruta_firma('usuario', numero_id)
        firma_empresa = buscar_ruta_firma('empresa', empresa_nit)
        
        # ═══════════════════════════════════════════════════════════════════
        # FASE 4: CONSTRUCCIÓN DEL DICCIONARIO DE DATOS
        # ═══════════════════════════════════════════════════════════════════
        
        # Normalizar valores de sexo para checkboxes
        sexo_bio = val(usuario[17]).lower().strip()  # sexoBiologico
        sexo_ident = val(usuario[18]).lower().strip()  # sexoIdentificacion
        
        data_dict = {
            # === DATOS PERSONALES ===
            'tipo_id': val(usuario[0]),
            'numero_id': val(usuario[1]),
            'nombre1': val(usuario[2]),
            'nombre2': val(usuario[3]),
            'apellido1': val(usuario[4]),
            'apellido2': val(usuario[5]),
            'correo_usuario': val(usuario[6]),
            'direccion': val(usuario[7]),
            'telefono_fijo': val(usuario[8]),
            'telefono_celular': val(usuario[9]),
            'comuna_barrio': val(usuario[10]),
            
            # === DATOS DE NACIMIENTO ===
            'municipio_nacimiento': val(usuario[11]),
            'departamento_nacimiento': val(usuario[12]),
            'fecha_nacimiento': val(usuario[13]),
            'nacionalidad': val(usuario[14]),
            'pais_nacionalidad': val(usuario[15]),
            
            # === DATOS LABORALES ===
            'afp_usuario': val(usuario[16]),
            'fecha_ingreso': val(usuario[19]),
            
            # === CHECKBOXES DE SEXO BIOLÓGICO ===
            'sexo_biologico_masculino': PdfName('Yes') if sexo_bio == 'masculino' else PdfName('Off'),
            'sexo_biologico_femenino': PdfName('Yes') if sexo_bio == 'femenino' else PdfName('Off'),
            
            # === CHECKBOXES DE SEXO IDENTIFICACIÓN ===
            'sexo_identificacion_masculino': PdfName('Yes') if sexo_ident == 'masculino' else PdfName('Off'),
            'sexo_identificacion_femenino': PdfName('Yes') if sexo_ident == 'femenino' else PdfName('Off'),
            
            # === DATOS DE EMPRESA ===
            'nombre_empresa': val(empresa[0]),
            'nit': val(empresa[1]),
            'tipo_identificacion_empresa': 'NIT',  # Valor fijo
            'direccion_empresa': val(empresa[3]),
            'telefono_empresa': val(empresa[4]),
            'correo_empresa': val(empresa[5]),
            'afp_empresa': val(empresa[6]),
            'arl_empresa': val(empresa[7]) if empresa[7] else 'SURA',
            'ibc_empresa': val(empresa[8]),
            'departamento_empresa': val(empresa[9]),
            'ciudad_empresa': val(empresa[10]),
        }
        
        logger.info(f"✅ Diccionario de datos construido con {len(data_dict)} campos")
        
        # ═══════════════════════════════════════════════════════════════════
        # FASE 5: CARGA DEL TEMPLATE PDF
        # ═══════════════════════════════════════════════════════════════════
        if not os.path.exists(template_pdf):
            return jsonify({"error": f"Template PDF no encontrado: {template_pdf}"}), 500
        
        pdf_template = PdfReader(template_pdf)
        logger.info(f"✅ Template PDF cargado: {template_pdf}")
        
        # ═══════════════════════════════════════════════════════════════════
        # FASE 6: RELLENADO DE CAMPOS DE TEXTO Y CHECKBOXES
        # ═══════════════════════════════════════════════════════════════════
        campos_rellenados = 0
        checkboxes_marcados = 0
        
        for page in pdf_template.pages:
            annotations = page.get('/Annots')
            if annotations is None:
                continue
            
            for annotation in annotations:
                field_name = annotation.get('/T')
                if not field_name:
                    continue
                
                field_name = field_name.strip('()')
                
                if field_name in data_dict:
                    field_value = data_dict[field_name]
                    
                    # Determinar si es checkbox o campo de texto
                    # Los checkboxes usan PdfName, que en pdfrw se representa como string con /
                    if hasattr(field_value, '__class__') and field_value.__class__.__name__ == 'PdfName':
                        # Es un checkbox
                        annotation.update(PdfDict(V=field_value, AS=field_value))
                        checkboxes_marcados += 1
                    else:
                        # Es campo de texto
                        annotation.update(PdfDict(V=field_value, AP=PdfDict()))
                        campos_rellenados += 1
        
        logger.info(f"✅ Campos rellenados: {campos_rellenados}, Checkboxes marcados: {checkboxes_marcados}")
        
        # ═══════════════════════════════════════════════════════════════════
        # FASE 7: ESTAMPADO DE FIRMAS DIGITALES
        # ═══════════════════════════════════════════════════════════════════
        if firma_usuario or firma_empresa:
            overlay_buffer = crear_overlay_firmas(pdf_template, firma_usuario, firma_empresa)
            
            if overlay_buffer:
                pdf_template = fusionar_overlay_con_pdf(pdf_template, overlay_buffer)
                logger.info("✅ Firmas digitales estampadas correctamente")
        else:
            logger.warning("⚠️ No se encontraron firmas para estampar")
        
        # ═══════════════════════════════════════════════════════════════════
        # FASE 8: ACTIVAR NEEDAPPEARANCES Y GUARDAR PDF
        # ═══════════════════════════════════════════════════════════════════
        if '/AcroForm' in pdf_template.Root:
            pdf_template.Root.AcroForm.update(PdfDict(NeedAppearances=PdfObject('true')))
        
        # Generar nombre único para el archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"formulario_{usuario_id}_{empresa_nit}_{timestamp}.pdf"
        output_path = os.path.join(OUTPUT_FOLDER, filename)
        
        # Guardar PDF
        PdfWriter(output_path, trailer=pdf_template).write()
        logger.info(f"✅ PDF guardado en: {output_path}")
        
        # ═══════════════════════════════════════════════════════════════════
        # FASE 9: ENVÍO DEL ARCHIVO AL CLIENTE
        # ═══════════════════════════════════════════════════════════════════
        return send_file(
            output_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"❌ Error generando formulario: {e}", exc_info=True)
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                          RUTA DE DIAGNÓSTICO                              ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

@bp_formularios.route("/diagnostico", methods=["GET"])
def diagnostico():
    """
    Endpoint de diagnóstico para verificar configuración del módulo.
    
    Returns:
        JSON con información de configuración y estado
    """
    return jsonify({
        "modulo": "formularios",
        "version": "2.0.0",
        "fecha_reescritura": "2025-11-24",
        "configuracion": {
            "base_montero": BASE_MONTERO,
            "template_pdf": TEMPLATE_PDF,
            "output_folder": OUTPUT_FOLDER,
            "template_existe": os.path.exists(TEMPLATE_PDF),
            "output_folder_existe": os.path.exists(OUTPUT_FOLDER)
        },
        "rutas_verificadas": {
            "usuarios": os.path.exists(os.path.join(BASE_MONTERO, "USUARIOS")),
            "empresas": os.path.exists(os.path.join(BASE_MONTERO, "EMPRESAS"))
        }
    }), 200


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                          EXPORTACIÓN DEL MÓDULO                           ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

__all__ = ['bp_formularios', 'formularios']
