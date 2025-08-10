# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import hashlib
import secrets
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from fastapi import Request

from auth.api_key_repository import ApiKeyRepository
from config_service import ConfigService
from logger import HaivenLogger


# TODO Consider defining datamodel for the user-api-key
class ApiKeyAuthService:
    def __init__(self, config_service: ConfigService, repository: ApiKeyRepository):
        self.config_service = config_service
        self.repository = repository
        self.salt = config_service.load_api_key_pseudonymization_salt()

    def pseudonymize(self, data: str) -> str:
        """Pseudonymize data using a salt."""
        normalized = data.strip().lower()
        return hashlib.sha256((self.salt + normalized).encode()).hexdigest()

    def generate_api_key(
        self, name: str, user_id: str, expires_days: int = None
    ) -> str:
        """Generate a new API key and return the key string."""
        # Enforce max 30 days expiry
        if expires_days is None:
            expires_days = 30
        if expires_days > 30:
            raise ValueError("API key maximum expiry is 30 days")
        if expires_days < 1:
            raise ValueError("API key expiry must be at least 1 day")

        # Generate a secure random key
        key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(key.encode()).hexdigest()

        # Pseudonymize the user ID
        pseudonymized_user_id = self.pseudonymize(user_id)

        # Create key metadata
        # TODO: Rethink the structure and the primary / secondary keys
        key_data = {
            "name": name,
            "user_id": pseudonymized_user_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": (
                datetime.now(timezone.utc) + timedelta(days=expires_days)
            ).isoformat(),
            "last_used": None,
            "usage_count": 0,
        }

        # Save the key to the repository
        self.repository.save_key(key_hash, key_data)

        logger = HaivenLogger.get()
        if logger:
            logger.info(
                f"Generated API key '{name}' for user (hash) {pseudonymized_user_id}"
            )

        return key

    def validate_key(self, key: str) -> Optional[Dict[str, Any]]:
        """Validate an API key and return user information if valid."""
        if not key:
            return None

        # Hash the key to find it in the repository
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        key_info = self.repository.find_by_hash(key_hash)

        if not key_info:
            return None

        # Check if key is expired
        expires_at = key_info["expires_at"]
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
            # Ensure timezone awareness - if the parsed datetime is naive, assume UTC
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires_at:
            logger = HaivenLogger.get()
            if logger:
                logger.warn(f"Expired API key used: {key_info['name']}")
            return None

        # Update last used timestamp and usage count
        key_info["last_used"] = datetime.now(timezone.utc).isoformat()
        key_info["usage_count"] += 1
        self.repository.update_key(key_hash, key_info)

        return {
            "name": key_info["name"],
            "user_id": key_info["user_id"],
            "key_hash": key_hash,
        }

    def revoke_key(self, key_hash: str) -> bool:
        """Revoke an API key by its hash."""
        # TODO: Change this to soft delete / deactivate the key instead of hard delete
        return self.repository.delete_key(key_hash)

    def list_keys(self) -> Dict[str, Dict[str, Any]]:
        """List all API keys (without the actual key values)."""
        return self.repository.find_all()

    def list_keys_for_user(self, user_id: str) -> Dict[str, Dict[str, Any]]:
        """List API keys for a specific user."""
        pseudonymized_user_id = self.pseudonymize(user_id)
        return self.repository.find_by_user_id(pseudonymized_user_id)

    @staticmethod
    def extract_api_key_from_request(request: Request) -> Optional[str]:
        """Extract API key from request headers."""
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return api_key
        return None

    @staticmethod
    def create_api_user_session(user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create a user session from API key user information."""
        return {
            "user_id": user_info["user_id"],
            "name": user_info["name"],
            "auth_type": "api_key",
            "key_hash": user_info["key_hash"],
        }

    @staticmethod
    def is_mcp_endpoint(request_path: str) -> bool:
        """Check if a request path is an MCP endpoint."""
        if request_path == "/api/prompts":
            return True
        if request_path.startswith("/api/download-prompt"):
            return True
        return False

    async def authenticate_with_api_key(
        self, request: Request
    ) -> Optional[Dict[str, Any]]:
        """Authenticate a request using an API key."""
        api_key = self.extract_api_key_from_request(request)
        if not api_key:
            return None
        user_info = self.validate_key(api_key)
        if user_info:
            return self.create_api_user_session(user_info)
        return None

    async def authenticate_with_api_key_for_mcp_only(
        self, request: Request
    ) -> Optional[Dict[str, Any]]:
        """Authenticate a request using an API key, but only for MCP endpoints.
        Currently, Unused because service already checks MCP endpoints."""
        if not self.is_mcp_endpoint(request.url.path):
            return None
        return await self.authenticate_with_api_key(request)

    async def authenticate_with_api_key_optimized(
        self, request: Request
    ) -> Optional[Dict[str, Any]]:
        """Authenticate a request using an API key (optimized version without redundant MCP check)."""
        return await self.authenticate_with_api_key(request)
