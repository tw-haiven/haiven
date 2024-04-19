# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.

import os

from langchain_core.documents import Document
from teamai_cli.services.file_service import FileService
from unittest.mock import patch, MagicMock, mock_open, PropertyMock


class TestFileService:
    @patch("teamai_cli.services.file_service.pickle")
    @patch("builtins.open", new_callable=mock_open)
    def test_write_pickles(self, mock_file, mock_pickle):
        document = Document(page_content="content", metadata={"metadata": "metadata"})
        documents = [document]
        output_dir = "output_dir"
        pickle_file_path = "pickle_file_path"
        os.makedirs(output_dir, exist_ok=True)
        file_service = FileService()

        file_service.write_pickles(documents, output_dir, pickle_file_path)

        mock_file.assert_called_once_with(f"{output_dir}/{pickle_file_path}", "wb")
        mock_pickle.dump.assert_called_once_with(documents, mock_file())
        os.rmdir(output_dir)

    @patch("teamai_cli.services.file_service.pickle")
    @patch("builtins.open", new_callable=mock_open)
    def test_write_pickles_creates_output_dir_if_it_does_not_exist(
        self, mock_file, mock_pickle
    ):
        document = Document(page_content="content", metadata={"metadata": "metadata"})
        documents = [document]
        output_dir = "output_dir"
        pickle_file_path = "pickle_file_path"
        file_service = FileService()

        file_service.write_pickles(documents, output_dir, pickle_file_path)

        assert os.path.exists(output_dir)
        os.rmdir(output_dir)

    @patch("teamai_cli.services.file_service.PdfReader")
    def test_get_text_and_metadata_from_pdf(self, mock_pdf_reader):
        pdf_file_name = "pdf_file_path.pdf"
        pdf_file = MagicMock()
        type(pdf_file).name = PropertyMock(return_value=pdf_file_name)
        first_text = "first text"
        first_page = MagicMock()
        first_page.extract_text.return_value = first_text
        second_text = "second text"
        second_page = MagicMock()
        second_page.extract_text.return_value = second_text
        pages = [first_page, second_page]
        pdf_reader = MagicMock()
        type(pdf_reader).pages = PropertyMock(return_value=pages)
        mock_pdf_reader.return_value = pdf_reader
        file_service = FileService()

        text, metadas = file_service.get_text_and_metadata_from_pdf(pdf_file)

        mock_pdf_reader.assert_called_once_with(pdf_file)
        first_metadata = metadas[0]
        assert first_metadata["page"] == 1
        assert first_metadata["file"] == pdf_file_name

        second_metadata = metadas[1]
        assert second_metadata["page"] == 2
        assert second_metadata["file"] == pdf_file_name

        assert first_text in text
        assert second_text in text

    @patch("teamai_cli.services.file_service.os")
    def test_get_files_path_from_directory(self, mock_os):
        source_dir = "source_dir"
        file_path = "file_path"
        mock_os.walk.return_value = [(source_dir, [], [file_path])]
        mock_os.path.join.return_value = os.path.join(source_dir, file_path)
        file_service = FileService()

        files = file_service.get_files_path_from_directory(source_dir)

        assert len(files) == 1
        assert files[0] == f"{source_dir}/{file_path}"
        mock_os.walk.assert_called_once_with(source_dir)

    def test_write_metadata_file(self):
        key = "a key"
        title = "a title"
        description = "a description"
        source = "a source"
        path = "a path"
        provider = "a provider"
        sample_question = "a sample question"

        metadata = {
            "key": key,
            "title": title,
            "description": description,
            "source": source,
            "path": path,
            "provider": provider,
            "sample_question": sample_question,
        }
        metadata_file_path = "test_metadata.yml"

        file_service = FileService()
        file_service.write_metadata_file(metadata, metadata_file_path)

        expected_metadata_file_content = f"""---
key: {key}
title: {title}
description: {description}
source: {source}
path: {path}
provider: {provider}
sample_question: {sample_question}
---
"""
        with open(metadata_file_path, "r") as f:
            metadata_file_content = f.read()
            assert metadata_file_content == expected_metadata_file_content

        os.remove(metadata_file_path)

    def test_write_architecture_file(self):
        arch_file_path = "test_architecture.md"
        arch_description = "a description of the architecture"
        file_service = FileService()
        file_service.write_architecture_file(arch_file_path, arch_description)

        expected_arch_file_content = """---
        key: architecture
        title: Architecture

        a description of the architecture
        ---
        """

        with open(arch_file_path, "r") as f:
            arch_file_content = f.read()
            assert arch_file_content == expected_arch_file_content

        os.remove(arch_file_path)
