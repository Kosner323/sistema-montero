# -*- coding: utf-8 -*-
"""
cotizaciones.py - REFACTORIZADO CON ORM
====================================================
Maneja la lógica para registrar y consultar cotizaciones usando SQLAlchemy ORM.
Elimina SQL manual y usa modelos ORM al 100%.
"""
import os
import traceback
from datetime import datetime

from flask import Blueprint, jsonify, request, session, current_app, render_template
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from logger import logger
from extensions import db
from models.orm_models import Cotizacion, Empresa
from logic.pila_engine import CalculadoraPILA

# --- IMPORTACIÓN CENTRALIZADA ---
try:
    from ..utils import login_required
except (ImportError, ValueError):
    from utils import login_required
# -------------------------------

# ==================== DEFINICIÓN DEL BLUEPRINT ====================
bp_cotizaciones = Blueprint("bp_cotizaciones", __name__, url_prefix="/api/cotizaciones")

# ==================== ENDPOINTS DE COTIZACIONES ====================


@bp_cotizaciones.route("", methods=["GET"])
@login_required
def get_cotizaciones():
    """
    Obtiene todos los registros de cotizaciones usando ORM.

    Returns:
        JSON con lista de cotizaciones ordenadas por fecha
    """
    try:
        # ✅ Usando ORM en lugar de SQL manual
        cotizaciones = Cotizacion.query.order_by(Cotizacion.fecha_creacion.desc()).all()

        logger.debug(f"Se consultaron {len(cotizaciones)} registros de cotizaciones usando ORM")

        # Convertir objetos ORM a diccionarios
        return jsonify([cotizacion.to_dict() for cotizacion in cotizaciones])

    except SQLAlchemyError as e:
        logger.error(f"Error de SQLAlchemy obteniendo cotizaciones: {e}", exc_info=True)
        return jsonify({"error": "No se pudo obtener la lista de cotizaciones."}), 500
    except Exception as e:
        logger.error(f"Error inesperado obteniendo cotizaciones: {e}", exc_info=True)
        return jsonify({"error": "Error interno del servidor."}), 500


@bp_cotizaciones.route("", methods=["POST"])
@login_required
def add_cotizacion():
    """
    Añade un nuevo registro de cotización usando ORM.

    Request JSON:
        - cliente: Nombre del cliente (requerido)
        - email: Email del cliente (opcional)
        - servicio: Descripción del servicio (requerido)
        - monto: Monto de la cotización (requerido)
        - notas: Notas adicionales (opcional)
        - estado: Estado de la cotización (opcional, default: 'Enviada')

    Returns:
        JSON con la cotización creada
    """
    try:
        data = request.get_json()

        # Validación básica
        required_fields = ["cliente", "monto", "servicio"]
        if not all(field in data for field in required_fields):
            logger.warning("Intento de agregar cotización con campos faltantes")
            return (
                jsonify({"error": "Faltan campos obligatorios (cliente, monto, servicio)."}),
                400,
            )

        # Validar monto
        try:
            monto = float(data["monto"])
            if monto <= 0:
                logger.warning(f"Intento de agregar cotización con monto inválido: {monto}")
                return jsonify({"error": "El monto debe ser un valor positivo."}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "El monto debe ser un número válido."}), 400

        # Generar ID único de cotización
        fecha_actual = datetime.now()
        fecha_str = fecha_actual.strftime("%Y-%m-%d")
        id_cotizacion = f"COT-{fecha_actual.strftime('%Y%m%d%H%M%S')}"

        # ✅ Crear nueva cotización usando ORM
        nueva_cotizacion = Cotizacion(
            id_cotizacion=id_cotizacion,
            cliente=data["cliente"],
            email=data.get("email"),
            servicio=data["servicio"],
            monto=monto,
            notas=data.get("notas"),
            fecha_creacion=fecha_str,
            estado=data.get("estado", "Enviada")
        )

        # ✅ Guardar en la base de datos
        db.session.add(nueva_cotizacion)
        db.session.commit()

        logger.info(f"Nueva cotización registrada con ID: {nueva_cotizacion.id} - {id_cotizacion} para cliente {data['cliente']}")

        # Devolver el registro completo
        return jsonify(nueva_cotizacion.to_dict()), 201

    except IntegrityError as ie:
        db.session.rollback()
        logger.error(f"Error de integridad al agregar cotización: {ie}", exc_info=True)
        return (
            jsonify({"error": "Error de integridad, el ID de cotización ya existe o hay datos duplicados."}),
            409,
        )
    except SQLAlchemyError as se:
        db.session.rollback()
        logger.error(f"Error de SQLAlchemy al agregar cotización: {se}", exc_info=True)
        return jsonify({"error": "Error de base de datos al crear cotización."}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error general al agregar cotización: {e}", exc_info=True)
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500


@bp_cotizaciones.route("/simular-pila", methods=["POST"])
@login_required
def simular_pila():
    """
    Simula el cálculo de Seguridad Social (PILA) usando el Motor v1.1.
    
    NO guarda nada en la base de datos. Es una calculadora en tiempo real.
    
    Request JSON:
        - salario_base: float - Salario mensual en COP (requerido)
        - nivel_riesgo: int - Nivel de riesgo ARL 1-5 (requerido)
        - es_salario_integral: bool - Si es salario integral (opcional, default: false)
        - es_empresa_exonerada: bool - Si aplica exoneración de Salud (opcional, default: true)
    
    Returns:
        JSON con desglose completo de PILA:
        - datos_entrada: {salario_base, ibc, nivel_riesgo, flags}
        - salud: {empleado, empleador, total, exonerado}
        - pension: {empleado, empleador, total}
        - arl: {empleador, tasa}
        - parafiscales: {ccf, sena, icbf, total, aplica_sena_icbf}
        - totales: {empleado, empleador, general}
        - metadata: {fecha_calculo, advertencias, salario_neto}
    
    Status Codes:
        200: Cálculo exitoso
        400: Parámetros inválidos
        500: Error interno del servidor
    
    Ejemplo Request:
        {
            "salario_base": 1300000,
            "nivel_riesgo": 1,
            "es_salario_integral": false,
            "es_empresa_exonerada": true
        }
    """
    try:
        data = request.get_json()
        
        # ==================== VALIDACIÓN DE ENTRADA ====================
        
        # Validar campos requeridos
        if not data:
            logger.warning("Petición simular-pila sin JSON")
            return jsonify({"error": "Se requiere un JSON en el cuerpo de la petición."}), 400
        
        required_fields = ["salario_base", "nivel_riesgo"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            logger.warning(f"Petición simular-pila con campos faltantes: {missing_fields}")
            return jsonify({
                "error": f"Faltan campos obligatorios: {', '.join(missing_fields)}",
                "campos_requeridos": required_fields
            }), 400
        
        # Validar y extraer parámetros
        try:
            salario_base = float(data["salario_base"])
        except (ValueError, TypeError) as e:
            logger.warning(f"salario_base inválido: {data.get('salario_base')} - {e}")
            return jsonify({
                "error": "El campo 'salario_base' debe ser un número válido.",
                "ejemplo": 1300000
            }), 400
        
        try:
            nivel_riesgo = int(data["nivel_riesgo"])
        except (ValueError, TypeError) as e:
            logger.warning(f"nivel_riesgo inválido: {data.get('nivel_riesgo')} - {e}")
            return jsonify({
                "error": "El campo 'nivel_riesgo' debe ser un número entero entre 1 y 5.",
                "ejemplo": 1
            }), 400
        
        # Parámetros opcionales con defaults
        es_salario_integral = bool(data.get("es_salario_integral", False))
        es_empresa_exonerada = bool(data.get("es_empresa_exonerada", True))
        
        # ==================== CÁLCULO CON MOTOR PILA ====================
        
        # Instanciar calculadora (puede lanzar ValueError si parámetros inválidos)
        calc = CalculadoraPILA(
            salario_base=salario_base,
            nivel_riesgo_arl=nivel_riesgo,
            es_empresa_exonerada=es_empresa_exonerada,
            es_salario_integral=es_salario_integral
        )
        
        # Ejecutar cálculo
        resultado = calc.calcular()
        
        logger.info(
            f"Simulación PILA exitosa - Salario: ${salario_base:,.0f}, "
            f"Riesgo: {nivel_riesgo}, Integral: {es_salario_integral}, "
            f"Exonerada: {es_empresa_exonerada}"
        )
        
        # ==================== SERIALIZAR RESULTADO A JSON ====================
        
        # Convertir Decimal y datetime a tipos serializables
        response = {
            "datos_entrada": {
                "salario_base": float(resultado.salario_base),
                "ibc": float(resultado.ibc),
                "nivel_riesgo_arl": resultado.nivel_riesgo_arl,
                "es_salario_integral": resultado.es_salario_integral,
                "es_empresa_exonerada": resultado.es_empresa_exonerada,
                "salario_ajustado": resultado.salario_ajustado,
                "ibc_limitado": resultado.ibc_limitado
            },
            "salud": {
                "empleado": float(resultado.salud_empleado),
                "empleador": float(resultado.salud_empleador),
                "total": float(resultado.salud_total),
                "empleador_exonerado": resultado.salud_empleador_exonerado
            },
            "pension": {
                "empleado": float(resultado.pension_empleado),
                "empleador": float(resultado.pension_empleador),
                "total": float(resultado.pension_total)
            },
            "arl": {
                "empleador": float(resultado.arl_empleador),
                "tasa_porcentaje": float(resultado.tasa_arl * 100)  # Convertir a porcentaje
            },
            "parafiscales": {
                "ccf": float(resultado.ccf),
                "sena": float(resultado.sena),
                "icbf": float(resultado.icbf),
                "total": float(resultado.parafiscales_total),
                "aplica_sena_icbf": resultado.aplica_sena_icbf
            },
            "totales": {
                "empleado": float(resultado.total_empleado),
                "empleador": float(resultado.total_empleador),
                "general": float(resultado.total_general),
                "salario_neto": float(resultado.salario_base - resultado.total_empleado)
            },
            "metadata": {
                "fecha_calculo": resultado.fecha_calculo.strftime("%Y-%m-%d %H:%M:%S"),
                "advertencias": resultado.advertencias,
                "version_motor": "1.1.0"
            }
        }
        
        return jsonify(response), 200
    
    except ValueError as ve:
        # Errores de validación del Motor PILA (ej: nivel_riesgo inválido, salario negativo)
        logger.warning(f"Error de validación en Motor PILA: {ve}")
        return jsonify({
            "error": str(ve),
            "tipo": "error_validacion_motor_pila"
        }), 400
    
    except Exception as e:
        # Errores inesperados
        logger.error(f"Error inesperado en simular-pila: {e}", exc_info=True)
        return jsonify({
            "error": "Error interno del servidor al calcular PILA.",
            "detalle": str(e)
        }), 500


# ==================== GUARDAR SIMULACIÓN COMO COTIZACIÓN REAL ====================

@bp_cotizaciones.route("/guardar-simulacion", methods=["POST"])
@login_required
def guardar_simulacion():
    """
    Guarda una simulación PILA como cotización real en la base de datos.
    
    Request JSON:
        - empresa: Nombre de la empresa/cliente (requerido)
        - email: Email del cliente (opcional)
        - salario_base: Salario base usado en la simulación (requerido)
        - nivel_riesgo: Nivel de riesgo ARL (requerido)
        - total_empleado: Total a pagar por empleado (requerido)
        - total_empleador: Total a pagar por empleador (requerido)
        - total_general: Total general de la cotización (requerido)
        - notas: Notas adicionales (opcional)
    
    Returns:
        JSON con la cotización creada
    """
    try:
        data = request.get_json()
        
        # Validación de campos requeridos
        required_fields = ["empresa", "salario_base", "nivel_riesgo", "total_general"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            logger.warning(f"Campos faltantes en guardar simulación: {missing_fields}")
            return jsonify({
                "error": f"Faltan campos obligatorios: {', '.join(missing_fields)}"
            }), 400
        
        # Validar tipos de datos
        try:
            salario_base = float(data["salario_base"])
            total_general = float(data["total_general"])
            nivel_riesgo = int(data["nivel_riesgo"])
            
            if salario_base <= 0 or total_general <= 0:
                return jsonify({"error": "Los montos deben ser valores positivos"}), 400
            
            if nivel_riesgo not in [1, 2, 3, 4, 5]:
                return jsonify({"error": "El nivel de riesgo debe estar entre 1 y 5"}), 400
                
        except (ValueError, TypeError) as e:
            return jsonify({"error": f"Datos inválidos: {str(e)}"}), 400
        
        # Generar ID único de cotización
        fecha_actual = datetime.now()
        fecha_str = fecha_actual.strftime("%Y-%m-%d")
        id_cotizacion = f"PILA-{fecha_actual.strftime('%Y%m%d%H%M%S')}"
        
        # Construir descripción del servicio
        servicio = f"Aportes PILA - Salario Base: ${salario_base:,.0f} | Riesgo ARL: Nivel {nivel_riesgo}"
        
        # Construir notas detalladas
        notas_base = data.get("notas", "")
        total_empleado = float(data.get("total_empleado", 0))
        total_empleador = float(data.get("total_empleador", 0))
        
        notas_completas = f"""SIMULACIÓN PILA GUARDADA
Salario Base: ${salario_base:,.0f}
Nivel de Riesgo ARL: {nivel_riesgo}
Total Empleado: ${total_empleado:,.0f}
Total Empleador: ${total_empleador:,.0f}
Total General: ${total_general:,.0f}

{notas_base}

Generado por Simulador PILA v1.1.0"""
        
        # Crear nueva cotización usando ORM
        nueva_cotizacion = Cotizacion(
            id_cotizacion=id_cotizacion,
            cliente=data["empresa"],
            email=data.get("email", ""),
            servicio=servicio,
            monto=total_general,
            notas=notas_completas,
            fecha_creacion=fecha_str,
            estado="Simulación PILA"
        )
        
        # Guardar en la base de datos
        db.session.add(nueva_cotizacion)
        db.session.commit()
        
        logger.info(f"✅ Simulación PILA guardada como cotización: {id_cotizacion} - Empresa: {data['empresa']} - Monto: ${total_general:,.0f}")
        
        # Devolver respuesta exitosa
        return jsonify({
            "success": True,
            "message": "Simulación guardada exitosamente",
            "cotizacion": nueva_cotizacion.to_dict(),
            "id_cotizacion": id_cotizacion
        }), 201
        
    except IntegrityError as ie:
        db.session.rollback()
        logger.error(f"Error de integridad al guardar simulación: {ie}", exc_info=True)
        return jsonify({
            "error": "Error de integridad en la base de datos"
        }), 409
        
    except SQLAlchemyError as se:
        db.session.rollback()
        logger.error(f"Error de SQLAlchemy al guardar simulación: {se}", exc_info=True)
        return jsonify({
            "error": "Error de base de datos al guardar simulación"
        }), 500
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error general al guardar simulación PILA: {e}", exc_info=True)
        return jsonify({
            "error": f"Error interno del servidor: {str(e)}"
        }), 500


# ==================== INTERFAZ VISUAL SIMULADOR PILA ====================

@bp_cotizaciones.route("/simulador", methods=["GET"])
@login_required
def simulador_pila_page():
    """
    Renderiza la interfaz visual del Simulador PILA.
    
    Esta página consume el endpoint POST /api/cotizaciones/simular-pila
    y muestra los resultados de manera interactiva.
    
    Returns:
        HTML template del simulador PILA
    """
    try:
        logger.info(f"Usuario {session.get('user_name')} accedió al Simulador PILA")
        return render_template("simulador_pila.html")
    
    except Exception as e:
        logger.error(f"Error al renderizar simulador PILA: {e}", exc_info=True)
        return jsonify({
            "error": "Error al cargar el simulador",
            "detalle": str(e)
        }), 500
