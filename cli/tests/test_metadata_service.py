from haiven_cli.services.metadata_service import MetadataService


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
            "key": "source_file_path",
            "title": "source file path",
            "description": "a description",
            "source": "source_file_path.pdf",
            "path": "source_file_path.kb",
            "provider": "provider",
        }
