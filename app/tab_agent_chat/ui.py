# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

from typing import List
import gradio as gr
from dotenv import load_dotenv
from shared.user_feedback import UserFeedback
from shared.services.agents_service import AgentsService


def enable_agent_chat(
    agent_info: List[dict],
    user_identifier_state: gr.State,
):
    load_dotenv()
    tab_id = "agent_chat"

    main_tab = gr.Tab("Agent Chat", id=tab_id)
    with main_tab:
        with gr.Row():
            with gr.Column(scale=3):
                with gr.Group(elem_classes="haiven-group"):
                    gr.Markdown(
                        "## 1. Select the agent you want to chat with:",
                        elem_classes="haiven-group-title",
                    )
                    with gr.Group():
                        with gr.Row(elem_classes="knowledge-advice"):
                            agent_choices = [
                                (agent["agentName"], agent["agentId"])
                                for agent in agent_info
                            ]
                            ui_agent_choice = gr.Dropdown(
                                agent_choices,
                                label="Choose an agent",
                                elem_id="agent_choice",
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

        def ask_question(
            question: str,
            chat_session_key_value: str,
            ui_agent_choice: str,
            request: gr.Request,
        ):
            if not ui_agent_choice:
                raise ValueError("Please select an agent to chat with.")

            selected_agent = [
                agent for agent in agent_info if agent["agentId"] == ui_agent_choice
            ][0]
            response, sources_markdown = AgentsService.get_agent_response(
                question, ui_agent_choice, selected_agent["agentAliasId"]
            )
            sources_markdown = "### Sources\n\n" + sources_markdown
            history = [(question, response + "\n\n" + sources_markdown)]
            return {
                ui_question: "",
                ui_chatbot: history,
                state_chat_session_key: chat_session_key_value,
            }

        state_chat_session_key = gr.State()

        def load_agent(ui_agent_choice: str, user_identifier_state: gr.State):
            if ui_agent_choice:
                selected_agent = [
                    agent for agent in agent_info if agent["agentId"] == ui_agent_choice
                ][0]

            return {
                ui_loaded_file_label: f"Loaded: {selected_agent['agentName']}\n\nDescription: {selected_agent['description']}",
                ui_question: "",
            }

        ui_agent_choice.change(
            fn=load_agent,
            inputs=[ui_agent_choice, user_identifier_state],
            outputs=[ui_loaded_file_label, ui_question],
        )

        ui_question.submit(
            ask_question,
            [ui_question, state_chat_session_key, ui_agent_choice],
            [ui_question, ui_chatbot, state_chat_session_key],
        )

        def on_vote(ui_agent_choice, ui_chatbot, vote: gr.LikeData):
            data = {
                "selected_agent": ui_agent_choice,
                "selected_agent_alias": [
                    x["agentAliasId"]
                    for x in agent_info
                    if x["agentId"] == ui_agent_choice
                ][0],
                "interaction": ui_chatbot,
            }
            UserFeedback.on_message_voted(
                "liked" if vote.liked else "disliked",
                data,
            )

        ui_chatbot.like(on_vote, inputs=[ui_agent_choice, ui_chatbot], outputs=None)
