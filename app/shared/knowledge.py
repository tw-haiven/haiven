# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import os
from typing import List

import frontmatter
from shared.services.config_service import ConfigService
from shared.models.embedding_model import EmbeddingModel
from shared.document_retriever import DocumentRetrieval
from shared.embeddings import Embeddings
from langchain.docstore.document import Document


class KnowledgeBaseMarkdown:
    def __init__(self, team_name, root_dir="teams"):
        directory = root_dir + "/" + team_name + "/knowledge"
        knowledge_files = sorted(
            [f for f in os.listdir(directory) if f.endswith(".md") and f != "README.md"]
        )
        file_contents = [
            frontmatter.load(os.path.join(directory, filename))
            for filename in knowledge_files
        ]

        self._knowledge = {}
        self._knowledge_content_dict = {}
        for content in file_contents:
            if content.metadata["key"]:
                self._knowledge_content_dict[content.metadata.get("key")] = (
                    content.content
                )
                self._knowledge[content.metadata.get("key")] = content

    def get_content(self, key) -> str:
        entry = self._knowledge.get(key, None)
        if entry:
            return entry.content
        return None

    def get_all_keys(self):
        return list(self._knowledge.keys())

    def get_knowledge_content_dict(self):
        return self._knowledge_content_dict


class KnowledgeEntryVectorStore:
    def __init__(
        self, key, retriever, title, source, sample_question, description, provider
    ):
        self.key = key
        self.retriever = retriever
        self.title = title
        self.source = source
        self.sample_question = sample_question
        self.description = description
        self.provider = provider

    def get_documents(self, query) -> List[Document]:
        # !! Only works for the "Documents" type entries, design is a little wonky here, sorry...
        documents = DocumentRetrieval.get_docs_and_sources_from_document_store(
            self.retriever,
            query=f"What context could be relevant to the following request: {query}",
            chat_history=[],
        )
        return documents


class KnowledgeBaseVectorStore:
    def __init__(
        self, team_name, sub_dir, root_dir="teams", config_file_path="config.yaml"
    ):
        directory = root_dir + "/" + team_name + "/knowledge/" + sub_dir
        knowledge_files = sorted(
            [f for f in os.listdir(directory) if f.endswith(".md") and f != "README.md"]
        )
        knowledge_metadata = [
            frontmatter.load(os.path.join(directory, filename))
            for filename in knowledge_files
        ]

        self.config_file_path = config_file_path
        embedding_model: EmbeddingModel = ConfigService.load_embedding_model(
            config_file_path
        )
        provider = embedding_model.provider.lower()

        self._knowledge_dict = {}
        for metadata in knowledge_metadata:
            knowledge_provider = metadata.metadata.get("provider").lower()
            # only load knowledge that has been created with the same provider as the one used by the application
            if knowledge_provider == provider:
                kb_path = metadata.metadata["path"]
                kb_full_path = directory + "/" + kb_path
                self._knowledge_dict[metadata.metadata["key"]] = (
                    KnowledgeEntryVectorStore(
                        key=metadata.metadata["key"],
                        retriever=self.get_retriever(kb_full_path),
                        title=metadata.metadata["title"],
                        source=metadata.metadata.get("source", ""),
                        sample_question=metadata.metadata.get("sample_question", ""),
                        description=metadata.metadata["description"],
                        provider=metadata.metadata["provider"],
                    )
                )

    def get_retriever(self, kb_path: str):
        raise NotImplementedError("Subclasses must implement the get_retriever method.")

    def get(self, key) -> KnowledgeEntryVectorStore:
        return self._knowledge_dict.get(key, None)

    def get_all_keys(self):
        return list(self._knowledge_dict.keys())

    def get_knowledge(self):
        return self._knowledge_dict

    def get_title_id_tuples(self):
        return [(self._knowledge_dict[key].title, key) for key in self._knowledge_dict]


class KnowledgeBasePDFs(KnowledgeBaseVectorStore):
    def __init__(self, team_name, root_dir="teams", config_file_path="config.yaml"):
        super().__init__(team_name, "pdfs", root_dir, config_file_path)

    def get_retriever(self, kb_path: str):
        embeddings_provider = Embeddings(
            ConfigService.load_embedding_model(self.config_file_path)
        )
        return embeddings_provider.generate_from_filesystem(kb_path)


class KnowledgeBaseDocuments(KnowledgeBaseVectorStore):
    def __init__(self, team_name, root_dir="teams", config_file_path="config.yaml"):
        super().__init__(team_name, "documents", root_dir, config_file_path)

    def get_retriever(self, kb_path: str):
        return DocumentRetrieval.get_document_retriever(kb_path, self.config_file_path)


class DocumentationBase:
    def __init__(self, root_dir="teams"):
        directory = root_dir + "/documentation"
        doc_files = sorted(
            [f for f in os.listdir(directory) if f.endswith(".md") and f != "README.md"]
        )
        self._documentation = [
            frontmatter.load(os.path.join(directory, filename))
            for filename in doc_files
        ]

    def get_documentation_filtered(self, filter_categories):
        if filter_categories is not None:
            return list(
                filter(
                    lambda prompt: (
                        not prompt.metadata["categories"]
                        or any(
                            category in prompt.metadata["categories"]
                            for category in filter_categories
                        )
                    ),
                    self._documentation,
                )
            )
        return self._documentation
