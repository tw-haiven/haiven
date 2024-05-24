# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import pytest
from shared.services.models_service import ModelsService
from shared.models.model import Model


class TestModelsService:
    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        ModelsService.reset_instance()

        mocker.patch(
            "shared.services.models_service.ConfigService.load_models",
            return_value=[
                Model(
                    id="1",
                    name="gpt3",
                    provider="azure",
                    features=["chat-completion", "streaming"],
                ),
                Model(
                    id="2", name="gpt4", provider="azure", features=["image-to-text"]
                ),
                Model(
                    id="3",
                    name="gemini-pro",
                    provider="gcp",
                    features=["chat-completion", "streaming"],
                ),
                Model(
                    id="4",
                    name="gemini-ultra",
                    provider="gcp",
                    features=["chat-completion", "streaming", "image-to-text"],
                ),
                Model(
                    id="5",
                    name="claude-2",
                    provider="aws",
                    features=["chat-completion", "streaming"],
                ),
            ],
        )
        self.service = ModelsService.get_instance()

    def test_singleton(self):
        with pytest.raises(Exception):
            ModelsService()

    def test_get_model_returns_correct_model(self):
        model = self.service.get_model("1")
        assert model.id == "1"

    def test_get_model_returns_none_when_not_found(self):
        model = self.service.get_model("test")
        assert model is None

    def test_get_models_return_all_models(self):
        models = self.service.get_models()
        assert len(models) == 5

    def test_get_models_by_provider_return_only_models_by_provider(self):
        models = self.service.get_models(providers=["azure"])
        assert len(models) == 2

    def test_get_models_by_feature(self):
        models = self.service.get_models(features=["image-to-text"])
        assert len(models) == 2

    def test_get_models_by_features(self):
        models = self.service.get_models(features=["chat-completion", "image-to-text"])
        assert len(models) == 1

    def test_get_models_by_provider_and_features(self):
        models = self.service.get_models(
            providers=["azure"], features=["image-to-text"]
        )
        assert len(models) == 1

    def test_get_models_by_features_not_found(self):
        models = self.service.get_models(features=["agi"])
        assert len(models) == 0

    def test_get_models_by_provider_return_all_models_with_provider_in_filter(self):
        models = self.service.get_models(providers=["azure", "gcp"])
        assert len(models) == 4
