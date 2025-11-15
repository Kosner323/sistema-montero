# -*- coding: utf-8 -*-
"""
Módulo de Encriptación Fernet - Sistema Montero
===============================================
Provee una clase wrapper 'FernetEncryptor' para encriptar y desencriptar
texto de forma simétrica usando la librería cryptography.
"""

import base64
import os

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from logger import logger

# (CORREGIDO: Importa la instancia global 'logger')


# --- Configuración ---
# (CORREGIDO: No es necesario llamar a get_logger())
# from logger import logger
SALT_SIZE = 16  # 16 bytes (128 bits) para el salt
DEFAULT_ITERATIONS = 390000  # Iteraciones recomendadas por OWASP


class FernetEncryptor:
    """
    Wrapper para Fernet que maneja la derivación de claves y la (des)encriptación.
    """

    def __init__(self, key: str = None, salt: bytes = None):
        """
        Inicializa el encriptador.
        Si se provee una clave (ENCRYPTION_KEY), la usa.
        Si no, intenta cargarla desde variables de entorno.
        """
        try:
            if key is None:
                key = os.getenv("ENCRYPTION_KEY")

            if not key:
                # (CORREGIDO: usa 'logger')
                logger.error("ENCRYPTION_KEY no encontrada en variables de entorno.")
                raise ValueError("La clave de encriptación no está configurada.")

            self._fernet = Fernet(self._derive_key(key, salt))
            # (CORREGIDO: usa 'logger')
            logger.info("FernetEncryptor inicializado correctamente.")
        except Exception as e:
            # (CORREGIDO: usa 'logger')
            logger.critical(f"Error fatal al inicializar FernetEncryptor: {e}", exc_info=True)
            self._fernet = None

    @staticmethod
    def _derive_key(key: str, salt: bytes = None) -> bytes:
        """
        Deriva una clave Fernet de 32 bytes a partir de la ENCRYPTION_KEY
        usando PBKDF2HMAC.
        """
        if salt is None:
            # Si no se provee salt, usamos uno fijo (no ideal para alta seguridad,
            # pero necesario si la clave base es siempre la misma)
            # Un mejor enfoque sería almacenar un salt fijo en _env
            salt = os.getenv("ENCRYPTION_SALT", "default_salt_change_me").encode("utf-8")
            if len(salt) < 16:
                salt = salt.ljust(16, b"_")  # Asegurar longitud mínima

        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt[:16],  # Usar solo 16 bytes
                iterations=DEFAULT_ITERATIONS,
                backend=default_backend(),
            )
            derived_key = base64.urlsafe_b64encode(kdf.derive(key.encode("utf-8")))
            return derived_key
        except Exception as e:
            # (CORREGIDO: usa 'logger')
            logger.error(f"Error al derivar la clave de encriptación: {e}", exc_info=True)
            raise

    @staticmethod
    def generate_key() -> str:
        """
        Genera una nueva clave Fernet (32 bytes, URL-safe base64 encoded).
        Esta es una clave de ALTA ENTROPÍA, ideal para la ENCRYPTION_KEY en .env.
        """
        return Fernet.generate_key().decode("utf-8")

    def encrypt(self, data: str) -> str | None:
        """
        Encripta un string y devuelve un string encriptado.
        Devuelve None si los datos están vacíos o si hay un error.
        """
        if not data:
            return None

        if not self._fernet:
            # (CORREGIDO: usa 'logger')
            logger.error("Intento de encriptar, pero el encriptador no está inicializado.")
            return None

        try:
            token = self._fernet.encrypt(data.encode("utf-8"))
            return token.decode("utf-8")
        except Exception as e:
            # (CORREGIDO: usa 'logger')
            logger.error(f"Error durante la encriptación: {e}", exc_info=True)
            return None

    def decrypt(self, token: str, ttl: int = None) -> str | None:
        """
        Desencripta un token y devuelve el string original.
        Devuelve None si el token está vacío, es inválido o si hay un error.
        'ttl' (en segundos) es opcional para verificar la antigüedad del token.
        """
        if not token:
            return None

        if not self._fernet:
            # (CORREGIDO: usa 'logger')
            logger.error("Intento de desencriptar, pero el encriptador no está inicializado.")
            return None

        try:
            # Convertir el token de string a bytes
            token_bytes = token.encode("utf-8")

            if ttl:
                decrypted_data = self._fernet.decrypt(token_bytes, ttl=ttl)
            else:
                decrypted_data = self._fernet.decrypt(token_bytes)

            return decrypted_data.decode("utf-8")

        except InvalidToken:
            # (CORREGIDO: usa 'logger')
            logger.warning("Intento de desencriptar un token inválido o corrupto.")
            return None
        except Exception as e:
            # (CORREGIDO: usa 'logger')
            logger.error(f"Error durante la desencriptación: {e}", exc_info=True)
            return None

    def encrypt_dict_fields(self, data_dict: dict, fields_to_encrypt: list) -> dict:
        """
        Encripta campos específicos dentro de un diccionario.
        Modifica el diccionario in-place.
        """
        if not self._fernet:
            # (CORREGIDO: usa 'logger')
            logger.error("Intento de encriptar dict, pero el encriptador no está inicializado.")
            return data_dict

        for field in fields_to_encrypt:
            if field in data_dict and data_dict[field]:
                try:
                    data_dict[field] = self.encrypt(data_dict[field])
                except Exception as e:
                    # (CORREGIDO: usa 'logger')
                    logger.error(f"Error al encriptar el campo '{field}': {e}", exc_info=True)
                    data_dict[field] = None  # Poner a None por seguridad
        return data_dict

    def decrypt_dict_fields(self, data_dict: dict, fields_to_decrypt: list) -> dict:
        """
        Desencripta campos específicos dentro de un diccionario.
        Modifica el diccionario in-place.
        """
        if not self._fernet:
            # (CORREGIDO: usa 'logger')
            logger.error("Intento de desencriptar dict, pero el encriptador no está inicializado.")
            return data_dict

        for field in fields_to_decrypt:
            if field in data_dict and data_dict[field]:
                try:
                    data_dict[field] = self.decrypt(data_dict[field])
                except Exception as e:
                    # (CORREGIDO: usa 'logger')
                    logger.error(f"Error al desencriptar el campo '{field}': {e}", exc_info=True)
                    data_dict[field] = "--- ERROR AL DESENCRIPTAR ---"
        return data_dict

    def encrypt_credentials(self, credentials: dict) -> dict:
        """
        Helper específico para encriptar un diccionario de credenciales.
        Busca campos comunes como 'contrasena', 'password', 'secret', etc.
        """
        campos_comunes = ["contrasena", "password", "secret", "token", "api_key"]
        campos_a_encriptar = [campo for campo in campos_comunes if campo in credentials]

        if not campos_a_encriptar:
            # (CORREGIDO: usa 'logger')
            logger.warning("encrypt_credentials llamado, pero no se encontraron campos para encriptar.")

        return self.encrypt_dict_fields(credentials, campos_a_encriptar)

    def decrypt_credentials(self, credentials: dict) -> dict:
        """
        Helper específico para desencriptar un diccionario de credenciales.
        Busca campos comunes como 'contrasena', 'password', 'secret', etc.
        """
        campos_comunes = ["contrasena", "password", "secret", "token", "api_key"]
        campos_a_desencriptar = [campo for campo in campos_comunes if campo in credentials]

        if not campos_a_desencriptar:
            # (CORREGIDO: usa 'logger')
            logger.warning("decrypt_credentials llamado, pero no se encontraron campos para desencriptar.")

        return self.decrypt_dict_fields(credentials, campos_a_desencriptar)


# --- Instancia Global ---
# Se puede crear una instancia global si la clave es estable (desde _env)
# Esto evita reinicializar el encriptador en cada importación.
try:
    global_encryptor = FernetEncryptor()
    # (CORREGIDO: usa 'logger')
    logger.info("Instancia global de FernetEncryptor creada exitosamente.")
except ValueError as e:
    global_encryptor = None
    # (CORREGIDO: usa 'logger')
    logger.critical(
        f"No se pudo crear la instancia global de FernetEncryptor: {e}. "
        "La encriptación fallará hasta que se configure ENCRYPTION_KEY."
    )

# --- Funciones de Ayuda (para uso simple) ---


def encrypt_data(data: str) -> str | None:
    """Función helper global para encriptar datos."""
    if not global_encryptor:
        # (CORREGIDO: usa 'logger')
        logger.error("encrypt_data falló: El encriptador global no está inicializado.")
        return None
    return global_encryptor.encrypt(data)


def decrypt_data(token: str) -> str | None:
    """Función helper global para desencriptar datos."""
    if not global_encryptor:
        # (CORREGIDO: usa 'logger')
        logger.error("decrypt_data falló: El encriptador global no está inicializado.")
        return None
    return global_encryptor.decrypt(token)
