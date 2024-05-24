import os
from typing import List

import gradio as gr
from dotenv import load_dotenv
from shared.documents_utils import DocumentsUtils, get_text_and_metadata_from_pdf
from shared.services.embeddings_service import EmbeddingsService
from shared.llm_config import LLMConfig
from shared.chats import DocumentsChat, ServerChatSessionMemory
from shared.models.chat_context import ChatContext
from shared.user_feedback import UserFeedback
from shared.user_context import user_context


def enable_knowledge_chat(
    CHAT_SESSION_MEMORY: ServerChatSessionMemory,
    llm_config: LLMConfig,
    active_knowledge_context: str,
    user_identifier_state: gr.State,
    category_filter: List[str],
    knowledge_context_select: gr.Dropdown = None,
):
    load_dotenv()
    tab_id = "knowledge_chat"

    chat_context = ChatContext(
        tab_id=tab_id,
        interaction_pattern=category_filter[0],
        model="",
        temperature=0.2,
        prompt="Knowledge chat",
        message="",
    )

    main_tab = gr.Tab("Knowledge Chat", id=tab_id)
    with main_tab:
        with gr.Row():
            with gr.Column(scale=3):
                with gr.Group(elem_classes="haiven-group"):
                    gr.Markdown(
                        "## 1. What knowledge do you want to search?",
                        elem_classes="haiven-group-title",
                    )
                    with gr.Group():
                        with gr.Row(elem_classes="knowledge-advice"):
                            context_selected = active_knowledge_context
                            knowledge_documents = [("All documents", "all")]
                            knowledge_documents.extend(
                                (embedding.title, embedding.key)
                                for embedding in EmbeddingsService.get_embedded_documents(
                                    context=context_selected
                                )
                            )
                            ui_knowledge_choice = gr.Dropdown(
                                knowledge_documents,
                                label="Choose an existing knowledge base",
                                elem_id="knowledge_chat_prompt_choice",
                            )
                        with gr.Row():
                            ui_loaded_file_label = gr.Markdown("Loaded: None")

            with gr.Column(scale=5):
                with gr.Group(elem_classes="haiven-group"):
                    gr.Markdown(
                        "## 2. Ask a question", elem_classes="haiven-group-title"
                    )
                    ui_question = gr.Textbox(label="Question (Hit Enter to send)")
                    ui_chatbot = gr.Chatbot(
                        label="Answer", height=550, show_copy_button=True, likeable=True
                    )

        def load_pdf(file):
            chat_context.prompt = "Knowledge chat - Upload"
            with open(file, "rb") as pdf_file:
                text, metadata = get_text_and_metadata_from_pdf(pdf_file)
                documents = (text, metadata)
                EmbeddingsService.generate_base_document_from_text(
                    document_key=pdf_file.name,
                    document_metadata={
                        "title": metadata[0].title,
                        "source": metadata[0].source,
                        "author": metadata[0].author,
                        "sample_question": "",  # LLM can potentially generate this
                        "description": "",  # LLM can potentially generate this
                    },
                    content=documents,
                )

            udated_dd = gr.update(
                choices=[
                    (embedding.title, embedding.key)
                    for embedding in EmbeddingsService.get_embedded_documents()
                ]
            )

            info_text = "{} is loaded.".format(os.path.basename(file.name))
            return {
                ui_loaded_file_label: info_text,
                # clear question and answer
                ui_question: "",
                ui_chatbot: [],
                ui_knowledge_choice: udated_dd,
            }

        def load_knowledge(
            knowledge_document_selected: str,
            user_identifier_state: str,
            request: gr.Request,
        ):
            info_text = "No documents selected"

            knowledge_key = None
            knowledge_context = None

            if knowledge_document_selected:
                chat_context.prompt = "Knowledge chat - Existing"
                if knowledge_document_selected == "all":
                    knowledge_key = knowledge_document_selected
                    knowledge_context = user_context.get_value(
                        request, "active_knowledge_context", app_level=True
                    )
                else:
                    knowledge = EmbeddingsService.get_embedded_document(
                        knowledge_document_selected
                    )
                    knowledge_key = knowledge.key
                    knowledge_context = knowledge.context

                chat_session_key_value, chat_session = (
                    CHAT_SESSION_MEMORY.get_or_create_chat(
                        lambda: DocumentsChat(
                            llm_config=llm_config,
                            knowledge=knowledge_key,
                            context=knowledge_context,
                        ),
                        None,
                        "knowledge-chat",
                        user_identifier_state,
                    )
                )

                if knowledge_document_selected == "all":
                    info_text = "All documents are loaded."
                elif knowledge_document_selected:
                    info_text = f'"{knowledge.title}" is loaded.\n\n**Source:** {DocumentsUtils.get_source_title_link(vars(knowledge))}\n\n**Sample question:** {knowledge.sample_question}'
                return {
                    ui_loaded_file_label: info_text,
                    state_chat_session_key: chat_session_key_value,
                    # clear the chat
                    ui_question: "",
                    ui_chatbot: [],
                }

            return {
                ui_loaded_file_label: info_text,
                state_chat_session_key: None,
                ui_question: "",
                ui_chatbot: [],
            }

        def ask_question(
            question: str, chat_session_key_value: str, request: gr.Request
        ):
            try:
                chat_session = CHAT_SESSION_MEMORY.get_chat(chat_session_key_value)

                llm_config_from_session = user_context.get_value(
                    request, "llm_model", app_level=True
                )
                temperature_from_session = user_context.get_value(
                    request, "llm_tone", app_level=True
                )
                if llm_config_from_session:
                    chat_session.llm_config.change_model(llm_config_from_session)
                if temperature_from_session:
                    chat_session.llm_config.change_temperature(temperature_from_session)

                response, sources_markdown = chat_session.next(question)
                history = [(question, response + "\n\n" + sources_markdown)]
                return {
                    ui_question: "",
                    ui_chatbot: history,
                    state_chat_session_key: chat_session_key_value,
                }
            except ValueError as e:
                raise ValueError(
                    "Could not identify chat session, make sure to select a PDF first: "
                    + str(e)
                )

        state_chat_session_key = gr.State()

        ui_knowledge_choice.change(
            fn=load_knowledge,
            inputs=[ui_knowledge_choice, user_identifier_state],
            outputs=[
                ui_loaded_file_label,
                state_chat_session_key,
                ui_question,
                ui_chatbot,
            ],
        )

        ui_question.submit(
            ask_question,
            [ui_question, state_chat_session_key],
            [ui_question, ui_chatbot, state_chat_session_key],
        )

        def on_vote(vote: gr.LikeData):
            chat_context.model = llm_config.service_name
            chat_context.temperature = llm_config.temperature
            chat_context.message = vote.value

            UserFeedback.on_message_voted(
                "liked" if vote.liked else "disliked",
                chat_context.to_dict(),
            )

        ui_chatbot.like(on_vote, None, None)

    def is_empty(value) -> bool:
        return value is None or value == "" or len(value) == 0

    def on_knowledge_context_selected(knowledge_context_select, request: gr.Request):
        if is_empty(knowledge_context_select):
            return

        choices = [("All Documents", "all")]
        choices.extend(
            (embedding.title, embedding.key)
            for embedding in EmbeddingsService.get_embedded_documents(
                context=knowledge_context_select
            )
        )

        udated_dd = gr.update(choices=choices, value=None)

        return udated_dd

    if knowledge_context_select:
        gr.on(
            triggers=[knowledge_context_select.change],
            fn=on_knowledge_context_selected,
            inputs=knowledge_context_select,
            outputs=ui_knowledge_choice,
        )
