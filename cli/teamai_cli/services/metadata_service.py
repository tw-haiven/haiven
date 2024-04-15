# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
class MetadataService:
    def create_metadata(source_file_path: str, description: str, provider: str):
        title = source_file_path.split(".")[0]
        return {
            "title": title,
            "description": description,
            "source": source_file_path,
            "path": f"{title}.kb",
            "provider": provider,
        }
