# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from teamai_cli.services.metadata_service import MetadataService


class TestMetadataService:
    def test_create_metadata(self):
        source_file_path = "/very/long/path/to/source_file_path.pdf"
        description = "a description"
        provider = "provider"
        output_dir = "output_dir"
        metadata = MetadataService.create_metadata(
            source_file_path, description, provider, output_dir
        )
        assert metadata == {
            "title": "source_file_path",
            "description": "a description",
            "source": "/very/long/path/to/source_file_path.pdf",
            "path": "output_dir/source_file_path.kb",
            "provider": "provider",
        }
