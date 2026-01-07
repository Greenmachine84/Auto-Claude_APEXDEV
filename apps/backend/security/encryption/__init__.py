"""Encryption module for credential and data protection.

Provides enterprise-grade encryption for:
- All 8 LLM provider credentials
- AES-256-GCM encryption
- Secure key management
- OWASP-compliant key derivation
"""
from .credential_vault import CredentialVault
from .key_manager import KeyManager
from .crypto_utils import (
    encrypt_aes_gcm,
    decrypt_aes_gcm,
    derive_key,
    generate_salt,
    secure_random_bytes,
)

__all__ = [
    "CredentialVault",
    "KeyManager",
    "encrypt_aes_gcm",
    "decrypt_aes_gcm",
    "derive_key",
    "generate_salt",
    "secure_random_bytes",
]
