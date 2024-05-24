# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import pytest

from haiven_cli.services.knowledge_service import KnowledgeService
from unittest.mock import MagicMock, patch


class TestKnowledgeService:
    def test_save_knowledge_to_path_raises_error_if_text_is_None(self):
        text = None
        metadatas = {}
        embedding_model = MagicMock()
        ouput_dir = "test knowledge base path"

        token_service = MagicMock()
        embedding_service = MagicMock()
        knowledge_service = KnowledgeService(token_service, embedding_service)

        with pytest.raises(ValueError) as e:
            knowledge_service.index(text, metadatas, embedding_model, ouput_dir)
        assert str(e.value) == "file content has no value"

    def test_save_knowledge_to_path_raises_error_if_text_is_empty(self):
        text = ""
        metadatas = {}
        embedding_model = MagicMock()
        ouput_dir = "test knowledge base path"

        token_service = MagicMock()
        embedding_service = MagicMock()
        knowledge_service = KnowledgeService(token_service, embedding_service)

        with pytest.raises(ValueError) as e:
            knowledge_service.index(text, metadatas, embedding_model, ouput_dir)
        assert str(e.value) == "file content has no value"

    def test_save_knowledge_to_path_raises_error_if_embedding_is_none(self):
        text = "something cool"
        metadatas = {}
        embedding_model = None
        ouput_dir = "test knowledge base path"
        token_service = MagicMock()
        embedding_service = MagicMock()
        knowledge_service = KnowledgeService(token_service, embedding_service)

        with pytest.raises(ValueError) as e:
            knowledge_service.index(text, metadatas, embedding_model, ouput_dir)
        assert str(e.value) == "embedding model has no value"

    @patch("haiven_cli.services.knowledge_service.FAISS")
    @patch("haiven_cli.services.knowledge_service.RecursiveCharacterTextSplitter")
    def test_save_knowledge_to_new_path(self, mock_text_splitter, mock_faiss):
        text = "something cool"
        texts = [text]
        metadatas = {}
        embedding_model = MagicMock()
        ouput_dir = "test knowledge base path"

        token_service = MagicMock()

        documents = MagicMock()
        text_splitter = MagicMock()
        text_splitter.create_documents.return_value = documents
        mock_text_splitter.return_value = text_splitter

        embeddings = MagicMock()
        embedding_service = MagicMock()
        embedding_service.load_embeddings.return_value = embeddings

        local_db = MagicMock()
        mock_faiss.from_documents.return_value = local_db
        mock_faiss.load_local.side_effect = ValueError("Some Error")

        knowledge_service = KnowledgeService(token_service, embedding_service)
        knowledge_service.index(texts, metadatas, embedding_model, ouput_dir)

        mock_text_splitter.assert_called_once_with(
            chunk_size=100,
            chunk_overlap=20,
            length_function=token_service.get_tokens_length,
            separators=["\n\n", "\n", " ", ""],
        )
        text_splitter.create_documents.assert_called_once_with(texts, metadatas)
        embedding_service.load_embeddings.assert_called_once_with(embedding_model)
        mock_faiss.from_documents.assert_called_once_with(documents, embeddings)
        mock_faiss.load_local.assert_called_once_with(ouput_dir, embeddings)
        local_db.save_local.assert_called_once_with(ouput_dir)

    @patch("haiven_cli.services.knowledge_service.FAISS")
    @patch("haiven_cli.services.knowledge_service.RecursiveCharacterTextSplitter")
    def test_save_knowledge_to_existing_path(self, mock_text_splitter, mock_faiss):
        text = "something cool"
        texts = [text]
        metadatas = {}
        embedding_model = MagicMock()
        ouput_dir = "test knowledge base path"

        token_service = MagicMock()

        documents = MagicMock()
        text_splitter = MagicMock()
        text_splitter.create_documents.return_value = documents
        mock_text_splitter.return_value = text_splitter

        embeddings = MagicMock()
        embedding_service = MagicMock()
        embedding_service.load_embeddings.return_value = embeddings

        local_db = MagicMock()
        mock_faiss.from_documents.return_value = local_db
        db = MagicMock()
        mock_faiss.load_local.return_value = db

        knowledge_service = KnowledgeService(token_service, embedding_service)
        knowledge_service.index(texts, metadatas, embedding_model, ouput_dir)

        mock_text_splitter.assert_called_once_with(
            chunk_size=100,
            chunk_overlap=20,
            length_function=token_service.get_tokens_length,
            separators=["\n\n", "\n", " ", ""],
        )
        text_splitter.create_documents.assert_called_once_with(texts, metadatas)
        embedding_service.load_embeddings.assert_called_once_with(embedding_model)
        mock_faiss.from_documents.assert_called_once_with(documents, embeddings)
        mock_faiss.load_local.assert_called_once_with(ouput_dir, embeddings)
        db.merge_from.assert_called_once_with(local_db)
        db.save_local.assert_called_once_with(ouput_dir)
