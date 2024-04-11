# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import os

import frontmatter


class KnowledgeBaseMarkdown:
    def __init__(self, team_name, root_dir="teams"):
        directory = root_dir + "/" + team_name + "/knowledge"
        knowledge_files = sorted(
            [f for f in os.listdir(directory) if f.endswith(".md") and f != "README.md"]
        )
        file_contents = [
            frontmatter.load(os.path.join(directory, filename))
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


class DocumentationBase:
    def __init__(self, root_dir="teams"):
        directory = root_dir + "/documentation"
        doc_files = sorted(
            [f for f in os.listdir(directory) if f.endswith(".md") and f != "README.md"]
        )
        self._documentation = [
            frontmatter.load(os.path.join(directory, filename))
            for filename in doc_files
        ]

    def get_documentation_filtered(self, filter_categories):
        if filter_categories is not None:
            return list(
                filter(
                    lambda prompt: (
                        not prompt.metadata["categories"]
                        or any(
                            category in prompt.metadata["categories"]
                            for category in filter_categories
                        )
                    ),
                    self._documentation,
                )
            )
        return self._documentation
