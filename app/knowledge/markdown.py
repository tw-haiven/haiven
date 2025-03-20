# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os
from dataclasses import dataclass
from logger import HaivenLogger

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
    _knowledge: dict[str, list[KnowledgeMarkdown]]

    def __init__(self):
        self._knowledge = {}

    def _load_context(self, path: str) -> list[KnowledgeMarkdown]:
        # path = os.path.abspath(path)  # Convert relative path to absolute

        if not os.path.exists(path):
            raise FileNotFoundError(f"Path does not exist: {path}")

        context_content = []

        def process_markdown_file(file_path: str) -> None:
            HaivenLogger.get().info(
                f"_load_context process_markdown_file file-path: {file_path}",
                extra={"INFO": "CustomSystemMessageLoaded"},
            )
            if not file_path.endswith(".md") or file_path.endswith("README.md"):
                return
            try:
                content = frontmatter.load(file_path)
                HaivenLogger.get().info(
                    f"_load_context process_markdown_file content: {content}",
                    extra={"INFO": "CustomSystemMessageLoaded"},
                )
                if content.metadata.get("key"):
                    context_content.append(
                        KnowledgeMarkdown(content.content, content.metadata)
                    )
            except Exception as e:
                print(f"Error processing markdown file {file_path}: {str(e)}")

        if os.path.isfile(path):
            HaivenLogger.get().info(
                f"_load_context isfile: {path}",
                extra={"INFO": "CustomSystemMessageLoaded"},
            )
            process_markdown_file(path)
        elif os.path.isdir(path):
            HaivenLogger.get().info(
                f"_load_context isdir file-path: {path}",
                extra={"INFO": "CustomSystemMessageLoaded"},
            )
            for root, _, files in os.walk(path):
                for file in sorted(files):
                    file_path = os.path.join(root, file)
                    HaivenLogger.get().info(
                        f"_load_context isdir nested file-path: {file_path}",
                        extra={"INFO": "CustomSystemMessageLoaded"},
                    )
                    process_markdown_file(file_path)
        else:
            raise ValueError(f"Path must be a file or directory: {path}")

        HaivenLogger.get().info(
            f"_load_context context_content len: {len(context_content)}",
            extra={"INFO": "CustomSystemMessageLoaded"},
        )
        HaivenLogger.get().info(
            f"_load_context context_content: {context_content}",
            extra={"INFO": "CustomSystemMessageLoaded"},
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

    def get_all_contexts_metadata(self) -> list[ContextMetadata]:
        """
        Returns a list of ContextMetadata objects containing the key and title for each context.
        If a context doesn't have a title in its metadata, the key is used as the title.
        """
        context_metadata = []

        HaivenLogger.get().info(
            f"All keys count: {len(self._knowledge.keys())}",
            extra={"INFO": "CustomSystemMessageLoaded"},
        )
        for context_key in self._knowledge.keys():
            # Get the first document in the context to extract title, if available
            context_docs = self._knowledge[context_key]
            title = context_key  # Default to key if no title found

            HaivenLogger.get().info(
                f"Context docs: {context_docs}",
                extra={"INFO": "CustomSystemMessageLoaded"},
            )
            HaivenLogger.get().info(
                f"Context key: {context_key}",
                extra={"INFO": "CustomSystemMessageLoaded"},
            )

            if context_docs:
                # Try to get title from the first document's metadata
                first_doc = context_docs[0]
                title = first_doc.metadata.get("title", context_key)

            context_metadata.append(ContextMetadata(key=context_key, title=title))
        HaivenLogger.get().info(
            f"Context metadata: {context_metadata}",
            extra={"INFO": "CustomSystemMessageLoaded"},
        )
        HaivenLogger.get().info(
            f"Context metadata count: {len(context_metadata)}",
            extra={"INFO": "CustomSystemMessageLoaded"},
        )
        return context_metadata

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
