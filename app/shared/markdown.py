# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import gradio as gr


def editor(markdown: str = ""):
    with gr.Row():
        with gr.Column(scale=0.5):
            code = gr.Code(
                markdown,
                language="markdown",
                interactive=True,
                label="Markdown",
                elem_classes="markdown-editor",
            )
        with gr.Column(scale=0.5):
            viewer = gr.Markdown(markdown, elem_classes="markdown")

        def update_view(content: str):
            return content

        code.change(update_view, inputs=[code], outputs=[viewer])

    return code, viewer
