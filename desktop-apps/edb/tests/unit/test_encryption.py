"""Unit tests for AES-256 encryption."""

from edb.security.encryption import EncryptionManager


def test_encrypt_decrypt():
    mgr = EncryptionManager("test-password")
    plaintext = "Hello, eDB!"

    encrypted = mgr.encrypt(plaintext)
    assert encrypted != plaintext

    decrypted = mgr.decrypt(encrypted)
    assert decrypted == plaintext


def test_different_encryptions():
    mgr = EncryptionManager("test-password")

    enc1 = mgr.encrypt("same text")
    enc2 = mgr.encrypt("same text")
    assert enc1 != enc2  # Different nonces = different ciphertext


def test_encrypt_dict_fields():
    mgr = EncryptionManager("test-password")
    data = {"name": "Alice", "ssn": "123-45-6789", "age": 30}

    encrypted = mgr.encrypt_dict_fields(data, ["ssn"])
    assert encrypted["name"] == "Alice"
    assert encrypted["ssn"] != "123-45-6789"
    assert encrypted["age"] == 30

    decrypted = mgr.decrypt_dict_fields(encrypted, ["ssn"])
    assert decrypted["ssn"] == "123-45-6789"


def test_auto_generated_key():
    mgr = EncryptionManager()
    encrypted = mgr.encrypt("test")
    decrypted = mgr.decrypt(encrypted)
    assert decrypted == "test"


def test_key_from_bytes():
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    key = AESGCM.generate_key(bit_length=256)
    mgr = EncryptionManager(key)

    encrypted = mgr.encrypt("test")
    decrypted = mgr.decrypt(encrypted)
    assert decrypted == "test"
