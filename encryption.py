# -*- coding: utf-8 -*-
"""
encryption.py
====================================================
Módulo para encriptar y desencriptar credenciales
de forma segura usando Fernet (criptografía simétrica).
====================================================
"""

import os
import base64
from cryptography.fernet import Fernet
from logger import get_logger
import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde la raíz del proyecto (dashboard)
# Esto asume que encryption.py está en la carpeta 'dashboard'
project_root = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(project_root, "_env")
load_dotenv(env_path)

logger = get_logger(__name__)


class CredentialEncryption:
    """
    Clase para manejar la encriptación y desencriptación de credenciales.
    Usa Fernet (AES-128 en modo CBC con HMAC para autenticación).
    """

    def __init__(self):
        """
        Inicializa el sistema de encriptación.
        Genera o carga la clave de encriptación desde las variables de entorno.
        """
        self.fernet = self._initialize_fernet()

    def _initialize_fernet(self):
        """
        Inicializa el objeto Fernet con la clave de encriptación.
        Si no existe una clave, genera una nueva y la guarda en el archivo .env

        Returns:
            Fernet: Objeto Fernet para encriptar/desencriptar
        """
        try:
            # Intentar obtener la clave de encriptación desde variable de entorno
            encryption_key = os.getenv("ENCRYPTION_KEY", "").strip()

            if not encryption_key:
                logger.warning(
                    "No se encontró ENCRYPTION_KEY. Generando nueva clave..."
                )
                encryption_key = self._generate_and_save_key()

            # Validar que la clave tenga el formato correcto (debe ser base64)
            try:
                fernet = Fernet(encryption_key.encode())
                logger.info("Sistema de encriptación inicializado correctamente")
                return fernet
            except Exception as e:
                logger.error(f"Clave de encriptación inválida: {e}")
                logger.warning("Generando nueva clave de encriptación...")
                encryption_key = self._generate_and_save_key()
                return Fernet(encryption_key.encode())

        except Exception as e:
            logger.error(f"Error crítico al inicializar encriptación: {e}")
            raise

    def _generate_and_save_key(self):
        """
        Genera una nueva clave de encriptación y la guarda en el archivo .env

        Returns:
            str: Nueva clave de encriptación en formato base64
        """
        try:
            # Generar una nueva clave Fernet
            new_key = Fernet.generate_key()
            new_key_str = new_key.decode()

            # Leer el archivo .env actual
            env_path = os.path.join(os.path.dirname(__file__), "_env")

            if os.path.exists(env_path):
                with open(env_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                # Actualizar o agregar la línea ENCRYPTION_KEY
                key_found = False
                for i, line in enumerate(lines):
                    if line.startswith("ENCRYPTION_KEY="):
                        lines[i] = f"ENCRYPTION_KEY={new_key_str}\n"
                        key_found = True
                        break

                if not key_found:
                    lines.append(f"\nENCRYPTION_KEY={new_key_str}\n")

                # Escribir el archivo actualizado
                with open(env_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)

                logger.info("Nueva clave de encriptación generada y guardada en _env")
            else:
                logger.error("Archivo _env no encontrado")
                raise FileNotFoundError("No se pudo encontrar el archivo _env")

            # Actualizar la variable de entorno en el proceso actual
            os.environ["ENCRYPTION_KEY"] = new_key_str

            return new_key_str

        except Exception as e:
            logger.error(f"Error generando y guardando clave: {e}")
            raise

    def encrypt(self, text):
        """
        Encripta un texto plano.

        Args:
            text (str): Texto a encriptar (contraseña, usuario, etc.)

        Returns:
            str: Texto encriptado en formato base64
        """
        try:
            if not text:
                return ""

            # Convertir el texto a bytes y encriptar
            encrypted_bytes = self.fernet.encrypt(text.encode("utf-8"))

            # Retornar como string base64
            return encrypted_bytes.decode("utf-8")

        except Exception as e:
            logger.error(f"Error encriptando datos: {e}")
            raise

    def decrypt(self, encrypted_text):
        """
        Desencripta un texto encriptado.

        Args:
            encrypted_text (str): Texto encriptado en formato base64

        Returns:
            str: Texto desencriptado
        """
        try:
            if not encrypted_text:
                return ""

            # Convertir de base64 a bytes y desencriptar
            decrypted_bytes = self.fernet.decrypt(encrypted_text.encode("utf-8"))

            # Retornar como string
            return decrypted_bytes.decode("utf-8")

        except Exception as e:
            logger.error(f"Error desencriptando datos: {e}")
            # Si falla la desencriptación, puede ser que los datos no estén encriptados
            logger.warning(
                "No se pudo desencriptar. Los datos podrían estar en texto plano."
            )
            return encrypted_text

    def encrypt_credential(self, credential_dict):
        """
        Encripta los campos sensibles de un diccionario de credencial.

        Args:
            credential_dict (dict): Diccionario con datos de credencial

        Returns:
            dict: Diccionario con campos sensibles encriptados
        """
        try:
            encrypted_dict = credential_dict.copy()

            # Campos a encriptar
            sensitive_fields = ["usuario", "contrasena", "password", "user"]

            for field in sensitive_fields:
                if field in encrypted_dict and encrypted_dict[field]:
                    encrypted_dict[field] = self.encrypt(encrypted_dict[field])

            return encrypted_dict

        except Exception as e:
            logger.error(f"Error encriptando credencial: {e}")
            raise

    def decrypt_credential(self, credential_dict):
        """
        Desencripta los campos sensibles de un diccionario de credencial.

        Args:
            credential_dict (dict): Diccionario con datos de credencial encriptados

        Returns:
            dict: Diccionario con campos sensibles desencriptados
        """
        try:
            decrypted_dict = credential_dict.copy()

            # Campos a desencriptar
            sensitive_fields = ["usuario", "contrasena", "password", "user"]

            for field in sensitive_fields:
                if field in decrypted_dict and decrypted_dict[field]:
                    decrypted_dict[field] = self.decrypt(decrypted_dict[field])

            return decrypted_dict

        except Exception as e:
            logger.error(f"Error desencriptando credencial: {e}")
            raise


# Instancia global del sistema de encriptación
_encryption_instance = None


def get_encryption():
    """
    Obtiene la instancia singleton del sistema de encriptación.

    Returns:
        CredentialEncryption: Instancia del sistema de encriptación
    """
    global _encryption_instance
    if _encryption_instance is None:
        _encryption_instance = CredentialEncryption()
    return _encryption_instance


def encrypt_text(text):
    """
    Función helper para encriptar texto rápidamente.

    Args:
        text (str): Texto a encriptar

    Returns:
        str: Texto encriptado
    """
    return get_encryption().encrypt(text)


def decrypt_text(encrypted_text):
    """
    Función helper para desencriptar texto rápidamente.

    Args:
        encrypted_text (str): Texto encriptado

    Returns:
        str: Texto desencriptado
    """
    return get_encryption().decrypt(encrypted_text)
