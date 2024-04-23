# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from typing import List
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document

from shared.logger import TeamAILogger


class DocumentEmbedding:
    def __init__(
        self,
        key: str,
        retriever: FAISS,
        title: str,
        source: str,
        sample_question: str,
        description: str,
        kind: str,
        provider: str,
    ):
        self.key = key
        self.retriever = retriever
        self.title = title
        self.source = source
        self.sample_question = sample_question
        self.description = description
        self.provider = provider
        self.kind = kind

    def similarity_search(self, query) -> List[Document]:
        docs = self.retriever.get_relevant_documents(
            f"What context could be relevant to the following request: {query}"
        )
        TeamAILogger.get().analytics(f"Found {len(docs)} matches in {self.title}")

        return docs
