# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os
from typing import List


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
        self.contexts = contexts

        if len(self.contexts) == 0:
            self._auto_discovery_contexts()

    def _auto_discovery_contexts(self):
        context_path = os.path.join(self.path, "contexts")

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
