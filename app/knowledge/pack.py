# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os
from typing import List
<<<<<<< HEAD
import frontmatter
from logger import HaivenLogger
=======
>>>>>>> 2fb1ff4 (Revert "#361 | Change folder format of context to file format")


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
