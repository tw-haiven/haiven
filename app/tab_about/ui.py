# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import gradio as gr


def enable_about():
    with gr.Tab("About Team AI"):
        gr.Markdown(
            "[Remember to be mindful](https://central.thoughtworks.net/home/about-our-company/our-craft/technology-thoughtworks/generative-ai-thoughtworks/generative-ai-guardrails-for-practioners) of the data you enter and upload here.",
            elem_classes="disclaimer",
        )
        gr.Markdown("""
            **Team AI is an accelerator to help software delivery teams build their own lightweight prompting application as an *assistant and knowledge amplifier for frequently done tasks* across their software delivery process.**
                    
            This demo shows some examples of the types of tasks that can be supported by GenAI, and the types of interaction patterns teams can leverage.
                    
            Be mindful about the data you enter here and follow our [Assurance Guardrails](https://central.thoughtworks.net/home/about-our-company/our-craft/technology-thoughtworks/generative-ai-thoughtworks/generative-ai-guardrails-for-practioners)

            ### Benefits
            - Amplifying and scaling good prompt engineering via reusable prompts
            - Use GenAI optimized for a particular team's or organization's tasks, wherever existing products are too rigid
            - Knowledge exchange via the prepared context parts of the prompts
            - Helping people with tasks they have never done before (e.g. if team members have little experience with story-writing)
            - The "Q&A" pattern in particular helps leverage LLMs for brainstorming and finding gaps earlier in the delivery process

            ### How does the "acceleration" work?            
            When a team takes the codebase as a starting point to deploy their own Team AI, they can use existing demo components as a basis for their own task support. E.g., use the "Story writing" example as a basis if you want to support a task with a Question<>Answer interaction. It's not a lot of code, the "Story writing" example is just about 70 lines of Python code, plus the prompting template.

            ### More
            Find more [context about Team AI here](https://docs.google.com/presentation/d/11VGcwOP-HxCXqDhUAd-PE6LWBeiMNbIItrdtyBRtkMI/edit?usp=sharing)
            
        """)
