# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from teamai_cli.services.metadata_service import MetadataService


class TestMetadataService:
    def test_create_metadata(self):
        source_file_path = "source_file_path.pdf"
        description = "a description"
        provider = "provider"
        metadata = MetadataService.create_metadata(
            source_file_path, description, provider
        )
        assert metadata == {
            "title": "source_file_path",
            "description": "a description",
            "source": "source_file_path.pdf",
            "path": "source_file_path.kb",
            "provider": "provider",
        }
