# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from google.cloud import firestore
import uuid
from datetime import datetime, timedelta, timezone


class ApiKeyManager:
    def __init__(self, project_id: str):
        self.db = firestore.Client(project=project_id)
        self.temp_links_collection = self.db.collection("temp_api_links")
        self.api_keys_collection = self.db.collection("api_keys")

    def create_temporary_link(self) -> str:
        token = str(uuid.uuid4())
        now_utc = datetime.now(timezone.utc)
        expires_at = now_utc + timedelta(minutes=15)

        self.temp_links_collection.document(token).set(
            {
                "token": token,
                "created_at": now_utc,
                "expires_at": expires_at,
                "used": False,
            }
        )

        return f"/api/generate-api-key?token={token}"

    def get_api_key_from_temp_link(self, token: str, user_id: str = None) -> str | None:
        doc_ref = self.temp_links_collection.document(token)
        doc = doc_ref.get()

        if not doc.exists:
            return None

        link_data = doc.to_dict()
        if link_data["used"] or datetime.now(timezone.utc) > link_data["expires_at"]:
            return None

        # Mark the link as used
        doc_ref.update({"used": True})

        # Generate a new API key
        new_api_key = str(uuid.uuid4())

        # Store the new API key in Firestore
        self.api_keys_collection.document(new_api_key).set(
            {
                "api_key": new_api_key,
                "created_at": datetime.now(timezone.utc),
                "user_id": user_id,  # Can be None if user is not logged in yet
                "valid_until": datetime.now(timezone.utc)
                + timedelta(days=365),  # Example: Valid for a year
            }
        )

        return new_api_key

    def validate_user_api_key(self, api_key: str) -> bool:
        doc_ref = self.api_keys_collection.document(api_key)
        doc = doc_ref.get()

        if not doc.exists:
            return False

        key_data = doc.to_dict()
        if datetime.now(timezone.utc) > key_data["valid_until"]:
            return False

        return True
