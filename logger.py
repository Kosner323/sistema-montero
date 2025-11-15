# -*- coding: utf-8 -*-
"""
Configuración del sistema de logging para el Sistema Montero.
Crea una instancia 'logger' global que puede ser importada
por otros módulos.
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_logger(name="montero_system", log_level="INFO"):
    """
    Configura un logger profesional con rotación de archivos y salida a consola.
    """

    # Asegura que el directorio 'logs' exista
    try:
        log_dir = os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(log_dir, exist_ok=True)
    except Exception:
        # Fallback si __file__ no está definido (ej. en algunos entornos interactivos)
        log_dir = os.path.abspath("logs")
        os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, f"montero_system.log")

    # Obtiene la instancia del logger
    logger_instance = logging.getLogger(name)

    # Previene que se añadan múltiples handlers si se importa varias veces
    if logger_instance.hasHandlers():
        return logger_instance

    # Establece el nivel de logging
    logger_instance.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Formato del log
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(module)s.%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Handler 1: Escribir a un archivo con rotación
    # 10MB por archivo, mantiene 5 archivos de backup
    file_handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger_instance.addHandler(file_handler)

    # Handler 2: Escribir a la consola (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger_instance.addHandler(console_handler)

    return logger_instance


# --- Instancia Global ---
# Esta es la línea clave:
# Crea la instancia 'logger' que otros módulos (como auth.py) importarán.
logger = setup_logger()
