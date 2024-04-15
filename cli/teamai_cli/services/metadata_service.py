# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import os


class MetadataService:
    def create_metadata(
        source_file_path: str, description: str, provider: str, output_dir: str
    ):
        title = os.path.basename(os.path.normpath(f"{source_file_path.split('.')[0]}"))
        return {
            "title": title,
            "description": description,
            "source": source_file_path,
            "path": f"{output_dir}/{title}.kb",
            "provider": provider,
        }
