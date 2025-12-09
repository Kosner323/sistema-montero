#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
routes/gestor_archivos.py
=========================
Gestor Jerárquico de Archivos de Usuarios
Fase 11: Navegación y visualización de documentos organizados por carpetas

Autor: Senior Backend Developer
Fecha: 2025-11-30
"""

import os
from flask import Blueprint, request, jsonify, send_file, session
from functools import wraps
from pathlib import Path

# Logger
try:
    from logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Blueprint
bp_archivos = Blueprint('archivos', __name__, url_prefix='/api/archivos')

# Ruta base de archivos (configurable)
BASE_UPLOADS_PATH = os.path.join('static', 'uploads', 'usuarios')


# =============================================================================
# DECORADOR: AUTENTICACIÓN
# =============================================================================

def login_required(f):
    """Decorador para requerir autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            logger.warning("Intento de acceso no autenticado al gestor de archivos")
            return jsonify({
                'success': False,
                'error': 'Debes iniciar sesión'
            }), 401
        return f(*args, **kwargs)
    return decorated_function


# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def construir_arbol_archivos(ruta_base: str, nivel_maximo: int = 5) -> dict:
    """
    Construye un árbol jerárquico de archivos y carpetas.

    Args:
        ruta_base: Ruta raíz desde donde escanear
        nivel_maximo: Profundidad máxima a escanear (evita recursión infinita)

    Returns:
        dict: Estructura de árbol
            {
                "nombre": "2024",
                "tipo": "carpeta",
                "ruta": "static/uploads/usuarios/123/2024",
                "hijos": [
                    {
                        "nombre": "Recibos",
                        "tipo": "carpeta",
                        "hijos": [
                            {
                                "nombre": "recibo_enero.pdf",
                                "tipo": "archivo",
                                "extension": ".pdf",
                                "tamano": 102400,
                                "ruta": "..."
                            }
                        ]
                    }
                ]
            }
    """
    def escanear_directorio(ruta, nivel=0):
        """Escanea recursivamente un directorio"""
        if nivel > nivel_maximo:
            return None

        if not os.path.exists(ruta):
            return None

        nombre = os.path.basename(ruta)

        # Si es un archivo
        if os.path.isfile(ruta):
            extension = os.path.splitext(nombre)[1].lower()
            tamano = os.path.getsize(ruta)

            return {
                'nombre': nombre,
                'tipo': 'archivo',
                'extension': extension,
                'tamano': tamano,
                'tamano_legible': formato_tamano(tamano),
                'ruta_relativa': ruta.replace('\\', '/'),
                'modificado': os.path.getmtime(ruta)
            }

        # Si es un directorio
        elif os.path.isdir(ruta):
            hijos = []

            try:
                for item in sorted(os.listdir(ruta)):
                    ruta_completa = os.path.join(ruta, item)
                    hijo = escanear_directorio(ruta_completa, nivel + 1)

                    if hijo:
                        hijos.append(hijo)

            except PermissionError:
                logger.warning(f"Sin permisos para leer: {ruta}")
                return None

            return {
                'nombre': nombre,
                'tipo': 'carpeta',
                'ruta_relativa': ruta.replace('\\', '/'),
                'hijos': hijos,
                'total_archivos': contar_archivos(hijos),
                'total_carpetas': contar_carpetas(hijos)
            }

        return None

    return escanear_directorio(ruta_base)


def contar_archivos(hijos: list) -> int:
    """Cuenta recursivamente el total de archivos"""
    total = 0
    for hijo in hijos:
        if hijo['tipo'] == 'archivo':
            total += 1
        elif hijo['tipo'] == 'carpeta':
            total += contar_archivos(hijo.get('hijos', []))
    return total


def contar_carpetas(hijos: list) -> int:
    """Cuenta recursivamente el total de carpetas"""
    total = 0
    for hijo in hijos:
        if hijo['tipo'] == 'carpeta':
            total += 1
            total += contar_carpetas(hijo.get('hijos', []))
    return total


def formato_tamano(bytes_size: int) -> str:
    """
    Convierte bytes a formato legible (KB, MB, GB).

    Args:
        bytes_size: Tamaño en bytes

    Returns:
        str: Tamaño formateado
    """
    for unidad in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unidad}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


# =============================================================================
# ENDPOINT: GET /api/archivos/arbol/<usuario_id>
# =============================================================================

@bp_archivos.route('/arbol/<string:usuario_id>', methods=['GET'])
@login_required
def obtener_arbol_archivos(usuario_id):
    """
    FASE 11: Obtiene el árbol jerárquico de archivos de un usuario.

    Args:
        usuario_id: Identificación del usuario

    Query Params:
        - nivel_maximo: Profundidad máxima de escaneo (default: 5)

    Response JSON:
        {
            "success": true,
            "usuario_id": "1234567890",
            "arbol": {
                "nombre": "1234567890",
                "tipo": "carpeta",
                "hijos": [...]
            },
            "estadisticas": {
                "total_archivos": 45,
                "total_carpetas": 8,
                "tamano_total": "15.3 MB"
            }
        }
    """
    try:
        # Parámetros
        nivel_maximo = request.args.get('nivel_maximo', 5, type=int)

        # Construir ruta del usuario
        ruta_usuario = os.path.join(BASE_UPLOADS_PATH, usuario_id)

        logger.info(f"📂 Escaneando archivos de usuario: {usuario_id}, ruta: {ruta_usuario}")

        # Verificar que la carpeta existe
        if not os.path.exists(ruta_usuario):
            logger.warning(f"⚠️ Carpeta no existe: {ruta_usuario}")

            # Crear carpeta vacía
            os.makedirs(ruta_usuario, exist_ok=True)

            return jsonify({
                'success': True,
                'usuario_id': usuario_id,
                'arbol': {
                    'nombre': usuario_id,
                    'tipo': 'carpeta',
                    'hijos': [],
                    'ruta_relativa': ruta_usuario.replace('\\', '/')
                },
                'estadisticas': {
                    'total_archivos': 0,
                    'total_carpetas': 0,
                    'tamano_total': '0 B'
                },
                'mensaje': 'Carpeta creada (estaba vacía)'
            }), 200

        # Construir árbol
        arbol = construir_arbol_archivos(ruta_usuario, nivel_maximo)

        if not arbol:
            return jsonify({
                'success': False,
                'error': 'No se pudo construir el árbol de archivos'
            }), 500

        # Calcular estadísticas
        total_archivos = arbol.get('total_archivos', 0)
        total_carpetas = arbol.get('total_carpetas', 0)

        # Calcular tamaño total
        def calcular_tamano_total(nodo):
            """Suma recursiva de tamaños"""
            if nodo['tipo'] == 'archivo':
                return nodo.get('tamano', 0)
            elif nodo['tipo'] == 'carpeta':
                total = 0
                for hijo in nodo.get('hijos', []):
                    total += calcular_tamano_total(hijo)
                return total
            return 0

        tamano_total_bytes = calcular_tamano_total(arbol)

        logger.info(f"✅ Árbol construido: {total_archivos} archivos, {total_carpetas} carpetas, {formato_tamano(tamano_total_bytes)}")

        return jsonify({
            'success': True,
            'usuario_id': usuario_id,
            'arbol': arbol,
            'estadisticas': {
                'total_archivos': total_archivos,
                'total_carpetas': total_carpetas,
                'tamano_total': formato_tamano(tamano_total_bytes),
                'tamano_total_bytes': tamano_total_bytes
            }
        }), 200

    except Exception as e:
        logger.error(f"❌ Error obteniendo árbol de archivos: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Error al obtener árbol de archivos',
            'detalle': str(e)
        }), 500


# =============================================================================
# ENDPOINT: GET /api/archivos/ver/<path:filepath>
# =============================================================================

@bp_archivos.route('/ver/<path:filepath>', methods=['GET'])
@login_required
def ver_archivo(filepath):
    """
    FASE 11: Visualiza o descarga un archivo específico.

    Args:
        filepath: Ruta relativa del archivo desde la raíz de uploads

    Query Params:
        - descargar: Si está presente, fuerza descarga en lugar de visualizar

    Response:
        Archivo para visualizar o descargar
    """
    try:
        # Limpiar filepath (evitar path traversal attacks)
        filepath = filepath.replace('..', '').strip('/')

        # Construir ruta completa
        ruta_completa = os.path.join(filepath)

        logger.info(f"📄 Solicitando archivo: {filepath}")

        # Verificar que el archivo existe
        if not os.path.exists(ruta_completa):
            logger.warning(f"⚠️ Archivo no encontrado: {ruta_completa}")
            return jsonify({
                'success': False,
                'error': 'Archivo no encontrado'
            }), 404

        # Verificar que es un archivo (no directorio)
        if not os.path.isfile(ruta_completa):
            return jsonify({
                'success': False,
                'error': 'La ruta no es un archivo válido'
            }), 400

        # Determinar si se debe forzar descarga
        forzar_descarga = 'descargar' in request.args

        # Enviar archivo
        logger.info(f"✅ Enviando archivo: {os.path.basename(filepath)} ({'descarga' if forzar_descarga else 'visualización'})")

        return send_file(
            ruta_completa,
            as_attachment=forzar_descarga,
            download_name=os.path.basename(filepath)
        )

    except Exception as e:
        logger.error(f"❌ Error al enviar archivo: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Error al enviar archivo',
            'detalle': str(e)
        }), 500


# =============================================================================
# ENDPOINT: GET /api/archivos/buscar (BONUS)
# =============================================================================

@bp_archivos.route('/buscar', methods=['GET'])
@login_required
def buscar_archivos():
    """
    Busca archivos por nombre en la carpeta de un usuario.

    Query Params:
        - usuario_id: ID del usuario
        - query: Término de búsqueda
        - extension: Filtrar por extensión (.pdf, .jpg, etc.)

    Response JSON:
        {
            "success": true,
            "resultados": [
                {
                    "nombre": "recibo.pdf",
                    "ruta": "static/uploads/usuarios/123/2024/recibo.pdf",
                    "tamano": "150.2 KB"
                }
            ],
            "total": 5
        }
    """
    try:
        usuario_id = request.args.get('usuario_id')
        query = request.args.get('query', '').lower()
        extension_filtro = request.args.get('extension', '').lower()

        if not usuario_id:
            return jsonify({
                'success': False,
                'error': 'Falta parámetro usuario_id'
            }), 400

        ruta_usuario = os.path.join(BASE_UPLOADS_PATH, usuario_id)

        if not os.path.exists(ruta_usuario):
            return jsonify({
                'success': True,
                'resultados': [],
                'total': 0,
                'mensaje': 'Usuario sin archivos'
            }), 200

        # Buscar archivos
        resultados = []

        for root, dirs, files in os.walk(ruta_usuario):
            for file in files:
                # Filtro por nombre
                if query and query not in file.lower():
                    continue

                # Filtro por extensión
                extension = os.path.splitext(file)[1].lower()
                if extension_filtro and extension != extension_filtro:
                    continue

                ruta_completa = os.path.join(root, file)
                tamano = os.path.getsize(ruta_completa)

                resultados.append({
                    'nombre': file,
                    'ruta_relativa': ruta_completa.replace('\\', '/'),
                    'carpeta': os.path.dirname(ruta_completa).replace('\\', '/'),
                    'extension': extension,
                    'tamano': tamano,
                    'tamano_legible': formato_tamano(tamano)
                })

        logger.info(f"🔍 Búsqueda: '{query}', Resultados: {len(resultados)}")

        return jsonify({
            'success': True,
            'resultados': resultados,
            'total': len(resultados)
        }), 200

    except Exception as e:
        logger.error(f"❌ Error en búsqueda: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Error en búsqueda',
            'detalle': str(e)
        }), 500


if __name__ == "__main__":
    print("Módulo gestor de archivos cargado correctamente")
