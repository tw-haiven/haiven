# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

from typing import Optional, Dict, Any
from datetime import datetime

from google.cloud import firestore
from google.cloud.firestore import CollectionReference
from google.cloud.firestore_v1.base_document import DocumentSnapshot

from auth.api_key_repository import ApiKeyRepository
from config_service import ConfigService
from logger import HaivenLogger


class FirestoreApiKeyRepository(ApiKeyRepository):
    """Firestore-based implementation of API key storage."""

    def __init__(self, config: ConfigService):
        if not hasattr(config, "load_firestore_project_id"):
            raise ValueError(
                "FirestoreApiKeyRepository requires a ConfigService (or compatible) object with Firestore configuration."
            )

        self.project_id = config.load_firestore_project_id()
        self.collection_name = config.load_firestore_collection_name()
        self.db = firestore.Client(project=self.project_id)

        self.collection: CollectionReference = self.db.collection(self.collection_name)

        logger = HaivenLogger.get()
        if logger:
            logger.info(
                f"Initialized Firestore API key repository for project: {self.project_id}"
            )

    def save_key(self, key_hash: str, key_data: Dict[str, Any]) -> None:
        """Save an API key with its metadata."""
        try:
            # Convert datetime objects to ISO format strings for Firestore
            firestore_data = self._prepare_data_for_firestore(key_data)

            # Use key_hash as document ID
            doc_ref = self.collection.document(key_hash)
            doc_ref.set(firestore_data)

            logger = HaivenLogger.get()
            if logger:
                logger.info(
                    f"Saved API key '{key_data.get('name', 'unnamed')}' for user (hash) {key_data.get('user_id', 'unknown')}"
                )
        except Exception as e:
            logger = HaivenLogger.get()
            if logger:
                logger.error(f"Failed to save API key to Firestore: {e}")
            raise

    def find_by_hash(self, key_hash: str) -> Optional[Dict[str, Any]]:
        """Find an API key by its hash."""
        try:
            doc_ref = self.collection.document(key_hash)
            doc_snapshot: DocumentSnapshot = doc_ref.get()

            if doc_snapshot.exists:
                data = doc_snapshot.to_dict()
                return self._prepare_data_from_firestore(data)
            return None
        except Exception as e:
            logger = HaivenLogger.get()
            if logger:
                logger.error(f"Failed to find API key in Firestore: {e}")
            return None

    def update_key(self, key_hash: str, key_data: Dict[str, Any]) -> bool:
        """Update an API key's metadata."""
        try:
            # Convert datetime objects to ISO format strings for Firestore
            firestore_data = self._prepare_data_for_firestore(key_data)

            doc_ref = self.collection.document(key_hash)
            doc_ref.update(firestore_data)
            return True
        except Exception as e:
            logger = HaivenLogger.get()
            if logger:
                logger.error(f"Failed to update API key in Firestore: {e}")
            return False

    def delete_key(self, key_hash: str) -> bool:
        """Delete an API key by its hash."""
        try:
            doc_ref = self.collection.document(key_hash)
            doc_ref.delete()
            return True
        except Exception as e:
            logger = HaivenLogger.get()
            if logger:
                logger.error(f"Failed to delete API key from Firestore: {e}")
            return False

    def find_all(self) -> Dict[str, Dict[str, Any]]:
        """Find all API keys with their metadata."""
        try:
            keys = {}
            docs = self.collection.stream()

            for doc in docs:
                data = doc.to_dict()
                keys[doc.id] = self._prepare_data_from_firestore(data)

            return keys
        except Exception as e:
            logger = HaivenLogger.get()
            if logger:
                logger.error(f"Failed to find all API keys in Firestore: {e}")
            return {}

    def find_by_user_id(self, user_id: str) -> Dict[str, Dict[str, Any]]:
        """Find all API keys for a specific user."""
        try:
            keys = {}
            # Query by user_id field
            query = self.collection.where("user_id", "==", user_id)
            docs = query.stream()

            for doc in docs:
                data = doc.to_dict()
                keys[doc.id] = self._prepare_data_from_firestore(data)

            return keys
        except Exception as e:
            logger = HaivenLogger.get()
            if logger:
                logger.error(f"Failed to find API keys by user_id in Firestore: {e}")
            return {}

    def _prepare_data_for_firestore(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for Firestore storage by converting datetime objects to strings."""
        firestore_data = data.copy()

        # Convert datetime objects to ISO format strings
        for key, value in firestore_data.items():
            if isinstance(value, datetime):
                firestore_data[key] = value.isoformat()

        return firestore_data

    def _prepare_data_from_firestore(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data from Firestore by converting string timestamps back to datetime objects."""
        if not data:
            return data

        firestore_data = data.copy()

        # Convert ISO format strings back to datetime objects for specific fields
        datetime_fields = ["created_at", "expires_at", "last_used"]
        for field in datetime_fields:
            if field in firestore_data and firestore_data[field]:
                try:
                    firestore_data[field] = datetime.fromisoformat(
                        firestore_data[field]
                    )
                except (ValueError, TypeError):
                    # Keep as string if conversion fails
                    pass

        return firestore_data
