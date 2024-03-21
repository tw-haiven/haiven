# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import os
from typing import List

import gradio as gr
from dotenv import load_dotenv
from shared.llm_config import LLMConfig
from shared.chats import DocumentsChat, PDFChat, ServerChatSessionMemory
from shared.knowledge import (
    KnowledgeBaseDocuments,
    KnowledgeBasePDFs,
    KnowledgeEntryVectorStore,
)
from shared.models.chat_context import ChatContext
from shared.user_feedback import UserFeedback


def enable_knowledge_chat(
    CHAT_SESSION_MEMORY: ServerChatSessionMemory,
    knowledge_base_pdfs: KnowledgeBasePDFs,
    knowledge_base_documents: KnowledgeBaseDocuments,
    llm_config: LLMConfig,
    user_identifier_state: gr.State,
    category_filter: List[str] = None,
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

    with gr.Tab("Knowledge Chat", id=tab_id):
        with gr.Row():
            with gr.Column(scale=3):
                with gr.Group(elem_classes="teamai-group"):
                    gr.Markdown(
                        "## 1. What knowledge do you want to search?",
                        elem_classes="teamai-group-title",
                    )
                    with gr.Group():
                        with gr.Row(elem_classes="knowledge-advice"):
                            all_knowledge = knowledge_base_pdfs.get_title_id_tuples()
                            all_knowledge.extend(
                                knowledge_base_documents.get_title_id_tuples()
                            )
                            ui_knowledge_choice = gr.Dropdown(
                                all_knowledge, label="Choose an existing knowledge base"
                            )
                            ui_upload_button = gr.UploadButton(
                                "...or upload a PDF file",
                                file_types=["pdf"],
                                variant="primary",
                            )
                        with gr.Row():
                            ui_loaded_file_label = gr.Markdown("Loaded: None")

            with gr.Column(scale=5):
                with gr.Group(elem_classes="teamai-group"):
                    gr.Markdown(
                        "## 2. Ask a question", elem_classes="teamai-group-title"
                    )
                    ui_question = gr.Textbox(label="Question (Hit Enter to send)")
                    ui_chatbot = gr.Chatbot(
                        label="Answer", height=550, show_copy_button=True, likeable=True
                    )

        def load_pdf(file, user_identifier_state: str):
            chat_context.prompt = "Knowledge chat - Upload"
            chat_session_key_value, chat_session = (
                CHAT_SESSION_MEMORY.get_or_create_chat(
                    lambda: PDFChat.create_from_uploaded_pdf(
                        llm_config=llm_config, upload_file_name=file.name
                    ),
                    None,
                    "knowledge-chat",
                    user_identifier_state,
                )
            )

            info_text = "{} is loaded.".format(os.path.basename(file.name))
            return {
                ui_loaded_file_label: info_text,
                state_chat_session_key: chat_session_key_value,
                # clear question and answer
                ui_question: "",
                ui_chatbot: [],
            }

        def load_knowledge(choice: str, user_identifier_state: str):
            chat_context.prompt = "Knowledge chat - Existing"
            knowledge = knowledge_base_pdfs.get(choice)
            if knowledge is None:
                # DOCUMENTS
                knowledge: KnowledgeEntryVectorStore = knowledge_base_documents.get(
                    choice
                )
                chat_session_key_value, chat_session = (
                    CHAT_SESSION_MEMORY.get_or_create_chat(
                        lambda: DocumentsChat(
                            llm_config=llm_config, knowledge=knowledge
                        ),
                        None,
                        "knowledge-chat",
                        user_identifier_state,
                    )
                )
            else:
                # PDF
                chat_session_key_value, chat_session = (
                    CHAT_SESSION_MEMORY.get_or_create_chat(
                        lambda: PDFChat.create_from_knowledge(
                            llm_config=llm_config, knowledge_metadata=knowledge
                        ),
                        None,
                        "knowledge-chat",
                        user_identifier_state,
                    )
                )

            info_text = f'"{knowledge.title}" is loaded.\n\n**Source:** {knowledge.source}\n\n**Sample question:** {knowledge.sample_question}'
            return {
                ui_loaded_file_label: info_text,
                state_chat_session_key: chat_session_key_value,
                # clear the chat
                ui_question: "",
                ui_chatbot: [],
            }

        def ask_question(question: str, chat_session_key_value: str):
            try:
                chat_session = CHAT_SESSION_MEMORY.get_chat(chat_session_key_value)

                response, sources_markdown = chat_session.next(question)
                history = [(question, response + "\n\n" + sources_markdown)]
                return {
                    ui_question: "",
                    ui_chatbot: history,
                    state_chat_session_key: chat_session_key_value,
                }
            except ValueError:
                raise ValueError(
                    "Could not identify chat session, make sure to select a PDF first"
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

        ui_upload_button.upload(
            load_pdf,
            [ui_upload_button, user_identifier_state],
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
