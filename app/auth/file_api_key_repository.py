# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

import os
from typing import Optional, Dict, Any
import json

from auth.api_key_repository import ApiKeyRepository
from logger import HaivenLogger
from config_service import ConfigService


class FileApiKeyRepository(ApiKeyRepository):
    """File-based implementation of API key storage."""

    def __init__(self, config: ConfigService):
        if not hasattr(config, "load_api_key_repository_file_path"):
            raise ValueError(
                "FileApiKeyRepository requires a ConfigService (or compatible) object."
            )
        self.config_path = config.load_api_key_repository_file_path()
        self._load_keys()

    def _load_keys(self):
        """Load API keys from configuration file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    data = json.load(f)
                    self.keys = data.get("keys", {})
            else:
                self.keys = {}
                # Create default directory structure
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                self._save_keys()
        except Exception as e:
            logger = HaivenLogger.get()
            if logger:
                logger.error(f"Failed to load API keys: {e}")
            self.keys = {}

    def _save_keys(self):
        """Save API keys to configuration file."""
        try:
            with open(self.config_path, "w") as f:
                json.dump({"keys": self.keys}, f, indent=2)
        except Exception as e:
            logger = HaivenLogger.get()
            if logger:
                logger.error(f"Failed to save API keys: {e}")

    def save_key(self, key_hash: str, key_data: Dict[str, Any]) -> None:
        """Save an API key with its metadata."""
        self.keys[key_hash] = key_data
        self._save_keys()
        logger = HaivenLogger.get()
        if logger:
            logger.info(
                f"Saved API key '{key_data.get('name', 'unnamed')}' for user (hash) {key_data.get('user_id', 'unknown')}"
            )

    def find_by_hash(self, key_hash: str) -> Optional[Dict[str, Any]]:
        """Find an API key by its hash."""
        return self.keys.get(key_hash)

    def update_key(self, key_hash: str, key_data: Dict[str, Any]) -> bool:
        """Update an API key's metadata."""
        if key_hash in self.keys:
            self.keys[key_hash] = key_data
            self._save_keys()
            return True
        return False

    def delete_key(self, key_hash: str) -> bool:
        """Delete an API key by its hash."""
        if key_hash in self.keys:
            del self.keys[key_hash]
            self._save_keys()
            return True
        return False

    def find_all(self) -> Dict[str, Dict[str, Any]]:
        """Find all API keys with their metadata."""
        return self.keys.copy()

    def find_by_user_id(self, user_id: str) -> Dict[str, Dict[str, Any]]:
        """Find all API keys for a specific user."""
        return {
            key_hash: info
            for key_hash, info in self.keys.items()
            if info["user_id"] == user_id
        }
