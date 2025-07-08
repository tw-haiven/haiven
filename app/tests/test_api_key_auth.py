# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

import pytest
from unittest.mock import Mock, patch
from fastapi import Request

from auth.api_key_auth import (
    is_mcp_endpoint,
    authenticate_with_api_key_for_mcp_only,
)


class TestApiKeyAuthRestriction:
    """Test that API key authentication is restricted to MCP endpoints only."""

    def test_is_mcp_endpoint_identifies_correct_endpoints(self):
        """Test that is_mcp_endpoint correctly identifies MCP endpoints."""
        # MCP endpoints should return True
        assert is_mcp_endpoint("/api/prompts") is True
        assert is_mcp_endpoint("/api/download-prompt") is True
        assert is_mcp_endpoint("/api/download-prompt?prompt_id=test") is True

        # Non-MCP endpoints should return False
        assert is_mcp_endpoint("/api/prompt") is False
        assert is_mcp_endpoint("/api/apikeys") is False
        assert is_mcp_endpoint("/api/features") is False
        assert is_mcp_endpoint("/api/some-other-endpoint") is False
        assert is_mcp_endpoint("/") is False
        assert is_mcp_endpoint("/boba/dashboard") is False

    @pytest.mark.asyncio
    async def test_api_key_auth_allowed_for_mcp_endpoints(self):
        """Test that API key authentication works for MCP endpoints."""
        # Mock request for MCP endpoint
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/prompts"

        # Mock the authenticate_with_api_key function to return a user
        mock_user = {"email": "test@example.com", "auth_type": "api_key"}

        with patch(
            "auth.api_key_auth.authenticate_with_api_key", return_value=mock_user
        ):
            result = await authenticate_with_api_key_for_mcp_only(mock_request)
            assert result == mock_user

    @pytest.mark.asyncio
    async def test_api_key_auth_blocked_for_non_mcp_endpoints(self):
        """Test that API key authentication is blocked for non-MCP endpoints."""
        # Mock request for non-MCP endpoint
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/apikeys"

        # Even if authenticate_with_api_key would return a user, it should be blocked
        mock_user = {"email": "test@example.com", "auth_type": "api_key"}

        with patch(
            "auth.api_key_auth.authenticate_with_api_key", return_value=mock_user
        ):
            result = await authenticate_with_api_key_for_mcp_only(mock_request)
            assert result is None

    @pytest.mark.asyncio
    async def test_api_key_auth_blocked_for_download_prompt_variations(self):
        """Test API key auth works for different download-prompt URL variations."""
        # Test different variations of the download-prompt endpoint
        test_paths = [
            "/api/download-prompt",
            "/api/download-prompt?prompt_id=test-123",
            "/api/download-prompt?prompt_id=test&category=testing",
        ]

        mock_user = {"email": "test@example.com", "auth_type": "api_key"}

        for path in test_paths:
            mock_request = Mock(spec=Request)
            mock_request.url.path = path

            with patch(
                "auth.api_key_auth.authenticate_with_api_key", return_value=mock_user
            ):
                result = await authenticate_with_api_key_for_mcp_only(mock_request)
                assert result == mock_user, f"Failed for path: {path}"

    @pytest.mark.asyncio
    async def test_api_key_auth_respects_original_auth_failure(self):
        """Test that if original API key auth fails, it still returns None."""
        mock_request = Mock(spec=Request)
        mock_request.url.path = "/api/prompts"

        # Mock authenticate_with_api_key to return None (auth failure)
        with patch("auth.api_key_auth.authenticate_with_api_key", return_value=None):
            result = await authenticate_with_api_key_for_mcp_only(mock_request)
            assert result is None
