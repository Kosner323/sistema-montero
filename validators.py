# -*- coding: utf-8 -*-
"""
Decorador de Validación con Pydantic para Flask
================================================

Versión: 1.1 - Corregido para Flask-RESTX (TypeError)
"""

from functools import wraps
from flask import request, jsonify
from pydantic import BaseModel, ValidationError
from typing import Type, Callable, Any, Optional
import json


def validate_request(
    model: Type[BaseModel], source: str = "json", location: str = "body"
) -> Callable:
    """
    Decorador para validar datos de entrada usando un modelo Pydantic.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Obtener datos según la fuente
                data = _get_request_data(source)

                # Validar con Pydantic
                validated = model(**data)

                # Inyectar datos validados como argumento
                kwargs[location] = validated

                # Llamar a la función original
                return func(*args, **kwargs)

            # --- INICIO DE CORRECCIÓN ---
            # (Se quitaron las llamadas a 'jsonify()' para devolver
            #  diccionarios y códigos, que es lo que RESTX espera)
            except ValidationError as e:
                # Formatear errores de validación
                errors = _format_validation_errors(e)
                return {"error": "Datos inválidos", "detalles": errors}, 400

            except ValueError as e:
                # Error de conversión de datos
                return {"error": "Error en formato de datos", "mensaje": str(e)}, 400

            except Exception as e:
                # Error inesperado
                return {
                    "error": "Error interno",
                    "mensaje": "Error al procesar la solicitud",
                }, 500
            # --- FIN DE CORRECCIÓN ---

        return wrapper

    return decorator


def validate_json(model: Type[BaseModel]) -> Callable:
    """
    Decorador especializado para validar JSON.
    """
    return validate_request(model, source="json")


def validate_form(model: Type[BaseModel]) -> Callable:
    """
    Decorador especializado para validar form-data.
    """
    return validate_request(model, source="form")


def validate_query(model: Type[BaseModel]) -> Callable:
    """
    Decorador especializado para validar query parameters.
    """
    return validate_request(model, source="args")


def _get_request_data(source: str) -> dict:
    """
    Extrae datos de la request según la fuente especificada.
    """
    if source == "json":
        if not request.is_json:
            raise ValueError(
                "Se esperaba JSON pero el content-type no es application/json"
            )
        data = request.get_json(silent=True)
        if data is None:
            # --- INICIO DE CORRECCIÓN ---
            # Error más claro para cuerpos vacíos
            raise ValueError("JSON inválido o cuerpo de solicitud vacío")
            # --- FIN DE CORRECCIÓN ---
        return data

    elif source == "form":
        data = request.form.to_dict()
        for key in request.form.keys():
            values = request.form.getlist(key)
            if len(values) > 1:
                data[key] = values

        if not data:
            raise ValueError("Form-data vacío")
        return data

    elif source == "args":
        data = request.args.to_dict()
        for key in request.args.keys():
            values = request.args.getlist(key)
            if len(values) > 1:
                data[key] = values

        if not data:
            raise ValueError("Query parameters vacíos")
        return data

    elif source == "auto":
        if request.is_json:
            return _get_request_data("json")
        elif request.form:
            return _get_request_data("form")
        elif request.args:
            return _get_request_data("args")
        else:
            raise ValueError("No se encontraron datos en la request")

    else:
        raise ValueError(
            f"Fuente '{source}' no soportada. Use: json, form, args, o auto"
        )


def _format_validation_errors(validation_error: ValidationError) -> list:
    """
    Formatea los errores de Pydantic a un formato más amigable en español.
    """
    errors = []

    for error in validation_error.errors():
        location = " -> ".join(str(loc) for loc in error["loc"])
        error_type = error["type"]
        message = error["msg"]

        # Mapeo de mensajes comunes (Pydantic v2)
        if error_type == "missing":
            message = f"El campo '{location}' es obligatorio"
        elif error_type == "int_parsing":
            message = f"El campo '{location}' debe ser un número entero"
        elif error_type == "float_parsing":
            message = f"El campo '{location}' debe ser un número decimal"
        elif error_type == "string_type":
            message = f"El campo '{location}' debe ser texto"
        elif error_type == "bool_parsing":
            message = f"El campo '{location}' debe ser verdadero o falso"
        elif error_type == "value_error" and "email" in message:
            message = f"El campo '{location}' debe ser un email válido"
        elif "string_too_short" in error_type:
            ctx = error.get("ctx", {})
            message = f"El campo '{location}' es demasiado corto (mínimo {ctx.get('min_length', 'N/A')})"
        elif "string_too_long" in error_type:
            ctx = error.get("ctx", {})
            message = f"El campo '{location}' es demasiado largo (máximo {ctx.get('max_length', 'N/A')})"
        elif "greater_than_equal" in error_type:
            ctx = error.get("ctx", {})
            message = (
                f"El campo '{location}' debe ser mayor o igual a {ctx.get('ge', 'N/A')}"
            )
        elif "greater_than" in error_type:
            ctx = error.get("ctx", {})
            message = f"El campo '{location}' debe ser mayor que {ctx.get('gt', 'N/A')}"

        errors.append({"campo": location, "tipo_error": error_type, "mensaje": message})

    return errors


def validate_manual(
    model: Type[BaseModel], data: dict
) -> tuple[Optional[BaseModel], Optional[list]]:
    """
    Valida datos manualmente sin usar decorador.
    """
    try:
        validated = model(**data)
        return validated, None
    except ValidationError as e:
        errors = _format_validation_errors(e)
        return None, errors


def validate_list(model: Type[BaseModel], data_list: list) -> tuple[list, list]:
    """
    Valida una lista de objetos.
    """
    valid_objects = []
    errors = []

    for index, data in enumerate(data_list):
        try:
            validated = model(**data)
            valid_objects.append(validated)
        except ValidationError as e:
            formatted_errors = _format_validation_errors(e)
            errors.append({"indice": index, "datos": data, "errores": formatted_errors})

    return valid_objects, errors


def get_validation_schema(model: Type[BaseModel]) -> dict:
    """
    Obtiene el schema JSON de un modelo para documentación.
    """
    return model.model_json_schema()


def get_validation_example(model: Type[BaseModel]) -> dict:
    """
    Obtiene un ejemplo de datos válidos para un modelo.
    """
    schema = model.model_json_schema()

    if "examples" in schema and schema["examples"]:
        return schema["examples"][0]

    return {"info": "Ver schema para estructura completa"}


# ==============================================================================
# FUNCIONES DE AYUDA PARA RESPUESTAS
# (Estas se usan DENTRO de tus rutas)
# ==============================================================================


def success_response(data: Any, message: str = "Operación exitosa", status: int = 200):
    """
    Genera una respuesta exitosa estandarizada.
    """
    return jsonify({"success": True, "message": message, "data": data}), status


def error_response(message: str, errors: Optional[list] = None, status: int = 400):
    """
    Genera una respuesta de error estandarizada.
    """
    response = {"success": False, "error": message}

    if errors:
        response["detalles"] = errors

    return jsonify(response), status


def validation_error_response(validation_error: ValidationError):
    """
    Genera respuesta de error desde ValidationError de Pydantic.
    """
    errors = _format_validation_errors(validation_error)
    return error_response("Datos inválidos", errors, 400)


# ==============================================================================
# EXPORTACIONES
# ==============================================================================

__all__ = [
    "validate_request",
    "validate_json",
    "validate_form",
    "validate_query",
    "validate_manual",
    "validate_list",
    "get_validation_schema",
    "get_validation_example",
    "success_response",
    "error_response",
    "validation_error_response",
]
