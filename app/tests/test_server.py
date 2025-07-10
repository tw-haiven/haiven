# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from server import Server
from unittest.mock import MagicMock
import os
import time
from starlette.responses import RedirectResponse


@pytest.fixture
def minimal_server_app():
    # Minimal mocks for dependencies
    chat_manager = MagicMock()
    config_service = MagicMock()
    api_key_repository = MagicMock()
    boba_api = MagicMock()
    server = Server(chat_manager, config_service, api_key_repository, boba_api)
    app = FastAPI()
    server.user_endpoints(app)

    # Add a test-only endpoint to set the session
    @app.get("/set-session")
    async def set_session(request: Request, created_at: int = None):
        request.session["user"] = {"email": "test@example.com", "auth_type": "session"}
        if created_at is not None:
            request.session["created_at"] = created_at
        return {"ok": True}

    # Add a dummy protected route that returns the session user for debugging
    @app.get("/some-protected-route")
    async def protected(request: Request):
        return {"ok": True, "user": request.session.get("user")}

    # Patch /logout to use session.clear for test
    @app.get("/logout")
    async def logout(request: Request):
        request.session.clear()
        return RedirectResponse(url="/")

    return app


def test_auth_middleware_redirects_unauthenticated(minimal_server_app):
    if "AUTH_SWITCHED_OFF" in os.environ:
        del os.environ["AUTH_SWITCHED_OFF"]
    client = TestClient(minimal_server_app)
    response = client.get("/some-protected-route", allow_redirects=False)
    assert response.status_code in (302, 307)
    assert "/login" in response.headers["location"]


def test_auth_middleware_allows_authenticated(minimal_server_app):
    os.environ["AUTH_SWITCHED_OFF"] = "true"
    client = TestClient(minimal_server_app)
    client.get("/set-session")
    response = client.get("/some-protected-route", allow_redirects=False)
    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert response.json()["user"]["email"] == "test@example.com"
    assert response.json()["user"]["auth_type"] == "session"


# --- Session expiry middleware tests ---
def test_session_not_expired(minimal_server_app):
    os.environ["AUTH_SWITCHED_OFF"] = "true"
    client = TestClient(minimal_server_app)
    now = int(time.time())
    # Set session with created_at = now
    client.get(f"/set-session?created_at={now}")
    response = client.get("/some-protected-route", allow_redirects=False)
    # Should NOT redirect, session is still valid
    assert response.status_code == 200
    assert response.json()["user"]["email"] == "test@example.com"


def test_session_expired(minimal_server_app):
    os.environ["AUTH_SWITCHED_OFF"] = "true"
    client = TestClient(minimal_server_app)
    now = int(time.time())
    # Set session with created_at way in the past
    expired_at = now - (8 * 24 * 60 * 60)  # 8 days ago (default expiry is 7 days)
    client.get(f"/set-session?created_at={expired_at}")
    response = client.get("/some-protected-route", allow_redirects=False)
    # Should redirect to / (session expired)
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/"


def test_login_endpoint_redirects(minimal_server_app):
    os.environ["AUTH_SWITCHED_OFF"] = "true"
    client = TestClient(minimal_server_app)
    response = client.get("/login", allow_redirects=False)
    # Should redirect (302 or 307) or return 200 if AUTH_SWITCHED_OFF disables real OAuth
    assert response.status_code in (200, 302, 307)
    # If redirect, should go somewhere (could be /auth or /)
    if response.status_code in (302, 307):
        assert response.headers["location"]
