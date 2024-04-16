# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import os


class MetadataService:
    def create_metadata(
        source_file_path: str, description: str, provider: str, output_dir: str
    ):
        key = os.path.basename(os.path.normpath(f"{source_file_path.split('.')[0]}"))
        source = os.path.basename(os.path.normpath(source_file_path))
        title = key.replace("-", " ").replace("_", " ")
        return {
            "key": key,
            "title": title,
            "description": description,
            "source": source,
            "path": f"{key}.kb",
            "provider": provider,
        }
