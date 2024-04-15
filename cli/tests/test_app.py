# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import pytest

from teamai_cli.app.app import App
from unittest.mock import call, MagicMock, PropertyMock, patch, mock_open


class TestApp:
    def test_index_individual_file_raise_error_if_source_path_is_not_set(self):
        source_path = ""
        embedding_model = "an embedding model"
        config_path = "a config path"
        output_dir = "output_dir"
        metadata = {}

        config_service = MagicMock()
        file_service = MagicMock()
        knowledge_service = MagicMock()
        web_page_service = MagicMock()

        app = App(config_service, file_service, knowledge_service, web_page_service)

        with pytest.raises(ValueError) as e:
            app.index_individual_file(
                source_path, embedding_model, config_path, output_dir, metadata
            )

        assert str(e.value) == "please provide file path for source_path option"

    def test_index_individual_file_raise_error_if_file_is_not_txt_or_pdf(self):
        source_path = "file.whatever"
        embedding_model = "an embedding model"
        config_path = "a config path"
        output_dir = "output_dir"
        metadata = {}

        config_service = MagicMock()
        file_service = MagicMock()
        knowledge_service = MagicMock()
        web_page_service = MagicMock()

        app = App(config_service, file_service, knowledge_service, web_page_service)

        with pytest.raises(ValueError) as e:
            app.index_individual_file(
                source_path, embedding_model, config_path, output_dir, metadata
            )

        assert str(e.value) == "source file needs to be .txt or .pdf file"

    def test_index_individual_file_raise_error_if_embedding_is_not_defined_in_config(
        self,
    ):
        source_path = "file.txt"
        embedding_model = "an embedding model"
        config_path = "test_config.yaml"
        output_dir = "output_dir"
        metadata = {}

        config_embeddings = []
        config_service = MagicMock()
        config_service.load_embeddings.return_value = config_embeddings
        file_service = MagicMock()
        knowledge_service = MagicMock()
        web_page_service = MagicMock()

        app = App(config_service, file_service, knowledge_service, web_page_service)

        with pytest.raises(ValueError) as e:
            app.index_individual_file(
                source_path, embedding_model, config_path, output_dir, metadata
            )

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
        output_dir = "output_dir"
        metadata = {}

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

        web_page_service = MagicMock()

        app = App(config_service, file_service, knowledge_service, web_page_service)

        app.index_individual_file(
            source_path, embedding_model, config_path, output_dir, metadata
        )

        config_service.load_embeddings.assert_called_once_with(config_path)
        mock_file.assert_called_once_with(source_path, "r")
        knowledge_service.index.assert_called_once_with(
            [file_content], [{"file": source_path}], embedding, "output_dir/file.kb"
        )
        file_service.write_metadata_file.assert_called_once_with(
            metadata, "output_dir/file.md"
        )

    @patch("builtins.open", new_callable=mock_open)
    def test_index_individual_pdf_file(self, mock_file):
        source_path = "file.pdf"
        embedding_model = "an embedding model"
        config_path = "test_config.yaml"
        output_dir = "output_dir"
        metadata = {}

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

        web_page_service = MagicMock()

        app = App(config_service, file_service, knowledge_service, web_page_service)
        app.index_individual_file(
            source_path, embedding_model, config_path, output_dir, metadata
        )

        config_service.load_embeddings.assert_called_once_with(config_path)
        mock_file.assert_called_once_with(source_path, "rb")
        file_service.get_text_and_metadata_from_pdf.assert_called_once_with(file)
        knowledge_service.index.assert_called_once_with(
            file_content, metadatas, embedding, "output_dir/file.kb"
        )
        file_service.write_metadata_file.assert_called_once_with(
            metadata, "output_dir/file.md"
        )

    def test_index_all_files_fails_if_source_dir_is_not_set(self):
        source_dir = ""
        embedding_model = "embedding_model"
        config_path = "config_path"
        output_dir = "output_dir"
        metadata = {}

        config_service = MagicMock()
        file_service = MagicMock()
        knowledge_service = MagicMock()
        web_page_service = MagicMock()

        app = App(config_service, file_service, knowledge_service, web_page_service)

        with pytest.raises(ValueError) as e:
            app.index_all_files(
                source_dir, embedding_model, config_path, output_dir, metadata
            )

        assert str(e.value) == "please provide directory path for source_dir option"

    def test_index_all_files_fails_if_embedding_model_is_not_defined_in_config(self):
        source_dir = "source_dir"
        embedding_model = "embedding_model"
        config_path = "config_path"
        output_dir = "output_dir"
        metadata = {}

        config_service = MagicMock()
        config_service.load_embeddings.return_value = []
        file_service = MagicMock()
        knowledge_service = MagicMock()
        web_page_service = MagicMock()

        app = App(config_service, file_service, knowledge_service, web_page_service)

        with pytest.raises(ValueError) as e:
            app.index_all_files(
                source_dir, embedding_model, config_path, output_dir, metadata
            )

        assert (
            str(e.value)
            == "embeddings are not defined in config_path\nUsable models according to config file:"
        )

    def test_index_all_files_does_not_index_non_pdf_or_txt_files(self):
        source_dir = "source_dir"
        embedding_model = "embedding_model"
        config_path = "config_path"
        output_dir = "output_dir"
        metadata = {}

        embedding = MagicMock()
        type(embedding).id = PropertyMock(return_value=embedding_model)
        config_embeddings = [embedding]
        config_service = MagicMock()
        config_service.load_embeddings.return_value = config_embeddings
        file_path = "file_path"
        file_service = MagicMock()
        file_service.get_files_from_directory.return_value = [file_path]
        knowledge_service = MagicMock()
        web_page_service = MagicMock()

        app = App(config_service, file_service, knowledge_service, web_page_service)

        app.index_all_files(
            source_dir, embedding_model, config_path, output_dir, metadata
        )

        file_service.get_files_path_from_directory.assert_called_once_with(source_dir)
        assert knowledge_service.index.call_count == 0

    @patch("builtins.open", new_callable=mock_open)
    def test_index_all_files(self, mock_file):
        source_dir = "source_dir"
        embedding_model = "embedding_model"
        config_path = "config_path"
        output_dir = "output_dir"
        metadata = {}

        embedding = MagicMock()
        type(embedding).id = PropertyMock(return_value=embedding_model)
        config_embeddings = [embedding]
        config_service = MagicMock()
        config_service.load_embeddings.return_value = config_embeddings
        first_file_path = "text_file_path.txt"

        first_file_content = "the file content"
        first_file = MagicMock()
        first_file.read.return_value = first_file_content

        second_file_path = "pdf_file_path.pdf"
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

        web_page_service = MagicMock()

        app = App(config_service, file_service, knowledge_service, web_page_service)
        app.index_all_files(
            source_dir, embedding_model, config_path, output_dir, metadata
        )

        file_service.get_files_path_from_directory.assert_called_once_with(source_dir)
        file_service.get_text_and_metadata_from_pdf.assert_called_once_with(second_file)

        knowledge_service.index.assert_has_calls(
            [
                call(
                    [first_file_content],
                    [{"file": first_file_path}],
                    embedding,
                    "output_dir/text_file_path.kb",
                ),
                call(
                    second_file_content,
                    second_file_metadata,
                    embedding,
                    "output_dir/pdf_file_path.kb",
                ),
            ]
        )

        file_service.write_metadata_file.assert_has_calls(
            [
                call(metadata, "output_dir/text_file_path.md"),
                call(metadata, "output_dir/pdf_file_path.md"),
            ]
        )

    def test_index_web_page_fails_if_url_is_not_set(self):
        url = ""
        destination_path = "destination_path"
        html_filter = "html_filter"

        config_service = MagicMock()
        file_service = MagicMock()
        knowledge_service = MagicMock()
        web_page_service = MagicMock()
        app = App(config_service, file_service, knowledge_service, web_page_service)

        with pytest.raises(ValueError) as e:
            app.index_web_page(url, html_filter, destination_path)

        assert str(e.value) == "please provide url for url option"

    def test_index_web_page(self):
        url = "url"
        embedding_model = "embedding_model"
        destination_path = "destination_path"
        html_filter = "html_filter"

        embedding = MagicMock()
        type(embedding).id = PropertyMock(return_value=embedding_model)
        config_embeddings = [embedding]
        config_service = MagicMock()
        config_service.load_embeddings.return_value = config_embeddings
        file_service = MagicMock()
        knowledge_service = MagicMock()
        web_page_article = MagicMock()
        web_page_service = MagicMock()
        web_page_service.get_single_page.return_value = web_page_article
        app = App(config_service, file_service, knowledge_service, web_page_service)

        app.index_web_page(url, html_filter, destination_path)

        knowledge_service.pickle_documents.assert_called_once_with(
            web_page_article, destination_path
        )
