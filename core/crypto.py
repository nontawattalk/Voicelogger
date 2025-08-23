"""
Cryptographic utilities for Voicelogger.

Provides simple AES-GCM encryption and decryption helpers for protecting audio
files and transcripts. Keys are derived from a passphrase using PBKDF2-HMAC-SHA256.
"""

from __future__ import annotations

import os
import base64
import secrets
from typing import Tuple, Dict

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# Constants for key derivation and encryption
_SALT_SIZE = 16  # bytes
_NONCE_SIZE = 12  # bytes (recommended for AES-GCM)
_KDF_ITERATIONS = 200_000
_KEY_SIZE = 32  # 256-bit AES key


def _derive_key(passphrase: str, salt: bytes, iterations: int = _KDF_ITERATIONS) -> bytes:
    """Derive a symmetric key from a passphrase and salt using PBKDF2-HMAC-SHA256."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=_KEY_SIZE, salt=salt, iterations=iterations
    )
    return kdf.derive(passphrase.encode("utf-8"))


def encrypt_file_aes_gcm(src_path: str, dst_path: str, passphrase: str) -> Dict[str, str]:
    """Encrypt a file using AES-GCM and save the ciphertext to ``dst_path``.

    The encryption key is derived from ``passphrase`` and a random salt using
    PBKDF2-HMAC-SHA256. A new nonce is generated for each encryption. Metadata
    containing the salt and nonce (base64-encoded) is returned so that the file
    can be decrypted later.

    Args:
        src_path: Path to the plaintext file to encrypt.
        dst_path: Path to write the encrypted data.
        passphrase: Passphrase used to derive the encryption key.

    Returns:
        A dictionary with base64-encoded ``salt`` and ``nonce`` values.
    """
    salt = os.urandom(_SALT_SIZE)
    nonce = secrets.token_bytes(_NONCE_SIZE)
    key = _derive_key(passphrase, salt)

    aesgcm = AESGCM(key)
    with open(src_path, "rb") as f:
        plaintext = f.read()
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

    with open(dst_path, "wb") as f:
        f.write(ciphertext)

    meta = {
        "alg": "AES-256-GCM",
        "salt_b64": base64.b64encode(salt).decode(),
        "nonce_b64": base64.b64encode(nonce).decode(),
        "iterations": str(_KDF_ITERATIONS),
    }
    return meta


def decrypt_file_aes_gcm(
    enc_path: str,
    dst_path: str,
    passphrase: str,
    salt_b64: str,
    nonce_b64: str,
    iterations: int = _KDF_ITERATIONS,
) -> None:
    """Decrypt a file that was encrypted with :func:`encrypt_file_aes_gcm`.

    Args:
        enc_path: Path to the encrypted file.
        dst_path: Path to write the decrypted plaintext.
        passphrase: Passphrase used for key derivation.
        salt_b64: Base64-encoded salt from the encryption metadata.
        nonce_b64: Base64-encoded nonce from the encryption metadata.
        iterations: Number of KDF iterations (should match encryption).

    Raises:
        cryptography.exceptions.InvalidTag: If the passphrase or metadata is incorrect.
    """
    salt = base64.b64decode(salt_b64)
    nonce = base64.b64decode(nonce_b64)
    key = _derive_key(passphrase, salt, iterations=iterations)

    aesgcm = AESGCM(key)
    with open(enc_path, "rb") as f:
        ciphertext = f.read()
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)

    with open(dst_path, "wb") as f:
        f.write(plaintext)
