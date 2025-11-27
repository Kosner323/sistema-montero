# -*- coding: utf-8 -*-
"""
Extensiones de Flask para el Sistema Montero.
Centraliza la inicialización de extensiones como Flask-Limiter, Flask-Mail,
Flask-SQLAlchemy y Flask-Migrate.
"""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# =============================================================================
# Inicialización de Flask-Limiter
# =============================================================================
# Se inicializa sin app para permitir el patrón de factory
limiter = Limiter(
    key_func=get_remote_address,  # Identifica al cliente por su IP
    default_limits=["200 per day", "50 per hour"],  # Límites globales por defecto
    storage_uri="memory://",  # Almacenamiento en memoria (cambiar a Redis en producción)
    strategy="fixed-window",  # Estrategia de ventana fija
)

# =============================================================================
# Inicialización de Flask-Mail
# =============================================================================
# Se inicializa sin app para permitir el patrón de factory
mail = Mail()

# =============================================================================
# Inicialización de Flask-SQLAlchemy
# =============================================================================
# Se inicializa sin app para permitir el patrón de factory
db = SQLAlchemy()

# =============================================================================
# Inicialización de Flask-Migrate
# =============================================================================
# Se inicializa sin app para permitir el patrón de factory
migrate = Migrate()
