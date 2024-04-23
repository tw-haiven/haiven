# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import os

import frontmatter


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
        self._base_knowledge_content_dict = {}
        self._domain_knowledge = {}
        self._domain_knowledge_content_dict = {}

        for content in file_contents:
            if content.metadata["key"]:
                self._base_knowledge_content_dict[content.metadata.get("key")] = (
                    content.content
                )
                self._base_knowledge[content.metadata.get("key")] = content

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
                self._domain_knowledge_content_dict[content.metadata.get("key")] = (
                    content.content
                )
                self._domain_knowledge[content.metadata.get("key")] = content

    def get_content(self, key) -> str:
        entry = self._base_knowledge.get(key, None)
        if entry:
            return entry.content

        entry = self._domain_knowledge.get(key, None)
        if entry:
            return entry.content

        return None

    def get_all_keys(self):
        all_keys = list(self._base_knowledge.keys()) + list(
            self._domain_knowledge.keys()
        )
        return all_keys

    def get_knowledge_content_dict(self):
        merged_content_dict = {
            **self._base_knowledge_content_dict,
            **self._domain_knowledge_content_dict,
        }
        return merged_content_dict
