# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from knowledge.markdown import KnowledgeBaseMarkdown
from knowledge_manager import KnowledgeManager
from prompts.prompts import PromptList


class PromptsFactory:
    def __init__(self, prompts_parent_dir: str):
        self.prompts_parent_dir = prompts_parent_dir

    def create_all_prompts_for_user_choice(
        self,
        knowledge_base_markdown: KnowledgeBaseMarkdown,
        knowledge_manager: KnowledgeManager,
    ):
        return [
            PromptList(
                "chat",
                knowledge_base_markdown,
                knowledge_manager,
                root_dir=self.prompts_parent_dir,
            ),
            PromptList(
                "brainstorming",
                knowledge_base_markdown,
                knowledge_manager,
                root_dir=self.prompts_parent_dir,
            ),
            PromptList(
                "diagrams",
                knowledge_base_markdown,
                knowledge_manager,
                root_dir=self.prompts_parent_dir,
            ),
        ]

    def create_brainstorming_prompt_list(
        self,
        knowledge_base_markdown: KnowledgeBaseMarkdown,
        knowledge_manager: KnowledgeManager,
    ):
        return PromptList(
            "brainstorming",
            knowledge_base_markdown,
            knowledge_manager,
            root_dir=self.prompts_parent_dir,
        )

    def create_chat_prompt_list(
        self,
        knowledge_base_markdown: KnowledgeBaseMarkdown,
        knowledge_manager: KnowledgeManager,
    ):
        return PromptList(
            "chat",
            knowledge_base_markdown,
            knowledge_manager,
            root_dir=self.prompts_parent_dir,
        )

    def create_diagrams_prompt_list(
        self, knowledge_base: KnowledgeBaseMarkdown, variables
    ):
        return PromptList(
            "diagrams",
            knowledge_base,
            variables=variables,
            root_dir=self.prompts_parent_dir,
        )

    def create_guided_prompt_list(
        self, knowledge_base: KnowledgeBaseMarkdown, knowledge_manager: KnowledgeManager
    ):
        return PromptList(
            "guided",
            knowledge_base,
            knowledge_manager,
            variables=[
                "prompt",
                "rows",
                "columns",
                "idea_qualifiers",
                "num_ideas",
                "num_scenarios",
                "time_horizon",
                "num_scenarios",
                "optimism",
                "realism",
                "input",
            ],
            root_dir=self.prompts_parent_dir,
        )
