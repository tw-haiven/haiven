# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from typing import Dict

from auth.api_key_repository import ApiKeyRepository
from config_service import ConfigService


class ApiKeyRepositoryFactory:
    """
    Factory class for creating and managing ApiKeyRepository instances.
    This class implements the Singleton pattern to ensure that only one instance
    of each repository type is created.
    """

    _instances: Dict[str, ApiKeyRepository] = {}

    @classmethod
    def get_repository(cls, config_service: ConfigService) -> ApiKeyRepository:
        """
        Get or create an ApiKeyRepository instance based on the configuration.

        Args:
            config_service: The configuration service to use for creating the repository.

        Returns:
            An ApiKeyRepository instance.

        Raises:
            NotImplementedError: If the repository type specified in the configuration is not implemented.
        """
        repo_type = config_service.load_api_key_repository_type()

        # Return existing instance if available
        if repo_type in cls._instances:
            return cls._instances[repo_type]

        # Create new instance
        if repo_type == "file":
            from auth.file_api_key_repository import FileApiKeyRepository

            repository = FileApiKeyRepository(config_service)
        elif repo_type == "firestore":
            from auth.firestore_api_key_repository import FirestoreApiKeyRepository

            repository = FirestoreApiKeyRepository(config_service)
        # TODO: Uncomment and implement other repository types as needed
        # elif repo_type == "db":
        #     return DbApiKeyRepository(config_service)
        else:
            raise NotImplementedError(
                f"API key repository type '{repo_type}' is not implemented."
            )

        # Store instance for future use
        cls._instances[repo_type] = repository
        return repository

    @classmethod
    def reset(cls) -> None:
        """
        Reset the factory by clearing all cached instances.
        This is primarily useful for testing.
        """
        cls._instances.clear()
