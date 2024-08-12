# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import copy
from typing import List

from config_service import ConfigService
from llms.model import Model


class ModelsService:
    __instance = None

    def __init__(self, config_path: str = "config.yaml"):
        models: List[Model] = ConfigService.load_models(config_path)
        self.models = models

        if ModelsService.__instance is not None:
            raise Exception(
                "ModelsService is a singleton class. Use get_instance() to get the instance."
            )

        ModelsService.__instance = self

    def _get_model(self, model_id: str) -> Model:
        return next((model for model in self.models if model.id == model_id), None)

    def _get_models(
        self, providers: List[str] = [], features: List[str] = []
    ) -> List[Model]:
        filtered_models = copy.deepcopy(self.models)

        if providers and len(providers) > 0:
            filtered_models = [
                model
                for model in filtered_models
                if any(
                    model.provider.lower() == model_provider.lower()
                    for model_provider in providers
                )
            ]

        if features and len(features) > 0:
            filtered_models = [
                model
                for model in filtered_models
                if all(
                    feature.lower()
                    in [model_feature.lower() for model_feature in model.features]
                    for feature in features
                )
            ]

        return filtered_models

    @staticmethod
    def get_model(model_id: str) -> Model:
        return ModelsService.get_instance()._get_model(model_id)

    @staticmethod
    def get_models(providers: List[str] = [], features: List[str] = []) -> List[Model]:
        """
        Get a list of models based on the given providers and features.

        Args:
            providers (List[str], optional): List of providers to filter the models. When more than one provider is passed, models are returned if belong to any of the providers. Defaults to [].
            features (List[str], optional): List of features to filter the models. When more than one feature is passed, models are returned if have all the features. Defaults to [].

        Returns:
            List[Model]: List of filtered models.
        """
        return ModelsService.get_instance()._get_models(providers, features)

    @staticmethod
    def get_instance():
        if ModelsService.__instance is None:
            ModelsService()

        return ModelsService.__instance

    @staticmethod
    def reset_instance():
        ModelsService.__instance = None
