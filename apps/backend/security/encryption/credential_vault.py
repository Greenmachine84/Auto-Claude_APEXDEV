"""Secure credential vault for all 8 LLM providers.

World-Class Standards:
- AES-256-GCM encryption (FIPS 197 compliant)
- Provider-specific credential schemas
- Secure storage with integrity verification
- Key rotation support

Supported Providers:
- copilot (GitHub Copilot)
- openrouter
- ollama (local)
- lmstudio (local)
- gemini (Google)
- openai
- anthropic
- azure (Azure OpenAI)
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from ..models import PROVIDER_CREDENTIALS, SUPPORTED_PROVIDERS, EncryptedCredential
from .crypto_utils import decrypt_aes_gcm, encrypt_aes_gcm
from .key_manager import KeyManager


class CredentialVault:
    """Secure vault for LLM provider credentials.

    Provides encrypted storage for API keys and credentials
    for all 8 supported LLM providers.

    Example:
        vault = CredentialVault()
        await vault.initialize()

        # Store OpenAI credentials
        await vault.store_credential("openai", {"api_key": "sk-..."})

        # Retrieve credentials
        cred = await vault.get_credential("openai")
    """

    def __init__(
        self,
        vault_path: Path | None = None,
        key_manager: KeyManager | None = None,
    ):
        """Initialize vault.

        Args:
            vault_path: Path to vault storage directory
            key_manager: Optional key manager instance
        """
        self._vault_path = vault_path or Path.home() / ".autoclaudedev" / "vault"
        self._key_manager = key_manager or KeyManager()
        self._credentials: dict[str, EncryptedCredential] = {}
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the vault and key manager."""
        if self._initialized:
            return

        # Ensure vault directory exists
        self._vault_path.mkdir(parents=True, exist_ok=True)

        # Set secure permissions (owner only)
        if os.name != "nt":  # Unix-like
            os.chmod(self._vault_path, 0o700)

        # Initialize key manager
        await self._key_manager.initialize()

        # Load existing credentials
        await self._load_credentials()

        self._initialized = True

    async def _load_credentials(self) -> None:
        """Load encrypted credentials from storage."""
        creds_file = self._vault_path / "credentials.enc"

        if not creds_file.exists():
            return

        try:
            encrypted_data = creds_file.read_bytes()
            master_key = await self._key_manager.get_master_key()

            # Decrypt credential store
            decrypted = decrypt_aes_gcm(encrypted_data, master_key)
            creds_dict = json.loads(decrypted.decode("utf-8"))

            for provider, cred_data in creds_dict.items():
                self._credentials[provider] = EncryptedCredential(
                    provider=cred_data["provider"],
                    encrypted_data=bytes.fromhex(cred_data["encrypted_data"]),
                    nonce=bytes.fromhex(cred_data["nonce"]),
                    created_at=cred_data["created_at"],
                    last_rotated=cred_data.get("last_rotated"),
                    key_id=cred_data.get("key_id", "master"),
                )
        except Exception:
            # Failed to load - vault may be corrupt or key changed
            self._credentials = {}

    async def _save_credentials(self) -> None:
        """Save encrypted credentials to storage."""
        # Serialize credentials
        creds_dict = {
            provider: {
                "provider": cred.provider,
                "encrypted_data": cred.encrypted_data.hex(),
                "nonce": cred.nonce.hex(),
                "created_at": cred.created_at,
                "last_rotated": cred.last_rotated,
                "key_id": cred.key_id,
            }
            for provider, cred in self._credentials.items()
        }

        # Encrypt and save
        master_key = await self._key_manager.get_master_key()
        json_data = json.dumps(creds_dict).encode("utf-8")
        encrypted = encrypt_aes_gcm(json_data, master_key)

        creds_file = self._vault_path / "credentials.enc"
        creds_file.write_bytes(encrypted)

        # Secure file permissions
        if os.name != "nt":
            os.chmod(creds_file, 0o600)

    def _validate_provider(self, provider: str) -> None:
        """Validate provider name."""
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unsupported provider: {provider}. "
                f"Supported: {', '.join(SUPPORTED_PROVIDERS)}"
            )

    def _validate_credentials(
        self,
        provider: str,
        credentials: dict[str, Any],
    ) -> None:
        """Validate credential fields for provider."""
        required_fields = PROVIDER_CREDENTIALS.get(provider, [])
        missing = [f for f in required_fields if f not in credentials]

        if missing:
            raise ValueError(
                f"Missing required fields for {provider}: {', '.join(missing)}"
            )

    async def store_credential(
        self,
        provider: str,
        credentials: dict[str, Any],
        validate: bool = True,
    ) -> EncryptedCredential:
        """Store encrypted credentials for a provider.

        Args:
            provider: Provider name (e.g., 'openai', 'anthropic')
            credentials: Credential dictionary
            validate: Whether to validate fields

        Returns:
            Encrypted credential object
        """
        if not self._initialized:
            await self.initialize()

        self._validate_provider(provider)

        if validate:
            self._validate_credentials(provider, credentials)

        # Encrypt credentials
        master_key = await self._key_manager.get_master_key()
        json_data = json.dumps(credentials).encode("utf-8")
        encrypted = encrypt_aes_gcm(json_data, master_key)

        # Extract nonce (first 12 bytes of encrypted data)
        nonce = encrypted[:12]

        # Create credential record
        now = datetime.utcnow().isoformat()
        cred = EncryptedCredential(
            provider=provider,
            encrypted_data=encrypted,
            nonce=nonce,
            created_at=now,
            last_rotated=now,
            key_id="master",
        )

        self._credentials[provider] = cred
        await self._save_credentials()

        return cred

    async def get_credential(self, provider: str) -> dict[str, Any] | None:
        """Retrieve decrypted credentials for a provider.

        Args:
            provider: Provider name

        Returns:
            Decrypted credential dictionary or None
        """
        if not self._initialized:
            await self.initialize()

        self._validate_provider(provider)

        cred = self._credentials.get(provider)
        if not cred:
            return None

        # Decrypt
        master_key = await self._key_manager.get_master_key()
        decrypted = decrypt_aes_gcm(cred.encrypted_data, master_key)

        return json.loads(decrypted.decode("utf-8"))

    async def delete_credential(self, provider: str) -> bool:
        """Delete credentials for a provider.

        Args:
            provider: Provider name

        Returns:
            True if deleted, False if not found
        """
        if not self._initialized:
            await self.initialize()

        self._validate_provider(provider)

        if provider not in self._credentials:
            return False

        del self._credentials[provider]
        await self._save_credentials()

        return True

    async def list_providers(self) -> list[str]:
        """List providers with stored credentials."""
        if not self._initialized:
            await self.initialize()

        return list(self._credentials.keys())

    async def has_credential(self, provider: str) -> bool:
        """Check if credentials exist for a provider."""
        if not self._initialized:
            await self.initialize()

        return provider in self._credentials

    async def rotate_credentials(
        self,
        provider: str,
        new_credentials: dict[str, Any],
    ) -> EncryptedCredential:
        """Rotate credentials for a provider.

        Stores new credentials and updates rotation timestamp.

        Args:
            provider: Provider name
            new_credentials: New credential values

        Returns:
            Updated encrypted credential
        """
        old_cred = self._credentials.get(provider)
        new_cred = await self.store_credential(provider, new_credentials)

        if old_cred:
            new_cred.created_at = old_cred.created_at

        return new_cred

    async def get_credential_metadata(self, provider: str) -> dict[str, Any] | None:
        """Get credential metadata without decrypting.

        Args:
            provider: Provider name

        Returns:
            Metadata dict or None
        """
        if not self._initialized:
            await self.initialize()

        cred = self._credentials.get(provider)
        if not cred:
            return None

        return {
            "provider": cred.provider,
            "created_at": cred.created_at,
            "last_rotated": cred.last_rotated,
            "key_id": cred.key_id,
        }

    async def export_vault(
        self,
        export_key: bytes,
        include_credentials: bool = False,
    ) -> bytes:
        """Export vault for backup.

        Args:
            export_key: Key for export encryption
            include_credentials: Whether to include actual credentials

        Returns:
            Encrypted export data
        """
        if not self._initialized:
            await self.initialize()

        export_data = {
            "version": "1.0",
            "exported_at": datetime.utcnow().isoformat(),
            "providers": list(self._credentials.keys()),
        }

        if include_credentials:
            export_data["credentials"] = {
                provider: {
                    "encrypted_data": cred.encrypted_data.hex(),
                    "nonce": cred.nonce.hex(),
                    "created_at": cred.created_at,
                    "last_rotated": cred.last_rotated,
                }
                for provider, cred in self._credentials.items()
            }

        json_data = json.dumps(export_data).encode("utf-8")
        return encrypt_aes_gcm(json_data, export_key)
