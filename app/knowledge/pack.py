# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os
from typing import List
import frontmatter
from logger import HaivenLogger


class KnowledgePackError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class KnowledgeContext:
    def __init__(self, name: str, path: str, title: str = None):
        self.name = name
        self.path = path
        self.title = title or name

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name"),
            path=data.get("path"),
            title=data.get("title"),
        )


class KnowledgePack:
    def __init__(self, path: str, contexts: List[KnowledgeContext] = None):
        self.path = path
        self.contexts: List[KnowledgeContext] = contexts if contexts is not None else []

        if len(self.contexts) == 0:
            self._auto_discovery_contexts()

    def _auto_discovery_contexts(self):
        context_path = os.path.join(self.path, "contexts")

        if os.path.exists(context_path):
            markdown_files = [
                file
                for file in os.listdir(context_path)
                if os.path.isfile(os.path.join(context_path, file))
                and file.endswith(".md")
                and not file.startswith("README")
            ]

            for md_file in markdown_files:
                file_path = os.path.join(context_path, md_file)
                name = os.path.splitext(md_file)[0]
                try:
                    content = frontmatter.load(file_path)
                    title = content.metadata.get("title", name)
                except Exception as e:
                    title = name
                    HaivenLogger.get().error(
                        f"Error processing markdown file {md_file}: {str(e)}",
                        extra={"INFO": "CustomSystemMessageLoaded"},
                    )
                self.contexts.append(
                    KnowledgeContext(name=name, path=name + ".md", title=title)
                )
