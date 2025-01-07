# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os
import yaml
from typing import List

import frontmatter
from langchain.prompts import PromptTemplate
from knowledge.markdown import KnowledgeBaseMarkdown


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
            "guided": {"dir": root_dir + "/", "title": "Guided"},
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
        self.extra_variables = variables

        for prompt in self.prompts:
            if "title" not in prompt.metadata:
                prompt.metadata["title"] = "Unnamed use case"
            if "system" not in prompt.metadata:
                prompt.metadata["system"] = "You are a useful assistant"
            if "categories" not in prompt.metadata:
                prompt.metadata["categories"] = []
            if "type" not in prompt.metadata:
                prompt.metadata["type"] = "chat"
            if "editable" not in prompt.metadata:
                prompt.metadata["editable"] = False
            if "show" not in prompt.metadata:
                prompt.metadata["show"] = True

        self.prompt_flows = self.load_prompt_flows(
            os.path.join(directory, "prompt_flows.yaml")
        )

    def load_prompt_flows(self, prompt_flows_path):
        if prompt_flows_path and os.path.exists(prompt_flows_path):
            try:
                with open(prompt_flows_path, "r") as file:
                    return yaml.safe_load(file)
            except FileNotFoundError:
                print(
                    f"Warning: No file {prompt_flows_path} found, moving on without flows."
                )
                return []
        return []

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

    def create_template(
        self, active_knowledge_context: str, identifier: str
    ) -> PromptTemplate:
        prompt_data = self.get(identifier)
        if not prompt_data:
            raise ValueError(f"Prompt {identifier} not found")

        prompt_text = prompt_data.content
        variables = (
            ["user_input"]
            + self.knowledge_base.get_context_keys(active_knowledge_context)
            + self.extra_variables
        )
        return PromptTemplate(input_variables=variables, template=prompt_text)

    def get_rendered_context(self, active_knowledge_context, identifier):
        """
        Args:
            active_knowledge_context (str): The context identifier for the knowledge base.
            identifier (str): The identifier for the prompt

        Returns:
            str: The content of the context placeholder used in a prompt
        """
        knowledge = self.knowledge_base.get_knowledge_content_dict(
            active_knowledge_context
        )
        template = self.create_template(active_knowledge_context, identifier)
        result = ""
        for key in template.input_variables:
            if key in knowledge and key != "user_input":
                result += knowledge[key]
        return result

    def create_and_render_template(
        self, active_knowledge_context, identifier, variables, warnings=None
    ):
        if active_knowledge_context:
            knowledge_and_input = {
                **self.knowledge_base.get_knowledge_content_dict(
                    active_knowledge_context
                ),
                **variables,
            }
        else:
            knowledge_and_input = {**variables}

        template = self.create_template(active_knowledge_context, identifier)
        # template.get_input_schema()
        # template.dict()

        # make sure all input variables are present for template rendering (as it will otherwise fail)
        for key in template.input_variables:
            if key not in knowledge_and_input:
                knowledge_and_input[str(key)] = (
                    "None provided, please try to help without this information."  # placeholder for the prompt
                )
                if key != "user_input":
                    message = f"No context selected, no '{key}' added to the prompt."  # message shown to the user
                    if warnings is not None:
                        warnings.append(message)

        rendered = template.format(**knowledge_and_input)
        return rendered, template

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
        active_knowledge_context: str,
        prompt_choice: str,
        user_input: str,
        additional_vars: dict = {},
        warnings=None,
    ) -> str:
        if prompt_choice is not None:
            vars = additional_vars
            vars["user_input"] = user_input
            rendered, template = self.create_and_render_template(
                active_knowledge_context, prompt_choice, vars, warnings=warnings
            )
            return rendered, template
        return "", None

    def get_knowledge_used_keys(self, active_knowledge_context: str, identifier: str):
        if identifier is not None:
            template = self.create_template(active_knowledge_context, identifier).dict()
            return template["input_variables"]

    def get_default_context(self, prompt_choice: str):
        return self.get(prompt_choice).metadata.get("context", "None")

    def get_knowledge_used(self, prompt_choice: str, active_knowledge_context: str):
        prompt = self.get(prompt_choice)
        if prompt is not None:
            knowledge_keys = self.get_knowledge_used_keys(
                active_knowledge_context, prompt_choice
            )
            knowledge = []
            for key in knowledge_keys:
                knowledge_entry = self.knowledge_base.get_knowledge_document(
                    active_knowledge_context, key
                )
                if knowledge_entry:
                    knowledge.append(knowledge_entry.metadata)

            return knowledge

    def render_help_markdown(self, prompt_choice: str, context_selected: str):
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
            knowledge_used = self.get_knowledge_used(prompt_choice, context_selected)

            knowledge_used_markdown = (
                "**Knowledge used:** "
                + ", ".join(
                    f"_{knowledge['title']}_ from _{context_selected}_"
                    for knowledge in knowledge_used
                )
                if knowledge_used
                else None
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

    def get_follow_ups(self, identifier):
        follow_ups = []
        for flow in self.prompt_flows:
            if flow["firstStep"]["identifier"] == identifier:
                for follow_up in flow["followUps"]:
                    follow_up_id = follow_up["identifier"]
                    follow_up_prompt = self.get(follow_up_id)
                    if follow_up_prompt:
                        follow_ups.append(
                            {
                                "identifier": follow_up_id,
                                "title": follow_up_prompt.metadata.get("title"),
                                "help_prompt_description": follow_up_prompt.metadata.get(
                                    "help_prompt_description"
                                ),
                            }
                        )
        return follow_ups

    def get_prompts_with_follow_ups(self):
        prompts_with_follow_ups = []
        for prompt in self.prompts:
            follow_ups = self.get_follow_ups(prompt.metadata.get("identifier"))
            prompt_data = {
                "identifier": prompt.metadata.get("identifier"),
                "title": prompt.metadata.get("title"),
                "system": prompt.metadata.get("system"),
                "categories": prompt.metadata.get("categories"),
                "help_prompt_description": prompt.metadata.get(
                    "help_prompt_description"
                ),
                "help_user_input": prompt.metadata.get("help_user_input"),
                "follow_ups": follow_ups,
                "type": prompt.metadata.get("type", "chat"),
                "scenario_queries": prompt.metadata.get("scenario_queries"),
                "editable": prompt.metadata.get("editable"),
                "show": prompt.metadata.get("show"),
            }
            prompts_with_follow_ups.append(prompt_data)
        return prompts_with_follow_ups

    def produces_json_output(self, identifier):
        prompt = self.get(identifier)
        return (
            prompt.metadata.get("identifier").startswith("guided-")
            or prompt.metadata.get("type") == "cards"
        )
