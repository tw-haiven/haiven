# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import hashlib
from typing import Optional, Dict, Any
from fastapi import Request

from auth.api_key_repository import ApiKeyRepository
from config_service import ConfigService


def pseudonymize(data: str, salt: str) -> str:
    normalized = data.strip().lower()
    return hashlib.sha256((salt + normalized).encode()).hexdigest()


def generate_api_key_with_pseudonymization(
    repository: ApiKeyRepository, name: str, user_id: str, expires_days: int, salt: str
) -> str:
    pseudonymized = pseudonymize(user_id, salt)
    return repository.generate_api_key(name, pseudonymized, expires_days)


def list_keys_for_user_with_pseudonymization(
    repository: ApiKeyRepository, user_id: str, salt: str
) -> Dict[str, Any]:
    pseudonymized = pseudonymize(user_id, salt)
    return repository.list_keys_for_user(pseudonymized)


class ApiKeyAuthService:
    def __init__(self, config_service: ConfigService, repository: ApiKeyRepository):
        self.config_service = config_service
        self.repository = repository

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
        return {
            "user_id": user_info["user_id"],
            "name": user_info["name"],
            "auth_type": "api_key",
            "key_hash": user_info["key_hash"],
        }

    @staticmethod
    def is_mcp_endpoint(request_path: str) -> bool:
        if request_path == "/api/prompts":
            return True
        if request_path.startswith("/api/download-prompt"):
            return True
        return False

    async def authenticate_with_api_key(
        self, request: Request
    ) -> Optional[Dict[str, Any]]:
        api_key = self.extract_api_key_from_request(request)
        if not api_key:
            return None
        user_info = self.repository.validate_key(api_key)
        if user_info:
            return self.create_api_user_session(user_info)
        return None

    async def authenticate_with_api_key_for_mcp_only(
        self, request: Request
    ) -> Optional[Dict[str, Any]]:
        if not self.is_mcp_endpoint(request.url.path):
            return None
        return await self.authenticate_with_api_key(request)
