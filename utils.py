# -*- coding: utf-8 -*-
import mimetypes
import os
import sqlite3
from functools import wraps

# (CORREGIDO: Añadidos los imports necesarios)
from flask import current_app, g, jsonify, redirect, request, session, url_for
from werkzeug.utils import secure_filename

from logger import logger  # Importa el logger global

# --- Definiciones de rutas necesarias ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "mi_sistema.db")
# En Docker, los datos deben estar dentro de /app/data donde appuser tiene permisos
USER_DATA_FOLDER = os.path.join(DATA_DIR, "MONTERO_TOTAL", "USUARIOS")
COMPANY_DATA_FOLDER = os.path.join(DATA_DIR, "MONTERO_TOTAL", "EMPRESAS")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(USER_DATA_FOLDER, exist_ok=True)
os.makedirs(COMPANY_DATA_FOLDER, exist_ok=True)

# ==================== CONFIGURACIÓN DE ARCHIVOS PERMITIDOS ====================

# Extensiones permitidas por categoría
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "bmp"}
ALLOWED_DOCUMENT_EXTENSIONS = {"pdf", "doc", "docx", "xls", "xlsx", "txt"}
ALLOWED_ALL_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_DOCUMENT_EXTENSIONS

# MIME types permitidos (seguridad adicional)
ALLOWED_IMAGE_MIMES = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/gif",
    "image/webp",
    "image/bmp",
}
ALLOWED_DOCUMENT_MIMES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/plain",
}
ALLOWED_ALL_MIMES = ALLOWED_IMAGE_MIMES | ALLOWED_DOCUMENT_MIMES

# Tamaño máximo de archivo (en bytes)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB por defecto
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB para imágenes
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10 MB para documentos


# --- CONEXIÓN "SABUESO" (BUSCA LA BD REAL) ---
def buscar_bd_real():
    """Busca el archivo mi_sistema.db que tenga datos."""
    candidatos = [
        os.path.join(DATA_DIR, "mi_sistema.db"),                    # Opción 1: local data/
        os.path.abspath(os.path.join(BASE_DIR, "..", "data", "mi_sistema.db")), # Opción 2: src/data
        os.path.join(os.getcwd(), "data", "mi_sistema.db")          # Opción 3: cwd/data
    ]
    
    for ruta in candidatos:
        if os.path.exists(ruta) and os.path.getsize(ruta) > 0:
            logger.debug(f"🔍 BD encontrada: {ruta}")
            return ruta
    
    # Default al primero si no encuentra nada
    logger.warning(f"⚠️ BD no encontrada, usando default: {candidatos[0]}")
    return candidatos[0]

# --- Funciones de utilidad básicas ---
def get_db_connection():
    """
    Establece conexión con la base de datos SQLite UNIFICADA.
    Usa lógica de búsqueda inteligente para encontrar la BD real.
    """
    try:
        if "db" in g:
            return g.db

        # Primero intentar usar la configuración de Flask
        db_path = current_app.config.get("DATABASE_PATH")
        
        if not db_path:
            # Usar función sabueso para encontrar la BD real
            db_path = buscar_bd_real()
            logger.debug(f"🔌 Conexión Centralizada (sabueso): {db_path}")
        else:
            logger.debug(f"🔌 Conexión desde config: {db_path}")

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row

        if hasattr(g, 'db'):
            g.db = conn

        return conn

    except Exception as e:
        logger.critical(f"❌ ERROR CRÍTICO al intentar conectar a la base de datos: {e}", exc_info=True)
        raise Exception("Fallo en la conexión a la base de datos.")


def login_required(f):
    """
    Decorador para proteger rutas que requieren inicio de sesión.
    (CORREGIDO) Es inteligente: devuelve JSON para /api/ o redirige para web.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            logger.warning(f"Acceso no autorizado a: {request.path}")

            # Lógica inteligente: API vs Web
            if request.path.startswith("/api/"):
                # Es una API, devuelve JSON
                return jsonify({"error": "Acceso no autorizado. Se requiere inicio de sesión."}), 401
            else:
                # Es una página web, redirige al login
                # ✅ CORREGIDO: Usar el nombre correcto del blueprint main.login
                return redirect(url_for("main.login"))

        return f(*args, **kwargs)

    return decorated_function


def format_key(key):
    """Formatea claves de formulario para presentación legible."""
    s = "".join([" " + char if char.isupper() else char for char in key]).strip()
    return s.replace("_", " ").capitalize()


async def read_file_async(file):
    """Lectura asíncrona de archivos."""
    return file.read()


# ==================== FUNCIONES DE VALIDACIÓN DE ARCHIVOS ====================


def get_file_extension(filename):
    """
    Obtiene la extensión de un archivo.

    Args:
        filename (str): Nombre del archivo

    Returns:
        str: Extensión en minúsculas sin el punto, o cadena vacía si no hay extensión

    Example:
        >>> get_file_extension('documento.PDF')
        'pdf'
    """
    if "." in filename:
        return filename.rsplit(".", 1)[1].lower()
    return ""


def allowed_file(filename, allowed_extensions=None):
    """
    Verifica si un archivo tiene una extensión permitida.

    Args:
        filename (str): Nombre del archivo
        allowed_extensions (set, optional): Conjunto de extensiones permitidas.
                                            Por defecto usa ALLOWED_ALL_EXTENSIONS

    Returns:
        bool: True si la extensión está permitida, False en caso contrario

    Example:
        >>> allowed_file('documento.pdf')
        True
        >>> allowed_file('script.exe')
        False
    """
    if allowed_extensions is None:
        allowed_extensions = ALLOWED_ALL_EXTENSIONS

    return "." in filename and get_file_extension(filename) in allowed_extensions


def get_file_mimetype(file_storage):
    """
    Obtiene el MIME type de un archivo desde FileStorage de Flask.

    Args:
        file_storage: Objeto FileStorage de Werkzeug

    Returns:
        str: MIME type del archivo
    """
    # Primero intentar obtener del objeto file
    mime_type = file_storage.content_type

    # Si no está disponible, inferir desde la extensión
    if not mime_type or mime_type == "application/octet-stream":
        mime_type, _ = mimetypes.guess_type(file_storage.filename)

    return mime_type or "application/octet-stream"


def validate_file_type(file_storage, allowed_mimes=None):
    """
    Valida el MIME type de un archivo.

    Args:
        file_storage: Objeto FileStorage de Werkzeug
        allowed_mimes (set, optional): MIME types permitidos

    Returns:
        bool: True si el MIME type es válido
    """
    if allowed_mimes is None:
        allowed_mimes = ALLOWED_ALL_MIMES

    mime_type = get_file_mimetype(file_storage)
    return mime_type in allowed_mimes


def get_file_size(file_storage):
    """
    Obtiene el tamaño de un archivo en bytes.

    Args:
        file_storage: Objeto FileStorage de Werkzeug

    Returns:
        int: Tamaño del archivo en bytes
    """
    # Guardar posición actual
    file_storage.seek(0, os.SEEK_END)
    size = file_storage.tell()
    # Volver al inicio
    file_storage.seek(0)
    return size


def validate_file_size(file_storage, max_size=None):
    """
    Valida el tamaño de un archivo.

    Args:
        file_storage: Objeto FileStorage de Werkzeug
        max_size (int, optional): Tamaño máximo en bytes

    Returns:
        bool: True si el tamaño es válido
    """
    if max_size is None:
        max_size = MAX_FILE_SIZE

    size = get_file_size(file_storage)
    return size <= max_size


def validate_upload(file_storage, file_type="all", max_size=None):
    """
    Validación completa de un archivo subido.

    Realiza múltiples validaciones:
    - Verifica que el archivo exista y tenga nombre
    - Valida la extensión del archivo
    - Valida el MIME type
    - Valida el tamaño del archivo

    Args:
        file_storage: Objeto FileStorage de Werkzeug
        file_type (str): Tipo de archivo ('image', 'document', 'all')
        max_size (int, optional): Tamaño máximo en bytes

    Returns:
        tuple: (bool, str) - (es_válido, mensaje_error)

    Example:
        >>> from werkzeug.datastructures import FileStorage
        >>> is_valid, error = validate_upload(file, file_type='image')
        >>> if not is_valid:
        >>>     return jsonify({"error": error}), 400
    """
    # 1. Verificar que el archivo existe
    if not file_storage or not file_storage.filename:
        return False, "No se proporcionó ningún archivo."

    filename = file_storage.filename

    # 2. Validar extensión
    if file_type == "image":
        allowed_extensions = ALLOWED_IMAGE_EXTENSIONS
        allowed_mimes = ALLOWED_IMAGE_MIMES
        if max_size is None:
            max_size = MAX_IMAGE_SIZE
    elif file_type == "document":
        allowed_extensions = ALLOWED_DOCUMENT_EXTENSIONS
        allowed_mimes = ALLOWED_DOCUMENT_MIMES
        if max_size is None:
            max_size = MAX_DOCUMENT_SIZE
    else:  # 'all'
        allowed_extensions = ALLOWED_ALL_EXTENSIONS
        allowed_mimes = ALLOWED_ALL_MIMES
        if max_size is None:
            max_size = MAX_FILE_SIZE

    if not allowed_file(filename, allowed_extensions):
        ext = get_file_extension(filename)
        allowed_ext_str = ", ".join(sorted(allowed_extensions))
        return (
            False,
            f"Tipo de archivo no permitido (.{ext}). Extensiones permitidas: {allowed_ext_str}",
        )

    # 3. Validar MIME type
    if not validate_file_type(file_storage, allowed_mimes):
        mime = get_file_mimetype(file_storage)
        return (
            False,
            f"Tipo MIME no permitido ({mime}). El archivo puede estar corrupto o ser malicioso.",
        )

    # 4. Validar tamaño
    if not validate_file_size(file_storage, max_size):
        size_mb = get_file_size(file_storage) / (1024 * 1024)
        max_mb = max_size / (1024 * 1024)
        return (
            False,
            f"Archivo demasiado grande ({size_mb:.1f} MB). Tamaño máximo: {max_mb:.1f} MB",
        )

    # Todas las validaciones pasaron
    return True, ""


def sanitize_and_save_file(file_storage, destination_folder, custom_filename=None):
    """
    Sanitiza el nombre de archivo y lo guarda de forma segura.

    Args:
        file_storage: Objeto FileStorage de Werkzeug
        destination_folder (str): Carpeta de destino
        custom_filename (str, optional): Nombre personalizado para el archivo

    Returns:
        str: Ruta completa del archivo guardado

    Raises:
        ValueError: Si el archivo no es válido
        IOError: Si hay error al guardar
    """
    # Validar el archivo primero
    is_valid, error_msg = validate_upload(file_storage)
    if not is_valid:
        raise ValueError(error_msg)

    # Crear carpeta si no existe
    os.makedirs(destination_folder, exist_ok=True)

    # Obtener nombre de archivo seguro
    if custom_filename:
        filename = secure_filename(custom_filename)
        # Asegurar que tenga la extensión correcta
        original_ext = get_file_extension(file_storage.filename)
        if not filename.endswith(f".{original_ext}"):
            filename = f"{filename}.{original_ext}"
    else:
        filename = secure_filename(file_storage.filename)

    # Construir ruta completa
    filepath = os.path.join(destination_folder, filename)

    # Evitar sobrescribir archivos existentes
    if os.path.exists(filepath):
        name, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(filepath):
            filename = f"{name}_{counter}{ext}"
            filepath = os.path.join(destination_folder, filename)
            counter += 1

    # Guardar el archivo
    try:
        file_storage.save(filepath)
        logger.info(f"✓ Archivo guardado: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Error guardando archivo: {e}")
        raise IOError(f"Error al guardar el archivo: {str(e)}")


def validate_multiple_uploads(files_list, file_type="all", max_size=None):
    """
    Valida múltiples archivos subidos.

    Args:
        files_list (list): Lista de objetos FileStorage
        file_type (str): Tipo de archivo ('image', 'document', 'all')
        max_size (int, optional): Tamaño máximo por archivo

    Returns:
        tuple: (bool, list) - (todos_válidos, lista_de_errores)

    Example:
        >>> files = request.files.getlist('documentos')
        >>> all_valid, errors = validate_multiple_uploads(files, 'document')
        >>> if not all_valid:
        >>>     return jsonify({"errors": errors}), 400
    """
    errors = []

    for i, file_storage in enumerate(files_list):
        if file_storage and file_storage.filename:
            is_valid, error_msg = validate_upload(file_storage, file_type, max_size)
            if not is_valid:
                errors.append(f"Archivo {i+1} ({file_storage.filename}): {error_msg}")

    return len(errors) == 0, errors


# ==================== FUNCIONES DE INFORMACIÓN ====================


def get_file_info(file_storage):
    """
    Obtiene información detallada de un archivo.

    Args:
        file_storage: Objeto FileStorage de Werkzeug

    Returns:
        dict: Información del archivo (nombre, extensión, mime, tamaño)
    """
    return {
        "filename": file_storage.filename,
        "extension": get_file_extension(file_storage.filename),
        "mime_type": get_file_mimetype(file_storage),
        "size_bytes": get_file_size(file_storage),
        "size_mb": round(get_file_size(file_storage) / (1024 * 1024), 2),
    }


def format_file_size(size_bytes):
    """
    Formatea un tamaño de archivo en bytes a formato legible.

    Args:
        size_bytes (int): Tamaño en bytes

    Returns:
        str: Tamaño formateado (ej: "1.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


# ==================== LOGGING ====================


def log_file_upload(filename, user_id, success=True, error=None):
    """
    Registra información sobre un upload de archivo.

    Args:
        filename (str): Nombre del archivo
        user_id: ID del usuario que subió el archivo
        success (bool): Si el upload fue exitoso
        error (str, optional): Mensaje de error si falló
    """
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if success:
        logger.info(f"[{timestamp}] ✓ UPLOAD EXITOSO - Usuario: {user_id}, Archivo: {filename}")
    else:
        logger.warning(f"[{timestamp}] Œ UPLOAD FALLIDO - Usuario: {user_id}, Archivo: {filename}, Error: {error}")


# ==================== FUNCIONES DE CONFIGURACIÓN CENTRALIZADA DE UPLOADS ====================

def get_upload_folder(subdir=None):
    """
    Obtiene la ruta de la carpeta de uploads desde la configuración global.
    
    Args:
        subdir (str, optional): Subcarpeta específica ('docs', 'formularios', 'tutelas', 'impuestos', 'temp')
    
    Returns:
        str: Ruta absoluta a la carpeta de uploads
    
    Example:
        >>> get_upload_folder('docs')
        '/app/static/uploads/docs'
    """
    base_upload = current_app.config.get('UPLOAD_FOLDER', os.path.join(BASE_DIR, 'static', 'uploads'))
    
    if subdir:
        upload_path = os.path.join(base_upload, subdir)
    else:
        upload_path = base_upload
    
    # Crear carpeta si no existe
    os.makedirs(upload_path, exist_ok=True)
    
    return upload_path


def get_max_file_size():
    """
    Obtiene el tamaño máximo de archivo permitido desde la configuración global.
    
    Returns:
        int: Tamaño máximo en bytes (por defecto 16MB)
    
    Example:
        >>> get_max_file_size()
        16777216
    """
    return current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)


def get_allowed_extensions():
    """
    Obtiene el conjunto de extensiones permitidas desde la configuración global.
    
    Returns:
        set: Conjunto de extensiones permitidas
    
    Example:
        >>> get_allowed_extensions()
        {'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'csv'}
    """
    return current_app.config.get('ALLOWED_EXTENSIONS', ALLOWED_ALL_EXTENSIONS)


def is_file_allowed(filename):
    """
    Verifica si un archivo está permitido según la configuración global.
    
    Args:
        filename (str): Nombre del archivo a validar
    
    Returns:
        bool: True si el archivo está permitido, False en caso contrario
    
    Example:
        >>> is_file_allowed('documento.pdf')
        True
        >>> is_file_allowed('virus.exe')
        False
    """
    if not filename or '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    allowed_extensions = get_allowed_extensions()
    
    return extension in allowed_extensions


def validate_file_size(file_content):
    """
    Valida que el tamaño del archivo no exceda el límite configurado.
    
    Args:
        file_content (bytes): Contenido del archivo en bytes
    
    Returns:
        tuple: (bool, str) - (es_válido, mensaje_error)
    
    Example:
        >>> validate_file_size(b'contenido')
        (True, None)
    """
    max_size = get_max_file_size()
    file_size = len(file_content)
    
    if file_size > max_size:
        max_mb = max_size / (1024 * 1024)
        actual_mb = file_size / (1024 * 1024)
        return False, f"Archivo demasiado grande ({actual_mb:.2f}MB). Máximo permitido: {max_mb:.0f}MB"
    
    return True, None


def save_uploaded_file(file, subdir, custom_filename=None):
    """
    Guarda un archivo subido usando la configuración centralizada.
    
    Args:
        file: Objeto FileStorage de Flask
        subdir (str): Subcarpeta donde guardar ('docs', 'formularios', 'tutelas', etc.)
        custom_filename (str, optional): Nombre personalizado para el archivo
    
    Returns:
        tuple: (ruta_completa, ruta_relativa, mensaje_error)
    
    Example:
        >>> save_uploaded_file(file, 'docs', 'informe_2024.pdf')
        ('/app/static/uploads/docs/informe_2024.pdf', 'uploads/docs/informe_2024.pdf', None)
    """
    try:
        # Validar que el archivo existe
        if not file or not file.filename:
            return None, None, "Archivo no válido"
        
        # Validar extensión
        if not is_file_allowed(file.filename):
            return None, None, f"Tipo de archivo no permitido. Extensiones válidas: {', '.join(get_allowed_extensions())}"
        
        # Leer contenido para validar tamaño
        file_content = file.read()
        is_valid, error_msg = validate_file_size(file_content)
        if not is_valid:
            return None, None, error_msg
        
        # Resetear puntero del archivo
        file.seek(0)
        
        # Obtener carpeta de destino
        upload_folder = get_upload_folder(subdir)
        
        # Determinar nombre del archivo
        if custom_filename:
            filename = secure_filename(custom_filename)
        else:
            filename = secure_filename(file.filename)
        
        # Construir ruta completa
        filepath = os.path.join(upload_folder, filename)
        
        # Guardar archivo
        file.save(filepath)
        
        # Calcular ruta relativa desde static/
        relative_path = os.path.relpath(filepath, os.path.join(BASE_DIR, 'static'))
        
        logger.info(f"Archivo guardado exitosamente: {filepath}")
        return filepath, relative_path, None
        
    except Exception as e:
        logger.error(f"Error al guardar archivo: {e}", exc_info=True)
        return None, None, str(e)


# (El resto de tu archivo utils.py de 13.000 líneas iría aquí...)

