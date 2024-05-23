# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from haiven_cli.services.embedding_service import EmbeddingService
from haiven_cli.services.token_service import TokenService


class KnowledgeService:
    def __init__(
        self, token_service: TokenService, embedding_service: EmbeddingService
    ):
        self.token_service = token_service
        self.embedding_service = embedding_service

    def index(self, texts, metadatas, embedding_model, output_dir):
        if texts is None or len(texts) == 0:
            raise ValueError("file content has no value")

        if embedding_model is None:
            raise ValueError("embedding model has no value")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=100,
            chunk_overlap=20,
            length_function=self.token_service.get_tokens_length,
            separators=["\n\n", "\n", " ", ""],
        )

        print("Creating documents out of", len(texts), "texts...")
        documents = text_splitter.create_documents(texts, metadatas)
        print("Loading embeddings model", embedding_model.name, "...")
        embeddings = self.embedding_service.load_embeddings(embedding_model)

        print("Creating DB...")
        db = FAISS.from_documents(documents, embeddings)
        try:
            local_db = FAISS.load_local(output_dir, embeddings)
            local_db.merge_from(db)
        except ValueError:
            print("Indexing to new path")
            local_db = db

        print("Saving DB to", output_dir)
        local_db.save_local(output_dir)
