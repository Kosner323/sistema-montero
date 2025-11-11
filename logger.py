# -*- coding: utf-8 -*-
"""
Sistema de Logging Profesional para Sistema Montero
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
import sys

LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")

if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

DEFAULT_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)-25s | %(funcName)-20s | %(message)s"
)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

COLORS = {
    "DEBUG": "\033[36m",
    "INFO": "\033[32m",
    "WARNING": "\033[33m",
    "ERROR": "\033[31m",
    "CRITICAL": "\033[35m",
    "RESET": "\033[0m",
}


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        if levelname in COLORS:
            record.levelname = f"{COLORS[levelname]}{levelname}{COLORS['RESET']}"
        return super().format(record)


def get_logger(
    name: str, log_to_file: bool = True, log_level: str = None
) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    level = getattr(logging, (log_level or DEFAULT_LOG_LEVEL).upper(), logging.INFO)
    logger.setLevel(level)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = ColoredFormatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    if log_to_file:
        log_file = os.path.join(LOGS_DIR, "montero_app.log")
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        error_log_file = os.path.join(LOGS_DIR, "montero_errors.log")
        error_handler = RotatingFileHandler(
            error_log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        logger.addHandler(error_handler)

    logger.propagate = False
    return logger


def log_startup_info():
    logger = get_logger("montero.startup")
    logger.info("=" * 80)
    logger.info("ðŸš€ SISTEMA MONTERO - INICIANDO")
    logger.info(f"ðŸ“… Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"ðŸ“‚ Directorio de logs: {LOGS_DIR}")
    logger.info(f"ðŸ“Š Nivel de log: {DEFAULT_LOG_LEVEL}")
    logger.info("=" * 80)


def log_shutdown_info():
    logger = get_logger("montero.shutdown")
    logger.info("=" * 80)
    logger.info("ðŸ›‘ SISTEMA MONTERO - APAGANDO")
    logger.info(f"ðŸ“… Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)


logging.getLogger("werkzeug").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
