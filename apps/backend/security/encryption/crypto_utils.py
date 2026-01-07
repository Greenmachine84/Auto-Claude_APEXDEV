"""Cryptographic utility functions.

World-Class Standards:
- AES-256-GCM encryption (FIPS 197)
- PBKDF2-SHA256 key derivation (600,000 iterations)
- Cryptographically secure random generation
- Constant-time comparison for security
"""
import os
import secrets
import hashlib
from typing import Optional, Tuple

# Cryptography library import with graceful fallback
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


# Constants
AES_KEY_SIZE = 32  # 256 bits
AES_NONCE_SIZE = 12  # 96 bits (GCM standard)
AES_TAG_SIZE = 16  # 128 bits authentication tag
PBKDF2_ITERATIONS = 600_000  # OWASP 2023 recommendation
SALT_SIZE = 32  # 256 bits


def secure_random_bytes(length: int) -> bytes:
    """Generate cryptographically secure random bytes.
    
    Args:
        length: Number of bytes to generate
        
    Returns:
        Random bytes
    """
    return secrets.token_bytes(length)


def generate_salt(length: int = SALT_SIZE) -> bytes:
    """Generate a random salt for key derivation.
    
    Args:
        length: Salt length in bytes
        
    Returns:
        Random salt bytes
    """
    return secure_random_bytes(length)


def derive_key(
    password: bytes,
    salt: bytes,
    iterations: int = PBKDF2_ITERATIONS,
    key_length: int = AES_KEY_SIZE,
) -> bytes:
    """Derive an encryption key from a password using PBKDF2-SHA256.
    
    Uses OWASP 2023 recommended 600,000 iterations for strong
    password-based key derivation.
    
    Args:
        password: Password bytes
        salt: Random salt
        iterations: PBKDF2 iterations (default: 600,000)
        key_length: Output key length
        
    Returns:
        Derived key bytes
    """
    if CRYPTO_AVAILABLE:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=key_length,
            salt=salt,
            iterations=iterations,
        )
        return kdf.derive(password)
    else:
        # Fallback using hashlib
        return hashlib.pbkdf2_hmac(
            "sha256",
            password,
            salt,
            iterations,
            dklen=key_length,
        )


def encrypt_aes_gcm(
    plaintext: bytes,
    key: bytes,
    associated_data: Optional[bytes] = None,
) -> bytes:
    """Encrypt data using AES-256-GCM.
    
    Format: nonce (12 bytes) + ciphertext + tag (16 bytes)
    
    Args:
        plaintext: Data to encrypt
        key: 256-bit encryption key
        associated_data: Optional authenticated data
        
    Returns:
        Encrypted data with nonce prepended
    """
    if len(key) != AES_KEY_SIZE:
        raise ValueError(f"Key must be {AES_KEY_SIZE} bytes")
    
    # Generate random nonce
    nonce = secure_random_bytes(AES_NONCE_SIZE)
    
    if CRYPTO_AVAILABLE:
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)
        return nonce + ciphertext
    else:
        # Fallback: simple XOR-based encryption (NOT secure for production)
        # This is a placeholder - real deployment must use cryptography library
        import warnings
        warnings.warn(
            "Using fallback encryption - install 'cryptography' for production use",
            RuntimeWarning,
        )
        return _fallback_encrypt(plaintext, key, nonce)


def decrypt_aes_gcm(
    ciphertext: bytes,
    key: bytes,
    associated_data: Optional[bytes] = None,
) -> bytes:
    """Decrypt data encrypted with AES-256-GCM.
    
    Args:
        ciphertext: Encrypted data (nonce + ciphertext + tag)
        key: 256-bit encryption key
        associated_data: Optional authenticated data
        
    Returns:
        Decrypted plaintext
        
    Raises:
        ValueError: If decryption fails (authentication error)
    """
    if len(key) != AES_KEY_SIZE:
        raise ValueError(f"Key must be {AES_KEY_SIZE} bytes")
    
    if len(ciphertext) < AES_NONCE_SIZE + AES_TAG_SIZE:
        raise ValueError("Ciphertext too short")
    
    # Extract nonce
    nonce = ciphertext[:AES_NONCE_SIZE]
    actual_ciphertext = ciphertext[AES_NONCE_SIZE:]
    
    if CRYPTO_AVAILABLE:
        aesgcm = AESGCM(key)
        try:
            return aesgcm.decrypt(nonce, actual_ciphertext, associated_data)
        except Exception as e:
            raise ValueError("Decryption failed - authentication error") from e
    else:
        return _fallback_decrypt(actual_ciphertext, key, nonce)


def _fallback_encrypt(plaintext: bytes, key: bytes, nonce: bytes) -> bytes:
    """Fallback encryption (NOT SECURE - for testing only)."""
    # Simple XOR with key stream - DO NOT USE IN PRODUCTION
    key_stream = hashlib.sha256(key + nonce).digest()
    
    result = []
    for i, byte in enumerate(plaintext):
        key_byte = key_stream[i % len(key_stream)]
        result.append(byte ^ key_byte)
    
    # Add simple "tag" (not cryptographic)
    tag = hashlib.sha256(bytes(result) + key).digest()[:AES_TAG_SIZE]
    
    return nonce + bytes(result) + tag


def _fallback_decrypt(ciphertext: bytes, key: bytes, nonce: bytes) -> bytes:
    """Fallback decryption (NOT SECURE - for testing only)."""
    # Verify tag
    actual_ciphertext = ciphertext[:-AES_TAG_SIZE]
    stored_tag = ciphertext[-AES_TAG_SIZE:]
    computed_tag = hashlib.sha256(actual_ciphertext + key).digest()[:AES_TAG_SIZE]
    
    if not secrets.compare_digest(stored_tag, computed_tag):
        raise ValueError("Decryption failed - authentication error")
    
    # XOR decrypt
    key_stream = hashlib.sha256(key + nonce).digest()
    
    result = []
    for i, byte in enumerate(actual_ciphertext):
        key_byte = key_stream[i % len(key_stream)]
        result.append(byte ^ key_byte)
    
    return bytes(result)


def secure_compare(a: bytes, b: bytes) -> bool:
    """Constant-time comparison to prevent timing attacks.
    
    Args:
        a: First bytes sequence
        b: Second bytes sequence
        
    Returns:
        True if equal, False otherwise
    """
    return secrets.compare_digest(a, b)


def generate_key() -> bytes:
    """Generate a random AES-256 key.
    
    Returns:
        Random 256-bit key
    """
    return secure_random_bytes(AES_KEY_SIZE)


def hash_data(data: bytes, algorithm: str = "sha256") -> bytes:
    """Hash data using specified algorithm.
    
    Args:
        data: Data to hash
        algorithm: Hash algorithm (sha256, sha512, sha3_256)
        
    Returns:
        Hash digest
    """
    hasher = hashlib.new(algorithm)
    hasher.update(data)
    return hasher.digest()


def hmac_sign(key: bytes, message: bytes) -> bytes:
    """Create HMAC-SHA256 signature.
    
    Args:
        key: HMAC key
        message: Message to sign
        
    Returns:
        HMAC signature
    """
    import hmac
    return hmac.new(key, message, hashlib.sha256).digest()


def hmac_verify(key: bytes, message: bytes, signature: bytes) -> bool:
    """Verify HMAC-SHA256 signature.
    
    Args:
        key: HMAC key
        message: Original message
        signature: Signature to verify
        
    Returns:
        True if signature is valid
    """
    expected = hmac_sign(key, message)
    return secure_compare(expected, signature)
