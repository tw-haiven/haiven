# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from shared.knowledge import KnowledgeBaseMarkdown
from shared.prompts import PromptList


class PromptsFactory:
    def __init__(self, prompts_parent_dir: str):
        self.prompts_parent_dir = prompts_parent_dir

    def create_all_prompts(self, knowledge_base_markdown: KnowledgeBaseMarkdown):
        return [
            PromptList(
                "chat", knowledge_base_markdown, root_dir=self.prompts_parent_dir
            ),
            PromptList(
                "brainstorming",
                knowledge_base_markdown,
                root_dir=self.prompts_parent_dir,
            ),
            PromptList(
                "diagrams", knowledge_base_markdown, root_dir=self.prompts_parent_dir
            ),
        ]

    def create_brainstorming_prompt(
        self, knowledge_base_markdown: KnowledgeBaseMarkdown
    ):
        return PromptList(
            "brainstorming", knowledge_base_markdown, root_dir=self.prompts_parent_dir
        )

    def create_chat_prompt(self, knowledge_base_markdown: KnowledgeBaseMarkdown):
        return PromptList(
            "chat", knowledge_base_markdown, root_dir=self.prompts_parent_dir
        )

    def create_diagrams_prompt(self, knowledge_base: KnowledgeBaseMarkdown, variables):
        return PromptList(
            "diagrams",
            knowledge_base,
            variables=variables,
            root_dir=self.prompts_parent_dir,
        )
