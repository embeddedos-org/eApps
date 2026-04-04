"""AES-256 encryption for eDB data at rest.

Provides field-level encryption for sensitive data using AES-256-GCM.
"""
from __future__ import annotations

import base64
import hashlib
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptionManager:
    """AES-256-GCM encryption manager for data at rest."""

    NONCE_SIZE = 12
    KEY_SIZE = 32  # 256 bits
    SALT_SIZE = 16

    def __init__(self, encryption_key: str | bytes | None = None) -> None:
        if encryption_key is None:
            self._key = AESGCM.generate_key(bit_length=256)
        elif isinstance(encryption_key, str):
            self._password = encryption_key
            self._key = self._derive_key(encryption_key)
        else:
            self._key = encryption_key
        self._aes = AESGCM(self._key)

    @property
    def key(self) -> bytes:
        """Return the raw encryption key."""
        return self._key

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string and return base64-encoded ciphertext."""
        nonce = os.urandom(self.NONCE_SIZE)
        ciphertext = self._aes.encrypt(nonce, plaintext.encode("utf-8"), None)
        combined = self._salt + nonce + ciphertext if hasattr(self, "_salt") else nonce + ciphertext
        return base64.b64encode(combined).decode("utf-8")

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt base64-encoded ciphertext and return plaintext."""
        combined = base64.b64decode(encrypted_data)
        if hasattr(self, "_password"):
            salt = combined[: self.SALT_SIZE]
            nonce = combined[self.SALT_SIZE : self.SALT_SIZE + self.NONCE_SIZE]
            ciphertext = combined[self.SALT_SIZE + self.NONCE_SIZE :]
            key = self._derive_key_with_salt(self._password, salt)
            aes = AESGCM(key)
            plaintext = aes.decrypt(nonce, ciphertext, None)
        else:
            nonce = combined[: self.NONCE_SIZE]
            ciphertext = combined[self.NONCE_SIZE :]
            plaintext = self._aes.decrypt(nonce, ciphertext, None)
        return plaintext.decode("utf-8")

    def encrypt_dict_fields(self, data: dict, fields: list[str]) -> dict:
        """Encrypt specific fields in a dictionary."""
        result = dict(data)
        for field in fields:
            if field in result and isinstance(result[field], str):
                result[field] = self.encrypt(result[field])
        return result

    def decrypt_dict_fields(self, data: dict, fields: list[str]) -> dict:
        """Decrypt specific fields in a dictionary."""
        import logging

        logger = logging.getLogger("edb.security.encryption")
        result = dict(data)
        for field in fields:
            if field in result and isinstance(result[field], str):
                try:
                    result[field] = self.decrypt(result[field])
                except Exception as e:
                    logger.warning("Failed to decrypt field '%s': %s", field, e)
        return result

    def _derive_key(self, password: str) -> bytes:
        """Derive an AES-256 key from a password using deterministic salt."""
        salt = hashlib.sha256(password.encode("utf-8")).digest()[: self.SALT_SIZE]
        self._salt = salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_SIZE,
            salt=salt,
            iterations=480000,
        )
        return kdf.derive(password.encode("utf-8"))

    def _derive_key_with_salt(self, password: str, salt: bytes) -> bytes:
        """Derive key using a specific salt (for decryption with stored salt)."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_SIZE,
            salt=salt,
            iterations=480000,
        )
        return kdf.derive(password.encode("utf-8"))
