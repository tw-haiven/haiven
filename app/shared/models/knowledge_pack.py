# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from typing import List


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
    def __init__(self, path: str, contexts: List[KnowledgeContext]):
        self.path = path
        self.contexts = contexts

    @classmethod
    def from_dict(cls, data):
        return cls(
            path=data.get("path"),
            contexts=[
                KnowledgeContext.from_dict(knowledge_context)
                for knowledge_context in data.get("contexts")
            ],
        )
