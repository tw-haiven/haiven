# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import os

import frontmatter

from shared.models.knowledge_entry import KnowledgeEntry


class KnowledgeBaseMarkdown:
    def __init__(self, path: str):
        knowledge_files = sorted(
            [f for f in os.listdir(path) if f.endswith(".md") and f != "README.md"]
        )
        file_contents = [
            frontmatter.load(os.path.join(path, filename))
            for filename in knowledge_files
        ]

        self._base_knowledge = {}
        self._domain_knowledge = {}

        for content in file_contents:
            if content.metadata["key"]:
                self._base_knowledge[content.metadata.get("key")] = KnowledgeEntry(
                    content.content, content.metadata
                )

    def set_domain_content(self, path: str):
        self._domain_knowledge = {}
        self._domain_knowledge_content_dict = {}

        knowledge_files = sorted(
            [f for f in os.listdir(path) if f.endswith(".md") and f != "README.md"]
        )
        file_contents = [
            frontmatter.load(os.path.join(path, filename))
            for filename in knowledge_files
        ]

        for content in file_contents:
            if content.metadata["key"]:
                self._domain_knowledge[content.metadata.get("key")] = KnowledgeEntry(
                    content.content, content.metadata
                )
                self._domain_knowledge[content.metadata.get("key")] = content

    def get_entry(self, key) -> KnowledgeEntry:
        entry = self._base_knowledge.get(key, None)
        if entry:
            return (entry.content, entry.metadata)

        entry = self._domain_knowledge.get(key, None)
        if entry:
            return (entry.content, entry.metadata)

        return None, None

    def get_all_keys(self):
        all_keys = list(self._base_knowledge.keys()) + list(
            self._domain_knowledge.keys()
        )
        return all_keys

    def get_knowledge_content_dict(self) -> dict[str, str]:
        merged_content_dict = {
            key: entry.content
            for dict_item in [self._base_knowledge, self._domain_knowledge]
            for key, entry in dict_item.items()
        }
        return merged_content_dict
