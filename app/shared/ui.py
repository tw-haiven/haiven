# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from typing import List

import gradio as gr
from dotenv import load_dotenv
from shared.services.embeddings_service import EmbeddingsService
from shared.services.config_service import ConfigService
from shared.services.models_service import ModelsService
from shared.knowledge import KnowledgeBaseMarkdown
from shared.llm_config import LLMConfig
from shared.prompts import PromptList


class UI:
    def __init__(self):
        load_dotenv()

    @staticmethod
    def PATH_KNOWLEDGE() -> str:
        return "knowledge"

    def styling(self) -> tuple[gr.themes.Base, str]:
        theme = gr.themes.Base(
            radius_size="none",
            primary_hue=gr.themes.Color(
                c200="#f2617aff",  # background color primary button
                c600="#fff",  # Font color primary button
                c50="#a0a0a0",  # background color chat bubbles
                c300="#d1d5db",  # border color chat bubbles
                c500="#f2617aff",  # color of the loader
                c100="#fae8ff",
                c400="#e879f9",
                c700="#a21caf",
                c800="#86198f",
                c900="#701a75",
                c950="#f2617a",
            ),
            font=["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
            font_mono=["Consolas", "ui-monospace", "Consolas", "monospace"],
        )

        with open("resources/styles/teamai.css", "r") as file:
            css = file.read()

        return theme, css

    def ui_header(self, navigation=None):
        with gr.Row(elem_classes="header"):
            with gr.Column(elem_classes="header-title"):
                gr.Markdown(
                    """
                    # Team AI Demo
                    """
                )

            with gr.Column(elem_classes="header-logo"):
                gr.Markdown(
                    """
                    ![Team AI](../static/thoughtworks_logo.png)
                    """
                )
        if navigation:
            with gr.Row(elem_classes="header"):
                navigation_html = ""
                for item in navigation["items"]:
                    icon_html = ""
                    classes = ""
                    if item["path"] == self.PATH_KNOWLEDGE():
                        icon_html = (
                            "<img src='/static/icon_knowledge_blue.png' class='icon'>"
                        )
                        classes = "knowledge"

                    navigation_html += f"<div class='item'><a href='/{item['path']}' class='item-link {classes} {'selected' if navigation['selected'] == item['path'] else ''}'>{icon_html}{item['title']}</a></div>"
                gr.HTML(f"<div class='navigation'>{navigation_html}</div>")

    def ui_show_knowledge(
        self,
        knowledge_base_markdown: KnowledgeBaseMarkdown,
    ):
        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("## Domain knowledge")
                for key in knowledge_base_markdown.get_all_keys():
                    gr.Textbox(
                        knowledge_base_markdown.get_content(key),
                        label=knowledge_base_markdown._knowledge.get(key)["title"],
                        lines=10,
                        show_copy_button=True,
                    )
            with gr.Column(scale=2):
                gr.Markdown("## Documents")
                pdf_knowledge = EmbeddingsService.get_embedded_documents()
                for knowledge in pdf_knowledge:
                    gr.Markdown(f"""
    ### {knowledge.title}

    **File:** {knowledge.source}

    **Description:** {knowledge.description}

                    """)

            with gr.Column(scale=1, elem_classes="user-help-col"):
                gr.Markdown("""
                "Team Knowledge" is maintained at a central place, and can be pulled into the prompts across the application.

                **Benefits:**
                - Users don't have to repeat over and over again for the AI what the domain or technical context is
                - Team members can benefit from the knowledge of others, in particular when they are new to the team or less experienced
                    """)

    def ui_show_about(self):
        gr.Markdown(
            """
                **Team AI is an accelerator to help software delivery teams build their own lightweight prompting application as an *assistant and knowledge amplifier for frequently done tasks* across their software delivery process.**

                This demo shows some examples of the types of tasks that can be supported by GenAI, and the types of interaction patterns teams can leverage.

                Be mindful about the data you enter here and follow our [Assurance Guardrails](https://central.thoughtworks.net/home/about-our-company/our-craft/technology-thoughtworks/generative-ai-thoughtworks/generative-ai-guardrails-for-practioners)

                ### Benefits
                - Amplifying and scaling good prompt engineering via reusable prompts
                - Use GenAI optimized for a particular team's or organization's tasks, wherever existing products are too rigid
                - Knowledge exchange via the prepared context parts of the prompts
                - Helping people with tasks they have never done before (e.g. if team members have little experience with story-writing)
                - The "Brainstorming" pattern in particular helps leverage LLMs for brainstorming and finding gaps earlier in the delivery process

                ![Overview of Team AI setup](/static/teamai_overview.png)

                ### How does the "acceleration" work?
                When a team takes the codebase as a starting point to deploy their own Team AI, they can use it as a starting point and plug in their own prompts and team knowledge.

                ### More
                Contact the [GenAI Pod](mailto:gen-ai-pod@thoughtworks.com), [Birgitta Boeckeler](mailto:bboeckel@thoughtworks.com), or the Head of Tech of your region's DEC to learn more about using Team AI with a client.

            """,
            elem_classes="about",
        )

    def create_llm_settings_ui(
        self, features_filter: List[str] = []
    ) -> tuple[gr.Dropdown, gr.Radio, LLMConfig]:
        available_options: List[tuple[str, str]] = _get_services(features_filter)
        default_temperature: float = _get_default_temperature()

        if len(available_options) == 0:
            raise ValueError(
                "No providers enabled, please check your environment variables"
            )

        dropdown = gr.Dropdown(
            available_options,
            label="Choose AI service and model to use",
            interactive=True,
            elem_classes=["model-settings", "model-settings-service"],
        )
        dropdown.value = available_options[0][1]

        tone_radio = gr.Radio(
            _get_valid_tone_values(),
            label="Temperature",
            interactive=True,
            elem_classes="model-settings",
        )
        tone_radio.value = default_temperature

        if ConfigService.load_default_models().chat is not None:
            dropdown.value = ConfigService.load_default_models().chat
            dropdown.interactive = False
            dropdown.label = "Default model set in configuration"

        llmConfig = LLMConfig(dropdown.value, tone_radio.value)

        return dropdown, tone_radio, llmConfig

    def create_about_tab_for_task_area(
        self,
        category_names: str,
        category_metadata,
        all_prompt_lists: List[PromptList],
        addendum_markdown: str = "",
    ):
        prompt_lists_copy = all_prompt_lists.copy()
        prompt_list_markdown = ""
        for prompt_list in prompt_lists_copy:
            prompt_list.filter(category_names)
            prompt_list_markdown += f"\n#### {prompt_list.interaction_pattern_name}\n\n{prompt_list.render_prompts_summary_markdown()}\n"

        videos_markdown = ""
        if "videos" in category_metadata:
            videos_markdown += "\n## Demo Videos\n\n"
            videos_markdown += "\n".join(
                [
                    f"- [{item['title']}]({item['url']})"
                    for item in category_metadata["videos"]
                ]
            )
            videos_markdown += "\n\nFor more examples, check out the 'About' sections of the other task areas."

        with gr.Tab("ABOUT", elem_id="about"):
            gr.Markdown(
                "[Remember to be mindful](https://central.thoughtworks.net/home/about-our-company/our-craft/technology-thoughtworks/generative-ai-thoughtworks/generative-ai-guardrails-for-practioners) of the data you enter and upload here.",
                elem_classes="disclaimer",
            )
            section_title = category_metadata["title"]
            markdown = f"# {section_title}\n## Available prompts\n{prompt_list_markdown}\n{addendum_markdown}\n{videos_markdown}"
            gr.Markdown(markdown, line_breaks=True)


def _get_valid_tone_values() -> List[tuple[str, float]]:
    return [
        ("More creative (0.8)", 0.8),
        ("Balanced (0.5)", 0.5),
        ("More precise (0.2)", 0.2),
    ]


def _get_default_temperature() -> float:
    return 0.2


def _get_services(features_filter: List[str]) -> List[tuple[str, str]]:
    active_model_providers = ConfigService.load_enabled_providers()
    models = ModelsService.get_models(
        providers=active_model_providers, features=features_filter
    )
    services = [(model.name, model.id) for model in models]

    return services
