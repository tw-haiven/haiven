# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import pytest

from teamai_cli.services.knowledge_service import KnowledgeService
from unittest.mock import MagicMock, patch, mock_open


class TestKnowledgeService:
    def test_save_knowledge_to_path_raises_error_if_text_is_None(self):
        text = None
        metadatas = {}
        embedding_model = MagicMock()
        knowledge_base_path = "test knowledge base path"

        token_service = MagicMock()
        knowledge_service = KnowledgeService(knowledge_base_path, token_service)

        with pytest.raises(ValueError) as e:
            knowledge_service.index(text, metadatas, embedding_model)
        assert str(e.value) == "file content has no value"

    def test_save_knowledge_to_path_raises_error_if_text_is_empty(self):
        text = ""
        metadatas = {}
        embedding_model = MagicMock()
        knowledge_base_path = "test knowledge base path"

        token_service = MagicMock()
        knowledge_service = KnowledgeService(knowledge_base_path, token_service)

        with pytest.raises(ValueError) as e:
            knowledge_service.index(text, metadatas, embedding_model)
        assert str(e.value) == "file content has no value"

    def test_save_knowledge_to_path_raises_error_if_embedding_is_none(self):
        text = "something cool"
        metadatas = {}
        embedding_model = None
        knowledge_base_path = "test knowledge base path"
        token_service = MagicMock()
        knowledge_service = KnowledgeService(knowledge_base_path, token_service)

        with pytest.raises(ValueError) as e:
            knowledge_service.index(text, metadatas, embedding_model)
        assert str(e.value) == "embedding model has no value"

    @patch("teamai_cli.services.knowledge_service.FAISS")
    @patch("teamai_cli.services.knowledge_service.EmbeddingService")
    @patch("teamai_cli.services.knowledge_service.RecursiveCharacterTextSplitter")
    def test_save_knowledge_to_new_path(
        self, mock_text_splitter, mock_embedding_service, mock_faiss
    ):
        text = "something cool"
        texts = [text]
        metadatas = {}
        embedding_model = MagicMock()
        knowledge_base_path = "test knowledge base path"

        token_service = MagicMock()

        documents = MagicMock()
        text_splitter = MagicMock()
        text_splitter.create_documents.return_value = documents
        mock_text_splitter.return_value = text_splitter

        embeddings = MagicMock()
        mock_embedding_service.load_embeddings.return_value = embeddings

        local_db = MagicMock()
        mock_faiss.from_documents.return_value = local_db
        mock_faiss.load_local.side_effect = ValueError("Some Error")

        knowledge_service = KnowledgeService(knowledge_base_path, token_service)
        knowledge_service.index(texts, metadatas, embedding_model)

        mock_text_splitter.assert_called_once_with(
            chunk_size=100,
            chunk_overlap=20,
            length_function=token_service.get_tokens_length,
            separators=["\n\n", "\n", " ", ""],
        )
        text_splitter.create_documents.assert_called_once_with(texts, metadatas)
        mock_embedding_service.load_embeddings.assert_called_once_with(embedding_model)
        mock_faiss.from_documents.assert_called_once_with(documents, embeddings)
        mock_faiss.load_local.assert_called_once_with(knowledge_base_path, embeddings)
        local_db.save_local.assert_called_once_with(knowledge_base_path)

    @patch("teamai_cli.services.knowledge_service.FAISS")
    @patch("teamai_cli.services.knowledge_service.EmbeddingService")
    @patch("teamai_cli.services.knowledge_service.RecursiveCharacterTextSplitter")
    def test_save_knowledge_to_existing_path(
        self, mock_text_splitter, mock_embedding_service, mock_faiss
    ):
        text = "something cool"
        texts = [text]
        metadatas = {}
        embedding_model = MagicMock()
        knowledge_base_path = "test knowledge base path"

        token_service = MagicMock()

        documents = MagicMock()
        text_splitter = MagicMock()
        text_splitter.create_documents.return_value = documents
        mock_text_splitter.return_value = text_splitter

        embeddings = MagicMock()
        mock_embedding_service.load_embeddings.return_value = embeddings

        local_db = MagicMock()
        mock_faiss.from_documents.return_value = local_db
        db = MagicMock()
        mock_faiss.load_local.return_value = db

        knowledge_service = KnowledgeService(knowledge_base_path, token_service)
        knowledge_service.index(texts, metadatas, embedding_model)

        mock_text_splitter.assert_called_once_with(
            chunk_size=100,
            chunk_overlap=20,
            length_function=token_service.get_tokens_length,
            separators=["\n\n", "\n", " ", ""],
        )
        text_splitter.create_documents.assert_called_once_with(texts, metadatas)
        mock_embedding_service.load_embeddings.assert_called_once_with(embedding_model)
        mock_faiss.from_documents.assert_called_once_with(documents, embeddings)
        mock_faiss.load_local.assert_called_once_with(knowledge_base_path, embeddings)
        db.merge_from.assert_called_once_with(local_db)
        db.save_local.assert_called_once_with(knowledge_base_path)

    @patch("builtins.open", new_callable=mock_open)
    @patch("teamai_cli.services.knowledge_service.pickle")
    def test_pickle_documents(self, mock_pickle, mock_file):
        file = MagicMock()
        mock_file.return_value.__enter__.return_value = file
        documents = [MagicMock()]
        path = "test path"
        knowledge_service = KnowledgeService("test knowledge base path", MagicMock())
        knowledge_service.pickle_documents(documents, path)

        mock_file.assert_called_once_with(path, "wb")
        mock_pickle.dump.assert_called_once_with(documents, file)
