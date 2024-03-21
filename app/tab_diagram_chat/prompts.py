# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from langchain.prompts import PromptTemplate

DIAGRAM_DISCUSSION_TEMPLATE = """
You are an expert in software development..

I am a team member in a software delivery team.

Some context about the application we are building:
===CONTEXT DESCRIPTION
{context}
===END OF CONTEXT DESCRIPTION

I received an image that describes: {image_purpose}. Here is a description of that image:
===IMAGE DESCRIPTION
{image_description}
===END IMAGE_DESCRIPTION

With the context and the image description, please help me the following task:
{user_input}

"""

prompt_user_input_key = "user_input"
prompt_context_key = "context"
prompt_image_description_key = "image_description"
prompt_image_purpose_key = "image_purpose"

prompt_diagrams_template = PromptTemplate(
    input_variables=[
        prompt_context_key,
        prompt_user_input_key,
        prompt_image_description_key,
    ],
    template=DIAGRAM_DISCUSSION_TEMPLATE,
)
