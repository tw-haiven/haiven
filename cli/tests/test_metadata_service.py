# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from haiven_cli.services.metadata_service import MetadataService


class TestMetadataService:
    def test_create_metadata_file_name(self):
        source_file_path = "/very/long/path/to/source_file_path.pdf"
        description = "a description"
        provider = "provider"
        output_dir = "output_dir"
        metadata = MetadataService.create_metadata(
            source_file_path, description, provider, output_dir
        )
        assert metadata == {
            "key": "source_file_path",
            "title": "source file path",
            "description": "a description",
            "source": "source_file_path.pdf",
            "path": "source_file_path.kb",
            "provider": "provider",
        }

    def test_create_metadata_dir_name(self):
        source_file_path = "/very/long/path/to/source_directory"
        description = "a description"
        provider = "provider"
        output_dir = "output_dir"
        metadata = MetadataService.create_metadata(
            source_file_path, description, provider, output_dir
        )
        assert metadata == {
            "key": "source_directory",
            "title": "source directory",
            "description": "a description",
            "source": "source_directory",
            "path": "source_directory.kb",
            "provider": "provider",
        }
