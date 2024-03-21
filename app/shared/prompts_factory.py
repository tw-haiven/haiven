# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from shared.knowledge import KnowledgeBaseDocuments, KnowledgeBaseMarkdown
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

    def create_diagrams_prompt(
        self, knowledge_base_documents: KnowledgeBaseDocuments, variables
    ):
        return PromptList(
            "diagrams",
            knowledge_base_documents,
            variables=variables,
            root_dir=self.prompts_parent_dir,
        )
