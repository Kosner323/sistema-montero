# -*- coding: utf-8 -*-
"""
unificacion.py - Módulo de Unificación de Formularios
====================================================
Maneja la lógica de vinculación laboral y otros formularios unificados.
"""
import os
import traceback
from datetime import datetime
from flask import Blueprint, jsonify, request, session, render_template
from logger import logger

# --- IMPORTACIÓN CENTRALIZADA ---
try:
    from ..utils import get_db_connection, login_required
except (ImportError, ValueError):
    from utils import get_db_connection, login_required
# -------------------------------

# ==============================================================================
# DEFINICIÓN DEL BLUEPRINT
# ==============================================================================

bp_unificacion = Blueprint("bp_unificacion", __name__, url_prefix="/api/unificacion")


# ==============================================================================
# ENDPOINTS
# ==============================================================================


@bp_unificacion.route("/formulario_vinculacion/<int:user_id>", methods=["GET"])
@login_required
def formulario_vinculacion(user_id):
    """
    Renderiza el formulario de vinculación laboral en una nueva pestaña.
    
    Args:
        user_id (int): ID del usuario a vincular/editar
        
    Returns:
        Template HTML con el formulario de vinculación
    """
    conn = None
    try:
        logger.info(f"📋 Cargando formulario de vinculación para usuario ID: {user_id}")
        
        # Obtener conexión a la base de datos
        conn = get_db_connection()
        if not conn:
            logger.error("❌ No se pudo establecer conexión con la base de datos")
            flash("Error de conexión con la base de datos", "error")
            return redirect(url_for("main.unificacion"))
        
        # =======================================================================
        # 1. BUSCAR USUARIO POR ID
        # =======================================================================
        query_user = """
            SELECT
                u.id,
                u.primerNombre,
                u.segundoNombre,
                u.primerApellido,
                u.segundoApellido,
                u.numeroId,
                u.correoElectronico,
                u.role,
                u.estado,
                u.empresa_nit,
                e.nombre_empresa,
                e.rep_legal_nombre
            FROM usuarios u
            LEFT JOIN empresas e ON u.empresa_nit = e.nit
            WHERE u.id = ?
        """
        
        usuario_row = conn.execute(query_user, (user_id,)).fetchone()
        
        if not usuario_row:
            logger.warning(f"❌ Usuario con ID {user_id} no encontrado")
            flash(f"Usuario con ID {user_id} no existe", "error")
            return redirect(url_for("main.unificacion"))
        
        usuario = dict(usuario_row)
        logger.info(f"✅ Usuario encontrado: {usuario.get('primerNombre')} {usuario.get('primerApellido')}")
        
        # =======================================================================
        # 2. OBTENER LISTA DE EMPRESAS
        # =======================================================================
        query_empresas = """
            SELECT
                nit,
                nombre_empresa,
                rep_legal_nombre,
                ciudad_empresa,
                departamento_empresa
            FROM empresas
            ORDER BY nombre_empresa ASC
        """
        
        empresas_raw = conn.execute(query_empresas).fetchall()
        empresas = [dict(row) for row in empresas_raw]
        
        logger.info(f"✅ {len(empresas)} empresas cargadas para el select")
        
        # =======================================================================
        # 3. RENDERIZAR TEMPLATE
        # =======================================================================
        return render_template(
            "unificacion/form_vinculacion.html",
            usuario=usuario,
            empresas=empresas
        )
        
    except sqlite3.Error as db_err:
        logger.error(f"❌ Error de base de datos: {db_err}", exc_info=True)
        flash("Error al cargar el formulario de vinculación", "error")
        return redirect(url_for("main.unificacion"))
        
    except Exception as e:
        logger.error(f"❌ Error general: {e}", exc_info=True)
        flash("Error interno del servidor", "error")
        return redirect(url_for("main.unificacion"))
        
    finally:
        if conn:
            conn.close()
            logger.debug("🔌 Conexión a BD cerrada")


@bp_unificacion.route("/master", methods=["GET"])
@login_required
def get_master_unification():
    """
    Obtiene la vista maestra unificada de Usuarios y Empresas.

    Returns:
        JSON con estructura:
        {
            "usuarios": [...],
            "empresas": [...],
            "stats": {
                "total_usuarios": int,
                "total_empresas": int,
                "usuarios_con_empresa": int,
                "usuarios_sin_empresa": int,
                "roles_distribution": {...}
            }
        }
    """
    conn = None
    try:
        logger.info("📊 Iniciando carga de datos de unificación master...")

        # Obtener conexión a la base de datos
        conn = get_db_connection()
        if not conn:
            logger.error("❌ No se pudo establecer conexión con la base de datos")
            raise Exception("No hay conexión a la base de datos.")

        logger.debug("✅ Conexión a BD establecida correctamente")

        # =======================================================================
        # 1. CONSULTA MAESTRA - TODOS LOS DATOS OPERATIVOS (FUERZA LABORAL)
        # =======================================================================
        # ✅ FILTRO CRÍTICO: Excluir admin, superadmin, administrador
        # ✅ INCLUYE: Entidades de Seguridad Social, Costos, IBC, Fechas
        query_users = """
            SELECT
                u.id,
                u.tipoId,
                u.numeroId,
                u.primerNombre,
                u.segundoNombre,
                u.primerApellido,
                u.segundoApellido,
                u.correoElectronico,
                u.role,
                u.estado,
                u.empresa_nit,
                u.fechaNacimiento,

                -- ENTIDADES DE SEGURIDAD SOCIAL
                u.epsNombre,
                u.arlNombre,
                u.claseRiesgoARL,
                u.afpNombre,
                u.ccfNombre,

                -- DATOS LABORALES
                u.fechaIngreso,
                u.ibc,
                u.administracion,

                -- VALORES / COSTOS
                u.epsCosto,
                u.arlCosto,
                u.afpCosto,
                u.ccfCosto,

                -- EMPRESA VINCULADA
                e.nombre_empresa,
                e.rep_legal_nombre,
                e.nit as empresa_nit_verificado
            FROM usuarios u
            LEFT JOIN empresas e ON u.empresa_nit = e.nit
            WHERE LOWER(u.role) NOT IN ('admin', 'superadmin', 'administrador', 'super')
            ORDER BY u.id DESC
        """

        logger.debug("🔍 Ejecutando consulta maestra de usuarios...")
        usuarios_raw = conn.execute(query_users).fetchall()
        usuarios = [dict(row) for row in usuarios_raw]

        logger.info(f"✅ Usuarios cargados: {len(usuarios)}")

        # =======================================================================
        # 2. CONSULTA DE EMPRESAS ACTIVAS
        # =======================================================================
        query_empresas = """
            SELECT
                nit,
                nombre_empresa,
                rep_legal_nombre,
                direccion_empresa,
                telefono_empresa,
                correo_empresa,
                ciudad_empresa,
                departamento_empresa
            FROM empresas
            WHERE 1=1
            ORDER BY nombre_empresa ASC
        """

        logger.debug("🔍 Ejecutando consulta de empresas...")
        empresas_raw = conn.execute(query_empresas).fetchall()
        empresas = [dict(row) for row in empresas_raw]

        logger.info(f"✅ Empresas cargadas: {len(empresas)}")

        # =======================================================================
        # 3. CALCULAR ESTADÍSTICAS AVANZADAS
        # =======================================================================
        logger.debug("📈 Calculando estadísticas del sistema...")

        # Contar usuarios con/sin empresa
        usuarios_con_empresa = sum(1 for u in usuarios if u.get('empresa_nit'))
        usuarios_sin_empresa = len(usuarios) - usuarios_con_empresa

        # Distribución de roles
        roles_distribution = {}
        for user in usuarios:
            role = user.get('role', 'Sin Rol')
            roles_distribution[role] = roles_distribution.get(role, 0) + 1

        # Estadísticas consolidadas
        stats = {
            "total_usuarios": len(usuarios),
            "total_empresas": len(empresas),
            "usuarios_con_empresa": usuarios_con_empresa,
            "usuarios_sin_empresa": usuarios_sin_empresa,
            "roles_distribution": roles_distribution,
            "porcentaje_asignacion": round((usuarios_con_empresa / len(usuarios) * 100), 2) if usuarios else 0
        }

        logger.info(f"📊 Estadísticas calculadas: {stats}")

        # =======================================================================
        # 4. AGREGAR CAMPOS CALCULADOS A USUARIOS
        # =======================================================================
        
        for usuario in usuarios:
            # Nombre completo
            nombre_completo_parts = [
                usuario.get('primerNombre', ''),
                usuario.get('segundoNombre', ''),
                usuario.get('primerApellido', ''),
                usuario.get('segundoApellido', '')
            ]
            usuario['nombre_completo'] = ' '.join(filter(None, nombre_completo_parts))

            # Calcular EDAD
            fecha_nacimiento = usuario.get('fechaNacimiento')
            if fecha_nacimiento:
                try:
                    # Intentar parsear la fecha en diferentes formatos
                    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d']:
                        try:
                            nacimiento = datetime.strptime(fecha_nacimiento, fmt)
                            break
                        except ValueError:
                            continue
                    else:
                        # Si ningún formato funcionó
                        usuario['edad'] = 'N/A'
                        continue
                    
                    hoy = datetime.now()
                    edad = hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))
                    usuario['edad'] = edad
                except Exception as e:
                    logger.warning(f"Error calculando edad para usuario {usuario.get('id')}: {e}")
                    usuario['edad'] = 'N/A'
            else:
                usuario['edad'] = 'N/A'

            # Estado de asignación de empresa
            usuario['tiene_empresa'] = bool(usuario.get('empresa_nit'))

            # Badge de rol (para frontend)
            usuario['role_badge'] = {
                'SUPER': {'color': 'danger', 'text': 'Administrador'},
                'ADMIN': {'color': 'warning', 'text': 'Admin'},
                'USER': {'color': 'primary', 'text': 'Usuario'},
                'EMPLEADO': {'color': 'info', 'text': 'Empleado'}
            }.get(usuario.get('role', 'USER'), {'color': 'secondary', 'text': 'Usuario'})

        logger.info("✅ Unificación master cargada exitosamente")

        # =======================================================================
        # 5. RESPUESTA JSON
        # =======================================================================
        return jsonify({
            "success": True,
            "usuarios": usuarios,
            "empresas": empresas,
            "stats": stats,
            "timestamp": conn.execute("SELECT datetime('now', 'localtime') as now").fetchone()['now']
        }), 200

    except sqlite3.Error as db_err:
        logger.error(f"❌ Error de base de datos en unificación/master: {db_err}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Error de base de datos al cargar datos unificados",
            "detalle": str(db_err)
        }), 500

    except Exception as e:
        logger.error(f"❌ Error general en unificación/master: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Error interno al cargar datos unificados",
            "detalle": str(e)
        }), 500

    finally:
        if conn:
            conn.close()
            logger.debug("🔌 Conexión a BD cerrada")


# ==============================================================================
# ENDPOINT: ACTUALIZAR VINCULACIÓN LABORAL
# ==============================================================================

@bp_unificacion.route("/update_vinculacion", methods=["PUT"])
@login_required
def update_vinculacion():
    """
    Actualiza la vinculación laboral de un empleado.
    
    Request Body (JSON):
        {
            "user_id": int,
            "primerNombre": str,
            "primerApellido": str,
            "numeroId": str,
            "correoElectronico": str,
            "role": str,
            "estado": str,
            "empresa_nit": str (puede ser "" para desvincular)
        }

    Returns:
        JSON con resultado de la operación
    """
    conn = None
    try:
        logger.info("📝 Iniciando actualización de vinculación laboral")

        # Validar que el request tenga JSON
        if not request.is_json:
            logger.warning("❌ Request sin Content-Type: application/json")
            return jsonify({
                "success": False,
                "error": "Se requiere Content-Type: application/json"
            }), 400

        # Obtener datos del request
        data = request.get_json()
        logger.debug(f"Datos recibidos: {data}")

        # Validar campos requeridos
        required_fields = ["user_id", "primerNombre", "primerApellido", "numeroId", "correoElectronico", "role"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            logger.warning(f"❌ Campos faltantes: {missing_fields}")
            return jsonify({
                "success": False,
                "error": f"Campos requeridos faltantes: {', '.join(missing_fields)}"
            }), 400

        # Extraer y validar datos
        user_id = data.get("user_id")
        primer_nombre = data.get("primerNombre", "").strip()
        primer_apellido = data.get("primerApellido", "").strip()
        numero_id = data.get("numeroId", "").strip()
        correo = data.get("correoElectronico", "").strip()
        role = data.get("role", "empleado").strip()
        estado = data.get("estado", "activo").strip().lower()
        empresa_nit = data.get("empresa_nit", "").strip()
        
        # ✅ Si empresa_nit está vacío, convertir a NULL para desvincular
        if not empresa_nit:
            empresa_nit = None
            logger.info(f"📤 Usuario {user_id} será DESVINCULADO (empresa_nit = NULL)")

        # Validación de email
        if "@" not in correo or "." not in correo:
            logger.warning(f"❌ Email inválido: {correo}")
            return jsonify({
                "success": False,
                "error": "El correo electrónico no tiene un formato válido"
            }), 400

        # Validar estado
        if estado not in ["activo", "inactivo"]:
            logger.warning(f"❌ Estado inválido: {estado}")
            return jsonify({
                "success": False,
                "error": "Estado inválido. Valores permitidos: activo, inactivo"
            }), 400

        # Obtener conexión a la base de datos
        conn = get_db_connection()
        if not conn:
            logger.error("❌ No se pudo establecer conexión con la base de datos")
            raise Exception("No hay conexión a la base de datos.")

        # Verificar que el usuario existe Y obtener datos anteriores
        usuario_anterior = conn.execute("""
            SELECT 
                id, 
                empresa_nit, 
                ibc, 
                fechaIngreso,
                primerNombre,
                primerApellido
            FROM usuarios 
            WHERE id = ?
        """, (user_id,)).fetchone()

        if not usuario_anterior:
            logger.warning(f"❌ Usuario ID {user_id} no encontrado")
            return jsonify({
                "success": False,
                "error": f"Usuario con ID {user_id} no existe"
            }), 404
        
        usuario_anterior = dict(usuario_anterior)
        empresa_anterior_nit = usuario_anterior.get('empresa_nit')

        # Si se asignó empresa, verificar que existe
        if empresa_nit:
            empresa_exists = conn.execute(
                "SELECT nit FROM empresas WHERE nit = ?",
                (empresa_nit,)
            ).fetchone()

            if not empresa_exists:
                logger.warning(f"❌ Empresa con NIT {empresa_nit} no encontrada")
                return jsonify({
                    "success": False,
                    "error": f"La empresa con NIT {empresa_nit} no existe"
                }), 404

        # Actualizar usuario en la base de datos
        logger.info(f"💾 Actualizando vinculación de usuario ID {user_id}...")

        conn.execute("""
            UPDATE usuarios
            SET
                primerNombre = ?,
                primerApellido = ?,
                numeroId = ?,
                correoElectronico = ?,
                role = ?,
                estado = ?,
                empresa_nit = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            primer_nombre,
            primer_apellido,
            numero_id,
            correo,
            role,
            estado,
            empresa_nit,  # ✅ NULL si está desvinculado
            user_id
        ))

        # ✅ GUARDAR EN HISTORIAL LABORAL SI CAMBIÓ LA EMPRESA
        if empresa_anterior_nit != empresa_nit:
            logger.info(f"📝 Guardando cambio en historial laboral...")
            
            # Determinar tipo de operación
            if empresa_anterior_nit is None and empresa_nit is not None:
                tipo_operacion = 'VINCULACION'
                motivo_auto = 'Vinculación inicial'
            elif empresa_anterior_nit is not None and empresa_nit is None:
                tipo_operacion = 'DESVINCULACION'
                motivo_auto = 'Desvinculación de empresa'
            else:
                tipo_operacion = 'CAMBIO'
                motivo_auto = 'Cambio de empresa'
            
            # Obtener ID y nombre del responsable (usuario autenticado)
            responsable_id = session.get('user_id')
            responsable_nombre = session.get('user_name', 'Sistema')
            
            conn.execute("""
                INSERT INTO historial_laboral (
                    usuario_id,
                    empresa_anterior_nit,
                    empresa_nueva_nit,
                    motivo,
                    responsable_id,
                    responsable_nombre,
                    tipo_operacion,
                    ibc_anterior,
                    fecha_ingreso_anterior,
                    observaciones
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                empresa_anterior_nit,
                empresa_nit,
                data.get('motivo', motivo_auto),
                responsable_id,
                responsable_nombre,
                tipo_operacion,
                usuario_anterior.get('ibc'),
                usuario_anterior.get('fechaIngreso'),
                f"Actualización individual desde módulo de unificación"
            ))
            
            logger.info(f"✅ Historial registrado: {tipo_operacion}")

        conn.commit()
        
        accion = "VINCULADO" if empresa_nit else "DESVINCULADO"
        logger.info(f"✅ Usuario ID {user_id} {accion} exitosamente")

        # Obtener datos actualizados del usuario
        updated_user = conn.execute("""
            SELECT 
                u.id,
                u.primerNombre,
                u.segundoNombre,
                u.primerApellido,
                u.segundoApellido,
                u.numeroId,
                u.correoElectronico,
                u.role,
                u.estado,
                u.empresa_nit,
                e.nombre_empresa
            FROM usuarios u
            LEFT JOIN empresas e ON u.empresa_nit = e.nit
            WHERE u.id = ?
        """, (user_id,)).fetchone()

        return jsonify({
            "success": True,
            "message": f"Vinculación actualizada exitosamente ({accion})",
            "usuario": dict(updated_user) if updated_user else None
        }), 200

    except sqlite3.IntegrityError as ie:
        logger.error(f"❌ Error de integridad en BD: {ie}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Error de integridad de datos",
            "detalle": str(ie)
        }), 400

    except sqlite3.Error as db_err:
        logger.error(f"❌ Error de base de datos: {db_err}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Error de base de datos al actualizar vinculación",
            "detalle": str(db_err)
        }), 500

    except Exception as e:
        logger.error(f"❌ Error general al actualizar vinculación: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Error interno al actualizar vinculación",
            "detalle": str(e)
        }), 500

    finally:
        if conn:
            conn.close()
            logger.debug("🔌 Conexión a BD cerrada")


# ==============================================================================
# ENDPOINT: ACTUALIZAR USUARIO (LEGACY - Mantener por compatibilidad)
# ==============================================================================

@bp_unificacion.route("/update_user/<int:user_id>", methods=["PUT"])
@login_required
def update_user(user_id):
    """
    Actualiza los datos de un usuario específico.

    Args:
        user_id (int): ID del usuario a actualizar

    Request Body (JSON):
        {
            "primerNombre": str,
            "primerApellido": str,
            "numeroId": str (documento),
            "correoElectronico": str,
            "role": str,
            "empresa_nit": str (opcional),
            "estado": str (opcional - "activo"/"inactivo")
        }

    Returns:
        JSON con resultado de la operación
    """
    conn = None
    try:
        logger.info(f"📝 Iniciando actualización de usuario ID: {user_id}")

        # Validar que el request tenga JSON
        if not request.is_json:
            logger.warning("❌ Request sin Content-Type: application/json")
            return jsonify({
                "success": False,
                "error": "Se requiere Content-Type: application/json"
            }), 400

        # Obtener datos del request
        data = request.get_json()
        logger.debug(f"Datos recibidos: {data}")

        # Validar campos requeridos
        required_fields = ["primerNombre", "primerApellido", "numeroId", "correoElectronico", "role"]
        missing_fields = [field for field in required_fields if not data.get(field)]

        if missing_fields:
            logger.warning(f"❌ Campos faltantes: {missing_fields}")
            return jsonify({
                "success": False,
                "error": f"Campos requeridos faltantes: {', '.join(missing_fields)}"
            }), 400

        # Extraer y validar datos
        primer_nombre = data.get("primerNombre", "").strip()
        primer_apellido = data.get("primerApellido", "").strip()
        numero_id = data.get("numeroId", "").strip()
        correo = data.get("correoElectronico", "").strip()
        role = data.get("role", "USER").strip()
        empresa_nit = data.get("empresa_nit", "").strip() or None
        estado = data.get("estado", "activo").strip().lower()  # Por defecto "activo"

        # Validación adicional de email
        if "@" not in correo or "." not in correo:
            logger.warning(f"❌ Email inválido: {correo}")
            return jsonify({
                "success": False,
                "error": "El correo electrónico no tiene un formato válido"
            }), 400

        # Validar rol (SOLO FUERZA LABORAL - No admin/superadmin)
        valid_roles = ["USER", "EMPLEADO", "AFILIADO", "OPERATIVO"]
        if role not in valid_roles:
            logger.warning(f"❌ Rol inválido: {role}")
            return jsonify({
                "success": False,
                "error": f"Rol inválido. Valores permitidos: {', '.join(valid_roles)}"
            }), 400

        # Validar estado
        valid_estados = ["activo", "inactivo"]
        if estado not in valid_estados:
            logger.warning(f"❌ Estado inválido: {estado}")
            return jsonify({
                "success": False,
                "error": f"Estado inválido. Valores permitidos: {', '.join(valid_estados)}"
            }), 400

        # Obtener conexión a la base de datos
        conn = get_db_connection()
        if not conn:
            logger.error("❌ No se pudo establecer conexión con la base de datos")
            raise Exception("No hay conexión a la base de datos.")

        # Verificar que el usuario existe
        user_exists = conn.execute(
            "SELECT id FROM usuarios WHERE id = ?",
            (user_id,)
        ).fetchone()

        if not user_exists:
            logger.warning(f"❌ Usuario ID {user_id} no encontrado")
            return jsonify({
                "success": False,
                "error": f"Usuario con ID {user_id} no existe"
            }), 404

        # Si se asignó empresa, verificar que existe
        if empresa_nit:
            empresa_exists = conn.execute(
                "SELECT nit FROM empresas WHERE nit = ?",
                (empresa_nit,)
            ).fetchone()

            if not empresa_exists:
                logger.warning(f"❌ Empresa con NIT {empresa_nit} no encontrada")
                return jsonify({
                    "success": False,
                    "error": f"La empresa con NIT {empresa_nit} no existe"
                }), 404

        # Actualizar usuario en la base de datos
        logger.info(f"💾 Actualizando usuario ID {user_id}...")

        # Actualizar todos los campos incluyendo documento (numeroId) y estado
        conn.execute("""
            UPDATE usuarios
            SET
                primerNombre = ?,
                primerApellido = ?,
                numeroId = ?,
                correoElectronico = ?,
                role = ?,
                empresa_nit = ?
            WHERE id = ?
        """, (
            primer_nombre,
            primer_apellido,
            numero_id,
            correo,
            role,
            empresa_nit,
            user_id
        ))

        # Intentar actualizar el campo "estado" si existe en la tabla
        try:
            conn.execute("""
                UPDATE usuarios
                SET estado = ?
                WHERE id = ?
            """, (estado, user_id))
            logger.debug(f"✅ Estado actualizado a: {estado}")
        except sqlite3.OperationalError:
            # La columna "estado" no existe en la tabla, continuar sin error
            logger.debug("⚠️ Campo 'estado' no existe en la tabla usuarios, se omite")

        conn.commit()
        logger.info(f"✅ Usuario ID {user_id} actualizado exitosamente")

        # Obtener datos actualizados del usuario
        updated_user = conn.execute("""
            SELECT 
                u.id,
                u.primerNombre,
                u.primerApellido,
                u.correoElectronico,
                u.role,
                u.empresa_nit,
                e.nombre_empresa
            FROM usuarios u
            LEFT JOIN empresas e ON u.empresa_nit = e.nit
            WHERE u.id = ?
        """, (user_id,)).fetchone()

        return jsonify({
            "success": True,
            "message": "Usuario actualizado exitosamente",
            "usuario": dict(updated_user) if updated_user else None
        }), 200

    except sqlite3.IntegrityError as ie:
        logger.error(f"❌ Error de integridad en BD: {ie}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Error de integridad de datos",
            "detalle": str(ie)
        }), 400

    except sqlite3.Error as db_err:
        logger.error(f"❌ Error de base de datos: {db_err}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Error de base de datos al actualizar usuario",
            "detalle": str(db_err)
        }), 500

    except Exception as e:
        logger.error(f"❌ Error general al actualizar usuario: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Error interno al actualizar usuario",
            "detalle": str(e)
        }), 500

    finally:
        if conn:
            conn.close()
            logger.debug("🔌 Conexión a BD cerrada")


# ==============================================================================
# NUEVA RUTA: GET MASTER COMPLETO (CON TODOS LOS CAMPOS)
# ==============================================================================

@bp_unificacion.route("/master_completo", methods=["GET"])
@login_required
def get_master_completo():
    """
    Obtiene TODOS los campos de usuarios y empresas para vinculación masiva.
    Incluye: EPS, ARL, AFP, CCF, costos, IBC, fechas, etc.
    
    Returns:
        JSON con estructura completa de usuarios y empresas
    """
    conn = None
    try:
        logger.info(" Cargando datos completos para vinculación masiva...")

        conn = get_db_connection()
        if not conn:
            raise Exception("No hay conexión a la base de datos")

        # Query completa con TODOS los campos
        query_usuarios = """
            SELECT
                u.id,
                u.tipoId,
                u.numeroId,
                u.primerNombre,
                u.segundoNombre,
                u.primerApellido,
                u.segundoApellido,
                u.correoElectronico,
                u.role,
                u.estado,
                u.empresa_nit,
                u.fechaNacimiento,
                
                -- SEGURIDAD SOCIAL
                u.epsNombre as eps_nombre,
                u.arlNombre as arl_nombre,
                u.claseRiesgoARL as riesgo_nivel,
                u.afpNombre as pension_nombre,
                u.ccfNombre as caja_nombre,
                
                -- DATOS LABORALES
                u.fechaIngreso as fecha_ingreso,
                strftime('%Y-%m', u.fechaIngreso) as mes_ingreso,
                u.ibc,
                u.administracion,
                
                -- COSTOS / APORTES
                u.epsCosto as aporte_eps,
                u.arlCosto as aporte_arl,
                u.afpCosto as aporte_pension,
                u.ccfCosto as aporte_caja,
                
                -- EMPRESA
                e.nombre_empresa,
                e.nit as empresa_nit_verificado
            FROM usuarios u
            LEFT JOIN empresas e ON u.empresa_nit = e.nit
            WHERE LOWER(u.role) NOT IN ('admin', 'superadmin', 'administrador', 'super')
            ORDER BY u.primerNombre, u.primerApellido
        """

        usuarios_raw = conn.execute(query_usuarios).fetchall()
        usuarios = [dict(row) for row in usuarios_raw]

        # Calcular EDAD para cada usuario
        
        for usuario in usuarios:
            fecha_nacimiento = usuario.get('fechaNacimiento')
            if fecha_nacimiento:
                try:
                    # Intentar parsear la fecha en diferentes formatos
                    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d']:
                        try:
                            nacimiento = datetime.strptime(fecha_nacimiento, fmt)
                            break
                        except ValueError:
                            continue
                    else:
                        # Si ningún formato funcionó
                        usuario['edad'] = 'N/A'
                        continue
                    
                    hoy = datetime.now()
                    edad = hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))
                    usuario['edad'] = edad
                except Exception as e:
                    logger.warning(f"Error calculando edad para usuario {usuario.get('id')}: {e}")
                    usuario['edad'] = 'N/A'
            else:
                usuario['edad'] = 'N/A'

        # Query empresas
        query_empresas = """
            SELECT
                nit,
                nombre_empresa,
                rep_legal_nombre,
                direccion_empresa,
                telefono_empresa,
                correo_empresa,
                ciudad_empresa,
                departamento_empresa
            FROM empresas
            ORDER BY nombre_empresa ASC
        """

        empresas_raw = conn.execute(query_empresas).fetchall()
        empresas = [dict(row) for row in empresas_raw]

        logger.info(f" Master completo: {len(usuarios)} usuarios, {len(empresas)} empresas")

        return jsonify({
            "success": True,
            "usuarios": usuarios,
            "empresas": empresas,
            "timestamp": None
        }), 200

    except Exception as e:
        logger.error(f" Error al cargar master completo: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

    finally:
        if conn:
            conn.close()


# ==============================================================================
# NUEVA RUTA: POST VINCULACIÓN MASIVA
# ==============================================================================

@bp_unificacion.route("/vincular_masivo", methods=["POST"])
@login_required
def vincular_masivo():
    """
    Vincula múltiples usuarios a una empresa de forma masiva.
    
    Payload JSON esperado:
    {
        "empresa_nit": "900123456-1",
        "usuarios_ids": [1, 2, 5, 10, 15]
    }
    
    Returns:
        JSON con resultado de la operación
    """
    conn = None
    try:
        logger.info(" Iniciando vinculación masiva de usuarios...")

        # Validar request
        if not request.is_json:
            raise ValueError("El request debe ser JSON")

        data = request.get_json()
        empresa_nit = data.get('empresa_nit')
        usuarios_ids = data.get('usuarios_ids', [])

        # Validaciones
        if not empresa_nit:
            raise ValueError("El NIT de la empresa es obligatorio")

        if not usuarios_ids or not isinstance(usuarios_ids, list):
            raise ValueError("Debe proporcionar una lista de IDs de usuarios")

        if len(usuarios_ids) == 0:
            raise ValueError("La lista de usuarios no puede estar vacía")

        logger.info(f" Vinculando {len(usuarios_ids)} usuarios a empresa NIT: {empresa_nit}")

        # Obtener conexión
        conn = get_db_connection()
        if not conn:
            raise Exception("No hay conexión a la base de datos")

        # Verificar que la empresa existe
        empresa = conn.execute("""
            SELECT nit, nombre_empresa 
            FROM empresas 
            WHERE nit = ?
        """, (empresa_nit,)).fetchone()

        if not empresa:
            raise ValueError(f"No existe una empresa con NIT: {empresa_nit}")

        logger.info(f" Empresa encontrada: {empresa['nombre_empresa']}")

        # ==================================================================
        # TRANSACCIÓN: Actualizar todos los usuarios Y guardar historial
        # ==================================================================
        try:
            # Obtener datos anteriores de los usuarios para el historial
            placeholders_ids = ','.join('?' * len(usuarios_ids))
            
            query_usuarios_anteriores = f"""
                SELECT id, empresa_nit, ibc, fechaIngreso, primerNombre, primerApellido
                FROM usuarios
                WHERE id IN ({placeholders_ids})
            """
            
            usuarios_anteriores = conn.execute(query_usuarios_anteriores, usuarios_ids).fetchall()
            usuarios_anteriores_dict = {row['id']: dict(row) for row in usuarios_anteriores}
            
            logger.info(f"📋 Datos anteriores capturados para {len(usuarios_anteriores_dict)} usuarios")
            
            # Preparar placeholders para la consulta IN
            query_update = f"""
                UPDATE usuarios 
                SET empresa_nit = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id IN ({placeholders_ids})
                AND LOWER(role) NOT IN ('admin', 'superadmin', 'administrador', 'super')
            """

            # Parámetros: empresa_nit + lista de IDs
            params = [empresa_nit] + usuarios_ids

            cursor = conn.execute(query_update, params)
            usuarios_actualizados = cursor.rowcount

            # ✅ GUARDAR HISTORIAL PARA CADA USUARIO
            responsable_id = session.get('user_id')
            responsable_nombre = session.get('user_name', 'Sistema')
            
            registros_historial = 0
            for usuario_id in usuarios_ids:
                usuario_ant = usuarios_anteriores_dict.get(usuario_id, {})
                empresa_anterior_nit = usuario_ant.get('empresa_nit')
                
                # Solo guardar si hay cambio real
                if empresa_anterior_nit != empresa_nit:
                    # Determinar tipo de operación
                    if empresa_anterior_nit is None:
                        tipo_operacion = 'VINCULACION'
                        motivo_auto = 'Vinculación masiva'
                    else:
                        tipo_operacion = 'CAMBIO'
                        motivo_auto = 'Cambio masivo de empresa'
                    
                    conn.execute("""
                        INSERT INTO historial_laboral (
                            usuario_id,
                            empresa_anterior_nit,
                            empresa_nueva_nit,
                            motivo,
                            responsable_id,
                            responsable_nombre,
                            tipo_operacion,
                            ibc_anterior,
                            fecha_ingreso_anterior,
                            observaciones
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        usuario_id,
                        empresa_anterior_nit,
                        empresa_nit,
                        motivo_auto,
                        responsable_id,
                        responsable_nombre,
                        tipo_operacion,
                        usuario_ant.get('ibc'),
                        usuario_ant.get('fechaIngreso'),
                        f"Vinculación masiva desde panel de unificación - {len(usuarios_ids)} usuarios procesados"
                    ))
                    registros_historial += 1

            # Commit de la transacción
            conn.commit()

            logger.info(f"✅ Vinculación exitosa: {usuarios_actualizados} usuarios actualizados")
            logger.info(f"✅ Historial registrado: {registros_historial} cambios guardados")

            # Obtener nombres de usuarios actualizados para el log
            query_nombres = f"""
                SELECT id, primerNombre, primerApellido, numeroId
                FROM usuarios
                WHERE id IN ({placeholders_ids})
            """
            
            usuarios_afectados = conn.execute(query_nombres, usuarios_ids).fetchall()
            usuarios_afectados_list = [dict(row) for row in usuarios_afectados]

            logger.debug(f"📋 Usuarios vinculados: {usuarios_afectados_list}")

            return jsonify({
                "success": True,
                "message": f"Vinculación masiva completada exitosamente",
                "empresa_nit": empresa_nit,
                "empresa_nombre": empresa['nombre_empresa'],
                "usuarios_actualizados": usuarios_actualizados,
                "usuarios_procesados": len(usuarios_ids),
                "registros_historial": registros_historial,
                "usuarios_detalle": usuarios_afectados_list
            }), 200

        except sqlite3.Error as db_err:
            # Rollback en caso de error
            conn.rollback()
            logger.error(f"❌ Error en transacción SQL: {db_err}", exc_info=True)
            raise Exception(f"Error al actualizar usuarios: {str(db_err)}")

    except ValueError as ve:
        logger.warning(f" Error de validación: {ve}")
        return jsonify({
            "success": False,
            "error": str(ve)
        }), 400

    except Exception as e:
        logger.error(f" Error en vinculación masiva: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"Error interno: {str(e)}"
        }), 500

    finally:
        if conn:
            conn.close()
            logger.debug(" Conexión a BD cerrada")


# ==============================================================================
# RUTA: HISTORIAL DE USUARIO
# ==============================================================================

@bp_unificacion.route("/historial_usuario/<int:user_id>", methods=["GET"])
@login_required
def historial_usuario(user_id):
    """
    Muestra el historial de cambios y vinculaciones de un usuario.
    
    Args:
        user_id (int): ID del usuario
        
    Returns:
        Template HTML con el historial del usuario
    """
    conn = None
    try:
        logger.info(f" Cargando historial para usuario ID: {user_id}")
        
        conn = get_db_connection()
        if not conn:
            logger.error(" No se pudo establecer conexión con la base de datos")
            flash("Error de conexión con la base de datos", "error")
            return redirect('/dashboard')
        
        # Obtener datos del usuario
        query_usuario = """
            SELECT
                u.id,
                u.tipoId,
                u.numeroId,
                u.primerNombre,
                u.segundoNombre,
                u.primerApellido,
                u.segundoApellido,
                u.correoElectronico,
                u.role,
                u.estado,
                u.empresa_nit,
                u.fechaIngreso,
                u.ibc,
                e.nombre_empresa,
                e.rep_legal_nombre
            FROM usuarios u
            LEFT JOIN empresas e ON u.empresa_nit = e.nit
            WHERE u.id = ?
        """
        
        usuario = conn.execute(query_usuario, (user_id,)).fetchone()

        if not usuario:
            logger.warning(f"⚠️ Usuario ID {user_id} no encontrado")
            flash(f"Usuario con ID {user_id} no encontrado", "warning")
            return redirect('/dashboard')
        
        usuario_dict = dict(usuario)
        
        # ✅ CONSULTAR HISTORIAL REAL DESDE LA BASE DE DATOS
        query_historial = """
            SELECT 
                h.id,
                h.fecha_cambio,
                h.tipo_operacion,
                h.motivo,
                h.empresa_anterior_nit,
                ea.nombre_empresa AS empresa_anterior_nombre,
                h.empresa_nueva_nit,
                en.nombre_empresa AS empresa_nueva_nombre,
                h.responsable_nombre,
                h.ibc_anterior,
                h.ibc_nuevo,
                h.fecha_ingreso_anterior,
                h.fecha_ingreso_nueva,
                h.observaciones
            FROM historial_laboral h
            LEFT JOIN empresas ea ON h.empresa_anterior_nit = ea.nit
            LEFT JOIN empresas en ON h.empresa_nueva_nit = en.nit
            WHERE h.usuario_id = ?
            ORDER BY h.fecha_cambio DESC
        """
        
        historial_raw = conn.execute(query_historial, (user_id,)).fetchall()
        historial = []
        
        for registro in historial_raw:
            historial.append({
                "fecha": registro['fecha_cambio'],
                "accion": registro['tipo_operacion'],
                "empresa_anterior": registro['empresa_anterior_nombre'],
                "empresa_nueva": registro['empresa_nueva_nombre'],
                "usuario_responsable": registro['responsable_nombre'] or 'Sistema',
                "observaciones": registro['motivo'] or registro['observaciones']
            })
        
        logger.info(f"✅ Historial cargado para usuario: {usuario_dict.get('primerNombre')} {usuario_dict.get('primerApellido')} - {len(historial)} registros")
        
        return render_template(
            "unificacion/historial_usuario.html",
            usuario=usuario_dict,
            historial=historial
        )
        
    except Exception as e:
        logger.error(f"❌ Error al cargar historial: {e}", exc_info=True)
        flash(f"Error al cargar el historial: {str(e)}", "error")
        return redirect('/dashboard')
        
    finally:
        if conn:
            conn.close()


# ==============================================================================
# RUTA: EDITAR EMPRESA (REDIRECCIÓN)
# ==============================================================================

@bp_unificacion.route("/editar_empresa/<empresa_nit>", methods=["GET"])
@login_required
def editar_empresa_redirect(empresa_nit):
    """
    Redirige a la ruta de edición de empresas.
    Esta es una ruta de conveniencia desde el módulo de unificación.
    
    Args:
        empresa_nit (str): NIT de la empresa
        
    Returns:
        Redirección a la ruta de edición de empresas
    """
    logger.info(f" Redirigiendo a edición de empresa NIT: {empresa_nit}")
    
    # Redirigir a la ruta de empresas (asumiendo que existe)
    # Ajusta la ruta según tu estructura
    return redirect(url_for("bp_empresas.editar_empresa", empresa_nit=empresa_nit))
