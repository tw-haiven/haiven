# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os
from typing import List
from logger import HaivenLogger


class KnowledgePackError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class KnowledgeContext:
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name"),
            path=data.get("path"),
        )


class KnowledgePack:
    def __init__(self, path: str, contexts: List[KnowledgeContext] = []):
        self.path = path
        self.contexts: List[KnowledgeContext] = contexts

        if len(self.contexts) == 0:
            self._auto_discovery_contexts()

    def _auto_discovery_contexts(self):
        context_path = os.path.join(self.path, "contexts")
        HaivenLogger.get().info(
            f"Looking for contexts in path: {context_path}",
            extra={"INFO": "CustomSystemMessageLoaded"},
        )
        HaivenLogger.get().info(
            f"Path exists: {os.path.exists(context_path)}",
            extra={"INFO": "CustomSystemMessageLoaded"},
        )

        if os.path.exists(context_path):
            # Delete below code, adding it only for debugging purpose
            try:
                all_files = os.listdir(context_path)
                HaivenLogger.get().info(
                    f"All files in directory: {len(all_files)} {all_files}",
                    extra={"INFO": "CustomSystemMessageLoaded"},
                )
            except Exception as e:
                HaivenLogger.error(f"Error listing directory contents: {str(e)}")
            # Delete till here
            context_folders = [
                folder
                for folder in os.listdir(context_path)
                if os.path.isdir(os.path.join(context_path, folder))
            ]
            self.contexts = [
                KnowledgeContext(
                    name=folder,
                    path=folder,
                )
                for folder in context_folders
            ]
