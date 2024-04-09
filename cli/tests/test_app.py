# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import pytest

from app.app import App
from unittest.mock import MagicMock, PropertyMock, patch, mock_open


class TestApp:
    def test_index_individual_file_raise_error_if_source_path_is_not_set(self):
        source_path = ""
        embedding_model = "an embedding model"
        config_path = "a config path"

        config_service = MagicMock()
        file_service = MagicMock()
        knowledge_service = MagicMock()
        app = App(config_service, file_service, knowledge_service)

        with pytest.raises(ValueError) as e:
            app.index_individual_file(source_path, embedding_model, config_path)

        assert str(e.value) == "please provide file path for source_path option"

    def test_index_individual_file_raise_error_if_file_is_not_txt_or_pdf(self):
        source_path = "file.whatever"
        embedding_model = "an embedding model"
        config_path = "a config path"

        config_service = MagicMock()
        file_service = MagicMock()
        knowledge_service = MagicMock()
        app = App(config_service, file_service, knowledge_service)

        with pytest.raises(ValueError) as e:
            app.index_individual_file(source_path, embedding_model, config_path)

        assert str(e.value) == "source file needs to be .txt or .pdf file"

    def test_index_individual_file_raise_error_if_embedding_is_not_defined_in_config(
        self,
    ):
        source_path = "file.txt"
        embedding_model = "an embedding model"
        config_path = "test_config.yaml"

        config_embeddings = []
        config_service = MagicMock()
        config_service.load_embeddings.return_value = config_embeddings
        file_service = MagicMock()
        knowledge_service = MagicMock()
        app = App(config_service, file_service, knowledge_service)

        with pytest.raises(ValueError) as e:
            app.index_individual_file(source_path, embedding_model, config_path)

        config_service.load_embeddings.assert_called_once_with(config_path)
        assert (
            str(e.value)
            == "embeddings are not defined in test_config.yaml\nUsable models according to config file:"
        )

    @patch("builtins.open", new_callable=mock_open)
    def test_index_individual_file_from_txt_file(self, mock_file):
        source_path = "file.txt"
        embedding_model = "an embedding model"
        config_path = "test_config.yaml"

        embedding = MagicMock()
        type(embedding).id = PropertyMock(return_value=embedding_model)
        config_embeddings = [embedding]
        config_service = MagicMock()
        config_service.load_embeddings.return_value = config_embeddings

        knowledge_service = MagicMock()
        knowledge_service.return_value = knowledge_service

        file_service = MagicMock()

        file_content = "the file content"
        file = MagicMock()
        file.read.return_value = file_content
        mock_file.return_value.__enter__.return_value = file

        app = App(config_service, file_service, knowledge_service)

        app.index_individual_file(source_path, embedding_model, config_path)

        config_service.load_embeddings.assert_called_once_with(config_path)
        mock_file.assert_called_once_with(source_path, "r")
        knowledge_service.index.assert_called_once_with(
            [file_content], [{"file": source_path}], embedding
        )

    @patch("builtins.open", new_callable=mock_open)
    def test_index_individual_pdf_file(self, mock_file):
        source_path = "file.pdf"
        embedding_model = "an embedding model"
        config_path = "test_config.yaml"

        embedding = MagicMock()
        type(embedding).id = PropertyMock(return_value=embedding_model)
        config_embeddings = [embedding]
        config_service = MagicMock()
        config_service.load_embeddings.return_value = config_embeddings

        knowledge_service = MagicMock()

        file_content = "the file content"
        metadatas = MagicMock()

        file = MagicMock()
        mock_file.return_value.__enter__.return_value = file
        file_service = MagicMock()
        file_service.get_text_and_metadata_from_pdf.return_value = (
            file_content,
            metadatas,
        )

        app = App(config_service, file_service, knowledge_service)
        app.index_individual_file(source_path, embedding_model, config_path)

        config_service.load_embeddings.assert_called_once_with(config_path)
        mock_file.assert_called_once_with(source_path, "rb")
        file_service.get_text_and_metadata_from_pdf.assert_called_once_with(file)
        knowledge_service.index.assert_called_once_with(
            file_content, metadatas, embedding
        )

    def test_index_all_files_fails_if_source_dir_is_not_set(self):
        source_dir = ""
        embedding_model = "embedding_model"
        config_path = "config_path"

        config_service = MagicMock()
        file_service = MagicMock()
        knowledge_service = MagicMock()
        app = App(config_service, file_service, knowledge_service)

        with pytest.raises(ValueError) as e:
            app.index_all_files(source_dir, embedding_model, config_path)

        assert str(e.value) == "please provide directory path for source_dir option"

    def test_index_all_files_fails_if_embedding_model_is_not_defined_in_config(self):
        source_dir = "source_dir"
        embedding_model = "embedding_model"
        config_path = "config_path"

        config_service = MagicMock()
        config_service.load_embeddings.return_value = []
        file_service = MagicMock()
        knowledge_service = MagicMock()
        app = App(config_service, file_service, knowledge_service)

        with pytest.raises(ValueError) as e:
            app.index_all_files(source_dir, embedding_model, config_path)

        assert (
            str(e.value)
            == "embeddings are not defined in config_path\nUsable models according to config file:"
        )

    def test_index_all_files_does_not_index_non_pdf_or_txt_files(self):
        source_dir = "source_dir"
        embedding_model = "embedding_model"
        config_path = "config_path"

        embedding = MagicMock()
        type(embedding).id = PropertyMock(return_value=embedding_model)
        config_embeddings = [embedding]
        config_service = MagicMock()
        config_service.load_embeddings.return_value = config_embeddings
        file_path = "file_path"
        file_service = MagicMock()
        file_service.get_files_from_directory.return_value = [file_path]
        knowledge_service = MagicMock()
        app = App(config_service, file_service, knowledge_service)

        app.index_all_files(source_dir, embedding_model, config_path)

        file_service.get_files_path_from_directory.assert_called_once_with(source_dir)
        assert knowledge_service.index.call_count == 0

    @patch("builtins.open", new_callable=mock_open)
    def test_index_all_files(self, mock_file):
        source_dir = "source_dir"
        embedding_model = "embedding_model"
        config_path = "config_path"

        embedding = MagicMock()
        type(embedding).id = PropertyMock(return_value=embedding_model)
        config_embeddings = [embedding]
        config_service = MagicMock()
        config_service.load_embeddings.return_value = config_embeddings
        first_file_path = "file_path.txt"

        first_file_content = "the file content"
        first_file = MagicMock()
        first_file.read.return_value = first_file_content

        second_file_path = "file_path.pdf"
        second_file_content = "the second file content"
        second_file_metadata = MagicMock()
        second_file = MagicMock()

        mock_file.return_value.__enter__.side_effect = [first_file, second_file]

        file_service = MagicMock()
        file_service.get_files_path_from_directory.return_value = (
            first_file_path,
            second_file_path,
        )

        knowledge_service = MagicMock()
        file_service.get_text_and_metadata_from_pdf.return_value = (
            second_file_content,
            second_file_metadata,
        )

        app = App(config_service, file_service, knowledge_service)
        app.index_all_files(source_dir, embedding_model, config_path)

        file_service.get_files_path_from_directory.assert_called_once_with(source_dir)
        file_service.get_text_and_metadata_from_pdf.assert_called_once_with(second_file)

        knowledge_service.index.call_count == 2
