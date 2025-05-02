# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os
from typing import List
from dataclasses import dataclass

import frontmatter


@dataclass
class KnowledgeMarkdown:
    def __init__(self, content: str, metadata: dict):
        self.content = content
        self.metadata = metadata


@dataclass
class ContextMetadata:
    key: str
    title: str


class KnowledgeBaseMarkdown:
    _knowledge: dict[str, KnowledgeMarkdown]

    def __init__(self):
        self._knowledge = {}

    def _load_context(self, path: str) -> list[KnowledgeMarkdown]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Path does not exist: {path}")

        if os.path.isfile(path):
            if not path.endswith(".md") or path.endswith("README.md"):
                return
            try:
                content = frontmatter.load(path)
                if content.content != "":
                    return KnowledgeMarkdown(content.content, content.metadata)

            except Exception as e:
                print(f"Error processing markdown file {path}: {str(e)}")
        else:
            raise ValueError(f"Path must be a file or directory: {path}")

        return None

    def load_for_context(self, context: str, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"The specified path does not exist, no knowledge will be loaded: {path}"
            )

        context_content = self._load_context(path)
        self._knowledge[context] = context_content

    def get_all_contexts(self) -> dict[str, KnowledgeMarkdown]:
        """
        Returns a dictionary containing all available contexts
        """
        return self._knowledge

    def aggregate_all_contexts(
        self, contexts: List[str], user_context: str = None
    ) -> str:
        """
        Return all required contexts' contents appended as one string
        """
        knowledgePackContextsAggregated = None
        if contexts:
            knowledgePackContextsAggregated = "\n\n".join(
                self._knowledge[context_key].content for context_key in contexts
            )

        return "\n\n".join(
            filter(None, [knowledgePackContextsAggregated, user_context])
        )
