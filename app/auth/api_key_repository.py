# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class ApiKeyRepository(ABC):
    """Abstract interface for API key management operations."""

    @abstractmethod
    def generate_api_key(
        self, name: str, user_email: str, expires_days: int = 365
    ) -> str:
        """Generate a new API key and return the key string."""
        pass

    @abstractmethod
    def validate_key(self, key: str) -> Optional[Dict[str, Any]]:
        """Validate an API key and return user information if valid."""
        pass

    @abstractmethod
    def revoke_key(self, key_hash: str) -> bool:
        """Revoke an API key by its hash. Returns True if successful."""
        pass

    @abstractmethod
    def list_keys(self) -> Dict[str, Any]:
        """List all API keys (without the actual key values)."""
        pass

    @abstractmethod
    def list_keys_for_user(self, user_email: str) -> Dict[str, Any]:
        """List API keys for a specific user."""
        pass
