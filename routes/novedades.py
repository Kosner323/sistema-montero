# -*- coding: utf-8 -*-
import json
import sqlite3  # Importar para manejo de errores específicos si es necesario
import traceback
from datetime import datetime

from flask import Blueprint, g, jsonify, request, session  # Añadir g para usar g.db

from logger import logger
from utils import login_required

bp_novedades = Blueprint("bp_novedades", __name__, url_prefix="/api/novedades")

# --- Rutas CRUD para Novedades ---


@bp_novedades.route("", methods=["GET"])
@login_required
def get_novedades():
    """Obtiene todas las novedades de la base de datos."""
    try:
        conn = g.db
        # Añadir filtros si es necesario en el futuro (ej. ?status=Nuevo)
        # Considera usar parámetros de URL para filtrar aquí
        query = "SELECT * FROM novedades ORDER BY updateDate DESC, creationDate DESC"
        novedades = conn.execute(query).fetchall()

        # Convertir datos JSON de texto a objeto Python antes de enviar
        result = []
        for row in novedades:
            novedad_dict = dict(row)  # Convertir sqlite3.Row a diccionario
            try:
                # Cargar beneficiarios, asegurando que sea una lista si es null o inválido
                beneficiaries_str = novedad_dict.get("beneficiaries")
                novedad_dict["beneficiaries"] = json.loads(beneficiaries_str) if beneficiaries_str else []
            except (json.JSONDecodeError, TypeError):
                novedad_dict["beneficiaries"] = []  # Default a lista vacía si falla

            try:
                # Cargar historial, asegurando que sea una lista si es null o inválido
                history_str = novedad_dict.get("history")
                novedad_dict["history"] = json.loads(history_str) if history_str else []
            except (json.JSONDecodeError, TypeError):
                novedad_dict["history"] = []  # Default a lista vacía si falla

            result.append(novedad_dict)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error al obtener novedades: {e}")
        # traceback.print_exc()  # MIGRADO: reemplazar por logger.error con exc_info=True
        return jsonify({"error": f"Error interno al obtener novedades: {str(e)}"}), 500
    # g.db se cierra automáticamente por app.after_request


@bp_novedades.route("", methods=["POST"])
@login_required
def create_novedad():
    """Crea una nueva novedad en la base de datos."""
    if not request.is_json:
        return jsonify({"error": "Se esperaba Content-Type: application/json"}), 415

    data = request.get_json()
    try:
        conn = g.db
        # Validaciones básicas de campos requeridos
        required_fields = ["client", "subject", "priority", "status", "description"]
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return (
                jsonify({"error": f"Faltan campos obligatorios: {', '.join(missing_fields)}."}),
                400,
            )

        now_dt = datetime.now()
        now_str_datetime = now_dt.strftime("%Y-%m-%d %H:%M:%S")  # Fecha y hora para historial
        now_str_date = now_dt.strftime("%Y-%m-%d")  # Solo fecha para creation/update date

        # Preparar datos para inserción, convirtiendo listas a JSON string
        # Usar json.dumps con manejo de None o listas vacías
        beneficiaries_json = json.dumps(data.get("beneficiaries") or [])

        # Crear historial inicial
        user_name = session.get("user_name", "Usuario Desconocido")  # Obtener nombre de usuario de la sesión
        initial_history = [
            {
                "user": user_name,
                "timestamp": now_str_datetime,
                "action": "Creó el caso.",
                "comment": f"Estado inicial: {data['status']}, Prioridad: {data.get('priorityText', data['priority'])}.",
            }
        ]
        history_json = json.dumps(initial_history)

        # Convertir IBC a float si existe, sino None
        ibc_value = data.get("ibc")
        try:
            ibc_float = float(ibc_value) if ibc_value not in [None, ""] else None
        except (ValueError, TypeError):
            ibc_float = None  # Poner None si no se puede convertir

        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO novedades (
                client, subject, priority, status, priorityText,
                idType, idNumber, firstName, lastName, nationality, gender, birthDate, phone,
                department, city, address, neighborhood, email,
                beneficiaries, -- JSON String
                eps, arl, arlClass, ccf, pensionFund, ibc,
                description, radicado, solutionDescription,
                creationDate, updateDate, assignedTo, history -- JSON String
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                data.get("client"),
                data.get("subject"),
                data.get("priority"),
                data.get("status"),
                data.get("priorityText", data.get("priority")),  # Usar texto de prioridad
                data.get("idType"),
                data.get("idNumber"),
                data.get("firstName"),
                data.get("lastName"),
                data.get("nationality"),
                data.get("gender"),
                data.get("birthDate"),
                data.get("phone"),
                data.get("department"),
                data.get("city"),
                data.get("address"),
                data.get("neighborhood"),
                data.get("email"),
                beneficiaries_json,  # Guardar como JSON string
                data.get("eps"),
                data.get("arl"),
                data.get("arlClass"),
                data.get("ccf"),
                data.get("pensionFund"),
                ibc_float,  # Usar IBC convertido
                data.get("description"),
                data.get("radicado"),
                data.get("solutionDescription", ""),  # Solución vacía al crear
                now_str_date,
                now_str_date,  # creation y update son iguales al crear (solo fecha)
                data.get("assignedTo", "Sistema"),  # Asignado por defecto a Sistema
                history_json,  # Guardar historial inicial como JSON string
            ),
        )
        conn.commit()
        new_id = cursor.lastrowid  # Obtener el ID autoincremental asignado

        # Devolver el objeto creado consultándolo de la BD para asegurar consistencia
        novedad_creada_row = conn.execute("SELECT * FROM novedades WHERE id = ?", (new_id,)).fetchone()
        if not novedad_creada_row:
            # Esto no debería pasar si la inserción fue exitosa, pero es una verificación extra
            raise Exception("No se pudo recuperar la novedad recién creada.")

        novedad_creada_dict = dict(novedad_creada_row)
        # Convertir JSON strings de vuelta a listas/objetos para la respuesta
        novedad_creada_dict["beneficiaries"] = json.loads(novedad_creada_dict.get("beneficiaries") or "[]")
        novedad_creada_dict["history"] = json.loads(novedad_creada_dict.get("history") or "[]")

        return jsonify(novedad_creada_dict), 201

    except sqlite3.Error as db_err:
        conn.rollback()
        logger.error(f"Error de base de datos al crear novedad: {db_err}")
        # traceback.print_exc()  # MIGRADO: reemplazar por logger.error con exc_info=True
        return jsonify({"error": f"Error de base de datos: {str(db_err)}"}), 500
    except Exception as e:
        conn.rollback()
        logger.error(f"Error general al crear novedad: {e}")
        # traceback.print_exc()  # MIGRADO: reemplazar por logger.error con exc_info=True
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
    # g.db se cierra automáticamente por app.after_request


@bp_novedades.route("/<int:novedad_id>", methods=["PUT"])
@login_required
def update_novedad(novedad_id):
    """Actualiza una novedad existente (estado, prioridad, solución, comentario, etc.)."""
    if not request.is_json:
        return jsonify({"error": "Se esperaba Content-Type: application/json"}), 415

    data = request.get_json()  # Datos enviados desde el frontend para actualizar
    try:
        conn = g.db
        # 1. Obtener la novedad actual de la BD
        novedad_actual_row = conn.execute("SELECT * FROM novedades WHERE id = ?", (novedad_id,)).fetchone()
        if not novedad_actual_row:
            return jsonify({"error": "Novedad no encontrada."}), 404

        novedad_actual_dict = dict(novedad_actual_row)  # Convertir a diccionario
        try:
            # Cargar el historial actual desde el JSON string
            current_history = json.loads(novedad_actual_dict.get("history") or "[]")
        except (json.JSONDecodeError, TypeError):
            logger.info(f"Advertencia: Historial inválido para novedad {novedad_id}. Iniciando historial nuevo.")
            current_history = []

        now_dt = datetime.now()
        now_str_datetime = now_dt.strftime("%Y-%m-%d %H:%M:%S")  # Fecha y hora para historial
        now_str_date = now_dt.strftime("%Y-%m-%d")  # Solo fecha para update date

        updated_fields = {}  # Diccionario para guardar los campos SQL que realmente cambian
        action_description_parts = []  # Lista para construir la descripción de la acción

        user_name = session.get("user_name", "Usuario Desconocido")  # Usuario que realiza la acción

        # --- Comparar y actualizar campos ---
        # Iterar sobre los campos permitidos para actualización enviados en 'data'
        campos_actualizables = [
            "client",
            "subject",
            "priority",
            "status",
            "priorityText",
            "idType",
            "idNumber",
            "firstName",
            "lastName",
            "nationality",
            "gender",
            "birthDate",
            "phone",
            "department",
            "city",
            "address",
            "neighborhood",
            "email",
            "beneficiaries",  # Se tratará por separado
            "eps",
            "arl",
            "arlClass",
            "ccf",
            "pensionFund",
            "ibc",
            "description",
            "radicado",
            "solutionDescription",
            "assignedTo",
        ]

        for key in campos_actualizables:
            if key in data and data[key] != novedad_actual_dict.get(key):
                # Caso especial para beneficiarios: convertir a JSON string antes de guardar
                if key == "beneficiaries":
                    updated_fields[key] = json.dumps(data[key] or [])
                    action_description_parts.append(f"Actualizó beneficiarios.")  # Descripción genérica
                # Caso especial para IBC: convertir a float
                elif key == "ibc":
                    try:
                        ibc_float = float(data[key]) if data[key] not in [None, ""] else None
                        if ibc_float != novedad_actual_dict.get(key):  # Comparar después de convertir
                            updated_fields[key] = ibc_float
                            action_description_parts.append(f"Actualizó IBC a {ibc_float}.")
                    except (ValueError, TypeError):
                        print(f"Advertencia: valor IBC inválido '{data[key]}' no se actualizará.")
                # Otros campos
                else:
                    updated_fields[key] = data[key]
                    # Añadir descripción más específica para campos clave
                    if key == "status":
                        action_description_parts.append(f"Cambió estado a '{data[key]}'.")
                    elif key == "priority":
                        action_description_parts.append(f"Cambió prioridad a '{data.get('priorityText', data[key])}'.")
                    elif key == "assignedTo":
                        action_description_parts.append(f"Asignó a '{data[key]}'.")
                    elif key == "solutionDescription" and data[key]:
                        action_description_parts.append(f"Añadió/modificó solución.")
                    # else: action_description_parts.append(f"Actualizó {key}.") # Descripción genérica (opcional)

        # Manejar nuevo comentario
        new_comment = data.get("newComment", "").strip()

        # Construir entrada de historial solo si hubo cambios o comentario
        history_entry = None
        if updated_fields or new_comment:
            action_description = " ".join(action_description_parts) if action_description_parts else "Actualizó el caso."
            if not action_description_parts and new_comment:  # Si solo hay comentario
                action_description = "Añadió comentario."

            history_entry = {
                "user": user_name,
                "timestamp": now_str_datetime,
                "action": action_description,
                "comment": new_comment,  # Puede ser vacío si solo hubo cambios de campos
            }
            current_history.append(history_entry)
            updated_fields["history"] = json.dumps(current_history)  # Guardar historial actualizado
            updated_fields["updateDate"] = now_str_date  # Actualizar fecha de modificación

            # Construir y ejecutar la consulta SQL UPDATE
            set_clause = ", ".join([f"{key} = ?" for key in updated_fields.keys()])
            values = list(updated_fields.values())
            values.append(novedad_id)  # Añadir el ID para el WHERE

            query = f"UPDATE novedades SET {set_clause} WHERE id = ?"
            conn.execute(query, tuple(values))
            conn.commit()

            # Devolver la novedad actualizada completa consultándola de nuevo
            novedad_actualizada_row = conn.execute("SELECT * FROM novedades WHERE id = ?", (novedad_id,)).fetchone()
            novedad_actualizada_dict = dict(novedad_actualizada_row)
            # Convertir JSON strings de vuelta a listas/objetos para la respuesta
            novedad_actualizada_dict["beneficiaries"] = json.loads(novedad_actualizada_dict.get("beneficiaries") or "[]")
            novedad_actualizada_dict["history"] = json.loads(novedad_actualizada_dict.get("history") or "[]")

            return jsonify(novedad_actualizada_dict), 200
        else:
            # No hubo cambios detectables
            return jsonify({"message": "No se realizaron cambios."}), 200

    except sqlite3.Error as db_err:
        conn.rollback()
        logger.error(f"Error de base de datos al actualizar novedad {novedad_id}: {db_err}")
        # traceback.print_exc()  # MIGRADO: reemplazar por logger.error con exc_info=True
        return jsonify({"error": f"Error de base de datos: {str(db_err)}"}), 500
    except json.JSONDecodeError as json_err:
        # Error específico si falla la conversión JSON (puede pasar con datos corruptos)
        conn.rollback()
        logger.error(f"Error JSON al procesar novedad {novedad_id}: {json_err}")
        return (
            jsonify({"error": f"Error interno procesando datos JSON: {str(json_err)}"}),
            500,
        )
    except Exception as e:
        conn.rollback()
        logger.error(f"Error general al actualizar novedad {novedad_id}: {e}")
        # traceback.print_exc()  # MIGRADO: reemplazar por logger.error con exc_info=True
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
    # g.db se cierra automáticamente por app.after_request


# --- Endpoint para Eliminar (Opcional - Considerar borrado lógico) ---
@bp_novedades.route("/<int:novedad_id>", methods=["DELETE"])
@login_required
def delete_novedad(novedad_id):
    """Elimina una novedad (Â¡ACCIÓN PERMANENTE!)."""
    try:
        conn = g.db
        cursor = conn.cursor()
        cursor.execute("DELETE FROM novedades WHERE id = ?", (novedad_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Novedad no encontrada."}), 404
        else:
            # Registrar la acción (opcional)
            user_name = session.get("user_name", "Usuario Desconocido")
            print(f"Novedad {novedad_id} eliminada por {user_name} el {datetime.now()}")
            return (
                jsonify({"message": f"Novedad {novedad_id} eliminada correctamente."}),
                200,
            )

    except sqlite3.Error as db_err:
        conn.rollback()
        logger.error(f"Error de base de datos al eliminar novedad {novedad_id}: {db_err}")
        # traceback.print_exc()  # MIGRADO: reemplazar por logger.error con exc_info=True
        return jsonify({"error": f"Error de base de datos: {str(db_err)}"}), 500
    except Exception as e:
        conn.rollback()
        logger.error(f"Error general al eliminar novedad {novedad_id}: {e}")
        # traceback.print_exc()  # MIGRADO: reemplazar por logger.error con exc_info=True
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
    # g.db se cierra automáticamente por app.after_request
