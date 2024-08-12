# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from unittest import mock

import pytest
from embeddings.embeddings import Embeddings
from embeddings.embedding_model import EmbeddingModel


class TestEmbeddings:
    def test_generate_from_documents_fails_when_provider_not_supported(self):
        # given I have a list of Documents and a model
        embedding_config = EmbeddingModel(
            id="text-embedding-ada-002",
            name="Ada",
            provider="unknown_provider",
            config={"api_key": ""},
        )

        # when I call the function get_embeddings an error should be raised
        with pytest.raises(ValueError) as e:
            Embeddings(embedding_config)

        assert str(e.value) == "Provider unknown_provider not supported"

    def test_generate_from_documents_for_openai_api_fails_when_config_is_not_set(
        self,
    ):
        # given I have a list of Documents and a model
        embedding_config = EmbeddingModel(
            id="text-embedding-ada-002",
            name="Ada",
            provider="OpenAI",
            config={"model": "text-embedding-3-small", "api_key": ""},
        )

        # when I call the function get_embeddings an error should be raised
        with pytest.raises(ValueError) as e:
            Embeddings(embedding_config)

        assert str(e.value) == "api_key config is not set for the given embedding model"

        embedding_config = EmbeddingModel(
            id="text-embedding-ada-002",
            name="Ada",
            provider="OpenAI",
            config={"model": "", "api_key": "api-key"},
        )

        # when I call the function get_embeddings an error should be raised
        with pytest.raises(ValueError) as e:
            Embeddings(embedding_config)

        assert str(e.value) == "model config is not set for the given embedding model"

    def test_generate_from_documents_for_azure_api_fails_when_config_is_not_set(
        self,
    ):
        # given I have a list of Documents and a model
        text = "text"
        metadata = "metadata"

        azure_openai_api_key = "azure_openai_key"
        azure_endpoint = "https://test.openai.azure.com"
        azure_deployment_name = "test-deployment"
        azure_api_version = "2024-01-01-test"

        embedding_model = EmbeddingModel(
            id="text-embedding-ada-002",
            name="Ada",
            provider="Azure",
            config={
                "api_key": "",
                "azure_endpoint": azure_endpoint,
                "azure_deployment": azure_deployment_name,
                "api_version": azure_api_version,
            },
        )

        # when I call the function get_embeddings an error should be raised
        with pytest.raises(ValueError) as e:
            Embeddings(embedding_model)

        assert str(e.value) == "api_key config is not set for the given embedding model"

        embedding_model = EmbeddingModel(
            id="text-embedding-ada-002",
            name="Ada",
            provider="Azure",
            config={
                "api_key": azure_openai_api_key,
                "azure_endpoint": "",
                "azure_deployment": azure_deployment_name,
                "api_version": azure_api_version,
            },
        )

        # when I call the function get_embeddings an error should be raised
        with pytest.raises(ValueError) as e:
            Embeddings(embedding_model)

        assert (
            str(e.value)
            == "azure_endpoint config is not set for the given embedding model"
        )

        embedding_model = EmbeddingModel(
            id="text-embedding-ada-002",
            name="Ada",
            provider="Azure",
            config={
                "api_key": azure_openai_api_key,
                "azure_endpoint": azure_endpoint,
                "azure_deployment": "",
                "api_version": azure_api_version,
            },
        )

        # when I call the function get_embeddings an error should be raised
        with pytest.raises(ValueError) as e:
            embeddings = Embeddings(embedding_model)
            embeddings.generate_from_documents(text, metadata)
        assert (
            str(e.value)
            == "azure_deployment config is not set for the given embedding model"
        )

        embedding_model = EmbeddingModel(
            id="text-embedding-ada-002",
            name="Ada",
            provider="Azure",
            config={
                "api_key": azure_openai_api_key,
                "azure_endpoint": azure_endpoint,
                "azure_deployment": azure_deployment_name,
                "api_version": "",
            },
        )

        # when I call the function get_embeddings an error should be raised
        with pytest.raises(ValueError) as e:
            Embeddings(embedding_model)

        assert (
            str(e.value)
            == "api_version config is not set for the given embedding model"
        )

    def test_generate_from_documents_for_aws_api_fails_when_config_is_not_set(
        self,
    ):
        embedding_model = EmbeddingModel(
            id="amazon.titan-text-express-v1",
            name="Titan text Embedding on AWS",
            provider="AWS",
            config={
                "aws_region": "",
            },
        )

        # when I call the function get_embeddings an error should be raised
        with pytest.raises(ValueError) as e:
            Embeddings(embedding_model)

        assert (
            str(e.value) == "aws_region config is not set for the given embedding model"
        )

    @mock.patch("embeddings.embeddings.FAISS.load_local")
    @mock.patch("embeddings.embeddings.FAISS.from_documents")
    @mock.patch("embeddings.embeddings.RecursiveCharacterTextSplitter")
    @mock.patch("embeddings.embeddings.OpenAIEmbeddings")
    def test_generate_openai_provider_embeddings(
        self,
        openai_embeddings_mock,
        text_splitter_mock,
        from_documents_mock,
        load_local_mock,
    ):
        # given I have a list of Documents and a model
        openai_model = "text-embedding-3-small"
        openai_api_key = "azure_openai_key"
        text = "text"
        metadata = "metadata"
        embedding_config = EmbeddingModel(
            id="text-embedding-ada-002",
            name="Ada",
            provider="OpenAI",
            config={"model": openai_model, "api_key": openai_api_key},
        )

        text_splitter = mock.MagicMock()
        text_splitter_mock.return_value = text_splitter

        faiss_embeddings = "faiss_embeddings"
        from_documents_mock.return_value = faiss_embeddings

        embeddings = Embeddings(embedding_config)
        # when I call the function get_embeddings with the documents and a known model_id
        returned_embeddings = embeddings.generate_from_documents(text, metadata)

        # then embeddings generated by faiss should be returned
        assert returned_embeddings == faiss_embeddings
        text_splitter_mock.assert_called_with(
            chunk_size=500,
            chunk_overlap=80,
            length_function=embeddings._tiktoken_len,
            separators=["\n\n", "\n", " ", ""],
        )
        openai_embeddings_mock.assert_called_with(
            model=openai_model, api_key=openai_api_key
        )
        from_documents_mock.assert_called_with(
            text_splitter_mock().create_documents(), openai_embeddings_mock()
        )

        folder_path = "folder_path"
        embeddings.generate_from_filesystem(folder_path)
        load_local_mock.assert_called_with(
            folder_path=folder_path,
            embeddings=openai_embeddings_mock(),
            allow_dangerous_deserialization=True,
        )

    @mock.patch("embeddings.embeddings.FAISS.from_documents")
    @mock.patch("embeddings.embeddings.RecursiveCharacterTextSplitter")
    @mock.patch("embeddings.embeddings.AzureOpenAIEmbeddings")
    def test_generate_azure_provider_embeddings(
        self, azure_openai_embeddings_mock, text_splitter_mock, from_documents_mock
    ):
        # given I have a list of Documents and a model
        azure_openai_api_key = "azure_openai_key"
        azure_endpoint = "https://test.openai.azure.com"
        azure_deployment_name = "test-deployment"
        azure_api_version = "2024-01-01-test"
        text = "text"
        metadata = "metadata"
        embedding_config = EmbeddingModel(
            id="text-embedding-ada-002",
            name="Ada",
            provider="Azure",
            config={
                "api_key": azure_openai_api_key,
                "azure_endpoint": azure_endpoint,
                "azure_deployment": azure_deployment_name,
                "api_version": azure_api_version,
            },
        )

        text_splitter = mock.MagicMock()
        text_splitter_mock.return_value = text_splitter

        faiss_embeddings = "faiss_embeddings"
        from_documents_mock.return_value = faiss_embeddings

        embeddings = Embeddings(embedding_config)
        # when I call the function get_embeddings with the documents and a known model_id
        returned_embeddings = embeddings.generate_from_documents(text, metadata)

        # then embeddings generated by faiss should be returned
        assert returned_embeddings == faiss_embeddings
        text_splitter_mock.assert_called_with(
            chunk_size=500,
            chunk_overlap=80,
            length_function=embeddings._tiktoken_len,
            separators=["\n\n", "\n", " ", ""],
        )
        azure_openai_embeddings_mock.assert_called_with(
            api_key=azure_openai_api_key,
            azure_endpoint=azure_endpoint,
            azure_deployment=azure_deployment_name,
            api_version=azure_api_version,
        )
        from_documents_mock.assert_called_with(
            text_splitter_mock().create_documents(), azure_openai_embeddings_mock()
        )

    @mock.patch("embeddings.embeddings.FAISS.load_local")
    @mock.patch("embeddings.embeddings.FAISS.from_documents")
    @mock.patch("embeddings.embeddings.RecursiveCharacterTextSplitter")
    @mock.patch("embeddings.embeddings.BedrockEmbeddings")
    def test_generate_aws_provider_embeddings(
        self,
        bedrock_embeddings_mock,
        text_splitter_mock,
        from_documents_mock,
        load_local_mock,
    ):
        embedding_config = EmbeddingModel(
            id="amazon.titan-text-express-v1",
            name="Titan text Embedding on AWS",
            provider="AWS",
            config={
                "aws_region": "us-east-1",
            },
        )

        text_splitter = mock.MagicMock()
        text_splitter_mock.return_value = text_splitter

        faiss_embeddings = "faiss_embeddings"
        from_documents_mock.return_value = faiss_embeddings

        embeddings = Embeddings(embedding_config)
        # when I call the function get_embeddings with the documents and a known model_id
        returned_embeddings = embeddings.generate_from_documents("text", "metadata")

        # then embeddings generated by faiss should be returned
        assert returned_embeddings == faiss_embeddings
        text_splitter_mock.assert_called_with(
            chunk_size=500,
            chunk_overlap=80,
            length_function=embeddings._tiktoken_len,
            separators=["\n\n", "\n", " ", ""],
        )

        bedrock_embeddings_mock.assert_called_with(
            region_name=embedding_config.config.get("aws_region")
        )

        from_documents_mock.assert_called_with(
            text_splitter_mock().create_documents(), bedrock_embeddings_mock()
        )

        folder_path = "folder_path"
        embeddings.generate_from_filesystem(folder_path)
        load_local_mock.assert_called_with(
            folder_path=folder_path,
            embeddings=bedrock_embeddings_mock(),
            allow_dangerous_deserialization=True,
        )
