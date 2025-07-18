# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import hashlib

from auth.api_key_auth_service import ApiKeyAuthService
from logger import HaivenLogger
from config_service import ConfigService


class GenerateApiKeyRequest(BaseModel):
    name: str
    expires_days: int | None = None


class RevokeApiKeyRequest(BaseModel):
    key_hash: str


class ApiKeyManagementAPI:
    def __init__(
        self,
        app: FastAPI,
        api_key_service: ApiKeyAuthService,
        config_service: ConfigService,
    ):
        self.app = app
        self.api_key_service = api_key_service
        self.config_service = config_service
        self.register_endpoints()

    def get_user_email(self, request: Request) -> str:
        """Get the authenticated user's email from session."""
        user = request.session.get("user")
        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not authenticated. You must be logged in to generate or manage API keys, even in developer mode.",
            )
        return user.get("email")

    def register_endpoints(self):
        @self.app.get("/api/apikeys")
        async def list_api_keys(request: Request):
            """List all API keys for the authenticated user."""
            try:
                user_email = self.get_user_email(request)
                user_keys = self.api_key_service.list_keys_for_user(user_email)

                # Format for frontend
                formatted_keys = []
                for key_hash, info in user_keys.items():
                    # Convert datetime objects to ISO format strings for JSON serialization
                    created_at = info["created_at"]
                    expires_at = info["expires_at"]
                    last_used = info["last_used"]

                    # Convert to string if datetime object
                    if hasattr(created_at, "isoformat"):
                        created_at = created_at.isoformat()
                    if hasattr(expires_at, "isoformat"):
                        expires_at = expires_at.isoformat()
                    if last_used and hasattr(last_used, "isoformat"):
                        last_used = last_used.isoformat()

                    formatted_keys.append(
                        {
                            "key_hash": key_hash,
                            "name": info["name"],
                            "created_at": created_at,
                            "expires_at": expires_at,
                            "last_used": last_used,
                            "usage_count": info["usage_count"],
                        }
                    )

                # Sort by creation date (newest first)
                formatted_keys.sort(key=lambda x: x["created_at"], reverse=True)

                return JSONResponse(
                    {"keys": formatted_keys, "total": len(formatted_keys)}
                )

            except Exception as e:
                logger = HaivenLogger.get()
                if logger:
                    logger.error(f"Error listing API keys: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

        @self.app.post("/api/apikeys/generate")
        async def generate_api_key(request: Request, body: GenerateApiKeyRequest):
            """Generate a new API key for the authenticated user."""
            try:
                user_id = self.get_user_email(request)
                expires_days = (
                    body.expires_days if body.expires_days is not None else 30
                )
                if expires_days > 30:
                    raise HTTPException(
                        status_code=400, detail="API key maximum expiry is 30 days"
                    )
                if expires_days < 1:
                    raise HTTPException(
                        status_code=400, detail="API key expiry must be at least 1 day"
                    )
                api_key = self.api_key_service.generate_api_key(
                    name=body.name,
                    user_id=user_id,
                    expires_days=expires_days,
                )

                # Calculate key hash for response
                key_hash = hashlib.sha256(api_key.encode()).hexdigest()

                logger = HaivenLogger.get()
                if logger:
                    logger.info("API key generated via web UI.")

                return JSONResponse(
                    {
                        "success": True,
                        "api_key": api_key,
                        "key_hash": key_hash,
                        "name": body.name,
                        "expires_days": expires_days,
                        "message": f"API key generated successfully (expires in {expires_days} days)",
                    }
                )

            except HTTPException:
                raise
            except ValueError as ve:
                logger = HaivenLogger.get()
                if logger:
                    logger.error(f"Error generating API key: {str(ve)}")
                raise HTTPException(status_code=400, detail=str(ve))
            except Exception as e:
                logger = HaivenLogger.get()
                if logger:
                    logger.error(f"Error generating API key: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

        @self.app.post("/api/apikeys/revoke")
        async def revoke_api_key(request: Request, body: RevokeApiKeyRequest):
            """Revoke an API key."""
            try:
                user_email = self.get_user_email(request)
                # First verify the key belongs to the current user
                user_keys = self.api_key_service.list_keys_for_user(user_email)
                key_info = user_keys.get(body.key_hash)

                if not key_info:
                    raise HTTPException(status_code=404, detail="API key not found")

                # Revoke the key
                success = self.api_key_service.revoke_key(body.key_hash)

                if success:
                    logger = HaivenLogger.get()
                    if logger:
                        logger.info("API key revoked via web UI for user")
                    return JSONResponse(
                        {"success": True, "message": "API key revoked successfully"}
                    )
                else:
                    raise HTTPException(status_code=404, detail="API key not found")

            except HTTPException:
                raise
            except Exception as e:
                logger = HaivenLogger.get()
                if logger:
                    logger.error(f"Error revoking API key: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

        @self.app.get("/api/apikeys/usage")
        async def get_api_key_usage(request: Request):
            """Get API key usage statistics for the authenticated user."""
            try:
                user_email = self.get_user_email(request)
                # Get keys for the specific user
                user_keys = self.api_key_service.list_keys_for_user(user_email)

                # Calculate statistics
                total_keys = len(user_keys)
                total_usage = sum(info["usage_count"] for info in user_keys.values())

                # Find most recent usage
                most_recent_usage = None
                for info in user_keys.values():
                    if info["last_used"]:
                        last_used = info["last_used"]
                        # Convert to string if datetime object for JSON serialization
                        if hasattr(last_used, "isoformat"):
                            last_used = last_used.isoformat()

                        if (
                            not most_recent_usage
                            or info["last_used"] > most_recent_usage
                        ):
                            most_recent_usage = last_used

                return JSONResponse(
                    {
                        "total_keys": total_keys,
                        "total_usage": total_usage,
                        "most_recent_usage": most_recent_usage,
                    }
                )

            except Exception as e:
                logger = HaivenLogger.get()
                if logger:
                    logger.error(f"Error getting API key usage: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
