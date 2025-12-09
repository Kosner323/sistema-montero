# -*- coding: utf-8 -*-
"""
Blueprint para la gestión de Empresas.
Permite el CRUD (Crear, Leer, Actualizar, Eliminar) de las entidades de empresa
en el sistema.
"""

import base64
import os
import re
import sqlite3
import traceback
from datetime import datetime

from flask import Blueprint, current_app, g, jsonify, request, session
from pydantic import ValidationError

# (CORREGIDO: Importa la instancia global 'logger')
from logger import logger
from models.validation_models import EmpresaCreate, EmpresaUpdate
from utils import (
    get_db_connection,
    login_required,
    format_key,
    log_file_upload,
    validate_upload,
    sanitize_and_save_file
)

# --- Configuración del Blueprint ---
# (CORREGIDO: No es necesario llamar a get_logger())
# logger = get_logger(__name__)

# El nombre del blueprint SÍ ES 'empresas_bp'
empresas_bp = Blueprint("empresas", __name__, url_prefix="/api/empresas")

# ==================== CONFIGURACIÓN DE RUTAS ====================
RUTA_BASE_EXPEDIENTES = r"D:\Mi-App-React\MONTERO_NEGOCIO\MONTERO_TOTAL\EMPRESAS"


# ==================== FUNCIÓN AUXILIAR: GENERAR EXPEDIENTE EMPRESA ====================
def generar_expediente_empresa(empresa_data: dict, archivos_request=None) -> dict:
    """
    Genera la estructura de carpetas y archivos para un expediente de empresa.

    Args:
        empresa_data: Diccionario con los datos de la empresa (nit, nombre_empresa, etc.)
        archivos_request: request.files con los archivos adjuntos (PDFs, imágenes)

    Returns:
        dict: {
            "success": bool,
            "files_created": list,
            "errors": list,
            "path": str,
            "rutas_bd": {
                "ruta_carpeta": str,
                "ruta_firma": str,
                "ruta_logo": str,
                "ruta_rut": str,
                "ruta_camara_comercio": str,
                "ruta_cedula_representante": str,
                "ruta_arl": str,
                "ruta_cuenta_bancaria": str,
                "ruta_carta_autorizacion": str
            }
        }
    """
    resultado = {
        "success": False,
        "files_created": [],
        "errors": [],
        "path": "",
        "rutas_bd": {}
    }

    try:
        nit = empresa_data.get("nit")
        nombre_empresa = empresa_data.get("nombre_empresa", "")

        if not nit:
            resultado["errors"].append("NIT es obligatorio para generar expediente")
            return resultado

        # 1. CREAR CARPETA PRINCIPAL DE LA EMPRESA
        # Generar nombre seguro: NIT_NombreEmpresa (sin caracteres especiales)
        nombre_sanitizado = re.sub(r'[^\w\s-]', '', nombre_empresa)
        nombre_sanitizado = re.sub(r'[-\s]+', '_', nombre_sanitizado).strip('_')
        nombre_carpeta = f"{nit}_{nombre_sanitizado}"

        carpeta_empresa = os.path.join(RUTA_BASE_EXPEDIENTES, nombre_carpeta)
        os.makedirs(carpeta_empresa, exist_ok=True)
        resultado["path"] = carpeta_empresa
        resultado["rutas_bd"]["ruta_carpeta"] = os.path.relpath(carpeta_empresa, start=r"D:\Mi-App-React\MONTERO_NEGOCIO")
        logger.info(f"📁 Carpeta empresa creada/verificada: {carpeta_empresa}")

        # 2. CREAR SUBCARPETAS OBLIGATORIAS
        subcarpetas = [
            "COTIZACIONES",
            "EXTRACTOS BANCARIOS",
            "OTROS_ADJUNTOS",
            "PAGO DE IMPUESTOS",
            "USUARIOS Y CONTRASEÑAS"
        ]

        for subcarpeta in subcarpetas:
            ruta_subcarpeta = os.path.join(carpeta_empresa, subcarpeta)
            os.makedirs(ruta_subcarpeta, exist_ok=True)
            logger.debug(f"  ✓ Subcarpeta creada: {subcarpeta}")

        resultado["files_created"].append(f"Estructura de {len(subcarpetas)} carpetas")

        # 3. GENERAR ARCHIVO datos.txt CON TODA LA INFORMACIÓN
        archivo_datos = os.path.join(carpeta_empresa, "datos.txt")

        contenido = f"""
{'=' * 80}
                     INFORMACIÓN DE LA EMPRESA
{'=' * 80}

DATOS DE IDENTIFICACIÓN
-----------------------
NIT:                 {empresa_data.get('nit', 'N/A')}
Razón Social:        {empresa_data.get('nombre_empresa', 'N/A')}
Tipo de Empresa:     {empresa_data.get('tipo_empresa', 'N/A')}
Sector Económico:    {empresa_data.get('sector_economico', 'N/A')}
Fecha Constitución:  {empresa_data.get('fecha_constitucion', 'N/A')}

DATOS DE UBICACIÓN
------------------
Dirección:           {empresa_data.get('direccion_empresa', 'N/A')}
Ciudad:              {empresa_data.get('ciudad_empresa', 'N/A')}
Departamento:        {empresa_data.get('departamento', 'N/A')}

DATOS DE CONTACTO
-----------------
Teléfono:            {empresa_data.get('telefono_empresa', 'N/A')}
Correo Electrónico:  {empresa_data.get('correo_empresa', 'N/A')}

REPRESENTANTE LEGAL
-------------------
Nombre:              {empresa_data.get('rep_legal_nombre', 'N/A')}
Tipo ID:             {empresa_data.get('rep_legal_tipo_id', 'N/A')}
Número ID:           {empresa_data.get('rep_legal_numero_id', 'N/A')}
Teléfono:            {empresa_data.get('rep_legal_telefono', 'N/A')}
Correo:              {empresa_data.get('rep_legal_correo', 'N/A')}

DATOS LABORALES
---------------
Número de Empleados: {empresa_data.get('num_empleados', 'N/A')}
Estado:              {empresa_data.get('estado', 'Activo')}

DATOS BANCARIOS
---------------
Banco:               {empresa_data.get('banco', 'N/A')}
Tipo de Cuenta:      {empresa_data.get('tipo_cuenta', 'N/A')}
Número de Cuenta:    {empresa_data.get('numero_cuenta', 'N/A')}

DATOS DE SEGURIDAD SOCIAL
--------------------------
ARL:                 {empresa_data.get('arl', 'N/A')}
CCF:                 {empresa_data.get('ccf', 'N/A')}

{'=' * 80}
Fecha de Generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 80}
"""

        with open(archivo_datos, "w", encoding="utf-8") as f:
            f.write(contenido)

        resultado["files_created"].append("datos.txt")
        logger.info(f"📄 Archivo datos.txt creado/actualizado")

        # 4. GUARDAR FIRMA DIGITAL (BASE64 desde JSON)
        firma_base64 = empresa_data.get("firma_digital")
        if firma_base64 and isinstance(firma_base64, str):
            try:
                if "," in firma_base64:
                    _, encoded = firma_base64.split(",", 1)
                else:
                    encoded = firma_base64

                firma_bytes = base64.b64decode(encoded)

                if len(firma_bytes) > 5 * 1024 * 1024:  # 5MB máximo
                    resultado["errors"].append("Firma digital: Tamaño excedido (máximo 5MB)")
                else:
                    archivo_firma = os.path.join(carpeta_empresa, "firma_representante.png")
                    with open(archivo_firma, "wb") as f:
                        f.write(firma_bytes)

                    resultado["files_created"].append("firma_representante.png")
                    resultado["rutas_bd"]["ruta_firma"] = os.path.relpath(archivo_firma, start=r"D:\Mi-App-React\MONTERO_NEGOCIO")
                    logger.info(f"✍️ Firma digital guardada: {len(firma_bytes)} bytes")

            except Exception as e:
                logger.error(f"❌ Error al guardar firma: {e}", exc_info=True)
                resultado["errors"].append(f"Error al guardar firma: {str(e)}")

        # 5. GUARDAR LOGO DE LA EMPRESA (BASE64 desde JSON)
        logo_base64 = empresa_data.get("logo_empresa")
        if logo_base64 and isinstance(logo_base64, str):
            try:
                if "," in logo_base64:
                    _, encoded = logo_base64.split(",", 1)
                else:
                    encoded = logo_base64

                logo_bytes = base64.b64decode(encoded)

                if len(logo_bytes) > 5 * 1024 * 1024:  # 5MB máximo
                    resultado["errors"].append("Logo: Tamaño excedido (máximo 5MB)")
                else:
                    archivo_logo = os.path.join(carpeta_empresa, "logo.png")
                    with open(archivo_logo, "wb") as f:
                        f.write(logo_bytes)

                    resultado["files_created"].append("logo.png")
                    resultado["rutas_bd"]["ruta_logo"] = os.path.relpath(archivo_logo, start=r"D:\Mi-App-React\MONTERO_NEGOCIO")
                    logger.info(f"🖼️ Logo guardado: {len(logo_bytes)} bytes")

            except Exception as e:
                logger.error(f"❌ Error al guardar logo: {e}", exc_info=True)
                resultado["errors"].append(f"Error al guardar logo: {str(e)}")

        # 6. GUARDAR ARCHIVOS ADJUNTOS (PDFs desde request.files)
        if archivos_request:
            archivos_config = {
                "rut": ("rut.pdf", "ruta_rut"),
                "camara_comercio": ("camara_comercio.pdf", "ruta_camara_comercio"),
                "cedula_representante": ("cedula_representante.pdf", "ruta_cedula_representante"),
                "arl": ("arl.pdf", "ruta_arl"),
                "cuenta_bancaria": ("cuenta_bancaria.pdf", "ruta_cuenta_bancaria"),
                "carta_autorizacion": ("carta_autorizacion.pdf", "ruta_carta_autorizacion")
            }

            for field_name, (nombre_archivo, campo_bd) in archivos_config.items():
                if field_name in archivos_request:
                    archivo = archivos_request[field_name]
                    try:
                        # Validar extensión
                        if not archivo.filename.lower().endswith('.pdf'):
                            resultado["errors"].append(f"{field_name}: Solo se permiten archivos PDF")
                            continue

                        # Guardar archivo
                        ruta_destino = os.path.join(carpeta_empresa, nombre_archivo)
                        archivo.save(ruta_destino)

                        resultado["files_created"].append(nombre_archivo)
                        resultado["rutas_bd"][campo_bd] = os.path.relpath(ruta_destino, start=r"D:\Mi-App-React\MONTERO_NEGOCIO")
                        logger.info(f"📎 Archivo guardado: {nombre_archivo}")

                    except Exception as e:
                        logger.error(f"❌ Error al guardar {field_name}: {e}", exc_info=True)
                        resultado["errors"].append(f"Error al guardar {field_name}: {str(e)}")

        resultado["success"] = True
        logger.info(f"✅ Expediente generado exitosamente para empresa {nit}")

    except Exception as e:
        logger.error(f"❌ Error crítico al generar expediente: {e}", exc_info=True)
        resultado["errors"].append(f"Error crítico: {str(e)}")

    return resultado


# ==============================================================================
# ENDPOINTS CRUD
# ==============================================================================


@empresas_bp.route("", methods=["POST"])
@login_required
def add_empresa():
    """
    Crea una nueva empresa en la base de datos.
    Soporta dos modos:
    1. JSON (application/json) - Para datos básicos
    2. FormData (multipart/form-data) - Para datos + archivos adjuntos
    
    Genera automáticamente:
    - Estructura de carpetas física en MONTERO_TOTAL/EMPRESAS/
    - Archivo datos.txt con información completa
    - Almacenamiento de firma digital y logo (Base64)
    - Guardado de PDFs adjuntos (RUT, Cámara de Comercio, etc.)
    """
    conn = None
    nit = "desconocido"
    
    try:
        # ==================== FASE 1: DETECCIÓN DEL TIPO DE REQUEST ====================
        logger.info(f"📥 Content-Type recibido: {request.content_type}")
        
        is_json = request.is_json
        is_form_data = request.content_type and 'multipart/form-data' in request.content_type
        
        empresa_data = {}
        archivos = None
        
        if is_json or (not is_form_data):
            # ==================== MODO JSON ====================
            try:
                json_data = request.get_json(force=True) if not request.is_json else request.get_json()
                logger.info(f"📥 Datos JSON recibidos: {list(json_data.keys())}")
                
                # Validación con Pydantic
                data_validated = EmpresaCreate(**json_data)
                
                # Convertir a dict para usar en expediente
                empresa_data = {
                    "nit": data_validated.nit,
                    "nombre_empresa": data_validated.nombre_empresa,
                    "direccion_empresa": data_validated.direccion,
                    "telefono_empresa": data_validated.telefono,
                    "correo_empresa": data_validated.email,
                    "ciudad_empresa": data_validated.ciudad,
                    "rep_legal_nombre": data_validated.representante_legal,
                    # Campos opcionales de Base64
                    "firma_digital": json_data.get("firma_digital"),
                    "logo_empresa": json_data.get("logo_empresa")
                }
                
                nit = data_validated.nit
                
            except ValidationError as ve:
                logger.warning(f"❌ Error de validación Pydantic: {ve.errors()}")
                error_list = [{"field": err.get('loc', ['unknown'])[0], "message": err.get('msg', 'Error de validación')} for err in ve.errors()]
                return jsonify({"error": "Datos inválidos", "details": error_list}), 422
                
        elif is_form_data:
            # ==================== MODO FORM DATA ====================
            logger.info(f"📥 Recibiendo FormData con archivos")
            
            # Extraer datos del formulario
            form_data = request.form.to_dict()
            logger.info(f"📥 Campos del formulario: {list(form_data.keys())}")
            
            # Mapear campos del form a estructura de empresa
            empresa_data = {
                "nit": form_data.get("nit"),
                "nombre_empresa": form_data.get("nombre_empresa"),
                "direccion_empresa": form_data.get("direccion"),
                "telefono_empresa": form_data.get("telefono"),
                "correo_empresa": form_data.get("email") or form_data.get("correo"),
                "ciudad_empresa": form_data.get("ciudad"),
                "departamento_empresa": form_data.get("departamento_empresa") or form_data.get("departamento"),
                "rep_legal_nombre": form_data.get("representante_legal") or form_data.get("rep_legal_nombre"),
                "rep_legal_tipo_id": form_data.get("rep_legal_tipo_id"),
                "rep_legal_numero_id": form_data.get("rep_legal_numero_id"),
                "rep_legal_telefono": form_data.get("rep_legal_telefono"),
                "rep_legal_correo": form_data.get("rep_legal_correo"),
                "tipo_empresa": form_data.get("tipo_empresa"),
                "sector_economico": form_data.get("sector_economico"),
                "num_empleados": form_data.get("num_empleados"),
                "fecha_constitucion": form_data.get("fecha_constitucion"),
                "banco": form_data.get("banco"),
                "tipo_cuenta": form_data.get("tipo_cuenta"),
                "numero_cuenta": form_data.get("numero_cuenta"),
                "arl": form_data.get("arl"),
                "ccf": form_data.get("ccf"),
                # Base64 desde form (si existen) - Soportar ambos nombres de campo
                "firma_digital": form_data.get("firma_digital") or form_data.get("firmaDigitalBase64"),
                "logo_empresa": form_data.get("logo_empresa")
            }
            
            nit = empresa_data.get("nit")
            archivos = request.files
            
            if not nit or not empresa_data.get("nombre_empresa"):
                return jsonify({"error": "NIT y Nombre de Empresa son obligatorios"}), 400
        
        else:
            return jsonify({"error": "Content-Type no soportado. Use application/json o multipart/form-data"}), 400
        
        # ==================== FASE 2: VALIDACIÓN DE NIT ÚNICO ====================
        conn = get_db_connection()
        
        existe = conn.execute("SELECT id FROM empresas WHERE nit = ?", (nit,)).fetchone()
        if existe:
            logger.warning(f"Intento de crear empresa con NIT duplicado: {nit}")
            return jsonify({"error": f"El NIT {nit} ya está registrado."}), 409
        
        # ==================== FASE 3: GENERAR EXPEDIENTE FÍSICO ====================
        logger.info(f"📁 Generando expediente físico para empresa {nit}...")
        resultado_expediente = generar_expediente_empresa(empresa_data, archivos)
        
        if not resultado_expediente["success"]:
            logger.error(f"❌ Error al generar expediente: {resultado_expediente['errors']}")
            # No fallar la creación, pero advertir
        
        logger.info(f"✅ Archivos creados: {resultado_expediente['files_created']}")
        
        # ==================== FASE 4: INSERTAR EN BASE DE DATOS ====================
        rutas = resultado_expediente.get("rutas_bd", {})
        
        cursor = conn.execute(
            """
            INSERT INTO empresas (
                nombre_empresa, nit, direccion_empresa,
                telefono_empresa, correo_empresa, ciudad_empresa,
                departamento_empresa, tipo_empresa, sector_economico,
                num_empleados, fecha_constitucion,
                banco, tipo_cuenta, numero_cuenta,
                arl, ccf, ibc_empresa, afp_empresa, arl_empresa,
                rep_legal_nombre, rep_legal_tipo_id, rep_legal_numero_id,
                rep_legal_telefono, rep_legal_correo,
                ruta_carpeta, ruta_firma, ruta_logo,
                ruta_rut, ruta_camara_comercio, ruta_cedula_representante,
                ruta_arl, ruta_cuenta_bancaria, ruta_carta_autorizacion
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                empresa_data.get("nombre_empresa"),
                nit,
                empresa_data.get("direccion_empresa"),
                empresa_data.get("telefono_empresa"),
                empresa_data.get("correo_empresa"),
                empresa_data.get("ciudad_empresa"),
                empresa_data.get("departamento_empresa"),
                empresa_data.get("tipo_empresa"),
                empresa_data.get("sector_economico"),
                empresa_data.get("num_empleados"),
                empresa_data.get("fecha_constitucion"),
                empresa_data.get("banco"),
                empresa_data.get("tipo_cuenta"),
                empresa_data.get("numero_cuenta"),
                empresa_data.get("arl"),
                empresa_data.get("ccf"),
                empresa_data.get("ibc_empresa"),
                empresa_data.get("afp_empresa"),
                empresa_data.get("arl_empresa"),
                empresa_data.get("rep_legal_nombre"),
                empresa_data.get("rep_legal_tipo_id"),
                empresa_data.get("rep_legal_numero_id"),
                empresa_data.get("rep_legal_telefono"),
                empresa_data.get("rep_legal_correo"),
                rutas.get("ruta_carpeta"),
                rutas.get("ruta_firma"),
                rutas.get("ruta_logo"),
                rutas.get("ruta_rut"),
                rutas.get("ruta_camara_comercio"),
                rutas.get("ruta_cedula_representante"),
                rutas.get("ruta_arl"),
                rutas.get("ruta_cuenta_bancaria"),
                rutas.get("ruta_carta_autorizacion")
            ),
        )
        conn.commit()

        nueva_empresa_id = cursor.lastrowid
        logger.info(
            f"✅ Nueva empresa creada: {empresa_data.get('nombre_empresa')} (ID: {nueva_empresa_id}, NIT: {nit}) por usuario {session.get('user_id')}"
        )

        return jsonify({
            "message": "Empresa creada exitosamente.",
            "id": nueva_empresa_id,
            "nit": nit,
            "expediente": {
                "archivos_creados": resultado_expediente["files_created"],
                "errores": resultado_expediente["errors"],
                "ruta": resultado_expediente["path"]
            }
        }), 201

    except sqlite3.IntegrityError as e:
        logger.error(f"Error de integridad al crear empresa (NIT duplicado?): {nit} - {e}", exc_info=True)
        if conn:
            conn.rollback()
        return jsonify({"error": f"El NIT {nit} ya existe."}), 409
        
    except Exception as e:
        logger.critical(f"Error inesperado al crear empresa: {e}", exc_info=True)
        if conn:
            conn.rollback()
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
        
    finally:
        if conn:
            conn.close()


@empresas_bp.route("", methods=["GET"])
@login_required
def get_empresas():
    """
    Obtiene lista de empresas con paginación opcional.
    Query params:
      - page: número de página (default: 1)
      - per_page: items por página (default: 50, max: 200)
      - search: búsqueda por nombre o NIT
    """
    conn = None
    try:
        conn = get_db_connection()
        
        # Parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 200)  # Max 200
        search = request.args.get('search', '', type=str).strip()
        
        offset = (page - 1) * per_page
        
        # Construir query con búsqueda opcional
        if search:
            count_query = "SELECT COUNT(*) FROM empresas WHERE nombre_empresa LIKE ? OR nit LIKE ?"
            search_param = f"%{search}%"
            total = conn.execute(count_query, (search_param, search_param)).fetchone()[0]
            
            empresas = conn.execute(
                """SELECT nit, nombre_empresa, ciudad_empresa, created_at 
                   FROM empresas 
                   WHERE nombre_empresa LIKE ? OR nit LIKE ?
                   ORDER BY nombre_empresa 
                   LIMIT ? OFFSET ?""",
                (search_param, search_param, per_page, offset)
            ).fetchall()
        else:
            total = conn.execute("SELECT COUNT(*) FROM empresas").fetchone()[0]
            empresas = conn.execute(
                """SELECT nit, nombre_empresa, ciudad_empresa, created_at 
                   FROM empresas 
                   ORDER BY nombre_empresa 
                   LIMIT ? OFFSET ?""",
                (per_page, offset)
            ).fetchall()

        logger.debug(f"✅ Se consultaron {len(empresas)} empresas (página {page})")

        return jsonify({
            "items": [dict(row) for row in empresas],
            "total_items": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }), 200

    except Exception as e:
        logger.error(f"❌ Error al obtener lista de empresas: {e}", exc_info=True)
        return jsonify({
            "error": "Error interno del servidor al consultar empresas.",
            "detail": str(e)
        }), 500
    finally:
        if conn:
            conn.close()


@empresas_bp.route("/<string:nit>", methods=["GET"])
@login_required
def get_empresa_by_nit(nit):
    """
    Obtiene los detalles de una empresa específica por su NIT.
    """
    from flask import g

    conn = None
    try:
        conn = get_db_connection()
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


@empresas_bp.route("/editar/<string:nit>", methods=["GET"])
@login_required
def editar_empresa(nit):
    """
    Muestra un formulario para editar los datos de una empresa.
    """
    from flask import render_template
    
    conn = None
    try:
        logger.info(f"📝 Cargando formulario de edición para empresa NIT: {nit}")
        
        conn = get_db_connection()
        if not conn:
            logger.error("❌ No se pudo establecer conexión con la base de datos")
            return jsonify({"error": "Error de conexión con la base de datos"}), 500
        
        # Obtener datos de la empresa
        query = """
            SELECT 
                nit,
                nombre_empresa,
                rep_legal_tipo_id,
                rep_legal_numero_id,
                rep_legal_nombre,
                direccion,
                telefono,
                correo,
                ciudad,
                departamento,
                tipo_empresa,
                sector_economico,
                num_empleados,
                fecha_constitucion,
                estado
            FROM empresas
            WHERE nit = ?
        """
        
        empresa = conn.execute(query, (nit,)).fetchone()
        
        if not empresa:
            logger.warning(f"⚠️ Empresa con NIT {nit} no encontrada")
            return jsonify({"error": f"Empresa con NIT {nit} no encontrada"}), 404
        
        empresa_dict = dict(empresa)
        
        logger.info(f"✅ Empresa cargada: {empresa_dict.get('nombre_empresa')}")
        
        return render_template(
            "empresas/editar_empresa.html",
            empresa=empresa_dict
        )
        
    except Exception as e:
        logger.error(f"❌ Error al cargar formulario de edición: {e}", exc_info=True)
        return jsonify({"error": f"Error al cargar el formulario: {str(e)}"}), 500
        
    finally:
        if conn:
            conn.close()


@empresas_bp.route("/<string:nit>", methods=["PUT"])
@login_required
def update_empresa(nit):
    """
    Actualiza los datos de una empresa existente.
    Soporta JSON y FormData (con archivos).
    Actualiza expediente físico si hay cambios en archivos.
    """
    conn = None
    
    try:
        # ==================== FASE 1: DETECCIÓN DE TIPO DE REQUEST ====================
        logger.info(f"📝 Actualizando empresa NIT: {nit}")
        logger.info(f"📥 Content-Type: {request.content_type}")
        
        is_json = request.is_json
        is_form_data = request.content_type and 'multipart/form-data' in request.content_type
        
        empresa_data = {}
        archivos = None
        
        if is_json or (not is_form_data):
            # ==================== MODO JSON ====================
            try:
                json_data = request.get_json(force=True) if not request.is_json else request.get_json()
                data = EmpresaUpdate(**json_data)
                
                # Convertir a dict
                empresa_data = {
                    "nit": data.nit or nit,
                    "nombre_empresa": data.nombre_empresa,
                    "direccion_empresa": data.direccion,
                    "telefono_empresa": data.telefono,
                    "correo_empresa": data.email,
                    "ciudad_empresa": data.ciudad,
                    "rep_legal_nombre": data.representante_legal,
                    "firma_digital": json_data.get("firma_digital"),
                    "logo_empresa": json_data.get("logo_empresa")
                }
                
            except ValidationError as e:
                logger.warning(f"Validación fallida: {e.errors()}")
                error_details = [err["msg"] for err in e.errors()]
                return jsonify({"error": "Datos inválidos", "details": error_details}), 422
                
        elif is_form_data:
            # ==================== MODO FORM DATA ====================
            form_data = request.form.to_dict()
            
            empresa_data = {
                "nit": form_data.get("nit") or nit,
                "nombre_empresa": form_data.get("nombre_empresa"),
                "direccion_empresa": form_data.get("direccion"),
                "telefono_empresa": form_data.get("telefono"),
                "correo_empresa": form_data.get("email") or form_data.get("correo"),
                "ciudad_empresa": form_data.get("ciudad"),
                "departamento_empresa": form_data.get("departamento_empresa") or form_data.get("departamento"),
                "rep_legal_nombre": form_data.get("representante_legal") or form_data.get("rep_legal_nombre"),
                "rep_legal_tipo_id": form_data.get("rep_legal_tipo_id"),
                "rep_legal_numero_id": form_data.get("rep_legal_numero_id"),
                "rep_legal_telefono": form_data.get("rep_legal_telefono"),
                "rep_legal_correo": form_data.get("rep_legal_correo"),
                "tipo_empresa": form_data.get("tipo_empresa"),
                "sector_economico": form_data.get("sector_economico"),
                "num_empleados": form_data.get("num_empleados"),
                "fecha_constitucion": form_data.get("fecha_constitucion"),
                "banco": form_data.get("banco"),
                "tipo_cuenta": form_data.get("tipo_cuenta"),
                "numero_cuenta": form_data.get("numero_cuenta"),
                "arl": form_data.get("arl"),
                "ccf": form_data.get("ccf"),
                # Base64 desde form (si existen) - Soportar ambos nombres de campo
                "firma_digital": form_data.get("firma_digital") or form_data.get("firmaDigitalBase64"),
                "logo_empresa": form_data.get("logo_empresa")
            }
            
            archivos = request.files
        
        # ==================== FASE 2: VALIDAR EMPRESA EXISTENTE ====================
        conn = get_db_connection()
        
        empresa_existente = conn.execute("SELECT id, nombre_empresa FROM empresas WHERE nit = ?", (nit,)).fetchone()
        if not empresa_existente:
            logger.warning(f"Empresa no encontrada. NIT: {nit}")
            return jsonify({"error": "Empresa no encontrada"}), 404
        
        # Verificar conflicto de NIT si se intenta cambiar
        nuevo_nit = empresa_data.get("nit")
        if nuevo_nit and nuevo_nit != nit:
            nit_duplicado = conn.execute("SELECT id FROM empresas WHERE nit = ?", (nuevo_nit,)).fetchone()
            if nit_duplicado:
                logger.warning(f"Conflicto de NIT. {nuevo_nit} ya existe.")
                return jsonify({"error": f"El nuevo NIT {nuevo_nit} ya está en uso."}), 409
        
        # ==================== FASE 3: ACTUALIZAR EXPEDIENTE FÍSICO ====================
        logger.info(f"📁 Actualizando expediente físico...")
        resultado_expediente = generar_expediente_empresa(empresa_data, archivos)
        
        if not resultado_expediente["success"]:
            logger.warning(f"⚠️ Errores en expediente: {resultado_expediente['errors']}")
        
        logger.info(f"✅ Archivos actualizados: {resultado_expediente['files_created']}")
        
        # ==================== FASE 4: ACTUALIZAR BASE DE DATOS ====================
        rutas = resultado_expediente.get("rutas_bd", {})
        
        # Construir consulta dinámica solo con campos proporcionados
        update_fields = []
        update_values = []
        
        # Campos de datos
        campos_mapeo = {
            "nombre_empresa": empresa_data.get("nombre_empresa"),
            "nit": nuevo_nit,
            "direccion_empresa": empresa_data.get("direccion_empresa"),
            "telefono_empresa": empresa_data.get("telefono_empresa"),
            "correo_empresa": empresa_data.get("correo_empresa"),
            "ciudad_empresa": empresa_data.get("ciudad_empresa"),
            "departamento_empresa": empresa_data.get("departamento"),
            "tipo_empresa": empresa_data.get("tipo_empresa"),
            "sector_economico": empresa_data.get("sector_economico"),
            "num_empleados": empresa_data.get("num_empleados"),
            "fecha_constitucion": empresa_data.get("fecha_constitucion"),
            "banco": empresa_data.get("banco"),
            "tipo_cuenta": empresa_data.get("tipo_cuenta"),
            "numero_cuenta": empresa_data.get("numero_cuenta"),
            "arl": empresa_data.get("arl"),
            "ccf": empresa_data.get("ccf"),
            "ibc_empresa": empresa_data.get("ibc_empresa"),
            "afp_empresa": empresa_data.get("afp_empresa"),
            "arl_empresa": empresa_data.get("arl_empresa"),
            "rep_legal_nombre": empresa_data.get("rep_legal_nombre"),
            "rep_legal_tipo_id": empresa_data.get("rep_legal_tipo_id"),
            "rep_legal_numero_id": empresa_data.get("rep_legal_numero_id"),
            "rep_legal_telefono": empresa_data.get("rep_legal_telefono"),
            "rep_legal_correo": empresa_data.get("rep_legal_correo")
        }
        
        for campo, valor in campos_mapeo.items():
            if valor is not None:
                update_fields.append(f"{campo} = ?")
                update_values.append(valor)
        
        # Campos de rutas (solo si se generaron nuevos archivos)
        campos_rutas = {
            "ruta_carpeta": rutas.get("ruta_carpeta"),
            "ruta_firma": rutas.get("ruta_firma"),
            "ruta_logo": rutas.get("ruta_logo"),
            "ruta_rut": rutas.get("ruta_rut"),
            "ruta_camara_comercio": rutas.get("ruta_camara_comercio"),
            "ruta_cedula_representante": rutas.get("ruta_cedula_representante"),
            "ruta_arl": rutas.get("ruta_arl"),
            "ruta_cuenta_bancaria": rutas.get("ruta_cuenta_bancaria"),
            "ruta_carta_autorizacion": rutas.get("ruta_carta_autorizacion")
        }
        
        for campo, valor in campos_rutas.items():
            if valor:  # Solo actualizar si hay una nueva ruta
                update_fields.append(f"{campo} = ?")
                update_values.append(valor)
        
        if not update_fields:
            return jsonify({"error": "No se proporcionaron campos para actualizar"}), 400
        
        # Agregar NIT para WHERE
        update_values.append(nit)
        
        query = f"UPDATE empresas SET {', '.join(update_fields)} WHERE nit = ?"
        conn.execute(query, tuple(update_values))
        conn.commit()
        
        logger.info(f"✅ Empresa actualizada: NIT {nit} → {nuevo_nit or nit} por usuario {session.get('user_id')}")
        
        return jsonify({
            "message": "Empresa actualizada exitosamente.",
            "nit": nuevo_nit or nit,
            "expediente": {
                "archivos_actualizados": resultado_expediente["files_created"],
                "errores": resultado_expediente["errors"]
            }
        }), 200

    except Exception as e:
        logger.critical(f"Error inesperado al actualizar empresa {nit}: {e}", exc_info=True)
        if conn:
            conn.rollback()
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
        
    finally:
        if conn:
            conn.close()


@empresas_bp.route("/<string:nit>", methods=["DELETE"])
@login_required
def delete_empresa(nit):
    """
    FASE 10.4: SOFT DELETE - Inactiva una empresa en lugar de eliminarla físicamente.
    Cambia el estado de 'Activa' a 'Inactiva' para preservar el histórico.
    """
    from flask import g

    conn = None
    try:
        conn = get_db_connection()

        # Verificar si la empresa tiene usuarios asociados activos
        usuarios_activos = conn.execute(
            "SELECT COUNT(id) FROM usuarios WHERE empresa_nit = ? AND estado = 'Activo'",
            (nit,)
        ).fetchone()[0]

        if usuarios_activos > 0:
            logger.warning(f"Intento de inactivar empresa {nit} que tiene {usuarios_activos} usuarios activos.")
            return (
                jsonify(
                    {
                        "error": f"No se puede inactivar la empresa. Primero inactive o reasigne a los {usuarios_activos} usuarios activos asociados."
                    }
                ),
                409,
            )  # Conflicto

        # SOFT DELETE: Cambiar estado a 'Inactiva' en lugar de eliminar
        cursor = conn.execute(
            "UPDATE empresas SET estado = 'Inactiva' WHERE nit = ? AND estado = 'Activa'",
            (nit,)
        )

        if cursor.rowcount == 0:
            # Verificar si la empresa existe pero ya está inactiva
            existe = conn.execute("SELECT estado FROM empresas WHERE nit = ?", (nit,)).fetchone()

            if existe:
                if existe[0] == 'Inactiva':
                    return jsonify({"error": "La empresa ya está inactiva"}), 400
            else:
                logger.warning(f"Intento de inactivar empresa no existente. NIT: {nit}")
                return jsonify({"error": "Empresa no encontrada"}), 404

        conn.commit()
        logger.info(f"✅ Empresa inactivada (SOFT DELETE) - NIT: {nit}, Usuario: {session.get('user_id')}")
        return jsonify({
            "message": "Empresa inactivada exitosamente (soft delete).",
            "nit": nit,
            "nuevo_estado": "Inactiva"
        })

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
