# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from langchain.prompts import PromptTemplate


def question_answer_prompt():
    template = """You are a DocuDialog AI provides information over the following pieces of context to answer the question at the end. 
    Do not answer the question if its out of context provided.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.

    context:
    ```
    {context}
    ```
           
    {question}
    Answer in markdown:"""

    prompt = PromptTemplate(input_variables=["context", "question"], template=template)
    return prompt


def summary_prompt():
    template = """Write a concise summary of following conversation:
    {input}

    CONCISE SUMMARY WITH KEY ENTITIES:"""

    prompt = template
    return prompt
