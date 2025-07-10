# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

import hashlib
import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import secrets
import json

from auth.api_key_repository import ApiKeyRepository
from logger import HaivenLogger
from config_service import ConfigService


class FileApiKeyRepository(ApiKeyRepository):
    """File-based implementation of API key management."""

    def __init__(self, config: str | ConfigService = "app/config/api_keys.json"):
        if isinstance(config, ConfigService):
            self.config_path = config.load_api_key_repository_file_path()
        else:
            self.config_path = config
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

    def generate_api_key(
        self, name: str, user_email: str, expires_days: int = 365
    ) -> str:
        """Generate a new API key."""
        # Generate a secure random key
        key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(key.encode()).hexdigest()

        # Store key metadata
        self.keys[key_hash] = {
            "name": name,
            "user_email": user_email,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (
                datetime.utcnow() + timedelta(days=expires_days)
            ).isoformat(),
            "last_used": None,
            "usage_count": 0,
        }

        self._save_keys()
        logger = HaivenLogger.get()
        if logger:
            logger.info(f"Generated API key '{name}' for user {user_email}")
        return key

    def validate_key(self, key: str) -> Optional[Dict[str, Any]]:
        """Validate an API key and return user information."""
        if not key:
            return None

        key_hash = hashlib.sha256(key.encode()).hexdigest()
        key_info = self.keys.get(key_hash)

        if not key_info:
            return None

        # Check if key is expired
        expires_at = datetime.fromisoformat(key_info["expires_at"])
        if datetime.utcnow() > expires_at:
            logger = HaivenLogger.get()
            if logger:
                logger.warn(f"Expired API key used: {key_info['name']}")
            return None

        # Update last used timestamp and usage count
        key_info["last_used"] = datetime.utcnow().isoformat()
        key_info["usage_count"] += 1
        self._save_keys()

        return {
            "name": key_info["name"],
            "user_email": key_info["user_email"],
            "key_hash": key_hash,
        }

    def revoke_key(self, key_hash: str) -> bool:
        """Revoke an API key."""
        if key_hash in self.keys:
            del self.keys[key_hash]
            self._save_keys()
            return True
        return False

    def list_keys(self) -> Dict[str, Any]:
        """List all API keys (without the actual key values)."""
        return {
            key_hash: {
                "name": info["name"],
                "user_email": info["user_email"],
                "created_at": info["created_at"],
                "expires_at": info["expires_at"],
                "last_used": info["last_used"],
                "usage_count": info["usage_count"],
            }
            for key_hash, info in self.keys.items()
        }

    def list_keys_for_user(self, user_email: str) -> Dict[str, Any]:
        """List API keys for a specific user."""
        all_keys = self.list_keys()
        return {
            key_hash: info
            for key_hash, info in all_keys.items()
            if info["user_email"] == user_email
        }
