# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

from typing import Optional, Dict, Any

from fastapi import Request
from auth.api_key_repository import ApiKeyRepository
from auth.file_api_key_repository import FileApiKeyRepository
from config_service import ConfigService


# Global repository instance
_api_key_repository: Optional[ApiKeyRepository] = None
_api_key_repository_type: Optional[str] = None


def get_api_key_repository(
    config_service: Optional[ConfigService] = None,
) -> ApiKeyRepository:
    """Get the global API key repository instance, instantiating based on config if needed."""
    global _api_key_repository, _api_key_repository_type
    if _api_key_repository is not None:
        return _api_key_repository
    if config_service is None:
        # fallback for legacy usage, default to file
        _api_key_repository = FileApiKeyRepository()
        _api_key_repository_type = "file"
        return _api_key_repository
    repo_type = config_service.load_api_key_repository_type()
    if repo_type == "file":
        _api_key_repository = FileApiKeyRepository(config_service)
        _api_key_repository_type = "file"
    else:
        raise NotImplementedError(
            f"API key repository type '{repo_type}' is not implemented."
        )
    return _api_key_repository


def set_api_key_repository(
    repository: Optional[ApiKeyRepository],
    config_service: Optional[ConfigService] = None,
) -> None:
    """Set the global API key repository instance (for testing or different implementations)."""
    global _api_key_repository, _api_key_repository_type
    _api_key_repository = repository
    if repository is None and config_service is not None:
        # Reset to config-based default
        get_api_key_repository(config_service)


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


def is_mcp_endpoint(request_path: str) -> bool:
    """Check if the request path is an MCP endpoint that should allow API key authentication."""
    # Check exact match for prompts endpoint
    if request_path == "/api/prompts":
        return True

    # Check if it's the download-prompt endpoint (with or without query params)
    if request_path.startswith("/api/download-prompt"):
        return True

    return False


async def authenticate_with_api_key_for_mcp_only(
    request: Request,
) -> Optional[Dict[str, Any]]:
    """Authenticate request using API key, but only for MCP endpoints."""
    if not is_mcp_endpoint(request.url.path):
        return None

    return await authenticate_with_api_key(request)
