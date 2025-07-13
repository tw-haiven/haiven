# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from typing import Dict, List


class ModelConfig:
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
        self.temperature = 0.5

        self.lite_id = provider.lower() + "/" + self.id
        if self.provider.lower() == "azure":
            self.lite_id = (
                provider.lower() + "/" + self.config.get("azure_deployment", "")
            )
        elif self.provider.lower() == "aws":
            self.lite_id = "bedrock/" + self.config["model_id"]
        elif self.provider.lower() == "anthropic":
            self.lite_id = "anthropic/" + self.config["model_id"]
        elif self.provider.lower() == "google":
            self.lite_id = "gemini/" + self.config["model"]
        elif self.provider.lower() == "openai":
            self.lite_id = "openai/" + self.config["model_name"]
        elif self.provider.lower() == "ollama":
            self.lite_id = "ollama/" + self.config["model"]
        elif self.provider.lower() == "perplexity":
            self.lite_id = "perplexity/sonar-pro"
        elif self.provider.lower() == "xai":
            self.lite_id = "xai/" + self.config["model"]

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
