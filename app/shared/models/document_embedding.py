# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from langchain_community.vectorstores import FAISS


class DocumentEmbedding:
    def __init__(
        self,
        key: str,
        retriever: FAISS,
        title: str,
        source: str,
        sample_question: str,
        description: str,
        context: str,
        provider: str,
    ):
        self.key = key
        self.retriever = retriever
        self.title = title
        self.source = source
        self.sample_question = sample_question
        self.description = description
        self.provider = provider
        self.context = context
