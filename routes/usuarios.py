# -*- coding: utf-8 -*-
"""
usuarios.py - ACTUALIZADO con validación de archivos y logging
==================================================
"""
import os
import traceback
import base64
from datetime import datetime
from flask import Blueprint, jsonify, request, session
from logger import logger

# --- IMPORTACIÓN CENTRALIZADA ---
try:
    from ..utils import get_db_connection, login_required, format_key, log_file_upload, sanitize_and_save_file, validate_upload
except (ImportError, ValueError):
    from utils import get_db_connection, login_required, format_key, log_file_upload, sanitize_and_save_file, validate_upload
# -------------------------------

# Leer USER_DATA_FOLDER del entorno
USER_DATA_FOLDER = os.getenv("USER_DATA_FOLDER", "../../MONTERO_NEGOCIO/MONTERO_TOTAL/USUARIOS")

# Ruta base absoluta para expedientes
RUTA_BASE_EXPEDIENTES = r"D:\Mi-App-React\MONTERO_NEGOCIO\MONTERO_TOTAL\USUARIOS"

# ==================== DEFINICIÓN DEL BLUEPRINT ====================
usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/api/usuarios")


# ==================== FUNCIÓN AUXILIAR: GENERAR EXPEDIENTE ====================
def generar_expediente_usuario(user_data: dict, firma_base64: str = None) -> dict:
    """
    Genera la estructura de carpetas y archivos para un expediente de usuario.

    Args:
        user_data: Diccionario con los datos del usuario
        firma_base64: String base64 de la firma (formato data:image/png;base64,...)

    Returns:
        dict: {"success": bool, "files_created": list, "errors": list, "path": str}
    """
    resultado = {
        "success": False,
        "files_created": [],
        "errors": [],
        "path": ""
    }

    try:
        numero_id = user_data.get("numeroId") or user_data.get("numero_documento")

        if not numero_id:
            resultado["errors"].append("Número de identificación es obligatorio")
            return resultado

        # 1. CREAR CARPETA PRINCIPAL DEL USUARIO
        carpeta_usuario = os.path.join(RUTA_BASE_EXPEDIENTES, str(numero_id))
        os.makedirs(carpeta_usuario, exist_ok=True)
        resultado["path"] = carpeta_usuario
        logger.info(f"📁 Carpeta usuario creada/verificada: {carpeta_usuario}")

        # 2. CREAR SUBCARPETAS OBLIGATORIAS
        subcarpetas = [
            "BENEFICIARIOS",
            "DEPURACIONES",
            "EMPRESAS_AFILIADAS",
            "INCAPACIDADES",
            "MORAS",
            "NOVEDADES",
            "PLANILLAS",
            "RECIBOS",
            "TUTELAS",
            "USUARIOS Y CONTRASEÑAS"
        ]

        for subcarpeta in subcarpetas:
            ruta_subcarpeta = os.path.join(carpeta_usuario, subcarpeta)
            os.makedirs(ruta_subcarpeta, exist_ok=True)
            logger.debug(f"  ✓ Subcarpeta creada: {subcarpeta}")

        resultado["files_created"].append(f"Estructura de {len(subcarpetas)} carpetas")

        # 3. GENERAR ARCHIVO datos_usuario.txt
        archivo_datos = os.path.join(carpeta_usuario, "datos_usuario.txt")

        contenido = f"""
{'=' * 80}
                     INFORMACIÓN DEL USUARIO
{'=' * 80}

DATOS DE IDENTIFICACIÓN
-----------------------
Tipo de ID:          {user_data.get('tipoId', 'N/A')}
Número de ID:        {user_data.get('numeroId', 'N/A')}

DATOS PERSONALES
----------------
Primer Nombre:       {user_data.get('primerNombre', 'N/A')}
Segundo Nombre:      {user_data.get('segundoNombre', 'N/A')}
Primer Apellido:     {user_data.get('primerApellido', 'N/A')}
Segundo Apellido:    {user_data.get('segundoApellido', 'N/A')}
Sexo Biológico:      {user_data.get('sexoBiologico', 'N/A')}
Sexo Identificación: {user_data.get('sexoIdentificacion', 'N/A')}
Fecha Nacimiento:    {user_data.get('fechaNacimiento', 'N/A')}
Nacionalidad:        {user_data.get('nacionalidad', 'N/A')}

DATOS DE NACIMIENTO
-------------------
País:                {user_data.get('paisNacimiento', 'N/A')}
Departamento:        {user_data.get('departamentoNacimiento', 'N/A')}
Municipio:           {user_data.get('municipioNacimiento', 'N/A')}

DATOS DE CONTACTO
-----------------
Correo Electrónico:  {user_data.get('correoElectronico', 'N/A')}
Teléfono Celular:    {user_data.get('telefonoCelular', 'N/A')}
Teléfono Fijo:       {user_data.get('telefonoFijo', 'N/A')}
Dirección:           {user_data.get('direccion', 'N/A')}
Comuna/Barrio:       {user_data.get('comunaBarrio', 'N/A')}

DATOS DE SEGURIDAD SOCIAL
--------------------------
AFP:                 {user_data.get('afpNombre', 'N/A')}
EPS:                 {user_data.get('epsNombre', 'N/A')}
ARL:                 {user_data.get('arlNombre', 'N/A')}
CCF:                 {user_data.get('ccfNombre', 'N/A')}

DATOS LABORALES
---------------
Empresa (NIT):       {user_data.get('empresa_nit', 'N/A')}
Empresa (Nombre):    {user_data.get('empresa_nombre', 'N/A')}
Fecha Ingreso:       {user_data.get('fechaIngreso', 'N/A')}
IBC:                 {user_data.get('ibc', 'N/A')}

{'=' * 80}
Fecha de Generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 80}
"""

        with open(archivo_datos, "w", encoding="utf-8") as f:
            f.write(contenido)

        resultado["files_created"].append("datos_usuario.txt")
        logger.info(f"📄 Archivo datos_usuario.txt creado/actualizado")

        # 4. GUARDAR FIRMA DIGITAL (SI SE PROPORCIONA)
        if firma_base64 and isinstance(firma_base64, str):
            try:
                # Verificar si contiene el prefijo data:image
                if "," in firma_base64:
                    # Formato: data:image/png;base64,iVBORw0KGgoAAAANS...
                    _, encoded = firma_base64.split(",", 1)
                else:
                    # Ya es base64 puro
                    encoded = firma_base64

                # Decodificar
                firma_bytes = base64.b64decode(encoded)

                # Validar tamaño (máximo 5MB)
                if len(firma_bytes) > 5 * 1024 * 1024:
                    resultado["errors"].append("Firma digital: Tamaño excedido (máximo 5MB)")
                else:
                    # Guardar archivo
                    archivo_firma = os.path.join(carpeta_usuario, "firma_usuario.png")
                    with open(archivo_firma, "wb") as f:
                        f.write(firma_bytes)

                    resultado["files_created"].append("firma_usuario.png")
                    logger.info(f"✍️ Firma digital guardada: {len(firma_bytes)} bytes")

            except Exception as e:
                logger.error(f"❌ Error al guardar firma: {e}", exc_info=True)
                resultado["errors"].append(f"Error al guardar firma: {str(e)}")

        resultado["success"] = True
        logger.info(f"✅ Expediente generado exitosamente para usuario {numero_id}")

    except Exception as e:
        logger.error(f"❌ Error crítico al generar expediente: {e}", exc_info=True)
        resultado["errors"].append(f"Error crítico: {str(e)}")

    return resultado


# ==================== ENDPOINTS DE USUARIOS ====================
@usuarios_bp.route("", methods=["POST"])
@login_required
def add_usuario():
    """
    Endpoint para agregar usuarios.
    Soporta dos modos:
    1. JSON (para API simple): campos nombre_completo, email, tipo_documento, numero_documento, etc.
    2. Form data (para formulario completo con archivos)
    """
    from typing import Optional

    from flask import g
    from pydantic import BaseModel, Field, ValidationError

    # Modelo Pydantic para validación de JSON
    class UsuarioCreate(BaseModel):
        nombre_completo: str = Field(..., min_length=1)
        email: Optional[str] = None
        tipo_documento: Optional[str] = None
        numero_documento: str = Field(..., min_length=1)
        telefono: Optional[str] = None
        cargo: Optional[str] = None
        empresa_nit: Optional[str] = None

    conn = None
    numero_documento = "desconocido"
    numero_id = "desconocido"  # Para modo FormData

    try:
        # Log para debugging
        logger.info(f"📥 Content-Type recibido: {request.content_type}")
        
        # Detectar si es JSON o Form data
        is_json = request.is_json
        
        if not is_json:
            # Intentar forzar JSON
            try:
                json_data = request.get_json(force=True)
                is_json = True if json_data else False
                logger.info(f"✅ JSON parseado con force=True")
            except:
                is_json = False

        if is_json:
            # ==================== MODO JSON (API SIMPLE) ====================
            try:
                json_data = request.get_json(force=True) if not request.is_json else request.get_json()
                logger.info(f"📥 Datos JSON recibidos: {json_data}")
                
                # Validación con Pydantic
                usuario_data = UsuarioCreate(**json_data)
            except ValidationError as ve:
                logger.warning(f"❌ Error de validación Pydantic: {ve.errors()}")
                error_list = []
                for err in ve.errors():
                    field = err.get('loc', ['unknown'])[0]
                    msg = err.get('msg', 'Error de validación')
                    error_list.append({"field": field, "message": msg})
                
                return jsonify({"error": "Datos inválidos", "details": error_list}), 422

            numero_documento = usuario_data.numero_documento

            if not numero_documento:
                logger.warning("⚠️ Intento de agregar usuario sin Número de ID")
                return jsonify({"error": "Número de ID es obligatorio."}), 400

            # Dividir nombre_completo en partes
            nombre_parts = usuario_data.nombre_completo.strip().split() if usuario_data.nombre_completo else []
            primer_nombre = nombre_parts[0] if len(nombre_parts) > 0 else ''
            segundo_nombre = nombre_parts[1] if len(nombre_parts) > 1 else ''
            primer_apellido = nombre_parts[2] if len(nombre_parts) > 2 else ''
            segundo_apellido = nombre_parts[3] if len(nombre_parts) > 3 else ''

            # Guardar en base de datos (modo simple)
            conn = get_db_connection()

            # CAMBIO DE LÓGICA: empresa_nit ahora puede ser None (NULL en DB)
            empresa_nit_final = usuario_data.empresa_nit
            logger.info(f"📋 Empresa NIT asignado: {empresa_nit_final if empresa_nit_final else 'NULL (sin empresa)'}")
            
            try:
                conn.execute(
                    """
                    INSERT INTO usuarios (
                        empresa_nit, tipoId, numeroId, primerNombre, segundoNombre, 
                        primerApellido, segundoApellido, correoElectronico, telefonoCelular
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        empresa_nit_final,
                        usuario_data.tipo_documento,
                        usuario_data.numero_documento,
                        primer_nombre,
                        segundo_nombre,
                        primer_apellido,
                        segundo_apellido,
                        usuario_data.email,
                        usuario_data.telefono,
                    ),
                )
                conn.commit()

                # ==========================================================
                # CORRECCIÓN CODE 1: GENERAR EXPEDIENTE FÍSICO EN MODO JSON
                # ==========================================================
                logger.info("📂 Iniciando generación de expediente (Modo JSON)...")

                # 1. Preparar datos para la función
                datos_para_expediente = json_data.copy()
                # Asegurar campos críticos
                datos_para_expediente['numeroId'] = numero_documento
                datos_para_expediente['primerNombre'] = primer_nombre
                datos_para_expediente['primerApellido'] = primer_apellido
                datos_para_expediente['segundoNombre'] = segundo_nombre
                datos_para_expediente['segundoApellido'] = segundo_apellido
                datos_para_expediente['correoElectronico'] = usuario_data.email
                datos_para_expediente['telefonoCelular'] = usuario_data.telefono

                # 2. Obtener firma si existe en el JSON
                firma_b64 = json_data.get('firma_digital') or json_data.get('firmaDigitalData')

                # 3. Llamar a la función generadora
                resultado_expediente = generar_expediente_usuario(datos_para_expediente, firma_b64)

                if resultado_expediente['success']:
                    logger.info(f"✅ Expediente creado en: {resultado_expediente['path']}")
                else:
                    logger.warning(f"⚠️ Alerta expediente: {resultado_expediente['errors']}")

                # ==========================================================

                logger.info(f"✅ Usuario {numero_documento} creado exitosamente (modo JSON)")
                return jsonify({"message": f"Usuario creado exitosamente", "numero_documento": numero_documento}), 201

            except sqlite3.IntegrityError as ie:
                conn.rollback()
                if "UNIQUE constraint failed" in str(ie):
                    logger.warning(f"⚠️ Intento de duplicar usuario. ID: {numero_documento}")
                    return jsonify({"error": "El usuario ya existe."}), 409
                else:
                    logger.error(f"❌ Error de integridad: {ie}", exc_info=True)
                    return jsonify({"error": f"Error de integridad: {ie}"}), 409
            except Exception as db_err:
                conn.rollback()
                logger.error(f"❌ Error al guardar usuario {numero_documento}: {db_err}", exc_info=True)
                return jsonify({"error": f"Error al guardar: {str(db_err)}"}), 500

        else:
            # ==================== MODO FORM DATA (FORMULARIO COMPLETO) ====================
            data = request.form
            numero_id = data.get("numeroId")
            if not numero_id:
                logger.warning("Intento de agregar usuario sin Número de ID")
                return jsonify({"error": "Número de ID es obligatorio."}), 400

            numero_documento = numero_id

            # ==================== GENERAR EXPEDIENTE FÍSICO ====================
            # Convertir form data a diccionario para la función auxiliar
            user_data_dict = dict(data)
            firma_base64 = data.get("firmaDigitalData")

            # Llamar a la función auxiliar para generar toda la estructura
            expediente_result = generar_expediente_usuario(user_data_dict, firma_base64)

            if not expediente_result["success"]:
                logger.error(f"❌ Errores al generar expediente: {expediente_result['errors']}")
                # Continuar con el proceso aunque el expediente falle (no crítico)

            logger.info(f"📁 Expediente generado: {expediente_result['files_created']}")
            user_folder_path = expediente_result["path"]

            # ==================== VALIDACIÓN Y GUARDADO DE ARCHIVOS ====================
            saved_files = {}
            upload_errors = expediente_result.get("errors", [])
            user_session_id = session.get("user_id", "unknown")

            # 2. DOCUMENTO PDF (cédula) - VALIDACIÓN CRÍTICA
            if "documentoPdf" in request.files:
                pdf_file = request.files["documentoPdf"]
                if pdf_file and pdf_file.filename:
                    is_valid, error_msg = validate_upload(pdf_file, file_type="document")

                    if is_valid:
                        try:
                            custom_name = f"cedula_{numero_id}.pdf"
                            filepath = sanitize_and_save_file(pdf_file, user_folder_path, custom_name)
                            saved_files["cedula"] = os.path.basename(filepath)
                            log_file_upload(pdf_file.filename, user_session_id, success=True)

                        except (ValueError, IOError) as e:
                            upload_errors.append(f"Cédula PDF: {str(e)}")
                            log_file_upload(
                                pdf_file.filename,
                                user_session_id,
                                success=False,
                                error=str(e),
                            )
                    else:
                        upload_errors.append(f"Cédula PDF: {error_msg}")
                        log_file_upload(
                            pdf_file.filename,
                            user_session_id,
                            success=False,
                            error=error_msg,
                        )

            # Crear subcarpetas estándar
            subfolders = [
                "PLANILLAS",
                "MORAS",
                "EMPRESAS_AFILIADAS",
                "INCAPACIDADES",
                "BENEFICIARIOS",
                "NOVEDADES",
                "TUTELAS",
                "DEPURACIONES",
                "USUARIOS Y CONTRASEÑAS",
                "RECIBOS",
            ]
            for folder in subfolders:
                os.makedirs(os.path.join(user_folder_path, folder), exist_ok=True)

            os.makedirs(os.path.join(user_folder_path, "RECIBOS", "RECIBOS DE CAJA"), exist_ok=True)
            os.makedirs(
                os.path.join(user_folder_path, "RECIBOS", "COMPROBANTES DE CONSIGNACION"),
                exist_ok=True,
            )

            # ==================== GUARDAR EN BASE DE DATOS ====================
            conn = get_db_connection()
            try:
                # CAMBIO DE LÓGICA: empresa_nit ahora puede ser None (NULL en DB)
                empresa_nit = None
                if data.get("administracion"):
                    empresa = conn.execute(
                        "SELECT nit FROM empresas WHERE nombre_empresa = ?",
                        (data["administracion"],),
                    ).fetchone()
                    if empresa:
                        empresa_nit = empresa["nit"]
                    else:
                        logger.warning(
                            f"Advertencia: Empresa '{data['administracion']}' no encontrada en la tabla 'empresas' para el usuario {numero_id}."
                        )

                logger.info(f"📋 Empresa NIT asignado: {empresa_nit if empresa_nit else 'NULL (sin empresa)'}")

                afp_costo = float(data.get("afpCosto")) if data.get("afpCosto") else None
                eps_costo = float(data.get("epsCosto")) if data.get("epsCosto") else None
                arl_costo = float(data.get("arlCosto")) if data.get("arlCosto") else None
                ccf_costo = float(data.get("ccfCosto")) if data.get("ccfCosto") else None
                ibc = float(data.get("ibc")) if data.get("ibc") else None

                conn.execute(
                    """
                    INSERT INTO usuarios (
                        empresa_nit, tipoId, numeroId, primerNombre, segundoNombre, primerApellido, segundoApellido,
                        sexoBiologico, sexoIdentificacion, nacionalidad, fechaNacimiento, paisNacimiento,
                        departamentoNacimiento, municipioNacimiento, direccion, telefonoCelular, telefonoFijo,
                        correoElectronico, comunaBarrio, afpNombre, afpCosto, epsNombre, epsCosto, arlNombre,
                        arlCosto, ccfNombre, ccfCosto, administracion, ibc, claseRiesgoARL, fechaIngreso,
                        paisResidencia, departamentoResidencia, municipioResidencia, cargo, tipo_contrato
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        empresa_nit,
                        data.get("tipoId"),
                        numero_id,
                        data.get("primerNombre"),
                        data.get("segundoNombre"),
                        data.get("primerApellido"),
                        data.get("segundoApellido"),
                        data.get("sexoBiologico"),
                        data.get("sexoIdentificacion"),
                        data.get("nacionalidad"),
                        data.get("fechaNacimiento"),
                        data.get("paisNacimiento"),
                        data.get("departamentoNacimiento"),
                        data.get("municipioNacimiento"),
                        data.get("direccion"),
                        data.get("telefonoCelular"),
                        data.get("telefonoFijo"),
                        data.get("correoElectronico"),
                        data.get("comunaBarrio"),
                        data.get("afpNombre"),
                        afp_costo,
                        data.get("epsNombre"),
                        eps_costo,
                        data.get("arlNombre"),
                        arl_costo,
                        data.get("ccfNombre"),
                        ccf_costo,
                        data.get("administracion"),
                        ibc,
                        data.get("claseRiesgoARL"),
                        data.get("fechaIngreso"),
                        data.get("paisResidencia"),
                        data.get("departamentoResidencia"),
                        data.get("municipioResidencia"),
                        data.get("cargo"),
                        data.get("tipo_contrato"),
                    ),
                )
                conn.commit()

                logger.info(f"Usuario {numero_id} guardado exitosamente por user_id: {user_session_id}")

                response_data = {
                    "message": f"Usuario {numero_id} guardado exitosamente.",
                    "archivos_guardados": saved_files,
                }

                if upload_errors:
                    response_data["advertencias"] = upload_errors
                    response_data[
                        "mensaje_advertencia"
                    ] = f"Usuario creado pero {len(upload_errors)} archivo(s) no pudieron procesarse."
                    logger.warning(f"Usuario {numero_id} creado con {len(upload_errors)} errores de carga: {upload_errors}")

                return jsonify(response_data), 201

            except sqlite3.IntegrityError as ie:
                conn.rollback()
                # --- CORRECCIÓN: Detectar la restricción de constraint correcta ---
                # La restricción UNIQUE está en (tipoId, numeroId) según tu log anterior
                if "UNIQUE constraint failed: usuarios.tipoId, usuarios.numeroId" in str(ie):
                    logger.warning(f"Intento de duplicar usuario. ID: {numero_id}")
                    return jsonify({"error": "La combinación de Tipo de ID y Número de ID ya existe."}), 409
                # Fallback por si acaso
                elif "UNIQUE constraint failed: usuarios.numeroId" in str(ie):
                    logger.warning(f"Intento de duplicar usuario (solo numeroId). ID: {numero_id}")
                    return jsonify({"error": "El Número de ID ingresado ya existe."}), 409
                else:
                    logger.error(
                        f"Error de integridad al guardar usuario {numero_id}: {ie}",
                        exc_info=True,
                    )
                    return (
                        jsonify({"error": f"Error de integridad en base de datos: {ie}"}),
                        409,
                    )
            except Exception as db_err:
                conn.rollback()
                logger.error(
                    f"Error general al guardar usuario {numero_id} en DB: {db_err}",
                    exc_info=True,
                )
                return (
                    jsonify({"error": f"Error al guardar en base de datos: {str(db_err)}"}),
                    500,
                )
            finally:
                if conn:
                    conn.close()

    except Exception as e:
        logger.error(f"Error general en add_usuario (ID: {numero_id}): {e}", exc_info=True)
        return jsonify({"error": f"Error inesperado en el servidor: {str(e)}"}), 500


@usuarios_bp.route("", methods=["GET"])
@login_required
def get_usuarios():
    """Obtiene lista de usuarios con columnas que existen en la tabla"""
    conn = None
    try:
        conn = get_db_connection()
        empresa_nit = request.args.get("empresa_nit")

        # Consulta simplificada: solo columnas que existen en la tabla 'usuarios'
        query = "SELECT id, primerNombre, primerApellido, numeroId, correoElectronico, empresa_nit FROM usuarios"
        params = []

        if empresa_nit:
            query += " WHERE empresa_nit = ?"
            params.append(empresa_nit)

        query += " ORDER BY primerApellido, primerNombre"  # Ordena por campos existentes

        usuarios = conn.execute(query, params).fetchall()

        usuarios_list = []
        for row in usuarios:
            user_dict = dict(row)
            # CONCATENACIÓN en Python para el frontend
            user_dict['nombre_completo'] = f"{row['primerNombre']} {row['primerApellido']}"
            usuarios_list.append(user_dict)

        logger.debug(f"✅ Se consultaron {len(usuarios_list)} usuarios (filtro NIT: {empresa_nit or 'TODOS'})")

        return jsonify({"items": usuarios_list, "total_items": len(usuarios_list)})

    except Exception as e:
        logger.error(f"❌ Error obteniendo lista de usuarios: {e}", exc_info=True)
        return jsonify({"error": "No se pudo obtener la lista de usuarios."}), 500
    finally:
        if conn:
            conn.close()


# --- COPIAR Y PEGAR ESTE BLOQUE EN usuarios.py ---


@usuarios_bp.route("/buscar", methods=["GET"])
@login_required
def buscar_usuario():
    """
    Busca un usuario específico por tipo y número de ID.
    Optimizado para búsquedas rápidas desde el frontend.
    """
    conn = None
    try:
        tipo_id = request.args.get("tipoId")
        numero_id = request.args.get("numeroId")

        if not tipo_id or not numero_id:
            logger.warning(f"Búsqueda de usuario fallida: faltan parámetros (tipoId o numeroId)")
            return jsonify({"error": "Faltan tipoId y numeroId"}), 400

        conn = get_db_connection()
        usuario = conn.execute(
            "SELECT * FROM usuarios WHERE tipoId = ? AND numeroId = ?",
            (tipo_id, numero_id),
        ).fetchone()

        if usuario:
            logger.debug(f"Usuario encontrado por ID: {numero_id}")
            return jsonify(dict(usuario))  # Devolver el objeto de usuario único
        else:
            logger.warning(f"Usuario no encontrado por ID: {tipo_id} - {numero_id}")
            return jsonify({"error": "Usuario no encontrado"}), 404

    except Exception as e:
        logger.error(f"Error buscando usuario: {e}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500
    finally:
        if conn:
            conn.close()


@usuarios_bp.route("/<int:user_id>", methods=["GET"])
@login_required
def get_usuario_by_id(user_id):
    """
    Obtener un usuario específico por su ID para edición
    """
    conn = None
    try:
        conn = get_db_connection()
        
        usuario = conn.execute("""
            SELECT * FROM usuarios WHERE id = ?
        """, (user_id,)).fetchone()
        
        if not usuario:
            return jsonify({"error": f"Usuario con ID {user_id} no encontrado"}), 404
        
        # Convertir Row a dict
        usuario_dict = dict(usuario)
        
        logger.info(f"✅ Usuario ID {user_id} obtenido para edición")
        return jsonify(usuario_dict), 200
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo usuario {user_id}: {e}", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500
    finally:
        if conn:
            conn.close()


@usuarios_bp.route("/<int:user_id>", methods=["PUT"])
@login_required
def update_usuario(user_id):
    """
    Endpoint para actualizar un usuario existente.
    Soporta JSON y regenera el expediente físico automáticamente.
    """
    conn = None

    try:
        # Obtener datos del request
        data = request.get_json()

        if not data:
            return jsonify({"error": "No se proporcionaron datos para actualizar"}), 400

        conn = get_db_connection()

        # Verificar que el usuario existe
        usuario_actual = conn.execute(
            "SELECT * FROM usuarios WHERE id = ?",
            (user_id,)
        ).fetchone()

        if not usuario_actual:
            return jsonify({"error": "Usuario no encontrado"}), 404

        # Construir query dinámicamente solo con campos proporcionados
        update_fields = []
        update_values = []

        # Campos permitidos para actualización
        campos_actualizables = [
            'primerNombre', 'segundoNombre', 'primerApellido', 'segundoApellido',
            'tipoId', 'numeroId', 'sexoBiologico', 'sexoIdentificacion',
            'fechaNacimiento', 'nacionalidad', 'paisNacimiento',
            'departamentoNacimiento', 'municipioNacimiento',
            'correoElectronico', 'telefonoCelular', 'telefonoFijo',
            'direccion', 'comunaBarrio',
            'afpNombre', 'epsNombre', 'arlNombre', 'ccfNombre',
            'empresa_nit', 'fechaIngreso', 'ibc',
            'paisResidencia', 'departamentoResidencia', 'municipioResidencia',
            'cargo', 'tipo_contrato'
        ]

        for campo in campos_actualizables:
            if campo in data and data[campo] is not None:
                update_fields.append(f"{campo} = ?")
                update_values.append(data[campo])

        if not update_fields:
            return jsonify({"error": "No se proporcionaron campos válidos para actualizar"}), 400

        # Agregar timestamp de actualización
        update_fields.append("updated_at = CURRENT_TIMESTAMP")

        # Agregar user_id para la cláusula WHERE
        update_values.append(user_id)

        # Ejecutar UPDATE
        query = f"UPDATE usuarios SET {', '.join(update_fields)} WHERE id = ?"
        conn.execute(query, tuple(update_values))
        conn.commit()

        logger.info(f"✅ Usuario {user_id} actualizado exitosamente")

        # ==================== REGENERAR EXPEDIENTE FÍSICO ====================
        # Obtener los datos completos actualizados del usuario
        usuario_actualizado = conn.execute(
            "SELECT * FROM usuarios WHERE id = ?",
            (user_id,)
        ).fetchone()

        if usuario_actualizado:
            user_data_dict = dict(usuario_actualizado)

            # Obtener firma si se proporciona
            firma_base64 = data.get("firmaDigitalData")

            # Regenerar expediente con datos actualizados
            expediente_result = generar_expediente_usuario(user_data_dict, firma_base64)

            if expediente_result["success"]:
                logger.info(f"📁 Expediente actualizado: {expediente_result['files_created']}")
            else:
                logger.warning(f"⚠️ Errores al actualizar expediente: {expediente_result['errors']}")

        return jsonify({
            "message": "Usuario actualizado exitosamente",
            "expediente": {
                "success": expediente_result.get("success", False),
                "files_created": expediente_result.get("files_created", []),
                "errors": expediente_result.get("errors", [])
            }
        }), 200

    except sqlite3.IntegrityError as ie:
        if conn:
            conn.rollback()
        logger.error(f"❌ Error de integridad al actualizar usuario {user_id}: {ie}", exc_info=True)
        return jsonify({"error": f"Error de integridad: {str(ie)}"}), 409

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"❌ Error al actualizar usuario {user_id}: {e}", exc_info=True)
        return jsonify({"error": f"Error al actualizar: {str(e)}"}), 500

    finally:
        if conn:
            conn.close()


# --- FIN DEL BLOQUE PARA COPIAR ---
