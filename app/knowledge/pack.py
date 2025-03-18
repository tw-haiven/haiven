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
        HaivenLogger.get().info(
            f"Looking for contexts in path: {context_path}",
            extra={"INFO": "CustomSystemMessageLoaded"},
        )
        HaivenLogger.get().info(
            f"Path exists: {os.path.exists(context_path)}",
            extra={"INFO": "CustomSystemMessageLoaded"},
        )

        if os.path.exists(context_path):
            # Delete below code, adding it only for debugging purpose
            try:
                all_files = os.listdir(context_path)
                HaivenLogger.get().info(
                    f"All files in directory: {all_files}",
                    extra={"INFO": "CustomSystemMessageLoaded"},
                )
            except Exception as e:
                HaivenLogger.error(f"Error listing directory contents: {str(e)}")
            # Delete till here

            markdown_files = [
                file
                for file in os.listdir(context_path)
                if os.path.isfile(os.path.join(context_path, file))
                and file.endswith(".md")
                and not file.startswith("README")
            ]
            HaivenLogger.get().info(
                f"Number of markdown files: {len(markdown_files)}",
                extra={"INFO": "CustomSystemMessageLoaded"},
            )

            for md_file in markdown_files:
                file_path = os.path.join(context_path, md_file)
                name = os.path.splitext(md_file)[0]
                try:
                    content = frontmatter.load(file_path)
                    title = content.metadata.get("title", name)
                    HaivenLogger.get().info(
                        f"Processing markdown file: {md_file}, name: {name}",
                        extra={"INFO": "CustomSystemMessageLoaded"},
                    )
                except Exception as e:
                    title = name
                    HaivenLogger.get().error(
                        f"Error processing markdown file {md_file}: {str(e)}",
                        extra={"INFO": "CustomSystemMessageLoaded"},
                    )
                self.contexts.append(
                    KnowledgeContext(name=name, path=file_path, title=title)
                )
