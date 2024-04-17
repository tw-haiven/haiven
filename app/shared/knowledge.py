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

        self._knowledge = {}
        self._knowledge_content_dict = {}
        for content in file_contents:
            if content.metadata["key"]:
                self._knowledge_content_dict[content.metadata.get("key")] = (
                    content.content
                )
                self._knowledge[content.metadata.get("key")] = content

    def get_content(self, key) -> str:
        entry = self._knowledge.get(key, None)
        if entry:
            return entry.content
        return None

    def get_all_keys(self):
        return list(self._knowledge.keys())

    def get_knowledge_content_dict(self):
        return self._knowledge_content_dict
