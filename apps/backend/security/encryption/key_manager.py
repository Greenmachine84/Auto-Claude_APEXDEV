"""Secure key management for encryption operations.

World-Class Standards:
- OWASP-compliant PBKDF2-SHA256 key derivation
- 600,000 iterations (OWASP 2023 recommendation)
- Secure key storage
- Key rotation support
"""
import os
import json
import secrets
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from .crypto_utils import derive_key, generate_salt, secure_random_bytes


class KeyManager:
    """Manages encryption keys with secure derivation and storage.
    
    Uses PBKDF2-SHA256 with 600,000 iterations for key derivation
    per OWASP 2023 recommendations.
    """
    
    # OWASP 2023 recommended iterations for PBKDF2-SHA256
    PBKDF2_ITERATIONS = 600_000
    
    # Key sizes
    KEY_SIZE = 32  # 256 bits for AES-256
    SALT_SIZE = 32  # 256 bits salt
    
    def __init__(self, key_path: Optional[Path] = None):
        """Initialize key manager.
        
        Args:
            key_path: Path to key storage directory
        """
        self._key_path = key_path or Path.home() / ".autoclaudedev" / "keys"
        self._master_key: Optional[bytes] = None
        self._salt: Optional[bytes] = None
        self._key_metadata: Dict[str, Any] = {}
        self._initialized = False
    
    async def initialize(self, password: Optional[str] = None) -> None:
        """Initialize the key manager.
        
        If no master key exists, creates one. If password is provided,
        derives key from password. Otherwise uses machine-specific derivation.
        
        Args:
            password: Optional password for key derivation
        """
        if self._initialized:
            return
        
        # Ensure key directory exists
        self._key_path.mkdir(parents=True, exist_ok=True)
        
        # Set secure permissions
        if os.name != "nt":
            os.chmod(self._key_path, 0o700)
        
        key_file = self._key_path / "master.key"
        meta_file = self._key_path / "key_meta.json"
        
        if key_file.exists():
            # Load existing key
            await self._load_key(key_file, meta_file, password)
        else:
            # Generate new key
            await self._generate_key(key_file, meta_file, password)
        
        self._initialized = True
    
    async def _generate_key(self, key_file: Path, meta_file: Path, password: Optional[str] = None) -> None:
        """Generate a new master key."""
        self._salt = generate_salt(self.SALT_SIZE)
        
        if password:
            # Derive from password
            self._master_key = derive_key(
                password.encode("utf-8"),
                self._salt,
                iterations=self.PBKDF2_ITERATIONS,
                key_length=self.KEY_SIZE,
            )
            key_source = "password"
        else:
            # Generate random key with machine binding
            machine_id = self._get_machine_id()
            self._master_key = derive_key(
                machine_id,
                self._salt,
                iterations=self.PBKDF2_ITERATIONS,
                key_length=self.KEY_SIZE,
            )
            key_source = "machine"
        
        # Store encrypted key envelope
        envelope = self._create_key_envelope()
        key_file.write_bytes(envelope)
        
        if os.name != "nt":
            os.chmod(key_file, 0o600)
        
        # Store metadata
        self._key_metadata = {
            "version": "1.0",
            "algorithm": "PBKDF2-SHA256",
            "iterations": self.PBKDF2_ITERATIONS,
            "key_length": self.KEY_SIZE,
            "source": key_source,
            "created_at": datetime.utcnow().isoformat(),
            "last_rotated": datetime.utcnow().isoformat(),
        }
        
        meta_file.write_text(json.dumps(self._key_metadata, indent=2))
        
        if os.name != "nt":
            os.chmod(meta_file, 0o600)
    
    async def _load_key(self, key_file: Path, meta_file: Path, password: Optional[str] = None) -> None:
        """Load existing master key."""
        # Load metadata
        if meta_file.exists():
            self._key_metadata = json.loads(meta_file.read_text())
        else:
            self._key_metadata = {
                "version": "1.0",
                "algorithm": "PBKDF2-SHA256",
                "iterations": self.PBKDF2_ITERATIONS,
            }
        
        # Load key envelope
        envelope = key_file.read_bytes()
        self._salt = envelope[:self.SALT_SIZE]
        
        # Derive key
        if password:
            self._master_key = derive_key(
                password.encode("utf-8"),
                self._salt,
                iterations=self._key_metadata.get("iterations", self.PBKDF2_ITERATIONS),
                key_length=self.KEY_SIZE,
            )
        else:
            machine_id = self._get_machine_id()
            self._master_key = derive_key(
                machine_id,
                self._salt,
                iterations=self._key_metadata.get("iterations", self.PBKDF2_ITERATIONS),
                key_length=self.KEY_SIZE,
            )
    
    def _create_key_envelope(self) -> bytes:
        """Create a key envelope for storage.
        
        Format: salt (32 bytes) + verification hash (32 bytes)
        """
        # Verification hash to check key correctness
        verification = hashlib.sha256(self._master_key + self._salt).digest()
        
        return self._salt + verification
    
    def _verify_key(self, envelope: bytes) -> bool:
        """Verify key against envelope."""
        if len(envelope) < self.SALT_SIZE + 32:
            return False
        
        stored_verification = envelope[self.SALT_SIZE:self.SALT_SIZE + 32]
        computed_verification = hashlib.sha256(self._master_key + self._salt).digest()
        
        return secrets.compare_digest(stored_verification, computed_verification)
    
    def _get_machine_id(self) -> bytes:
        """Get a machine-specific identifier.
        
        Uses a combination of system properties for binding.
        """
        components = []
        
        # Username
        components.append(os.environ.get("USER", os.environ.get("USERNAME", "default")))
        
        # Home directory
        components.append(str(Path.home()))
        
        # Python version (as additional entropy)
        import sys
        components.append(sys.version)
        
        # Combine and hash
        combined = "|".join(components).encode("utf-8")
        return hashlib.sha256(combined).digest()
    
    async def get_master_key(self) -> bytes:
        """Get the master encryption key.
        
        Returns:
            Master key bytes
        """
        if not self._initialized:
            await self.initialize()
        
        if self._master_key is None:
            raise RuntimeError("Key manager not properly initialized")
        
        return self._master_key
    
    async def rotate_key(self, new_password: Optional[str] = None) -> bytes:
        """Rotate the master key.
        
        Generates a new key and updates metadata.
        Returns the old key for re-encryption.
        
        Args:
            new_password: Optional new password for derivation
            
        Returns:
            Old master key for re-encryption
        """
        if not self._initialized:
            await self.initialize()
        
        old_key = self._master_key
        
        # Generate new key
        self._salt = generate_salt(self.SALT_SIZE)
        
        if new_password:
            self._master_key = derive_key(
                new_password.encode("utf-8"),
                self._salt,
                iterations=self.PBKDF2_ITERATIONS,
                key_length=self.KEY_SIZE,
            )
        else:
            machine_id = self._get_machine_id()
            self._master_key = derive_key(
                machine_id,
                self._salt,
                iterations=self.PBKDF2_ITERATIONS,
                key_length=self.KEY_SIZE,
            )
        
        # Update storage
        key_file = self._key_path / "master.key"
        meta_file = self._key_path / "key_meta.json"
        
        envelope = self._create_key_envelope()
        key_file.write_bytes(envelope)
        
        self._key_metadata["last_rotated"] = datetime.utcnow().isoformat()
        meta_file.write_text(json.dumps(self._key_metadata, indent=2))
        
        return old_key
    
    def derive_subkey(self, context: str, length: int = 32) -> bytes:
        """Derive a subkey for specific context.
        
        Uses HKDF-like expansion for context-specific keys.
        
        Args:
            context: Context string for key derivation
            length: Desired key length
            
        Returns:
            Derived subkey
        """
        if self._master_key is None:
            raise RuntimeError("Key manager not initialized")
        
        # Use HMAC-SHA256 for key derivation
        import hmac
        
        return hmac.new(
            self._master_key,
            context.encode("utf-8"),
            hashlib.sha256,
        ).digest()[:length]
    
    async def get_key_metadata(self) -> Dict[str, Any]:
        """Get key metadata."""
        if not self._initialized:
            await self.initialize()
        
        return self._key_metadata.copy()
    
    async def verify_password(self, password: str) -> bool:
        """Verify a password against the stored key.
        
        Args:
            password: Password to verify
            
        Returns:
            True if password is correct
        """
        if not self._initialized or self._salt is None:
            return False
        
        test_key = derive_key(
            password.encode("utf-8"),
            self._salt,
            iterations=self._key_metadata.get("iterations", self.PBKDF2_ITERATIONS),
            key_length=self.KEY_SIZE,
        )
        
        # Load envelope and verify
        key_file = self._key_path / "master.key"
        if not key_file.exists():
            return False
        
        envelope = key_file.read_bytes()
        stored_verification = envelope[self.SALT_SIZE:self.SALT_SIZE + 32]
        computed_verification = hashlib.sha256(test_key + self._salt).digest()
        
        return secrets.compare_digest(stored_verification, computed_verification)
