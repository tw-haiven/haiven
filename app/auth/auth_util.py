# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
"""Authentication utility functions."""

import hashlib
import os
from typing import Optional
from fastapi import Request


def is_api_key_auth(request: Request) -> bool:
    """Check if the request is using API key authentication."""
    if request.session and request.session.get("user"):
        user = request.session.get("user")
        if user is not None:
            return user.get("auth_type") == "api_key"
    return False


def get_request_source(request: Request) -> str:
    """Get the source of the request (mcp, ui, or unknown)."""
    # Check if auth is switched off
    if os.environ.get("AUTH_SWITCHED_OFF") == "true":
        return "unknown"

    # Check if it's an API key auth (MCP)
    if is_api_key_auth(request):
        return "mcp"

    # Default to UI
    return "ui"


def get_hashed_user_id(request: Request) -> Optional[str]:
    """Get the hashed user ID from the request session."""
    if request.session and request.session.get("user"):
        user = request.session.get("user")
        if user is not None:
            # Check if auth_type is api_key, if so use user_id directly from the session
            if user.get("auth_type") == "api_key":
                user_id = user.get("user_id")
            else:
                user_id = user.get("email")

            if user_id is not None:
                hashed_user_id = hashlib.sha256(user_id.encode("utf-8")).hexdigest()
                return hashed_user_id
    return None
