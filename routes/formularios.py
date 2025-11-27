# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                   MÓDULO DE GENERACIÓN DE FORMULARIOS PDF                 ║
║                                                                           ║
║  Autor: Sistema Montero - REESCRITO COMPLETAMENTE                        ║
║  Fecha: 25 de Noviembre de 2025                                          ║
║  Descripción: Generación de PDFs con datos dinámicos, checkboxes y      ║
║               firmas digitales estampadas usando pdfrw + reportlab       ║
║                                                                           ║
║  CARACTERÍSTICAS:                                                         ║
║  ✅ Mapeo de datos desde BD (sin "None")                                 ║
║  ✅ Checkboxes marcados correctamente (Sexo)                             ║
║  ✅ Firmas digitales estampadas                                          ║
║  ✅ Validación de datos                                                  ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""
import os
import io
import base64
import traceback
from datetime import datetime
from flask import Blueprint, jsonify, request, send_file, render_template
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
# ║                       CONFIGURACIÓN DE RUTAS                              ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

# RUTA BASE DE LOS EXPEDIENTES (Estructura de carpetas)
BASE_DIR = r"D:\Mi-App-React\MONTERO_NEGOCIO\MONTERO_TOTAL"


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                       FUNCIONES AUXILIARES                                ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

def val(v):
    """
    Helper para evitar que salga 'None' en el PDF.
    Convierte None a cadena vacía.
    
    Args:
        v: Valor a validar
        
    Returns:
        str: Valor convertido a string o cadena vacía
    """
    return str(v) if v is not None else ''


def buscar_ruta_firma(tipo, id_clave):
    """
    Busca el archivo PNG de la firma en la estructura de carpetas.
    
    Args:
        tipo (str): 'usuario' o 'empresa'
        id_clave (str): numeroId (usuario) o NIT (empresa)
        
    Returns:
        str|None: Ruta completa al archivo PNG o None si no existe
        
    Estructura esperada:
        USUARIOS/<numeroId>/firma_usuario.png
        EMPRESAS/<NIT_NOMBRE>/firma_representante.png
    """
    try:
        if tipo == 'usuario':
            # Ruta: .../USUARIOS/<id>/firma_usuario.png
            ruta = os.path.join(BASE_DIR, 'USUARIOS', str(id_clave), 'firma_usuario.png')
            if os.path.exists(ruta):
                logger.info(f"✅ Firma Usuario encontrada: {ruta}")
                return ruta
        
        elif tipo == 'empresa':
            # Ruta: .../EMPRESAS/<NIT_NOMBRE>/firma_representante.png
            ruta_empresas = os.path.join(BASE_DIR, 'EMPRESAS')
            if os.path.exists(ruta_empresas):
                # Buscar carpeta que empiece con el NIT
                for carpeta in os.listdir(ruta_empresas):
                    if carpeta.startswith(f"{id_clave}_"):
                        ruta = os.path.join(ruta_empresas, carpeta, 'firma_representante.png')
                        if os.path.exists(ruta):
                            logger.info(f"✅ Firma Empresa encontrada: {ruta}")
                            return ruta
    except Exception as e:
        logger.warning(f"⚠️ Error buscando firma {tipo}: {e}")
    
    logger.warning(f"❌ Firma {tipo} NO encontrada para ID: {id_clave}")
    return None


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                       RUTAS DE VISTAS HTML                                ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

@bp_formularios_pages.route("/")
@login_required
def index():
    """
    Ruta principal: Gestor de Afiliaciones (Dashboard)
    """
    return render_template("formularios/index.html")


@bp_formularios_pages.route("/gestion")
@login_required
def gestion():
    """
    Vista de gestión de formularios
    """
    return render_template("formularios/gestion.html")


@bp_formularios_pages.route("/generador")
@login_required
def generador():
    """
    Vista del generador de formularios PDF rellenables.
    Permite generar PDFs con datos dinámicos de usuarios y empresas.
    """
    return render_template("formularios/generador.html")


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                       ENDPOINTS API - GENERACIÓN PDF                      ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

@bp_formularios.route('/generar', methods=['POST'])
def generar_pdf():
    """
    Endpoint principal para generación de PDFs con datos dinámicos.
    
    Payload JSON esperado:
    {
        "usuario_id": 123,
        "empresa_nit": "900123456-1",
        "formulario_id": 1
    }
    
    Returns:
        PDF generado con datos, checkboxes y firmas estampadas
    """
    try:
        # ══════════════════════════════════════════════════════════════
        # 1. VALIDACIÓN DE DATOS DE ENTRADA
        # ══════════════════════════════════════════════════════════════
        data = request.get_json()
        usuario_id = data.get('usuario_id')
        empresa_nit = data.get('empresa_nit')
        formulario_id = data.get('formulario_id')

        if not all([usuario_id, empresa_nit, formulario_id]):
            logger.error("❌ Faltan parámetros obligatorios")
            return jsonify({'error': 'Faltan datos para generar el PDF (usuario_id, empresa_nit, formulario_id)'}), 400

        logger.info(f"📋 Generando PDF - Usuario: {usuario_id}, Empresa: {empresa_nit}, Formulario: {formulario_id}")

        # ══════════════════════════════════════════════════════════════
        # 2. OBTENER DATOS DE LA BASE DE DATOS
        # ══════════════════════════════════════════════════════════════
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row  # Acceso por nombre de columna
        
        # Consultar datos del usuario
        u = conn.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
        
        # Consultar datos de la empresa
        e = conn.execute("SELECT * FROM empresas WHERE nit = ?", (empresa_nit,)).fetchone()
        
        # Consultar ruta del formulario template
        f = conn.execute("SELECT ruta_archivo FROM formularios WHERE id = ?", (formulario_id,)).fetchone()
        
        conn.close()

        # Validar que existan los registros
        if not u:
            logger.error(f"❌ Usuario {usuario_id} no encontrado")
            return jsonify({'error': f'Usuario con ID {usuario_id} no encontrado'}), 404
        
        if not e:
            logger.error(f"❌ Empresa {empresa_nit} no encontrada")
            return jsonify({'error': f'Empresa con NIT {empresa_nit} no encontrada'}), 404
        
        if not f:
            logger.error(f"❌ Formulario {formulario_id} no encontrado")
            return jsonify({'error': f'Formulario con ID {formulario_id} no encontrado'}), 404

        template_path = f['ruta_archivo']
        if not os.path.exists(template_path):
            logger.error(f"❌ Plantilla PDF no existe: {template_path}")
            return jsonify({'error': 'El archivo plantilla PDF no existe en el servidor'}), 404

        logger.info(f"✅ Datos obtenidos correctamente. Template: {template_path}")

        # ══════════════════════════════════════════════════════════════
        # 3. PREPARAR DATOS PARA MAPEO (Normalización)
        # ══════════════════════════════════════════════════════════════
        
        # Normalizar valores de sexo (para checkboxes)
        sexo_bio = (u['sexoBiologico'] or '').lower().strip()
        sexo_iden = (u['sexoIdentificacion'] or '').lower().strip()

        logger.debug(f"🔍 Sexo Biológico: '{sexo_bio}', Sexo Identificación: '{sexo_iden}'")

        # Diccionario de mapeo de campos del PDF
        data_dict = {
            # ═══════════════════ DATOS DEL USUARIO ═══════════════════
            'tipo_id': val(u['tipoId']),
            'numero_id': val(u['numeroId']),
            'nombre1': val(u['primerNombre']),
            'nombre2': val(u['segundoNombre']),
            'apellido1': val(u['primerApellido']),
            'apellido2': val(u['segundoApellido']),
            'correo_usuario': val(u['correoElectronico']),
            'direccion': val(u['direccion']),
            'telefono_fijo': val(u['telefonoFijo']),
            'telefono_celular': val(u['telefonoCelular']),
            'comuna_barrio': val(u['comunaBarrio']),
            'departamento_nacimiento': val(u['departamentoNacimiento']),
            'municipio_nacimiento': val(u['municipioNacimiento']),
            'pais_nacionalidad': val(u['paisNacimiento']),
            'nacionalidad': val(u['nacionalidad']),
            'fecha_nacimiento': val(u['fechaNacimiento']),
            'afp_usuario': val(u['afpNombre']),
            
            # ═══════════════════ DATOS DE LA EMPRESA ═══════════════════
            'nombre_empresa': val(e['nombre_empresa']),
            'nit': val(e['nit']),
            'direccion_empresa': val(e['direccion_empresa']),
            'telefono_empresa': val(e['telefono_empresa']),
            'correo_empresa': val(e['correo_empresa']),
            'arl_empresa': val(e['arl_empresa']),
            'ibc_empresa': val(u['ibc']),  # IBC viene del usuario
            'departamento_empresa': val(e['departamento_empresa']),
            'ciudad_empresa': val(e['ciudad_empresa']),
            'fecha_ingreso': val(u['fechaIngreso']),
            'tipo_identificacion_empresa': 'NIT',

            # ═══════════════════ CHECKBOXES DE SEXO ═══════════════════
            # Valores válidos: PdfName('Yes') para marcado, PdfName('Off') para desmarcado
            'sexo_biologico_masculino': PdfName('Yes') if sexo_bio == 'masculino' else PdfName('Off'),
            'sexo_biologico_femenino': PdfName('Yes') if sexo_bio == 'femenino' else PdfName('Off'),
            'sexo_identificacion_masculino': PdfName('Yes') if sexo_iden == 'masculino' else PdfName('Off'),
            'sexo_identificacion_femenino': PdfName('Yes') if sexo_iden == 'femenino' else PdfName('Off'),
        }

        logger.info("✅ Diccionario de datos preparado")

        # ══════════════════════════════════════════════════════════════
        # 4. PROCESAMIENTO DEL PDF - CARGA DEL TEMPLATE
        # ══════════════════════════════════════════════════════════════
        template_pdf = PdfReader(template_path)
        logger.info(f"✅ Template PDF cargado. Páginas: {len(template_pdf.pages)}")

        # ══════════════════════════════════════════════════════════════
        # 5. ESTAMPADO DE FIRMAS (ReportLab Overlay)
        # ══════════════════════════════════════════════════════════════
        
        # Buscar rutas de firmas en el sistema de archivos
        ruta_firma_user = buscar_ruta_firma('usuario', u['numeroId'])
        ruta_firma_emp = buscar_ruta_firma('empresa', e['nit'])

        logger.info(f"🔍 Firmas detectadas - Usuario: {ruta_firma_user is not None}, Empresa: {ruta_firma_emp is not None}")

        if ruta_firma_user or ruta_firma_emp:
            logger.info("🖊️ Procesando firmas digitales...")
            
            # Diccionario para guardar firmas por página
            firmas_por_pagina = {}
            
            # Recorrer todas las páginas del PDF para buscar campos de firma
            for i, page in enumerate(template_pdf.pages):
                annotations = page.get('/Annots')
                if annotations:
                    for annot in annotations:
                        field_name_obj = annot.get('/T')
                        if field_name_obj:
                            # Extraer nombre del campo (quitar paréntesis de pdfrw)
                            key = str(field_name_obj)[1:-1]
                            rect = annot.get('/Rect')  # [x1, y1, x2, y2]
                            
                            img_path = None
                            
                            # Determinar qué firma usar según el nombre del campo
                            if key == 'firma_usuario' and ruta_firma_user:
                                img_path = ruta_firma_user
                                logger.info(f"📌 Campo firma_usuario encontrado en página {i+1}")
                            elif key == 'firma_empleador' and ruta_firma_emp:
                                img_path = ruta_firma_emp
                                logger.info(f"📌 Campo firma_empleador encontrado en página {i+1}")
                            
                            # Guardar info de firma si existe
                            if img_path and rect:
                                if i not in firmas_por_pagina:
                                    firmas_por_pagina[i] = []
                                firmas_por_pagina[i].append({
                                    'key': key,
                                    'path': img_path,
                                    'rect': rect
                                })
                                logger.debug(f"✓ Firma {key} agregada a página {i+1}")
            
            # Estampar firmas en cada página
            for page_num, firmas in firmas_por_pagina.items():
                try:
                    # Crear overlay temporal para esta página
                    packet = io.BytesIO()
                    can = canvas.Canvas(packet, pagesize=(float(template_pdf.pages[page_num].MediaBox[2]), 
                                                          float(template_pdf.pages[page_num].MediaBox[3])))
                    
                    for firma_info in firmas:
                        try:
                            x1, y1, x2, y2 = map(float, firma_info['rect'])
                            width = x2 - x1
                            height = y2 - y1
                            
                            can.drawImage(
                                firma_info['path'], 
                                x1, y1, 
                                width=width, 
                                height=height, 
                                mask='auto', 
                                preserveAspectRatio=True
                            )
                            logger.info(f"✅ Firma estampada: {firma_info['key']} en página {page_num+1} ({x1:.1f}, {y1:.1f}, {width:.1f}x{height:.1f})")
                        except Exception as img_err:
                            logger.error(f"❌ Error dibujando {firma_info['key']}: {img_err}")
                    
                    can.save()
                    packet.seek(0)
                    
                    # Fusionar overlay con la página correspondiente
                    overlay_pdf = PdfReader(packet)
                    PageMerge(template_pdf.pages[page_num]).add(overlay_pdf.pages[0]).render()
                    logger.info(f"✅ Firmas fusionadas en página {page_num+1}")
                    
                except Exception as page_err:
                    logger.error(f"❌ Error procesando página {page_num+1}: {page_err}")
        else:
            logger.info("ℹ️ No se encontraron firmas para estampar")

        # ══════════════════════════════════════════════════════════════
        # 6. RELLENADO DE CAMPOS DE TEXTO Y CHECKBOXES (pdfrw)
        # ══════════════════════════════════════════════════════════════
        
        # Habilitar NeedAppearances para que los campos se muestren
        if "/AcroForm" not in template_pdf.Root:
            template_pdf.Root.AcroForm = PdfDict()
        template_pdf.Root.AcroForm.update(PdfDict(NeedAppearances=PdfObject('true')))

        campos_rellenados = 0
        
        # Iterar sobre todas las páginas
        for page in template_pdf.pages:
            annotations = page.get('/Annots')
            if annotations:
                for annot in annotations:
                    field_name_obj = annot.get('/T')
                    if field_name_obj:
                        key = str(field_name_obj)[1:-1]
                        
                        if key in data_dict:
                            val_to_set = data_dict[key]
                            
                            # Diferenciar entre checkboxes y campos de texto
                            if isinstance(val_to_set, BasePdfName):
                                # Checkbox: Usar AS (Appearance State) y V (Value)
                                annot.update(PdfDict(AS=val_to_set, V=val_to_set))
                                logger.debug(f"✓ Checkbox '{key}' = {val_to_set}")
                            else:
                                # Campo de texto: Solo usar V (Value)
                                annot.update(PdfDict(V='{}'. format(val_to_set)))
                                logger.debug(f"✓ Campo '{key}' = '{val_to_set}'")
                            
                            campos_rellenados += 1

        logger.info(f"✅ {campos_rellenados} campos rellenados en el PDF")

        # ══════════════════════════════════════════════════════════════
        # 7. GUARDAR Y ENVIAR EL PDF GENERADO
        # ══════════════════════════════════════════════════════════════
        
        # Crear nombre de archivo único
        output_filename = f"Formulario_{u['numeroId']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Directorio temporal de salida
        output_dir = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), 'temp')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)
        
        # Escribir el PDF final
        PdfWriter().write(output_path, template_pdf)
        logger.info(f"✅ PDF generado exitosamente: {output_path}")

        # Enviar archivo como respuesta
        return send_file(
            output_path, 
            as_attachment=True, 
            download_name=output_filename,
            mimetype='application/pdf'
        )

    except Exception as e:
        logger.error(f"❌ Error CRÍTICO generando PDF: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                       ENDPOINTS API ADICIONALES                           ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

@bp_formularios.route('/listar', methods=['GET'])
def listar_formularios():
    """
    Listar todos los formularios disponibles en la base de datos
    """
    try:
        conn = get_db_connection()
        formularios = conn.execute("""
            SELECT id, nombre, descripcion, ruta_archivo, created_at
            FROM formularios
            ORDER BY created_at DESC
        """).fetchall()
        conn.close()

        return jsonify({
            'success': True,
            'formularios': [dict(row) for row in formularios]
        }), 200

    except Exception as e:
        logger.error(f"Error listando formularios: {e}")
        return jsonify({'error': str(e)}), 500


@bp_formularios.route('', methods=['GET'])
@bp_formularios.route('/', methods=['GET'])
def listar_formularios_simple():
    """
    Alias de /listar para compatibilidad con frontend (GET /api/formularios)
    """
    try:
        conn = get_db_connection()
        formularios = conn.execute("""
            SELECT id, nombre, descripcion, ruta_archivo, nombre_archivo, created_at
            FROM formularios
            ORDER BY created_at DESC
        """).fetchall()
        conn.close()

        return jsonify([dict(row) for row in formularios]), 200

    except Exception as e:
        logger.error(f"Error listando formularios: {e}")
        return jsonify({'error': str(e)}), 500


@bp_formularios.route('/importar', methods=['POST'])
def importar_formulario():
    """
    Importar un nuevo formulario PDF template al sistema
    """
    try:
        # Validar que llegue el archivo
        if 'archivo' not in request.files:
            return jsonify({'error': 'No se recibió ningún archivo'}), 400
        
        archivo = request.files['archivo']
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        
        if not archivo or archivo.filename == '':
            return jsonify({'error': 'Archivo vacío'}), 400
        
        if not nombre:
            return jsonify({'error': 'Debe proporcionar un nombre para el formulario'}), 400
        
        # Validar extensión PDF
        if not archivo.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Solo se permiten archivos PDF'}), 400
        
        # Crear directorio de templates si no existe
        templates_dir = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), 'formularios_templates')
        os.makedirs(templates_dir, exist_ok=True)
        
        # Generar nombre único para el archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_archivo = f"{nombre.replace(' ', '_')}_{timestamp}.pdf"
        ruta_archivo = os.path.join(templates_dir, nombre_archivo)
        
        # Guardar archivo
        archivo.save(ruta_archivo)
        logger.info(f"✅ Formulario guardado: {ruta_archivo}")
        
        # Insertar en base de datos
        conn = get_db_connection()
        cursor = conn.execute("""
            INSERT INTO formularios (nombre, descripcion, ruta_archivo, nombre_archivo, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
        """, (nombre, descripcion, ruta_archivo, nombre_archivo))
        conn.commit()
        formulario_id = cursor.lastrowid
        conn.close()
        
        logger.info(f"✅ Formulario registrado en BD con ID: {formulario_id}")
        
        return jsonify({
            'success': True,
            'message': 'Formulario importado correctamente',
            'id': formulario_id,
            'nombre': nombre,
            'ruta': ruta_archivo
        }), 201
        
    except Exception as e:
        logger.error(f"❌ Error importando formulario: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@bp_formularios.route('/<int:formulario_id>', methods=['DELETE'])
def eliminar_formulario(formulario_id):
    """
    Eliminar un formulario del sistema
    """
    try:
        conn = get_db_connection()
        
        # Obtener datos del formulario
        formulario = conn.execute("SELECT * FROM formularios WHERE id = ?", (formulario_id,)).fetchone()
        
        if not formulario:
            conn.close()
            return jsonify({'error': f'Formulario con ID {formulario_id} no encontrado'}), 404
        
        # Eliminar archivo físico si existe
        ruta_archivo = formulario['ruta_archivo']
        if os.path.exists(ruta_archivo):
            try:
                os.remove(ruta_archivo)
                logger.info(f"✅ Archivo eliminado: {ruta_archivo}")
            except Exception as file_err:
                logger.warning(f"⚠️ No se pudo eliminar archivo: {file_err}")
        
        # Eliminar de base de datos
        conn.execute("DELETE FROM formularios WHERE id = ?", (formulario_id,))
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Formulario ID {formulario_id} eliminado de BD")
        
        return jsonify({
            'success': True,
            'message': f'Formulario "{formulario["nombre"]}" eliminado correctamente'
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error eliminando formulario {formulario_id}: {e}")
        return jsonify({'error': str(e)}), 500


@bp_formularios.route('/verificar_firma/<tipo>/<id_clave>', methods=['GET'])
def verificar_firma(tipo, id_clave):
    """
    Verificar si existe una firma para un usuario o empresa
    
    Args:
        tipo: 'usuario' o 'empresa'
        id_clave: numeroId o NIT
    """
    try:
        ruta = buscar_ruta_firma(tipo, id_clave)
        
        return jsonify({
            'success': True,
            'existe': ruta is not None,
            'ruta': ruta if ruta else None
        }), 200

    except Exception as e:
        logger.error(f"Error verificando firma: {e}")
        return jsonify({'error': str(e)}), 500


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                       EXPORTACIÓN DE BLUEPRINTS                           ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

__all__ = ['bp_formularios', 'bp_formularios_pages', 'formularios']
