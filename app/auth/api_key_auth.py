# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

from typing import Optional, Dict, Any

from fastapi import Request
from auth.api_key_repository import ApiKeyRepository
from auth.file_api_key_repository import FileApiKeyRepository


# Global repository instance
_api_key_repository: Optional[ApiKeyRepository] = None


def get_api_key_repository() -> ApiKeyRepository:
    """Get the global API key repository instance."""
    global _api_key_repository
    if _api_key_repository is None:
        _api_key_repository = FileApiKeyRepository()
    return _api_key_repository


def set_api_key_repository(repository: Optional[ApiKeyRepository]) -> None:
    """Set the global API key repository instance (for testing or different implementations)."""
    global _api_key_repository
    _api_key_repository = repository


# Legacy compatibility - keep the old class name for backward compatibility
class ApiKeyManager:
    """Legacy wrapper for the repository - deprecated, use get_api_key_repository() instead."""

    def __init__(self, config_path: str = "app/config/api_keys.json"):
        self.repository = FileApiKeyRepository(config_path)

    def generate_api_key(
        self, name: str, user_email: str, expires_days: int = 365
    ) -> str:
        return self.repository.generate_api_key(name, user_email, expires_days)

    def validate_key(self, key: str) -> Optional[Dict[str, Any]]:
        return self.repository.validate_key(key)

    def revoke_key(self, key_hash: str) -> bool:
        return self.repository.revoke_key(key_hash)

    def list_keys(self) -> Dict[str, Any]:
        return self.repository.list_keys()


# Legacy compatibility function - deprecated, use get_api_key_repository() instead
def get_api_key_manager() -> ApiKeyManager:
    """Get the global API key manager instance - deprecated, use get_api_key_repository() instead."""
    return ApiKeyManager()


def extract_api_key_from_request(request: Request) -> Optional[str]:
    """Extract API key from request headers."""
    # Try Authorization header first (Bearer token)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]  # Remove "Bearer " prefix

    # Try X-API-Key header
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return api_key

    return None


def create_api_user_session(user_info: Dict[str, Any]) -> Dict[str, Any]:
    """Create a user session object for API key authentication."""
    return {
        "email": user_info["user_email"],
        "name": user_info["name"],
        "auth_type": "api_key",
        "key_hash": user_info["key_hash"],
    }


async def authenticate_with_api_key(request: Request) -> Optional[Dict[str, Any]]:
    """Authenticate request using API key."""
    api_key = extract_api_key_from_request(request)
    if not api_key:
        return None

    repository = get_api_key_repository()
    user_info = repository.validate_key(api_key)

    if user_info:
        return create_api_user_session(user_info)

    return None
