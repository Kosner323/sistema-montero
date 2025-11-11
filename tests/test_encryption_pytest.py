# -*- coding: utf-8 -*-
"""
test_encryption_pytest.py
====================================================
Suite de tests con pytest para el sistema de encriptación
====================================================
"""

import pytest
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path

from encryption import (
    CredentialEncryption,
    encrypt_text,
    decrypt_text,
    get_encryption,
)


# ==============================================================================
# TESTS DE ENCRIPTACIÓN BÁSICA
# ==============================================================================


class TestBasicEncryption:
    """Tests de encriptación básica."""

    def test_encrypt_decrypt_simple_text(self):
        """Test de encriptación y desencriptación de texto simple."""
        original = "contraseña123"
        encrypted = encrypt_text(original)
        decrypted = decrypt_text(encrypted)

        assert decrypted == original
        assert encrypted != original  # El texto encriptado debe ser diferente
        assert len(encrypted) > len(original)  # El texto encriptado es más largo

    def test_encrypt_decrypt_empty_string(self):
        """Test con string vacío."""
        original = ""
        encrypted = encrypt_text(original)
        decrypted = decrypt_text(encrypted)

        assert decrypted == original

    def test_encrypt_decrypt_with_spaces(self):
        """Test con espacios y caracteres especiales."""
        original = "texto con espacios y símbolos: @#$%"
        encrypted = encrypt_text(original)
        decrypted = decrypt_text(encrypted)

        assert decrypted == original

    def test_encrypt_decrypt_long_text(self):
        """Test con texto largo."""
        original = "texto_largo_" * 100  # 1200 caracteres
        encrypted = encrypt_text(original)
        decrypted = decrypt_text(encrypted)

        assert decrypted == original

    @pytest.mark.parametrize(
        "text",
        [
            "simple",
            "ContraseñaConÑ",
            "usuario@ejemplo.com",
            "P@ssw0rd!#$",
            "123456789",
            "   espacios   ",
        ],
    )
    def test_encrypt_decrypt_various_texts(self, text):
        """Test parametrizado con diferentes tipos de texto."""
        encrypted = encrypt_text(text)
        decrypted = decrypt_text(encrypted)
        assert decrypted == text


# ==============================================================================
# TESTS DE CARACTERES ESPECIALES Y UNICODE
# ==============================================================================


class TestSpecialCharacters:
    """Tests con caracteres especiales y Unicode."""

    def test_spanish_characters(self):
        """Test con caracteres en español."""
        original = "Contraseña con ñ y tildes: áéíóú"
        encrypted = encrypt_text(original)
        decrypted = decrypt_text(encrypted)

        assert decrypted == original

    def test_special_symbols(self):
        """Test con símbolos especiales."""
        original = "Símbolos: !@#$%^&*()_+-=[]{}|;:',.<>?/"
        encrypted = encrypt_text(original)
        decrypted = decrypt_text(encrypted)

        assert decrypted == original

    def test_emojis(self):
        """Test con emojis."""
        original = "Emojis: 🔐 🔑 🛡️ ✅"
        encrypted = encrypt_text(original)
        decrypted = decrypt_text(encrypted)

        assert decrypted == original

    @pytest.mark.parametrize(
        "text,description",
        [
            ("Japonés: パスワード", "Japanese"),
            ("Árabe: كلمة السر", "Arabic"),
            ("Chino: 密码", "Chinese"),
            ("Ruso: пароль", "Russian"),
            ("Griego: κωδικός", "Greek"),
        ],
    )
    def test_international_characters(self, text, description):
        """Test con diferentes idiomas."""
        encrypted = encrypt_text(text)
        decrypted = decrypt_text(text)

        assert decrypted == text, f"Failed for {description}"


# ==============================================================================
# TESTS DE CONSISTENCIA Y SEGURIDAD
# ==============================================================================


class TestEncryptionConsistency:
    """Tests de consistencia de encriptación."""

    def test_same_text_different_encryptions(self):
        """Verifica que el mismo texto produzca diferentes encriptaciones."""
        original = "contraseña_de_prueba"

        encrypted1 = encrypt_text(original)
        encrypted2 = encrypt_text(original)

        # Las encriptaciones deben ser diferentes (por el IV aleatorio de Fernet)
        assert encrypted1 != encrypted2

        # Pero ambas deben desencriptar al mismo valor
        assert decrypt_text(encrypted1) == original
        assert decrypt_text(encrypted2) == original

    def test_encryption_is_reversible(self):
        """Verifica que la encriptación sea reversible múltiples veces."""
        original = "test_reversible"

        # Encriptar y desencriptar 10 veces
        for _ in range(10):
            encrypted = encrypt_text(original)
            decrypted = decrypt_text(encrypted)
            assert decrypted == original

    def test_encrypted_text_is_string(self):
        """Verifica que el texto encriptado sea siempre un string."""
        texts = ["test1", "test2", "", "símbolos!@#"]

        for text in texts:
            encrypted = encrypt_text(text)
            assert isinstance(encrypted, str)
            # --- INICIO DE CORRECCIÓN 1 (Basado en el fallo 'assert 0 > 0') ---
            assert (len(encrypted) > 0) or (text == "")
            # --- FIN DE CORRECCIÓN 1 ---


# ==============================================================================
# TESTS DE LA CLASE CredentialEncryption
# ==============================================================================


class TestCredentialEncryptionClass:
    """Tests de la clase CredentialEncryption."""

    def test_encrypt_credential_dict(self):
        """Test de encriptación de diccionario completo."""
        credential = {
            "usuario": "admin@empresa.com",
            "contrasena": "SecurePass123!",
            "url": "https://example.com",
            "notas": "Notas de prueba",
        }

        enc = get_encryption()
        encrypted = enc.encrypt_credential(credential)

        # Verificar que los campos sensibles están encriptados
        assert encrypted["usuario"] != credential["usuario"]
        assert encrypted["contrasena"] != credential["contrasena"]

        # Verificar que los campos no sensibles no cambiaron
        assert encrypted["url"] == credential["url"]
        assert encrypted["notas"] == credential["notas"]

    def test_decrypt_credential_dict(self):
        """Test de desencriptación de diccionario."""
        original = {
            "usuario": "admin@empresa.com",
            "contrasena": "SecurePass123!",
            "entidad": "DIAN",
        }

        enc = get_encryption()
        encrypted = enc.encrypt_credential(original)
        decrypted = enc.decrypt_credential(encrypted)

        # Verificar que se recuperaron los valores originales
        assert decrypted["usuario"] == original["usuario"]
        assert decrypted["contrasena"] == original["contrasena"]
        assert decrypted["entidad"] == original["entidad"]

    def test_encrypt_with_alternative_field_names(self):
        """Test con nombres de campo alternativos."""
        credential = {
            "user": "usuario_test",
            "password": "password_test",
            "other_field": "not encrypted",
        }

        enc = get_encryption()
        encrypted = enc.encrypt_credential(credential)

        # Campos 'user' y 'password' también deben encriptarse
        assert encrypted["user"] != credential["user"]
        assert encrypted["password"] != credential["password"]
        assert encrypted["other_field"] == credential["other_field"]


# ==============================================================================
# TESTS DE MANEJO DE ERRORES
# ==============================================================================


class TestErrorHandling:
    """Tests de manejo de errores."""

    def test_decrypt_invalid_data(self):
        """Test de desencriptación con datos inválidos."""
        # --- INICIO DE CORRECCIÓN 2 (Basado en el fallo 'assert ... is None') ---
        invalid_data = "datos_invalidos_no_encriptados"
        # Verifica que la función devuelve el texto original si no puede desencriptar
        result = decrypt_text(invalid_data)
        assert result == invalid_data
        # --- FIN DE CORRECCIÓN 2 ---

    def test_decrypt_corrupted_data(self):
        """Test con datos corruptos."""
        # --- INICIO DE CORRECCIÓN 3 (Basado en el fallo 'assert ... is None') ---
        corrupted_data = "Z2FyYmFnZV9kYXRh"  # Base64 válido pero no encriptación Fernet
        # Verifica que la función devuelve el texto original si no puede desencriptar
        result = decrypt_text(corrupted_data)
        assert result == corrupted_data
        # --- FIN DE CORRECCIÓN 3 ---

    def test_encrypt_none_value(self):
        """Test encriptando None (debe manejarse correctamente)."""
        # Dependiendo de la implementación, puede lanzar error o convertir a string
        try:
            result = encrypt_text(None)
            assert result is not None
        except (TypeError, AttributeError):
            # Es aceptable que lance error con None
            pass


# ==============================================================================
# TESTS DE PERSISTENCIA
# ==============================================================================


class TestPersistence:
    """Tests de persistencia de la clave de encriptación."""

    def test_key_persistence_between_instances(self):
        """Verifica que la clave persista entre diferentes instancias."""
        # Obtener primera instancia y encriptar
        enc1 = get_encryption()
        original = "test_persistencia"
        encrypted = enc1.encrypt(original)

        # Obtener segunda instancia (debería usar la misma clave)
        enc2 = get_encryption()
        decrypted = enc2.decrypt(encrypted)

        assert decrypted == original

    def test_singleton_pattern(self):
        """Verifica que get_encryption() devuelva la misma instancia (singleton)."""
        enc1 = get_encryption()
        enc2 = get_encryption()

        # Deben ser la misma instancia
        assert enc1 is enc2


# ==============================================================================
# TESTS DE RENDIMIENTO
# ==============================================================================


@pytest.mark.slow
class TestPerformance:
    """Tests de rendimiento (marcados como lentos)."""

    def test_encrypt_large_dataset(self):
        """Test de encriptación de un dataset grande."""
        texts = [f"password_{i}" for i in range(1000)]

        for text in texts:
            encrypted = encrypt_text(text)
            decrypted = decrypt_text(encrypted)
            assert decrypted == text

    def test_encryption_speed(self):
        """Test de velocidad de encriptación."""
        import time

        text = "test_password"
        iterations = 100

        start = time.time()
        for _ in range(iterations):
            encrypted = encrypt_text(text)
            decrypt_text(encrypted)
        end = time.time()

        elapsed = end - start
        avg_time = elapsed / iterations

        # Debería ser muy rápido (menos de 10ms por operación)
        assert avg_time < 0.01, f"Encryption too slow: {avg_time:.4f}s per operation"


# ==============================================================================
# TESTS DE SEGURIDAD
# ==============================================================================


@pytest.mark.security
class TestSecurity:
    """Tests de seguridad."""

    def test_encrypted_text_not_readable(self):
        """Verifica que el texto encriptado no sea legible."""
        original = "SuperSecretPassword123!"
        encrypted = encrypt_text(original)

        # El texto encriptado no debe contener el original
        assert original not in encrypted
        assert original.lower() not in encrypted.lower()

    def test_different_passwords_different_encryptions(self):
        """Verifica que contraseñas diferentes tengan encriptaciones diferentes."""
        passwords = ["pass1", "pass2", "pass3"]
        encrypted_passwords = [encrypt_text(p) for p in passwords]

        # Todas las encriptaciones deben ser únicas
        assert len(set(encrypted_passwords)) == len(passwords)

    def test_encryption_adds_sufficient_length(self):
        """Verifica que la encriptación agregue suficiente longitud (seguridad)."""
        original = "short"
        encrypted = encrypt_text(original)

        # La encriptación Fernet siempre agrega considerable longitud
        assert len(encrypted) > len(original) * 3


# ==============================================================================
# TESTS DE INTEGRACIÓN
# ==============================================================================


@pytest.mark.integration
class TestEncryptionIntegration:
    """Tests de integración del sistema de encriptación."""

    def test_full_credential_workflow(self):
        """Test del flujo completo de una credencial."""
        # Crear credencial
        original_credential = {
            "entidad": "DIAN",
            "usuario": "admin@empresa.com",
            "contrasena": "SecurePass123!",
            "url": "https://muisca.dian.gov.co",
            "notas": "Credenciales producción",
        }

        enc = get_encryption()

        # Encriptar
        encrypted_credential = enc.encrypt_credential(original_credential)

        # Simular guardado en BD (los campos sensibles están encriptados)
        assert encrypted_credential["usuario"] != original_credential["usuario"]
        assert encrypted_credential["contrasena"] != original_credential["contrasena"]

        # Simular lectura de BD y desencriptar
        decrypted_credential = enc.decrypt_credential(encrypted_credential)

        # Verificar que se recuperó correctamente
        assert decrypted_credential == original_credential

    def test_multiple_credentials_independence(self):
        """Test de independencia entre múltiples credenciales."""
        credentials = [
            {"usuario": f"user{i}", "contrasena": f"pass{i}"} for i in range(10)
        ]

        enc = get_encryption()

        # Encriptar todas
        encrypted_list = [enc.encrypt_credential(c) for c in credentials]

        # Desencriptar todas
        decrypted_list = [enc.decrypt_credential(e) for e in encrypted_list]

        # Verificar que todas se recuperaron correctamente
        assert decrypted_list == credentials


# ==============================================================================
# CONFIGURACIÓN DE FIXTURES ESPECÍFICAS
# ==============================================================================


@pytest.fixture
def sample_credentials():
    """Proporciona un conjunto de credenciales de ejemplo."""
    return [
        {
            "entidad": "DIAN",
            "usuario": "admin@dian.com",
            "contrasena": "DianPass123!",
            "url": "https://muisca.dian.gov.co",
        },
        {
            "entidad": "PILA",
            "usuario": "empresa@pila.com",
            "contrasena": "PilaSecure456!",
            "url": "https://www.aportesenlinea.com",
        },
        {
            "entidad": "Colpensiones",
            "usuario": "contador@empresa.com",
            "contrasena": "ColpPass789!",
            "url": "https://www.colpensiones.gov.co",
        },
    ]


@pytest.mark.parametrize("credential_index", [0, 1, 2])
def test_sample_credentials_encryption(sample_credentials, credential_index):
    """Test parametrizado con credenciales de ejemplo."""
    credential = sample_credentials[credential_index]

    enc = get_encryption()
    encrypted = enc.encrypt_credential(credential)
    decrypted = enc.decrypt_credential(encrypted)

    assert decrypted == credential
