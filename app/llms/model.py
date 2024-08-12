# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from typing import Dict, List


class Model:
    def __init__(
        self,
        id: str,
        provider: str,
        name: str,
        features: List[str] = None,
        config: Dict[str, str] = None,
    ):
        """
        Initialize a Model object.

        Args:
            id (str): The ID of the model.
            provider (str): The provider of the model.
            name (str): The name of the model.
            features (List[str], optional): The list of features of the model. Defaults to None.
            config (Dict[str, str], optional): The configuration of the model. Defaults to None.
        """
        self.id = id
        self.provider = provider
        self.name = name
        self.features = features if features else []
        self.config = config if config else {}

    @classmethod
    def from_dict(cls, data):
        """
        Create a Model object from a dictionary.

        Args:
            data (dict): The dictionary containing the model data.

        Returns:
            Model: The created Model object.
        """
        return cls(
            id=data.get("id"),
            provider=data.get("provider"),
            name=data.get("name"),
            features=data.get("features"),
            config=data.get("config"),
        )
