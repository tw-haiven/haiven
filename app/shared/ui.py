# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from typing import List

import gradio as gr
from dotenv import load_dotenv
from shared.documents_utils import DocumentsUtils
from shared.knowledge import KnowledgeBaseMarkdown
from shared.llm_config import LLMConfig
from shared.models.knowledge_pack import KnowledgePack
from shared.prompts import PromptList
from shared.services.config_service import ConfigService
from shared.services.embeddings_service import EmbeddingsService
from shared.services.models_service import ModelsService


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
                application_name = ConfigService.load_application_name()
                gr.HTML(f"<h1>{application_name}</h1><h2>Team assistant</h2>")

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
        knwoledge_pack_definition: KnowledgePack,
    ):
        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("## Context knowledge")
                for context_key in [
                    context.name for context in knwoledge_pack_definition.contexts
                ]:
                    context_content = (
                        knowledge_base_markdown.get_all_knowledge_documents(context_key)
                    )
                    with gr.Accordion(
                        label=context_key.replace("_", " ").title(), open=False
                    ):
                        if context_content and len(context_content) > 0:
                            for knowledge_entry in context_content:
                                gr.Textbox(
                                    knowledge_entry.content,
                                    label=knowledge_entry.metadata["title"],
                                    lines=10,
                                    show_copy_button=True,
                                )
                        else:
                            gr.Textbox(
                                "No knowledge found for this context", show_label=False
                            )
            with gr.Column(scale=2):
                gr.Markdown("## Documents")
                context_content = EmbeddingsService.get_embedded_documents()
                with gr.Accordion(label="Common documents", open=False):
                    if context_content and len(context_content) > 0:
                        for embbedding_document in context_content:
                            gr.Markdown(f"""
    ### {embbedding_document.title}

    **File:** {DocumentsUtils.get_source_title_link(vars(embbedding_document))}

    **Description:** {embbedding_document.description}

                    """)
                    else:
                        gr.Textbox(
                            "No knowledge found for this context", show_label=False
                        )

                for context_key in [
                    context.name for context in knwoledge_pack_definition.contexts
                ]:
                    context_content = EmbeddingsService.get_embedded_documents(
                        context_key, False
                    )
                    with gr.Accordion(
                        label=context_key.replace("_", " ").title(), open=False
                    ):
                        if context_content and len(context_content) > 0:
                            for embbedding_document in context_content:
                                gr.Markdown(f"""
    ### {embbedding_document.title}

    **File:** {DocumentsUtils.get_source_title_link(vars(embbedding_document))}

    **Description:** {embbedding_document.description}
                                """)
                        else:
                            gr.Textbox(
                                "No knowledge found for this context", show_label=False
                            )

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
            To learn more about how data is being processed, please refer to the 'Data processing' tab.
        """,
            elem_classes="disclaimer",
        )
        gr.Markdown(
            """
                ## !! "Team AI" is becoming "Haiven" !!

                **The Haiven team assistant is a tool to help software delivery teams evaluate the value of Generative AI as an *assistant and knowledge amplifier for frequently done tasks* across their software delivery lifecycle.**

                This setup allows the use of GenAI in a way that is optimized for a particular team's or organization's needs, 
                wherever existing products are too rigid or don't exist yet. Prompts can be created and shared across the team,
                and knowledge from the organisation can be infused into the chat sessions.

                ### Benefits
                - Amplifying and scaling good prompt engineering via reusable prompts
                - Knowledge exchange via the prepared context parts of the prompts
                - Helping people with tasks they have never done before (e.g. if team members have little experience with story-writing)
                - Using GenAI for divergent thinking, brainstorming and finding gaps earlier in the delivery process
                
                ![Overview of Haiven setup](/static/teamai_overview_more_details.png)

            """,
            elem_classes="about",
        )

    def ui_show_data_processing(self):
        gr.Markdown(
            """
            ## 3rd party model services
            """
        )
        gr.Markdown(
            """
            Please be conscious of this and responsible about what data you enter when 
            you're having a chat conversation.    
            """,
            elem_classes="disclaimer",
        )
        gr.Markdown("""

            Each chat message is shared with an AI model. Depending on which "AI service and model" you indicate 
            in the UI, that's where your chat messages go (typically either a cloud service, or a model running on 
            your local machine). 
                    
            Most of the 3rd party model services have terms & conditions that say that they do NOT use your data
            to fine-tune their models in the future. However, these services do typically persist chat conversations, 
            at least temporary, so your data is stored on their servers, at least temporarily.
                    
            Therefore, please comply with your organization's data privacy and security policies when using this tool.
            In particular, you should never add any PII (personally identifiable information) 
            as part of your instructions to the AI. For all other types of data, consider the sensitivity and confidentiality 
            in the context of your particular situation, and consult your organization's data privacy policies.
            
            ## Data Collection

            The only data that gets persisted by this application itself is in the form of logs. 

            The application logs data about the following events:
            - Whenever a page is loaded, to track amount of activity
            - Whenever a chat session is being started, to track amount of activity
            - How many times a certain prompt is used, to track popularity of a prompt
            - Clicks on thumbs up and thumbs down, to track how useful the tool is for users

            User IDs from the OAuth session are included in each log entry to get an idea of how many different users are using the application.

            The application does NOT persist the contents of the chat sessions.
            """)

    def create_knowledge_context_selector_ui(self, knowledge_pack: KnowledgePack):
        knowledge_context_choices: List[tuple[str, str]] = [
            (context.name.replace("_", " ").title(), context.path)
            for context in knowledge_pack.contexts
        ]
        knowledge_context_choices.sort(key=lambda x: x[0])
        knowledge_packs_selector = gr.Dropdown(
            knowledge_context_choices,
            label="Choose knowledge context",
            interactive=True,
            elem_classes=["knowledge-pack-selector"],
        )
        return knowledge_packs_selector

    def create_llm_settings_ui(
        self, features_filter: List[str] = []
    ) -> tuple[gr.Dropdown, gr.Radio, LLMConfig]:
        features_filter.append("text-generation")
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

        temperature_slider = gr.Slider(
            minimum=0.2,
            maximum=0.8,
            step=0.3,
            value=0.2,
            label="Temperature (More precise 0.2 - 0.8 More creative)",
            interactive=True,
            elem_classes="model-settings",
        )
        temperature_slider.value = default_temperature

        if ConfigService.load_default_models().chat is not None:
            dropdown.value = ConfigService.load_default_models().chat
            dropdown.interactive = False
            dropdown.label = "Default model set in configuration"

        llmConfig = LLMConfig(dropdown.value, temperature_slider.value)

        return dropdown, temperature_slider, llmConfig

    def create_about_tab_for_task_area(
        self, category_names: str, category_metadata, all_prompt_lists: List[PromptList]
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
            section_title = category_metadata["title"]
            markdown = f"# {section_title}\n## Available prompts\n{prompt_list_markdown}\n{videos_markdown}"
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
