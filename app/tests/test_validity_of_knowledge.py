# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import os
from unittest import mock

import pytest
from shared.models.embedding_model import EmbeddingModel
from shared.knowledge import (
    KnowledgeBaseDocuments,
    KnowledgeBaseMarkdown,
    KnowledgeBasePDFs,
)


@pytest.mark.skip(
    reason="This moved to a different path, plan is to move this check into startup routine with next commit"
)
def test_markdown_knowledge():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    teams_dir = os.path.join(root_dir, "teams")

    knowledge_base_markdown = KnowledgeBaseMarkdown("team_demo", root_dir=teams_dir)

    knowledge_dict = knowledge_base_markdown.get_knowledge_content_dict()

    for key, value in knowledge_dict.items():
        assert isinstance(key, str), "Key is not a string"
        assert isinstance(value, str), "Value is not a string"


@pytest.mark.skip(
    reason="This moved to a different path, plan is to move this check into startup routine with next commit"
)
@mock.patch("shared.services.config_service.ConfigService.load_embedding_model")
def test_pdfs_knowledge(load_embedding_model_mock):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    teams_dir = os.path.join(root_dir, "teams")

    embedding_model = EmbeddingModel(
        id="ada",
        provider="azure",
        name="Ada",
        config={
            "api_key": "bogus",
            "azure_endpoint": "bogus",
            "api_version": "bogus",
            "azure_deployment": "bogus",
        },
    )
    load_embedding_model_mock.return_value = embedding_model

    knowledge_base_pdfs = KnowledgeBasePDFs(
        "team_demo", root_dir=teams_dir, config_file_path="app/config.yaml"
    )
    knowledge_dict = knowledge_base_pdfs.get_knowledge()

    assert len(knowledge_dict.items()) == 3

    for key, value in knowledge_dict.items():
        assert isinstance(key, str), "Key is not a string"
        assert isinstance(value.title, str), "Title does not exist"
        assert isinstance(value.retriever, object), "Retriever does not exist"
        assert isinstance(
            value.provider, object
        ), "Need to know which provider created the embeddings (openai, ollama, ...)"


@pytest.mark.skip(
    reason="This moved to a different path, plan is to move this check into startup routine with next commit"
)
@mock.patch("shared.services.config_service.ConfigService.load_embedding_model")
def test_documents_knowledge(load_embedding_model_mock):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    teams_dir = os.path.join(root_dir, "teams")

    embedding_model = EmbeddingModel(
        id="ada",
        provider="azure",
        name="Ada",
        config={
            "api_key": "bogus",
            "azure_endpoint": "bogus",
            "api_version": "bogus",
            "azure_deployment": "bogus",
        },
    )
    load_embedding_model_mock.return_value = embedding_model

    knowledge_base_docs = KnowledgeBaseDocuments("team_demo", root_dir=teams_dir)
    knowledge_dict = knowledge_base_docs.get_knowledge()

    assert len(knowledge_dict.items()) == 1

    for key, value in knowledge_dict.items():
        assert isinstance(key, str), "Key is not a string"
        assert isinstance(value.title, str), "Title does not exist"
        assert isinstance(value.retriever, object), "Retriever does not exist"
        assert isinstance(
            value.provider, object
        ), "Need to know which provider created the embeddings (openai, ollama, ...)"
