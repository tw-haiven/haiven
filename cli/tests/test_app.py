# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import os
import pytest

from teamai_cli.app.app import App
from unittest.mock import call, MagicMock, PropertyMock, patch, mock_open


class TestApp:
    def test_index_individual_file_raise_error_if_source_path_is_not_set(self):
        source_path = ""
        embedding_model = "an embedding model"
        config_path = "a config path"
        output_dir = "output_dir"
        description = "description"

        config_service = MagicMock()
        file_service = MagicMock()
        knowledge_service = MagicMock()
        metadata_service = MagicMock()

        app = App(
            config_service,
            file_service,
            knowledge_service,
            metadata_service,
        )

        with pytest.raises(ValueError) as e:
            app.index_individual_file(
                source_path, embedding_model, config_path, output_dir, description
            )

        assert str(e.value) == "please provide file path for source_path option"

    def test_index_individual_file_raise_error_if_file_is_not_valid_extension(self):
        source_path = "file.whatever"
        embedding_model = "an embedding model"
        config_path = "a config path"
        output_dir = "output_dir"
        description = "description"

        config_service = MagicMock()
        file_service = MagicMock()
        knowledge_service = MagicMock()
        metadata_service = MagicMock()

        app = App(
            config_service,
            file_service,
            knowledge_service,
            metadata_service,
        )

        with pytest.raises(ValueError) as e:
            app.index_individual_file(
                source_path, embedding_model, config_path, output_dir, description
            )

        assert str(e.value) == "source file needs to be .pdf or .csv file"

    def test_index_individual_file_raise_error_if_embedding_is_not_defined_in_config(
        self,
    ):
        source_path = "file.csv"
        embedding_model = "an embedding model"
        config_path = "test_config.yaml"
        output_dir = "output_dir"
        description = "description"

        config_embeddings = []
        config_service = MagicMock()
        config_service.load_embeddings.return_value = config_embeddings
        file_service = MagicMock()
        knowledge_service = MagicMock()
        metadata_service = MagicMock()

        app = App(
            config_service,
            file_service,
            knowledge_service,
            metadata_service,
        )

        with pytest.raises(ValueError) as e:
            app.index_individual_file(
                source_path, embedding_model, config_path, output_dir, description
            )

        config_service.load_embeddings.assert_called_once_with(config_path)
        assert (
            str(e.value)
            == "embeddings are not defined in test_config.yaml\nUsable models according to config file:"
        )

    @patch("builtins.open", new_callable=mock_open)
    def test_index_individual_csv_file(self, mock_file):
        source_path = "/path/to/file.csv"
        embedding_model = "an embedding model"
        config_path = "test_config.yaml"
        output_dir = "output_dir"
        description = "description"

        embedding = MagicMock()
        type(embedding).id = PropertyMock(return_value=embedding_model)
        config_embeddings = [embedding]
        config_service = MagicMock()
        config_service.load_embeddings.return_value = config_embeddings

        knowledge_service = MagicMock()

        file_content = "the file content"
        metadatas = MagicMock()

        file_service = MagicMock()
        file_service.get_text_and_metadata_from_csv.return_value = (
            file_content,
            metadatas,
        )

        metadata = MagicMock()
        metadata_service = MagicMock()
        metadata_service.create_metadata.return_value = metadata

        app = App(
            config_service,
            file_service,
            knowledge_service,
            metadata_service,
        )

        # Act
        app.index_individual_file(
            source_path, embedding_model, config_path, output_dir, description
        )

        # Assert
        config_service.load_embeddings.assert_called_once_with(config_path)

        file_service.get_text_and_metadata_from_csv.assert_called_once_with(source_path)
        knowledge_service.index.assert_called_once_with(
            file_content, metadatas, embedding, "output_dir/file.kb"
        )
        metadata_service.create_metadata.assert_called_once_with(
            source_path, description, embedding.provider, output_dir
        )
        file_service.write_metadata_file.assert_called_once_with(
            metadata, "output_dir/file.md"
        )

    @patch("builtins.open", new_callable=mock_open)
    def test_index_individual_pdf_file(self, mock_file):
        source_path = "/path/to/file.pdf"
        embedding_model = "an embedding model"
        config_path = "test_config.yaml"
        output_dir = "output_dir"
        description = "description"

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

        metadata = MagicMock()
        metadata_service = MagicMock()
        metadata_service.create_metadata.return_value = metadata

        app = App(
            config_service,
            file_service,
            knowledge_service,
            metadata_service,
        )

        # Act
        app.index_individual_file(
            source_path, embedding_model, config_path, output_dir, description
        )

        config_service.load_embeddings.assert_called_once_with(config_path)
        mock_file.assert_called_once_with(source_path, "rb")
        file_service.get_text_and_metadata_from_pdf.assert_called_once_with(file)
        knowledge_service.index.assert_called_once_with(
            file_content, metadatas, embedding, "output_dir/file.kb"
        )
        metadata_service.create_metadata.assert_called_once_with(
            source_path, description, embedding.provider, output_dir
        )
        file_service.write_metadata_file.assert_called_once_with(
            metadata, "output_dir/file.md"
        )

    def test_index_all_files_fails_if_source_dir_is_not_set(self):
        source_dir = ""
        embedding_model = "embedding_model"
        config_path = "config_path"
        output_dir = "output_dir"
        description = "description"

        config_service = MagicMock()
        file_service = MagicMock()
        knowledge_service = MagicMock()

        metadata_service = MagicMock()

        app = App(
            config_service,
            file_service,
            knowledge_service,
            metadata_service,
        )

        with pytest.raises(ValueError) as e:
            app.index_all_files(
                source_dir, embedding_model, config_path, output_dir, description
            )

        assert str(e.value) == "please provide directory path for source_dir option"

    def test_index_all_files_fails_if_embedding_model_is_not_defined_in_config(self):
        source_dir = "source_dir"
        embedding_model = "embedding_model"
        config_path = "config_path"
        output_dir = "output_dir"
        description = "description"

        config_service = MagicMock()
        config_service.load_embeddings.return_value = []
        file_service = MagicMock()
        knowledge_service = MagicMock()

        metadata_service = MagicMock()

        app = App(
            config_service,
            file_service,
            knowledge_service,
            metadata_service,
        )

        with pytest.raises(ValueError) as e:
            app.index_all_files(
                source_dir, embedding_model, config_path, output_dir, description
            )

        assert (
            str(e.value)
            == "embeddings are not defined in config_path\nUsable models according to config file:"
        )

    def test_index_all_files_does_not_index_unsupported_files(self):
        source_dir = "source_dir"
        embedding_model = "embedding_model"
        config_path = "config_path"
        output_dir = "output_dir"
        description = "description"

        embedding = MagicMock()
        type(embedding).id = PropertyMock(return_value=embedding_model)
        config_embeddings = [embedding]
        config_service = MagicMock()
        config_service.load_embeddings.return_value = config_embeddings
        file_path = "file_path"
        file_service = MagicMock()
        file_service.get_files_from_directory.return_value = [file_path]
        knowledge_service = MagicMock()

        metadata_service = MagicMock()

        app = App(
            config_service,
            file_service,
            knowledge_service,
            metadata_service,
        )

        app.index_all_files(
            source_dir, embedding_model, config_path, output_dir, description
        )

        file_service.get_files_path_from_directory.assert_called_once_with(source_dir)
        assert knowledge_service.index.call_count == 0

    @patch("builtins.open", new_callable=mock_open)
    def test_index_all_files(self, mock_file):
        source_dir = "source_dir"
        embedding_model = "embedding_model"
        config_path = "config_path"
        output_dir = "output_dir"
        description = "description"
        provider = "provider"

        embedding = MagicMock()
        type(embedding).id = PropertyMock(return_value=embedding_model)
        type(embedding).provider = PropertyMock(return_value=provider)
        config_embeddings = [embedding]
        config_service = MagicMock()
        config_service.load_embeddings.return_value = config_embeddings

        first_file_path = "csv_file_path.csv"
        first_file_content = "the first file content"
        first_file_metadata = MagicMock()

        second_file_path = "pdf_file_path.pdf"
        second_file_content = "the second file content"
        second_file_metadata = MagicMock()
        second_file = MagicMock()

        mock_file.return_value.__enter__.side_effect = [second_file]

        file_service = MagicMock()
        file_service.get_files_path_from_directory.return_value = (
            first_file_path,
            second_file_path,
        )

        knowledge_service = MagicMock()
        file_service.get_text_and_metadata_from_csv.return_value = (
            first_file_content,
            first_file_metadata,
        )
        file_service.get_text_and_metadata_from_pdf.return_value = (
            second_file_content,
            second_file_metadata,
        )

        metadata_service = MagicMock()

        metadata = MagicMock()
        metadata_service.create_metadata.return_value = metadata

        app = App(
            config_service,
            file_service,
            knowledge_service,
            metadata_service,
        )

        # Act
        app.index_all_files(
            source_dir, embedding_model, config_path, output_dir, description
        )

        file_service.get_files_path_from_directory.assert_called_once_with(source_dir)
        file_service.get_text_and_metadata_from_csv.assert_called_once_with(
            first_file_path
        )
        file_service.get_text_and_metadata_from_pdf.assert_called_once_with(second_file)

        knowledge_service.index.assert_has_calls(
            [
                call(
                    first_file_content,
                    first_file_metadata,
                    embedding,
                    "output_dir/csv_file_path.kb",
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
                call(metadata, "output_dir/csv_file_path.md"),
                call(metadata, "output_dir/pdf_file_path.md"),
            ]
        )

        metadata_service.create_metadata.assert_has_calls(
            [
                call(first_file_path, description, provider, output_dir),
                call(second_file_path, description, provider, output_dir),
            ]
        )

    def test_create_context_structure_fails_if_context_name_is_not_set(self):
        context_name = ""
        parent_dir = "parent_dir"

        config_service = MagicMock()
        file_service = MagicMock()
        knowledge_service = MagicMock()
        metadata_service = MagicMock()

        app = App(
            config_service,
            file_service,
            knowledge_service,
            metadata_service,
        )

        with pytest.raises(ValueError) as e:
            app.create_context_structure(context_name, parent_dir)

        assert str(e.value) == "please provide context name for context_name option"

    def test_create_context_structure_fails_if_parent_dir_does_not_exist(self):
        context_name = "context_name"
        parent_dir = "parent_dir"

        config_service = MagicMock()
        file_service = MagicMock()
        knowledge_service = MagicMock()
        metadata_service = MagicMock()

        app = App(
            config_service,
            file_service,
            knowledge_service,
            metadata_service,
        )

        with pytest.raises(ValueError) as e:
            app.create_context_structure(context_name, parent_dir)

        assert str(e.value) == "parent directory parent_dir does not exist"

    def test_create_context_structure(self):
        context_name = "context_name"
        parent_dir = "test_parent_dir"
        os.makedirs(parent_dir, exist_ok=True)

        config_service = MagicMock()
        file_service = MagicMock()
        knowledge_service = MagicMock()
        metadata_service = MagicMock()

        app = App(
            config_service,
            file_service,
            knowledge_service,
            metadata_service,
        )

        app.create_context_structure(context_name, parent_dir)

        file_service.create_context_structure.assert_called_once_with(
            context_name, parent_dir
        )

        file_service.write_architecture_file.assert_called_once_with(
            f"{parent_dir}/{context_name}/architecture.md"
        )

        file_service.write_business_context_file.assert_called_once_with(
            f"{parent_dir}/{context_name}/business-context.md"
        )
