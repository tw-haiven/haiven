# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class ApiKeyRepository(ABC):
    """Abstract interface for API key storage operations."""

    @abstractmethod
    def save_key(self, key_hash: str, key_data: Dict[str, Any]) -> None:
        """Save an API key with its metadata."""
        pass

    @abstractmethod
    def find_by_hash(self, key_hash: str) -> Optional[Dict[str, Any]]:
        """Find an API key by its hash."""
        pass

    @abstractmethod
    def update_key(self, key_hash: str, key_data: Dict[str, Any]) -> bool:
        """Update an API key's metadata. Returns True if successful."""
        pass

    @abstractmethod
    def delete_key(self, key_hash: str) -> bool:
        """Delete an API key by its hash. Returns True if successful."""
        pass

    @abstractmethod
    def find_all(self) -> Dict[str, Dict[str, Any]]:
        """Find all API keys with their metadata."""
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> Dict[str, Dict[str, Any]]:
        """Find all API keys for a specific user."""
        pass
