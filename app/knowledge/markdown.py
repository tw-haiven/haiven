# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os

import frontmatter


class KnowledgeMarkdown:
    def __init__(self, content: str, metadata: dict):
        self.content = content
        self.metadata = metadata


class KnowledgeBaseMarkdown:
    _knowledge: dict[str, list[KnowledgeMarkdown]]

    def __init__(self):
        self._knowledge = {}

    def _load_context(self, path: str) -> list[KnowledgeMarkdown]:
        knowledge_files = sorted(
            [f for f in os.listdir(path) if f.endswith(".md") and f != "README.md"]
        )
        file_contents = [
            frontmatter.load(os.path.join(path, filename))
            for filename in knowledge_files
        ]

        context_content = []

        for content in file_contents:
            if content.metadata.get("key"):
                context_content.append(
                    KnowledgeMarkdown(content.content, content.metadata)
                )

        return context_content

    def load_for_base(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"The specified path does not exist, no knowledge will be loaded: {path}"
            )

        base_content = self._load_context(path)
        self._knowledge["base"] = base_content

    def load_for_context(self, context: str, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"The specified path does not exist, no knowledge will be loaded: {path}"
            )

        context_content = self._load_context(path)
        self._knowledge[context] = context_content

    def get_knowledge_document(
        self, context: str, knowledge_key: str
    ) -> KnowledgeMarkdown:
        """
        Retrieves a specific knowledge entry by its key from the specified context.

        Parameters:
            context (str): The context from which to retrieve the knowledge entry.
            knowledge_key (str): The key of the knowledge entry to retrieve.

        Returns:
            KnowledgeEntry: The knowledge entry corresponding to the given key within the specified context, or None if not found.
        """
        context_knowledge = self._knowledge.get(context, None)
        if context_knowledge:
            return next(
                (
                    knowledge
                    for knowledge in context_knowledge
                    if knowledge.metadata["key"] == knowledge_key
                ),
                None,
            )

        return None

    def get_all_contexts_keys(self) -> list[str]:
        all_keys = list(self._knowledge.keys())
        return all_keys

    def get_context_keys(self, context: str) -> list[str]:
        if context is None or context == "":
            return []
        all_keys = [
            knowledge_document.metadata["key"]
            for knowledge_document in self._knowledge[context]
        ]
        return all_keys

    def get_all_knowledge_documents(self, context: str) -> list[KnowledgeMarkdown]:
        all_knowledge = self._knowledge[context]
        return all_knowledge

    def get_knowledge_content_dict(self, context: str) -> dict[str, str]:
        merged_content_dict = {
            entry.metadata["key"]: entry.content for entry in self._knowledge[context]
        }
        return merged_content_dict
