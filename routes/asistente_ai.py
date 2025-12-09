# -*- coding: utf-8 -*-
"""
asistente_ai.py - Backend del Asistente IA Montero
==================================================
Endpoint para chat con el "Cerebro del Sistema"
Versión 2.0: Integrado con Google Gemini AI
Fallback a respuestas basadas en palabras clave si la API falla
"""

from flask import Blueprint, jsonify, request, session
from logger import logger
from datetime import datetime
from functools import wraps
import os

# ==================== INTEGRACIÓN GOOGLE GEMINI ====================
try:
    import google.generativeai as genai

    # Configurar API Key desde variable de entorno
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        GEMINI_AVAILABLE = True
        logger.info("🤖 Google Gemini API configurado correctamente")
    else:
        GEMINI_AVAILABLE = False
        logger.warning("⚠️ GEMINI_API_KEY no encontrado en variables de entorno. Usando fallback de palabras clave.")

except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("⚠️ google-generativeai no instalado. Usando fallback de palabras clave.")
# ==================================================================

# --- IMPORTACIÓN CENTRALIZADA ---
try:
    from ..utils import get_db_connection, login_required
except (ImportError, ValueError):
    from utils import get_db_connection, login_required
# -------------------------------

# ==================== DEFINICIÓN DEL BLUEPRINT ====================
asistente_bp = Blueprint("asistente", __name__, url_prefix="/api/asistente")


# ==================== DECORADOR DE AUTENTICACIÓN ====================
def require_auth(f):
    """Decorador para requerir autenticación en endpoints del asistente"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            logger.warning("🚫 Intento de acceso no autenticado al asistente")
            return jsonify({
                'error': 'No autenticado',
                'message': 'Debes iniciar sesión para usar el asistente'
            }), 401
        return f(*args, **kwargs)
    return decorated_function


# ==================== FUNCIÓN: OBTENER ESQUEMA DE BD ====================
def get_schema_str() -> str:
    """
    Inspecciona la base de datos y retorna un resumen del esquema.

    Returns:
        str: Resumen de tablas y columnas principales
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Obtener lista de tablas
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tablas = cursor.fetchall()

        schema_parts = ["=== ESQUEMA DE BASE DE DATOS ===\n"]

        for (tabla_name,) in tablas:
            # Obtener información de columnas para cada tabla
            cursor.execute(f"PRAGMA table_info({tabla_name})")
            columnas = cursor.fetchall()

            # Filtrar solo columnas clave (primeras 8 o las más importantes)
            columnas_clave = []
            for col in columnas[:8]:  # Limitar a 8 columnas por tabla
                col_id, col_name, col_type, not_null, default_val, pk = col
                pk_marker = " (PK)" if pk else ""
                columnas_clave.append(f"{col_name} {col_type}{pk_marker}")

            schema_parts.append(f"\nTabla: {tabla_name}")
            schema_parts.append(f"Columnas: {', '.join(columnas_clave)}")

        conn.close()

        schema_str = "\n".join(schema_parts)
        logger.info("📊 Esquema de base de datos generado exitosamente")
        return schema_str

    except Exception as e:
        logger.error(f"❌ Error al obtener esquema de BD: {e}")
        return "Error: No se pudo obtener el esquema de la base de datos"


# ==================== FUNCIÓN: EJECUTAR SQL SEGURO ====================
def ejecutar_sql_seguro(sql_query: str) -> dict:
    """
    Ejecuta consultas SQL de forma segura (solo SELECT permitido).

    Args:
        sql_query: Consulta SQL a ejecutar

    Returns:
        dict: {'success': bool, 'data': list, 'error': str}
    """
    try:
        # Normalizar query (eliminar espacios extras y convertir a mayúsculas para análisis)
        sql_upper = sql_query.strip().upper()

        # VALIDACIÓN DE SEGURIDAD: Solo permitir SELECT
        palabras_prohibidas = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'TRUNCATE', 'CREATE', 'GRANT', 'REVOKE']

        for palabra in palabras_prohibidas:
            if palabra in sql_upper:
                logger.warning(f"🚫 Intento de ejecutar query peligroso: {sql_query[:100]}")
                return {
                    'success': False,
                    'data': [],
                    'error': f'❌ OPERACIÓN PROHIBIDA: No se permiten comandos {palabra}. Solo consultas SELECT.'
                }

        # Verificar que sea un SELECT
        if not sql_upper.startswith('SELECT'):
            logger.warning(f"🚫 Query no comienza con SELECT: {sql_query[:100]}")
            return {
                'success': False,
                'data': [],
                'error': '❌ Solo se permiten consultas SELECT.'
            }

        # Ejecutar consulta
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        resultados = cursor.fetchall()

        # Obtener nombres de columnas
        columnas = [description[0] for description in cursor.description] if cursor.description else []

        conn.close()

        # Formatear resultados
        if not resultados:
            return {
                'success': True,
                'data': [],
                'message': 'Consulta ejecutada correctamente, pero no se encontraron resultados.'
            }

        # Convertir resultados a lista de diccionarios
        datos_formateados = []
        for fila in resultados[:100]:  # Limitar a 100 filas para evitar sobrecarga
            datos_formateados.append(dict(zip(columnas, fila)))

        logger.info(f"✅ SQL ejecutado exitosamente: {len(resultados)} filas retornadas")

        return {
            'success': True,
            'data': datos_formateados,
            'row_count': len(resultados),
            'columns': columnas
        }

    except Exception as e:
        logger.error(f"❌ Error al ejecutar SQL: {e}")
        return {
            'success': False,
            'data': [],
            'error': f'Error en la consulta: {str(e)}'
        }


# ==================== FUNCIÓN: PROCESAR CON GEMINI AI ====================
def procesar_con_gemini(mensaje: str, user_id: int = None) -> str:
    """
    Procesa el mensaje del usuario usando Google Gemini AI con capacidades de consulta a BD.
    Implementa ReAct Pattern: Reasoning + Acting (SQL execution).

    Args:
        mensaje: Texto del mensaje del usuario
        user_id: ID del usuario autenticado

    Returns:
        str: Respuesta generada por Gemini AI

    Raises:
        Exception: Si hay error en la API (para activar fallback)
    """
    try:
        import json
        import re

        # Inicializar modelo Gemini 2.5 Flash (rápido y eficiente)
        model = genai.GenerativeModel('gemini-flash-latest')

        # Obtener contexto del usuario
        user_name = session.get('user_name', 'Usuario')

        # Obtener esquema de la base de datos
        schema_bd = get_schema_str()

        # System Prompt: Define el rol y comportamiento del asistente
        system_context = f"""Tu nombre es **Jordy**. Eres el copiloto operativo del Sistema Montero.

INSTRUCCIÓN DE IDENTIDAD: Si te preguntan quién eres, preséntate como Jordy, el asistente inteligente del Sistema Montero.

ACTÚA CON PERSONALIDAD: Profesional pero cercano. Toma iniciativa, sugiere mejoras y actúa como un asesor de confianza.

Eres experto en:
- Marco Legal de Seguridad Social en Colombia (Ley 100 de 1993 y decretos reglamentarios)
- Procedimientos de Tutelas y Derechos de Petición en Colombia
- Liquidación de PILA (Planilla Integrada de Liquidación de Aportes) y Nómina
- Python y desarrollo de software
- Gestión financiera y contabilidad empresarial
- Gestión de recursos humanos y personal
- Análisis de datos empresariales y business intelligence
- SQL y bases de datos SQLite

INSTRUCCIÓN CLAVE: Si el usuario pregunta sobre una incapacidad negada, una deuda presunta de seguridad social, o cualquier tema legal relacionado con el sistema colombiano de salud y pensiones, analiza el caso bajo la ley colombiana y sugiere los pasos legales a seguir. Sé técnico pero claro.

Tu objetivo es ayudar a {user_name} a operar eficientemente el Sistema Montero, proporcionando asesoría legal, técnica y estratégica. Recuerda: eres Jordy, su copiloto de confianza.

ACCESO A BASE DE DATOS:
Tienes acceso EXCLUSIVAMENTE de LECTURA a la siguiente base de datos SQLite:

{schema_bd}

REGLAS PARA CONSULTAS SQL:
1. Si el usuario pregunta por datos específicos (cantidad, listados, reportes, etc.), DEBES generar una consulta SQL SQLite válida.
2. Cuando necesites consultar la BD, responde ÚNICAMENTE un objeto JSON con este formato EXACTO:
   {{"sql": "SELECT columnas FROM tabla WHERE condicion"}}
3. NO agregues texto adicional ni explicaciones cuando generes SQL, SOLO el JSON.
4. Solo puedes usar comandos SELECT (lectura). Nunca uses DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE.
5. Después de recibir los resultados, responde al usuario de forma natural y profesional.

REGLAS DE RESPUESTA:
1. Si NO necesitas consultar la BD, responde de forma BREVE, PROFESIONAL y DIRECTA (máximo 3-4 líneas).
2. Usa emojis moderadamente para hacer las respuestas más amigables.
3. Si no estás seguro de algo, admítelo honestamente.
4. Enfócate en soluciones prácticas y accionables.

CONTEXTO ACTUAL:
- Sistema: Montero (Gestión de usuarios, empresas, pagos, tutelas)
- Usuario actual: {user_name}
- Fecha: {datetime.now().strftime('%Y-%m-%d')}
"""

        # ========== CICLO REACT: REASONING + ACTING ==========
        max_iteraciones = 3  # Máximo 3 intentos para evitar loops infinitos
        iteracion = 0
        conversacion_actual = mensaje

        while iteracion < max_iteraciones:
            iteracion += 1

            # Construir prompt completo
            full_prompt = f"{system_context}\n\nUsuario pregunta: {conversacion_actual}\n\nRespuesta:"

            # Generar respuesta con Gemini
            response = model.generate_content(full_prompt)
            respuesta_texto = response.text.strip()

            logger.info(f"🔄 Iteración {iteracion} - Respuesta Gemini: {respuesta_texto[:100]}...")

            # Intentar detectar JSON con SQL
            # Buscar patrones como {"sql": "SELECT..."}
            json_match = re.search(r'\{[\s\n]*"sql"[\s\n]*:[\s\n]*"([^"]+)"[\s\n]*\}', respuesta_texto, re.IGNORECASE | re.DOTALL)

            if json_match:
                # Se detectó un JSON con SQL
                sql_query = json_match.group(1)
                logger.info(f"📊 SQL detectado: {sql_query}")

                # Ejecutar SQL de forma segura
                resultado_sql = ejecutar_sql_seguro(sql_query)

                if resultado_sql['success']:
                    # SQL ejecutado exitosamente
                    datos = resultado_sql['data']
                    row_count = resultado_sql.get('row_count', len(datos))

                    logger.info(f"✅ SQL exitoso - {row_count} filas")

                    # Formatear resultados para el siguiente prompt
                    if datos:
                        # Mostrar primeros 10 registros para no saturar el prompt
                        datos_muestra = datos[:10]
                        datos_str = json.dumps(datos_muestra, indent=2, ensure_ascii=False)
                        resumen = f"Consulta SQL ejecutada exitosamente.\nResultados ({row_count} filas totales, mostrando primeras {len(datos_muestra)}):\n{datos_str}"
                    else:
                        resumen = resultado_sql.get('message', 'Consulta ejecutada, sin resultados.')

                    # Re-promptear con los resultados
                    conversacion_actual = f"{mensaje}\n\n[RESULTADOS DE CONSULTA SQL]:\n{resumen}\n\nAhora responde al usuario de forma natural basándote en estos datos."

                else:
                    # Error al ejecutar SQL
                    error_msg = resultado_sql.get('error', 'Error desconocido')
                    logger.error(f"❌ Error SQL: {error_msg}")
                    conversacion_actual = f"{mensaje}\n\n[ERROR EN CONSULTA SQL]: {error_msg}\n\nInforma al usuario del error y sugiere una alternativa."

                # Continuar el loop para obtener respuesta final
                continue

            else:
                # No se detectó SQL, es una respuesta final
                logger.info(f"✅ Respuesta final generada (iteración {iteracion})")
                return respuesta_texto

        # Si se alcanzó el límite de iteraciones
        logger.warning(f"⚠️ Se alcanzó el límite de iteraciones ({max_iteraciones})")
        return "⚠️ Lo siento, la consulta se volvió muy compleja. ¿Puedes reformular tu pregunta de forma más específica?"

    except Exception as e:
        logger.error(f"❌ Error en Gemini AI: {e}")
        raise  # Re-lanzar para activar fallback


# ==================== FUNCIÓN: PROCESAR MENSAJE (FALLBACK) ====================
def procesar_mensaje_inteligente(mensaje: str, user_id: int = None) -> str:
    """
    Procesa el mensaje del usuario y genera una respuesta inteligente.
    
    Lógica actual: Palabras clave + consultas a BD
    TODO: Reemplazar con llamada a LLM (OpenAI, Claude, etc.)
    
    Args:
        mensaje: Texto del mensaje del usuario
        user_id: ID del usuario autenticado
        
    Returns:
        str: Respuesta generada por el asistente
    """
    mensaje_lower = mensaje.lower().strip()
    
    try:
        # =========================================
        # CATEGORÍA 1: SALUDOS
        # =========================================
        if any(palabra in mensaje_lower for palabra in ['hola', 'buenos días', 'buenas tardes', 'hey', 'hi']):
            user_name = session.get('user_name', 'Usuario')
            return f"¡Hola {user_name}! 👋 Soy el Asistente Montero, el cerebro del sistema. ¿En qué puedo ayudarte hoy?"
        
        # =========================================
        # CATEGORÍA 2: CONSULTAS DE USUARIOS
        # =========================================
        if 'usuario' in mensaje_lower or 'empleado' in mensaje_lower:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Total de usuarios
            if 'cuántos' in mensaje_lower or 'cantidad' in mensaje_lower or 'total' in mensaje_lower:
                cursor.execute("SELECT COUNT(*) FROM usuarios")
                total = cursor.fetchone()[0]
                conn.close()
                return f"📊 Actualmente hay **{total} usuarios** registrados en la base de datos del sistema."
            
            # Usuarios activos
            if 'activo' in mensaje_lower:
                cursor.execute("SELECT COUNT(*) FROM usuarios WHERE estado = 'activo'")
                activos = cursor.fetchone()[0]
                conn.close()
                return f"✅ Hay **{activos} usuarios activos** en el sistema."
            
            # Listado reciente
            if 'último' in mensaje_lower or 'reciente' in mensaje_lower:
                cursor.execute("""
                    SELECT nombre_completo, fecha_registro 
                    FROM usuarios 
                    ORDER BY fecha_registro DESC 
                    LIMIT 5
                """)
                ultimos = cursor.fetchall()
                conn.close()
                
                if ultimos:
                    lista = "\n".join([f"• {u[0]} (registrado: {u[1]})" for u in ultimos])
                    return f"📋 **Últimos 5 usuarios registrados:**\n{lista}"
                else:
                    return "No hay usuarios recientes registrados."
            
            conn.close()
            return "Puedo ayudarte con información sobre usuarios. Pregunta por el total, activos, o los más recientes."
        
        # =========================================
        # CATEGORÍA 3: CONSULTAS DE EMPRESAS
        # =========================================
        if 'empresa' in mensaje_lower or 'cliente' in mensaje_lower:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if 'cuántas' in mensaje_lower or 'cantidad' in mensaje_lower or 'total' in mensaje_lower:
                cursor.execute("SELECT COUNT(*) FROM empresas")
                total = cursor.fetchone()[0]
                conn.close()
                return f"🏢 Actualmente hay **{total} empresas** registradas en el sistema."
            
            if 'activa' in mensaje_lower:
                cursor.execute("SELECT COUNT(*) FROM empresas WHERE estado = 'activa'")
                activas = cursor.fetchone()[0]
                conn.close()
                return f"✅ Hay **{activas} empresas activas** en el sistema."
            
            conn.close()
            return "Puedo ayudarte con información sobre empresas. Pregunta por el total, activas, o detalles específicos."
        
        # =========================================
        # CATEGORÍA 4: CONSULTAS DE PAGOS
        # =========================================
        if 'pago' in mensaje_lower or 'cartera' in mensaje_lower or 'deuda' in mensaje_lower:
            return "💰 Para consultas sobre pagos y cartera, puedo ayudarte a:\n• Ver el estado de la cartera\n• Consultar pagos pendientes\n• Generar reportes de recaudo\n\n¿Qué información necesitas específicamente?"
        
        # =========================================
        # CATEGORÍA 5: AYUDA Y GUÍA
        # =========================================
        if 'ayuda' in mensaje_lower or 'help' in mensaje_lower or 'qué puedes' in mensaje_lower:
            return """🧠 **Soy el Asistente Montero**, puedo ayudarte con:

📊 **Consultas de datos:**
• Cantidad de usuarios, empresas, pagos
• Reportes y estadísticas

📋 **Información del sistema:**
• Estado de módulos
• Tareas pendientes
• Notificaciones

🔍 **Búsquedas:**
• Usuarios por nombre o documento
• Empresas por NIT
• Expedientes y formularios

💡 **Sugerencias:**
• Automatizaciones
• Optimizaciones de procesos

¿En qué te ayudo hoy?"""
        
        # =========================================
        # CATEGORÍA 6: DESPEDIDAS
        # =========================================
        if any(palabra in mensaje_lower for palabra in ['gracias', 'thank', 'adiós', 'chao', 'bye']):
            return "¡De nada! 😊 Estoy aquí cuando me necesites. Que tengas un excelente día."
        
        # =========================================
        # CATEGORÍA 7: RESPUESTA POR DEFECTO
        # =========================================
        return f"🤔 Entendido, estoy procesando tu solicitud: **\"{mensaje}\"**\n\nPor ahora estoy en versión beta. Pronto podré ayudarte con consultas más complejas. ¿Puedes reformular tu pregunta o intentar preguntar sobre usuarios, empresas o pagos?"
        
    except Exception as e:
        logger.error(f"❌ Error al procesar mensaje del asistente: {e}")
        return "⚠️ Lo siento, hubo un error al procesar tu mensaje. Por favor intenta nuevamente."


# ==================== ENDPOINT: POST /api/asistente/chat ====================
@asistente_bp.route('/chat', methods=['POST'])
@require_auth
def chat():
    """
    Endpoint principal del chat con el asistente.
    
    Request Body:
        {
            "message": "¿Cuántos usuarios tenemos?"
        }
    
    Response:
        {
            "response": "Actualmente hay 42 usuarios en el sistema.",
            "timestamp": "2025-11-27T10:30:00"
        }
    """
    try:
        # Validar request
        if not request.is_json:
            return jsonify({
                'error': 'Formato inválido',
                'message': 'El request debe ser JSON'
            }), 400
        
        data = request.get_json()
        mensaje = data.get('message', '').strip()
        
        # Validar mensaje
        if not mensaje:
            return jsonify({
                'error': 'Mensaje vacío',
                'message': 'Debes enviar un mensaje'
            }), 400
        
        # Obtener user_id de la sesión
        user_id = session.get('user_id')
        user_name = session.get('user_name', 'Usuario')
        
        # Log de la consulta
        logger.info(f"🧠 Asistente - Usuario: {user_name} (ID: {user_id}) - Mensaje: {mensaje}")

        # Procesar mensaje y generar respuesta
        # PRIORIDAD 1: Intentar usar Gemini AI
        if GEMINI_AVAILABLE:
            try:
                respuesta = procesar_con_gemini(mensaje, user_id)
                logger.info(f"✅ Gemini AI - Respuesta enviada a {user_name}")
            except Exception as gemini_error:
                logger.warning(f"⚠️ Gemini falló, usando fallback: {gemini_error}")
                respuesta = procesar_mensaje_inteligente(mensaje, user_id)
                logger.info(f"💬 Fallback - Respuesta enviada a {user_name}")
        else:
            # FALLBACK: Usar lógica de palabras clave
            respuesta = procesar_mensaje_inteligente(mensaje, user_id)
            logger.info(f"💬 Fallback - Respuesta enviada a {user_name}")
        
        # Retornar respuesta
        return jsonify({
            'response': respuesta,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error en endpoint /api/asistente/chat: {e}")
        return jsonify({
            'error': 'Error del servidor',
            'message': 'Hubo un problema al procesar tu mensaje. Intenta nuevamente.'
        }), 500


# ==================== ENDPOINT: GET /api/asistente/status ====================
@asistente_bp.route('/status', methods=['GET'])
@require_auth
def status():
    """
    Verifica el estado del asistente.
    
    Response:
        {
            "status": "online",
            "version": "1.0-beta",
            "features": ["keywords", "db_queries"],
            "timestamp": "2025-11-27T10:30:00"
        }
    """
    return jsonify({
        'status': 'online',
        'version': '2.0-gemini' if GEMINI_AVAILABLE else '1.0-fallback',
        'ai_engine': 'Google Gemini 2.5 Flash' if GEMINI_AVAILABLE else 'Keyword-based',
        'features': ['gemini_ai', 'db_queries', 'context_aware', 'fallback'] if GEMINI_AVAILABLE else ['keywords', 'db_queries'],
        'message': '🤖 Asistente Montero con Gemini AI activo' if GEMINI_AVAILABLE else '💬 Asistente Montero (modo fallback)',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


# ==================== FUNCIÓN: RECOLECTAR DATOS DEL SISTEMA ====================
def recolectar_datos_sistema() -> dict:
    """
    Recolecta datos clave del sistema para generar briefing proactivo.

    Returns:
        dict: Diccionario con estadísticas y alertas del sistema
    """
    try:
        from timedelta import timedelta
    except:
        from datetime import timedelta

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        datos = {
            'total_usuarios': 0,
            'total_empresas': 0,
            'tutelas_urgentes': [],
            'tutelas_count': 0,
            'usuarios_hoy': 0,
            'fecha_reporte': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'hora_del_dia': 'buenos días'
        }

        # Determinar saludo según hora
        hora_actual = datetime.now().hour
        if hora_actual < 12:
            datos['hora_del_dia'] = 'buenos días'
        elif hora_actual < 18:
            datos['hora_del_dia'] = 'buenas tardes'
        else:
            datos['hora_del_dia'] = 'buenas noches'

        # 1. Total de usuarios
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        datos['total_usuarios'] = cursor.fetchone()[0]

        # 2. Total de empresas
        try:
            cursor.execute("SELECT COUNT(*) FROM empresas")
            datos['total_empresas'] = cursor.fetchone()[0]
        except:
            datos['total_empresas'] = 0

        # 3. Usuarios creados hoy
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM usuarios
                WHERE DATE(fecha_creacion) = DATE('now')
            """)
            datos['usuarios_hoy'] = cursor.fetchone()[0]
        except:
            datos['usuarios_hoy'] = 0

        # 4. Tutelas próximas a vencer (5 días o menos) - CRÍTICO
        try:
            fecha_limite = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
            cursor.execute("""
                SELECT numero_tutela, fecha_fin, juzgado, usuario_id
                FROM tutelas
                WHERE fecha_fin <= ? AND estado = 'Radicada'
                ORDER BY fecha_fin ASC
                LIMIT 10
            """, (fecha_limite,))

            tutelas_raw = cursor.fetchall()
            datos['tutelas_count'] = len(tutelas_raw)

            for tutela in tutelas_raw:
                numero, fecha_fin, juzgado, usuario_id = tutela
                try:
                    dias_restantes = (datetime.strptime(fecha_fin, '%Y-%m-%d') - datetime.now()).days
                except:
                    dias_restantes = 0

                datos['tutelas_urgentes'].append({
                    'numero': numero,
                    'fecha_vencimiento': fecha_fin,
                    'juzgado': juzgado,
                    'dias_restantes': max(0, dias_restantes),
                    'usuario_id': usuario_id
                })
        except Exception as tutela_error:
            logger.warning(f"⚠️ No se pudieron obtener tutelas: {tutela_error}")
            datos['tutelas_count'] = 0

        # 5. Datos financieros opcionales (recaudos recientes)
        try:
            cursor.execute("""
                SELECT COUNT(*), SUM(monto)
                FROM pagos
                WHERE fecha >= date('now', '-7 days')
            """)
            pagos_data = cursor.fetchone()
            datos['pagos_recientes'] = {
                'cantidad': pagos_data[0] or 0,
                'monto_total': float(pagos_data[1] or 0)
            }
        except:
            datos['pagos_recientes'] = {'cantidad': 0, 'monto_total': 0.0}

        conn.close()
        logger.info(f"📊 Datos del sistema recolectados: {datos['total_usuarios']} usuarios, {datos['tutelas_count']} tutelas urgentes")
        return datos

    except Exception as e:
        logger.error(f"❌ Error al recolectar datos del sistema: {e}")
        return {
            'total_usuarios': 0,
            'total_empresas': 0,
            'tutelas_urgentes': [],
            'tutelas_count': 0,
            'usuarios_hoy': 0,
            'fecha_reporte': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'hora_del_dia': 'buenos días',
            'error': str(e)
        }


# ==================== FUNCIÓN: GENERAR BRIEFING CON IA ====================
def generar_briefing_ia(datos_sistema: dict, user_name: str) -> str:
    """
    Genera un briefing ejecutivo usando Gemini AI basado en datos del sistema.

    Args:
        datos_sistema: Diccionario con estadísticas del sistema
        user_name: Nombre del usuario

    Returns:
        str: Briefing generado por IA
    """
    try:
        if not GEMINI_AVAILABLE:
            return generar_briefing_fallback_completo(user_name, datos_sistema)

        # Inicializar modelo Gemini
        model = genai.GenerativeModel('gemini-flash-latest')

        # Construir contexto con datos reales
        tutelas_info = ""
        if datos_sistema['tutelas_count'] > 0:
            tutelas_info = f"\n- 🚨 ALERTA CRÍTICA: {datos_sistema['tutelas_count']} tutelas próximas a vencer (≤5 días):"
            for t in datos_sistema['tutelas_urgentes'][:3]:
                dias = t['dias_restantes']
                urgencia = "¡HOY!" if dias == 0 else f"{dias} día(s)"
                tutelas_info += f"\n  * Tutela #{t['numero']} - Vence en {urgencia} - {t['juzgado']}"

        pagos_info = ""
        if datos_sistema.get('pagos_recientes', {}).get('cantidad', 0) > 0:
            monto = datos_sistema['pagos_recientes']['monto_total']
            cantidad = datos_sistema['pagos_recientes']['cantidad']
            pagos_info = f"\n- Recaudos última semana: {cantidad} pagos (${monto:,.0f})"

        usuarios_hoy_info = ""
        if datos_sistema['usuarios_hoy'] > 0:
            usuarios_hoy_info = f"\n- Nuevos registros hoy: {datos_sistema['usuarios_hoy']} usuario(s)"

        # System Prompt para Briefing Ejecutivo
        prompt = f"""Actúa como el Jefe de Operaciones del Sistema de Gestión Montero.

DATOS ACTUALES DEL SISTEMA:
- Total de Usuarios Registrados: {datos_sistema['total_usuarios']}
- Total de Empresas Activas: {datos_sistema['total_empresas']}{usuarios_hoy_info}
- Tutelas Urgentes (próximas 5 días): {datos_sistema['tutelas_count']}{tutelas_info}{pagos_info}

FECHA Y HORA: {datos_sistema['fecha_reporte']}

MISIÓN:
Genera un "Informe Ejecutivo Diario" para {user_name} (CEO del sistema).

REQUISITOS ESTRICTOS:
1. Saludo breve y profesional según la hora ({datos_sistema['hora_del_dia']}).
2. Exactamente 3 PUNTOS CLAVE (bullet points):
   - Si hay tutelas urgentes, DEBE ser el primer punto (MÁXIMA PRIORIDAD).
   - Incluir estado operativo general (usuarios/empresas).
   - Si hay datos financieros o nuevos registros, incluirlos.
3. Usa emojis profesionales (máximo 4 en total).
4. Tono: Ejecutivo, conciso, accionable.
5. Máximo 150 palabras.
6. NO uses markdown (**), solo texto plano con emojis.

FORMATO:
[Saludo]

Puntos Clave del Día:
• [Punto 1 - Más urgente]
• [Punto 2 - Importante]
• [Punto 3 - Informativo]

[Cierre motivador en 1 línea]
"""

        # Generar respuesta con Gemini
        response = model.generate_content(prompt)
        briefing_texto = response.text.strip()

        logger.info(f"📋 Briefing generado con Gemini AI ({len(briefing_texto)} caracteres)")
        return briefing_texto

    except Exception as e:
        logger.error(f"❌ Error al generar briefing con IA: {e}")
        return generar_briefing_fallback_completo(user_name, datos_sistema)


# ==================== FUNCIÓN: GENERAR BRIEFING FALLBACK ====================
def generar_briefing_fallback_completo(user_name: str, datos_sistema: dict) -> str:
    """
    Genera un briefing completo sin IA (fallback).
    """
    hora_saludo = datos_sistema.get('hora_del_dia', 'buenos días')
    saludo_cap = hora_saludo.capitalize()

    briefing = f"{saludo_cap}, {user_name} 👋\n\nPuntos Clave del Día:\n"

    # Punto 1: Alertas críticas (tutelas)
    if datos_sistema['tutelas_count'] > 0:
        briefing += f"• 🚨 URGENTE: {datos_sistema['tutelas_count']} tutelas próximas a vencer en los próximos 5 días\n"
    else:
        briefing += f"• ✅ No hay tutelas urgentes en los próximos 5 días\n"

    # Punto 2: Estado operativo
    briefing += f"• 📊 Sistema operativo: {datos_sistema['total_usuarios']} usuarios y {datos_sistema['total_empresas']} empresas activas"
    if datos_sistema['usuarios_hoy'] > 0:
        briefing += f" (+{datos_sistema['usuarios_hoy']} nuevos hoy)"
    briefing += "\n"

    # Punto 3: Datos financieros o recomendación
    if datos_sistema.get('pagos_recientes', {}).get('cantidad', 0) > 0:
        monto = datos_sistema['pagos_recientes']['monto_total']
        cantidad = datos_sistema['pagos_recientes']['cantidad']
        briefing += f"• 💰 Recaudos última semana: {cantidad} pagos (${monto:,.0f})\n"
    else:
        briefing += f"• 💡 Recomendación: Revisar cartera vencida y hacer seguimiento\n"

    briefing += f"\n¡Excelente jornada! 🚀"

    return briefing


# ==================== ENDPOINT: GET /api/asistente/briefing ====================
@asistente_bp.route('/briefing', methods=['GET'])
@require_auth
def briefing():
    """
    Genera un briefing ejecutivo proactivo del estado del sistema.

    Recolecta datos clave (usuarios, tutelas urgentes, finanzas) y genera
    un informe ejecutivo usando IA.

    Response:
        {
            "briefing": "Texto del informe ejecutivo generado por IA",
            "alertas": [lista de IDs críticos de tutelas],
            "alertas_count": 3,
            "datos_raw": {
                "total_usuarios": 150,
                "total_empresas": 25,
                "tutelas_urgentes": 3,
                "pagos_recientes": {...}
            },
            "timestamp": "2025-11-27T10:30:00"
        }
    """
    try:
        user_name = session.get('user_name', 'Usuario')
        user_id = session.get('user_id')
        logger.info(f"📋 Briefing proactivo solicitado por: {user_name} (ID: {user_id})")

        # 1. Recolectar datos del sistema
        datos_sistema = recolectar_datos_sistema()

        # 2. Generar briefing con IA
        briefing_texto = generar_briefing_ia(datos_sistema, user_name)

        # 3. Extraer IDs de alertas críticas (tutelas urgentes)
        alertas_ids = [t['usuario_id'] for t in datos_sistema.get('tutelas_urgentes', [])]

        # 4. Retornar respuesta completa
        return jsonify({
            'briefing': briefing_texto,
            'alertas': alertas_ids,
            'alertas_count': len(alertas_ids),
            'datos_raw': {
                'total_usuarios': datos_sistema['total_usuarios'],
                'total_empresas': datos_sistema['total_empresas'],
                'tutelas_urgentes': datos_sistema['tutelas_count'],
                'usuarios_nuevos_hoy': datos_sistema['usuarios_hoy'],
                'pagos_recientes': datos_sistema.get('pagos_recientes', {})
            },
            'generated_at': datetime.utcnow().isoformat(),
            'ai_powered': GEMINI_AVAILABLE
        }), 200

    except Exception as e:
        logger.error(f"❌ Error en endpoint /api/asistente/briefing: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Error al generar briefing',
            'message': str(e),
            'briefing': f"¡{datos_sistema.get('hora_del_dia', 'Buenos días').capitalize()}! El sistema está operativo. 🚀"
        }), 500


# ==================== ENDPOINT: POST /api/asistente/feedback ====================
@asistente_bp.route('/feedback', methods=['POST'])
@require_auth
def feedback():
    """
    Recibe feedback del usuario sobre las respuestas del asistente.
    Útil para mejorar el modelo en el futuro.
    
    Request Body:
        {
            "message": "¿Cuántos usuarios hay?",
            "response": "Hay 42 usuarios",
            "rating": "positive" | "negative",
            "comment": "Muy útil" (opcional)
        }
    """
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        # Log del feedback
        logger.info(f"📊 Feedback del asistente - Usuario {user_id}: {data.get('rating')}")
        
        # TODO: Guardar en base de datos para análisis futuro
        
        return jsonify({
            'message': 'Gracias por tu feedback',
            'received': True
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error al procesar feedback: {e}")
        return jsonify({'error': 'Error al procesar feedback'}), 500


# ==================== LOGGING DE BLUEPRINT ====================
logger.info("🧠 Blueprint 'asistente' cargado correctamente")
