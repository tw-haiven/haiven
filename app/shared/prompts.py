# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import os
from typing import List
import frontmatter
from langchain.prompts import PromptTemplate

from shared.logger import TeamAILogger
from shared.knowledge import KnowledgeBaseMarkdown


class PromptList:
    def __init__(
        self,
        interaction_type,
        knowledge_base: KnowledgeBaseMarkdown,
        variables=[],
        root_dir="teams",
    ):
        data_sources = {
            "diagrams": {
                "dir": root_dir + "/prompts/diagrams",
                "title": "Diagrams",
            },
            "brainstorming": {
                "dir": root_dir + "/prompts/brainstorming",
                "title": "Brainstorming",
            },
            "chat": {
                "dir": root_dir + "/prompts/chat",
                "title": "Chat",
            },
        }

        self.interaction_pattern_name = data_sources[interaction_type]["title"]

        directory = data_sources[interaction_type]["dir"]
        prompt_files = sorted(
            [f for f in os.listdir(directory) if f.endswith(".md") and f != "README.md"]
        )
        self.prompts = [
            frontmatter.load(os.path.join(directory, filename))
            for filename in prompt_files
        ]

        self.knowledge_base = knowledge_base
        self.variables = ["user_input"] + self.knowledge_base.get_all_keys() + variables

        for prompt in self.prompts:
            if "title" not in prompt.metadata:
                prompt.metadata["title"] = "Unnamed use case"
            if "system" not in prompt.metadata:
                prompt.metadata["system"] = "You are a useful assistant"
            if "categories" not in prompt.metadata:
                prompt.metadata["categories"] = []

    def get_title_id_tuples(self):
        tuples = [
            (
                prompt.metadata.get("title", "Unnamed use case"),
                prompt.metadata.get("identifier"),
            )
            for prompt in self.prompts
        ]

        sorted_tuples = sorted(tuples, key=lambda x: x[0])

        return sorted_tuples

    def get(self, identifier):
        for prompt in self.prompts:
            if prompt.metadata.get("identifier") == identifier:
                return prompt
        return None

    def create_template(self, identifier) -> PromptTemplate:
        prompt_data = self.get(identifier)
        if not prompt_data:
            raise ValueError(f"Prompt {identifier} not found")

        prompt_text = prompt_data.content
        return PromptTemplate(input_variables=self.variables, template=prompt_text)

    def create_and_render_template(self, identifier, variables, warnings=None):
        knowledge_with_overwrites = {
            **self.knowledge_base.get_knowledge_content_dict(),
            **variables,
        }

        template = self.create_template(identifier)
        template.get_input_schema()
        template.dict()

        # check if input variables in template are present in the knowledge_with_overwrites
        for key in template.input_variables:
            if key not in knowledge_with_overwrites:
                message = f"A requested context '{key}' was not found. Quality of the output for the selected prompt might be affected."
                TeamAILogger.get().logger.warning(message)
                if warnings is not None:
                    warnings.append(message)
                knowledge_with_overwrites[str(key)] = (
                    f"No information was present for '{key}'."
                )

        rendered = template.format(**knowledge_with_overwrites)
        return template, rendered

    def filter(self, filter_categories: List[str]):
        if filter_categories is not None:
            self.prompts = list(
                filter(
                    lambda prompt: (
                        not prompt.metadata["categories"]
                        or any(
                            category in prompt.metadata["categories"]
                            for category in filter_categories
                        )
                    ),
                    self.prompts,
                )
            )

    def render_prompt(
        self,
        prompt_choice: str,
        user_input: str,
        additional_vars: dict = {},
        warnings=None,
    ) -> str:
        if prompt_choice is not None:
            vars = additional_vars
            vars["user_input"] = user_input
            _, rendered = self.create_and_render_template(
                prompt_choice, vars, warnings=warnings
            )
            return rendered
        return ""

    def get_knowledge_used_keys(self, identifier: str):
        if identifier is not None:
            template = self.create_template(identifier).dict()
            return template["input_variables"]

    def get_default_context(self, prompt_choice: str):
        return self.get(prompt_choice).metadata.get("context", "None")

    def get_knowledge_used(self, prompt_choice: str):
        prompt = self.get(prompt_choice)
        if prompt is not None:
            knowledge_keys = self.get_knowledge_used_keys(prompt_choice)
            knowledge = []
            for key in knowledge_keys:
                knowledge_entry = self.knowledge_base.get_entry(key)
                if knowledge_entry:
                    knowledge.append(knowledge_entry.metadata)

            return knowledge

    def render_help_markdown(self, prompt_choice: str):
        prompt = self.get(prompt_choice)
        if prompt is not None:
            title = f"## {prompt.metadata.get('title')}"

            prompt_description = prompt.metadata.get("help_prompt_description", "")
            prompt_markdown = (
                f"**Description:** {prompt_description}" if prompt_description else ""
            )
            user_input_description = prompt.metadata.get("help_user_input", "")
            user_input_markdown = (
                f"**User input:** {user_input_description}"
                if user_input_description
                else ""
            )
            knowledge_used = self.get_knowledge_used(prompt_choice)
            knowledge_used_markdown = (
                f"**Knowledge used:** {', '.join(knowledge['title'] for knowledge in knowledge_used)}"
                if knowledge_used
                else ""
            )

            sample_input = prompt.metadata.get("help_sample_input", "")
            sample_input_markdown = (
                f"**Sample input:** {sample_input}" if sample_input else ""
            )

            return (
                f"{title}\n{prompt_markdown}\n\n{user_input_markdown}\n\n{sample_input_markdown}",
                knowledge_used_markdown,
            )
        return None

    def render_prompts_summary_markdown(self):
        prompts_summary = ""
        for prompt in self.prompts:
            title = prompt.metadata.get("title")
            description = prompt.metadata.get("help_prompt_description")
            if title and description:
                prompt_summary = f"- **{title}**: {description}\n"
                prompts_summary += prompt_summary
        return prompts_summary
