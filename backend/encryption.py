"""Encryption utilities for securing API keys at rest.

Uses Fernet symmetric encryption from the cryptography library.
The encryption key is derived from the ENCRYPTION_KEY environment variable.
"""
import os
import base64
import hashlib
from cryptography.fernet import Fernet


def _get_fernet() -> Fernet:
    """
    Derive a Fernet key from the ENCRYPTION_KEY env var.
    Falls back to a deterministic key derived from JWT_SECRET.
    """
    raw_key = os.getenv(
        "ENCRYPTION_KEY",
        os.getenv("JWT_SECRET", "promptforge-dev-secret-change-in-production"),
    )
    # Fernet requires a 32-byte url-safe base64 encoded key.
    # Derive one from the raw secret using SHA-256.
    digest = hashlib.sha256(raw_key.encode()).digest()
    key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


def encrypt_value(plaintext: str) -> str:
    """Encrypt a plaintext string and return the ciphertext as a UTF-8 string."""
    if not plaintext:
        return ""
    f = _get_fernet()
    return f.encrypt(plaintext.encode()).decode()


def decrypt_value(ciphertext: str) -> str:
    """Decrypt a ciphertext string and return the original plaintext."""
    if not ciphertext:
        return ""
    f = _get_fernet()
    return f.decrypt(ciphertext.encode()).decode()


def mask_key(key: str) -> str:
    """Return a masked version of an API key for safe display.
    Shows first 4 and last 4 characters only.
    """
    if not key or len(key) <= 12:
        return "•" * max(len(key), 8)
    return key[:4] + "•" * (len(key) - 8) + key[-4:]
