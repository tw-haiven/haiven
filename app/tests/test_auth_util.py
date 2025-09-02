# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import hashlib
import os
from unittest.mock import Mock
from fastapi import Request

from auth.auth_util import is_api_key_auth, get_request_source, get_hashed_user_id


class TestAuthUtil:
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Store original environment variable value
        self.original_auth_switched_off = os.environ.get("AUTH_SWITCHED_OFF")

    def teardown_method(self):
        """Clean up after each test method."""
        # Restore original environment variable value
        if self.original_auth_switched_off is not None:
            os.environ["AUTH_SWITCHED_OFF"] = self.original_auth_switched_off
        elif "AUTH_SWITCHED_OFF" in os.environ:
            del os.environ["AUTH_SWITCHED_OFF"]

    def test_is_api_key_auth_with_api_key_user(self):
        """Test that API key authentication is detected correctly."""
        # Arrange
        request = Mock(spec=Request)
        request.session = {"user": {"auth_type": "api_key"}}

        # Act
        result = is_api_key_auth(request)

        # Assert
        assert result is True

    def test_is_api_key_auth_with_non_api_key_user(self):
        """Test that non-API key authentication is detected correctly."""
        # Arrange
        request = Mock(spec=Request)
        request.session = {"user": {"auth_type": "oauth"}}

        # Act
        result = is_api_key_auth(request)

        # Assert
        assert result is False

    def test_is_api_key_auth_with_no_session(self):
        """Test that no session returns False."""
        # Arrange
        request = Mock(spec=Request)
        request.session = None

        # Act
        result = is_api_key_auth(request)

        # Assert
        assert result is False

    def test_is_api_key_auth_with_no_user(self):
        """Test that no user in session returns False."""
        # Arrange
        request = Mock(spec=Request)
        request.session = {}

        # Act
        result = is_api_key_auth(request)

        # Assert
        assert result is False

    def test_get_request_source_when_auth_switched_off(self):
        """Test that request source is 'unknown' when auth is switched off."""
        # Arrange
        request = Mock(spec=Request)
        os.environ["AUTH_SWITCHED_OFF"] = "true"

        # Act
        result = get_request_source(request)

        # Assert
        assert result == "unknown"

    def test_get_request_source_for_mcp(self):
        """Test that request source is 'mcp' for API key authentication."""
        # Arrange
        request = Mock(spec=Request)
        request.session = {"user": {"auth_type": "api_key"}}
        # Ensure auth is not switched off
        if "AUTH_SWITCHED_OFF" in os.environ:
            del os.environ["AUTH_SWITCHED_OFF"]

        # Act
        result = get_request_source(request)

        # Assert
        assert result == "mcp"

    def test_get_request_source_for_ui(self):
        """Test that request source is 'ui' for non-API key authentication."""
        # Arrange
        request = Mock(spec=Request)
        request.session = {"user": {"auth_type": "oauth"}}
        # Ensure auth is not switched off
        if "AUTH_SWITCHED_OFF" in os.environ:
            del os.environ["AUTH_SWITCHED_OFF"]

        # Act
        result = get_request_source(request)

        # Assert
        assert result == "ui"

    def test_get_request_source_with_no_session(self):
        """Test that request source is 'ui' when no session exists."""
        # Arrange
        request = Mock(spec=Request)
        request.session = None
        # Ensure auth is not switched off
        if "AUTH_SWITCHED_OFF" in os.environ:
            del os.environ["AUTH_SWITCHED_OFF"]

        # Act
        result = get_request_source(request)

        # Assert
        assert result == "ui"

    def test_get_hashed_user_id_with_api_key_auth(self):
        """Test that hashed user ID is generated correctly for API key auth."""
        # Arrange
        user_id = "test_user_123"
        request = Mock(spec=Request)
        request.session = {"user": {"auth_type": "api_key", "user_id": user_id}}
        expected_hash = hashlib.sha256(user_id.encode("utf-8")).hexdigest()

        # Act
        result = get_hashed_user_id(request)

        # Assert
        assert result == expected_hash

    def test_get_hashed_user_id_with_email_auth(self):
        """Test that hashed user ID is generated correctly for email auth."""
        # Arrange
        email = "test@example.com"
        request = Mock(spec=Request)
        request.session = {"user": {"auth_type": "oauth", "email": email}}
        expected_hash = hashlib.sha256(email.encode("utf-8")).hexdigest()

        # Act
        result = get_hashed_user_id(request)

        # Assert
        assert result == expected_hash

    def test_get_hashed_user_id_with_no_session(self):
        """Test that None is returned when no session exists."""
        # Arrange
        request = Mock(spec=Request)
        request.session = None

        # Act
        result = get_hashed_user_id(request)

        # Assert
        assert result is None

    def test_get_hashed_user_id_with_no_user(self):
        """Test that None is returned when no user in session."""
        # Arrange
        request = Mock(spec=Request)
        request.session = {}

        # Act
        result = get_hashed_user_id(request)

        # Assert
        assert result is None

    def test_get_hashed_user_id_with_missing_user_id(self):
        """Test that None is returned when user_id/email is missing."""
        # Arrange
        request = Mock(spec=Request)
        request.session = {"user": {"auth_type": "api_key"}}  # No user_id

        # Act
        result = get_hashed_user_id(request)

        # Assert
        assert result is None

    def test_get_hashed_user_id_with_none_user_id(self):
        """Test that None is returned when user_id/email is None."""
        # Arrange
        request = Mock(spec=Request)
        request.session = {"user": {"auth_type": "api_key", "user_id": None}}

        # Act
        result = get_hashed_user_id(request)

        # Assert
        assert result is None
