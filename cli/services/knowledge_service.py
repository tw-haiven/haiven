# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from services.embedding_service import EmbeddingService
from services.token_service import TokenService


class KnowledgeService:
    def __init__(self, knowledge_base_path: str, token_service: TokenService):
        self.knowledge_base_path = knowledge_base_path
        self.token_service = token_service

    def index(self, texts, metadatas, embedding_model):
        if texts is None or len(texts) == 0 or texts[0] == "":
            raise ValueError("file content has no value")

        if embedding_model is None:
            raise ValueError("embedding model has no value")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=100,
            chunk_overlap=20,
            length_function=self.token_service.get_tokens_length,
            separators=["\n\n", "\n", " ", ""],
        )
        documents = text_splitter.create_documents(texts, metadatas)
        embeddings = EmbeddingService.load_embeddings(embedding_model)

        db = FAISS.from_documents(documents, embeddings)
        try:
            local_db = FAISS.load_local(self.knowledge_base_path)
            local_db.merge_from(db)
        except ValueError:
            print("indexing to new path")
            local_db = db

        local_db.save_local(self.knowledge_base_path)
