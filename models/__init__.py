# Contenido para: D:\Mi-App-React\src\dashboard\models\__init__.py

# Modelos de validación (Pydantic)
from .validation_models import (
    LoginRequest,
    RegisterRequest,
    EmpresaCreate,
    EmpresaUpdate,
)

# Modelos de base de datos (SQLAlchemy)
from .database import (
    Base,
    Empresa,
    Usuario,
    Pago,
    Tutela,
    Cotizacion,
    Incapacidad,
    Notificacion,
    get_engine,
    get_session,
    init_db,
)

__all__ = [
    # Modelos de validación
    "LoginRequest",
    "RegisterRequest",
    "EmpresaCreate",
    "EmpresaUpdate",
    # Modelos de base de datos
    "Base",
    "Empresa",
    "Usuario",
    "Pago",
    "Tutela",
    "Cotizacion",
    "Incapacidad",
    "Notificacion",
    # Funciones de ayuda
    "get_engine",
    "get_session",
    "init_db",
]
