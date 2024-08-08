# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os


class MetadataService:
    def create_metadata(
        source_file_path: str, description: str, provider: str, output_dir: str
    ):
        file_name_components = source_file_path.split(".")
        if len(file_name_components) == 1:
            name = source_file_path
        else:
            name = file_name_components[-2]
        key = os.path.basename(os.path.normpath(f"{name}"))
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
