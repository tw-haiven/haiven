# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import pytest

from haiven_cli.services.embedding_service import EmbeddingService
from unittest.mock import MagicMock, patch, PropertyMock


class TestEmbeddingService:
    def test_load_embeddings_fails_when_model_id_is_empty(self):
        model = MagicMock()
        type(model).id = PropertyMock(return_value="")

        with pytest.raises(ValueError) as e:
            EmbeddingService.load_embeddings(model)

        assert str(e.value) == "model id is not defined"

    def test_load_embeddings_for_fails_when_model_id_is_none(self):
        model = MagicMock()
        type(model).id = PropertyMock(return_value=None)

        with pytest.raises(ValueError) as e:
            EmbeddingService.load_embeddings(model)

        assert str(e.value) == "model id is not defined"

    def test_load_embeddings_fails_when_model_config_is_none(self):
        model = MagicMock()
        type(model).id = PropertyMock(return_value="id")
        type(model).config = PropertyMock(return_value=None)

        with pytest.raises(ValueError) as e:
            EmbeddingService.load_embeddings(model)

        assert str(e.value) == "model config is not defined for id"

    def test_load_embeddings_for_openai_fails_when_provider_is_not_recognised(self):
        model = MagicMock()
        type(model).provider = PropertyMock(return_value="")
        type(model).id = PropertyMock(return_value="id")
        type(model).config = PropertyMock(return_value={})

        with pytest.raises(ValueError) as e:
            EmbeddingService.load_embeddings(model)

        assert str(e.value) == "model provider is not defined in config for id"

    def test_load_openai_embeddings_fail_when_model_is_not_defined_in_embedding_config(
        self,
    ):
        model = MagicMock()
        type(model).provider = PropertyMock(return_value="openai")
        type(model).id = PropertyMock(return_value="id")
        type(model).config = PropertyMock(return_value={})

        with pytest.raises(ValueError) as e:
            EmbeddingService.load_embeddings(model)

        assert str(e.value) == "model field is not defined in config for id"

    def test_load_openai_embeddings_fail_when_model_is_empty_in_embedding_config(self):
        model = MagicMock()
        type(model).provider = PropertyMock(return_value="openai")
        type(model).id = PropertyMock(return_value="id")
        type(model).config = PropertyMock(return_value={"model": ""})

        with pytest.raises(ValueError) as e:
            EmbeddingService.load_embeddings(model)

        assert str(e.value) == "model field is not defined in config for id"

    def test_load_openai_embeddings_fail_when_api_key_is_not_defined_in_embedding_config(
        self,
    ):
        model = MagicMock()
        type(model).provider = PropertyMock(return_value="openai")
        type(model).id = PropertyMock(return_value="id")
        type(model).config = PropertyMock(return_value={"model": "model"})

        with pytest.raises(ValueError) as e:
            EmbeddingService.load_embeddings(model)

        assert str(e.value) == "api_key is not defined in config for id"

    @patch("haiven_cli.services.embedding_service.OpenAIEmbeddings")
    def test_load_openai_embeddings(self, mock_openai_embeddings):
        model = MagicMock()
        model_key = "model"
        api_key = "api_key"
        type(model).provider = PropertyMock(return_value="openai")
        type(model).id = PropertyMock(return_value="id")
        type(model).config = PropertyMock(
            return_value={"model": model_key, "api_key": api_key}
        )

        open_ai_embeddings = MagicMock()
        mock_openai_embeddings.return_value = open_ai_embeddings

        embeddings = EmbeddingService.load_embeddings(model)

        mock_openai_embeddings.assert_called_once_with(model=model_key, api_key=api_key)

        assert embeddings == open_ai_embeddings

    def test_load_azure_embeddings_fail_when_api_key_is_not_defined_in_embedding_config(
        self,
    ):
        model = MagicMock()
        type(model).provider = PropertyMock(return_value="azure")
        type(model).id = PropertyMock(return_value="id")
        type(model).config = PropertyMock(return_value={})

        with pytest.raises(ValueError) as e:
            EmbeddingService.load_embeddings(model)

        assert str(e.value) == "api_key is not defined in config for id"

    def test_load_azure_embeddings_fail_when_azure_endpoint_is_not_defined_in_embedding_config(
        self,
    ):
        model = MagicMock()
        type(model).provider = PropertyMock(return_value="azure")
        type(model).id = PropertyMock(return_value="id")
        type(model).config = PropertyMock(return_value={"api_key": "api_key"})

        with pytest.raises(ValueError) as e:
            EmbeddingService.load_embeddings(model)

        assert str(e.value) == "azure_endpoint is not defined in config for id"

    def test_load_azure_embeddings_fail_when_api_version_is_not_defined_in_embedding_config(
        self,
    ):
        model = MagicMock()
        type(model).provider = PropertyMock(return_value="azure")
        type(model).id = PropertyMock(return_value="id")
        type(model).config = PropertyMock(
            return_value={"api_key": "api_key", "azure_endpoint": "azure_endpoint"}
        )

        with pytest.raises(ValueError) as e:
            EmbeddingService.load_embeddings(model)

        assert str(e.value) == "api_version is not defined in config for id"

    def test_load_azure_embeddings_fail_when_azure_deployment_is_not_defined_in_embedding_config(
        self,
    ):
        model = MagicMock()
        type(model).provider = PropertyMock(return_value="azure")
        type(model).id = PropertyMock(return_value="id")
        type(model).config = PropertyMock(
            return_value={
                "api_key": "api_key",
                "azure_endpoint": "azure_endpoint",
                "api_version": "api_version",
            }
        )

        with pytest.raises(ValueError) as e:
            EmbeddingService.load_embeddings(model)

        assert str(e.value) == "azure_deployment is not defined in config for id"

    @patch("haiven_cli.services.embedding_service.AzureOpenAIEmbeddings")
    def test_load_azure_embeddings(self, mock_az_openai_embeddings):
        model = MagicMock()
        type(model).provider = PropertyMock(return_value="azure")
        type(model).id = PropertyMock(return_value="id")
        api_key = "api_key"
        azure_endpoint = "azure_endpoint"
        api_version = "api_version"
        azure_deployment = "azure_deployment"

        type(model).config = PropertyMock(
            return_value={
                "api_key": api_key,
                "azure_endpoint": azure_endpoint,
                "api_version": api_version,
                "azure_deployment": azure_deployment,
            }
        )

        az_embeddings = MagicMock()
        mock_az_openai_embeddings.return_value = az_embeddings

        embeddings = EmbeddingService.load_embeddings(model)

        mock_az_openai_embeddings.assert_called_once_with(
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            api_version=api_version,
            azure_deployment=azure_deployment,
        )
        assert embeddings == az_embeddings

    def test_load_aws_embeddings_fail_when_aws_region_is_not_defined_in_embedding_config(
        self,
    ):
        model = MagicMock()
        type(model).provider = PropertyMock(return_value="aws")
        type(model).id = PropertyMock(return_value="id")
        type(model).config = PropertyMock(return_value={})

        with pytest.raises(ValueError) as e:
            EmbeddingService.load_embeddings(model)

        assert str(e.value) == "aws_region is not defined in config for id"

    @patch("haiven_cli.services.embedding_service.BedrockEmbeddings")
    def test_load_aws_embeddings(self, mock_bedrock_embeddings):
        model = MagicMock()
        type(model).provider = PropertyMock(return_value="aws")
        type(model).id = PropertyMock(return_value="id")
        aws_region = "aws_region"
        type(model).config = PropertyMock(return_value={"aws_region": aws_region})

        bedrock_embeddings = MagicMock()
        mock_bedrock_embeddings.return_value = bedrock_embeddings

        embeddings = EmbeddingService.load_embeddings(model)

        mock_bedrock_embeddings.assert_called_once_with(region_name=aws_region)
        assert bedrock_embeddings == embeddings

    def test_load_ollama_embeddings_fail_when_base_url_is_not_defined_in_embedding_config(
        self,
    ):
        model = MagicMock()
        type(model).provider = PropertyMock(return_value="ollama")
        type(model).id = PropertyMock(return_value="id")
        type(model).config = PropertyMock(return_value={})

        with pytest.raises(ValueError) as e:
            EmbeddingService.load_embeddings(model)

        assert str(e.value) == "base_url is not defined in config for id"

    @patch("haiven_cli.services.embedding_service.OllamaEmbeddings")
    def test_load_ollama_embeddings(self, mock_ollama_embeddings):
        model = MagicMock()
        type(model).provider = PropertyMock(return_value="ollama")
        type(model).id = PropertyMock(return_value="id")
        base_url_value = "some_base_url"
        model_value = "some_model"
        type(model).config = PropertyMock(
            return_value={"base_url": base_url_value, "model": model_value}
        )

        ollama_embeddings = MagicMock
        mock_ollama_embeddings.return_value = ollama_embeddings

        embeddings = EmbeddingService.load_embeddings(model)

        mock_ollama_embeddings.assert_called_once_with(
            base_url=base_url_value, model=model_value
        )

        assert ollama_embeddings == embeddings
