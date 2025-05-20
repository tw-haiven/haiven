# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os
import yaml
from typing import List

import frontmatter
from langchain.prompts import PromptTemplate
from knowledge.markdown import KnowledgeBaseMarkdown
from knowledge_manager import KnowledgeManager


class PromptList:
    def __init__(
        self,
        interaction_type,
        knowledge_base: KnowledgeBaseMarkdown,
        knowledge_manager: KnowledgeManager,
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
            self.add_filename_to_metadata(
                frontmatter.load(os.path.join(directory, filename)), filename
            )
            for filename in prompt_files
        ]

        self.knowledge_base = knowledge_base
        self.knowledge_manager = knowledge_manager
        self.extra_variables = variables

        for prompt in self.prompts:
            if "title" not in prompt.metadata:
                prompt.metadata["title"] = "Unnamed use case"
            if "categories" not in prompt.metadata:
                prompt.metadata["categories"] = []
            if "type" not in prompt.metadata:
                prompt.metadata["type"] = "chat"
            if "editable" not in prompt.metadata:
                prompt.metadata["editable"] = False
            if "show" not in prompt.metadata:
                prompt.metadata["show"] = True
            if "grounded" not in prompt.metadata:
                prompt.metadata["grounded"] = False

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

    def get(self, identifier):
        for prompt in self.prompts:
            if prompt.metadata.get("identifier") == identifier:
                return prompt
        return None

    def create_template(self, identifier: str) -> PromptTemplate:
        prompt_data = self.get(identifier)
        if not prompt_data:
            raise ValueError(f"Prompt {identifier} not found")

        prompt_text = prompt_data.content

        variables = ["user_input"] + self.extra_variables

        return PromptTemplate(input_variables=variables, template=prompt_text)

    def create_and_render_template(
        self,
        identifier,
        variables,
    ):
        knowledge_and_input = {**variables}

        template = self.create_template(identifier)

        for key in template.input_variables:
            if key not in knowledge_and_input:
                knowledge_and_input[str(key)] = (
                    "None provided, please try to help without this information."  # placeholder for the prompt
                )

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
        prompt_choice: str,
        user_input: str,
        additional_vars: dict = {},
    ) -> str:
        if prompt_choice is not None:
            vars = additional_vars
            vars["user_input"] = user_input
            rendered, template = self.create_and_render_template(
                prompt_choice,
                vars,
            )
            return rendered, template
        return "", None

    def get_default_context(self, prompt_choice: str):
        return self.get(prompt_choice).metadata.get("context", "None")

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

    def get_prompts_with_follow_ups(self, includeContent=False, category=None):
        prompts_with_follow_ups = []
        prompts = self.prompts

        if category:
            prompts = [
                prompt
                for prompt in self.prompts
                if category in prompt.metadata.get("categories", [])
            ]

        for prompt in prompts:
            prompt_data = self.attach_follow_ups(prompt, includeContent)
            prompts_with_follow_ups.append(prompt_data)
        return prompts_with_follow_ups

    def get_a_prompt_with_follow_ups(self, prompt_id, includeContent=False):
        prompt = self.get(prompt_id)
        prompt_with_follow_ups = self.attach_follow_ups(prompt, includeContent)

        return prompt_with_follow_ups

    def attach_follow_ups(self, prompt, includeContent=False):
        follow_ups = self.get_follow_ups(prompt.metadata.get("identifier"))
        prompt_data = {
            "identifier": prompt.metadata.get("identifier"),
            "title": prompt.metadata.get("title"),
            "categories": prompt.metadata.get("categories"),
            "help_prompt_description": prompt.metadata.get("help_prompt_description"),
            "help_user_input": prompt.metadata.get("help_user_input"),
            "help_sample_input": prompt.metadata.get("help_sample_input"),
            "follow_ups": follow_ups,
            "type": prompt.metadata.get("type", "chat"),
            "scenario_queries": prompt.metadata.get("scenario_queries"),
            "editable": prompt.metadata.get("editable"),
            "show": prompt.metadata.get("show"),
            "filename": prompt.metadata.get("filename"),
            "grounded": prompt.metadata.get("grounded", False),
            **(
                {"content": prompt.content} if includeContent and prompt.content else {}
            ),
        }

        return prompt_data

    def produces_json_output(self, identifier):
        prompt = self.get(identifier)
        return (
            prompt.metadata.get("identifier").startswith("guided-")
            or prompt.metadata.get("type") == "cards"
        )

    def add_filename_to_metadata(self, prompt, filename):
        file_name_without_extension = os.path.splitext(filename)[0]
        prompt.metadata["filename"] = file_name_without_extension
        return prompt
