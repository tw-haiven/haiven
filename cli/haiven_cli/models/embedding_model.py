# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from typing import Dict


class EmbeddingModel:
    """
    Represents an embedding model.

    Attributes:
        id (str): The ID of the embedding model.
        provider (str): The provider of the embedding model.
        name (str): The name of the embedding model.
        config (Dict[str, str]): The configuration of the embedding model.
    """

    def __init__(
        self, id: str, provider: str, name: str, config: Dict[str, str] = None
    ):
        self.id = id
        self.provider = provider
        self.name = name
        self.config = config if config else {}

    @classmethod
    def from_dict(cls, data):
        """
        Creates an instance of EmbeddingModel from a dictionary.

        Args:
            data (dict): The dictionary containing the data for the embedding model.

        Returns:
            EmbeddingModel: An instance of EmbeddingModel.
        """
        return cls(
            id=data.get("id"),
            provider=data.get("provider"),
            name=data.get("name"),
            config=data.get("config"),
        )
