# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import pickle
from os.path import exists
from dotenv import load_dotenv
from shared.embeddings import Embeddings
from shared.services.config_service import ConfigService
from langchain_community.vectorstores import FAISS


def split_docs(documents, spliter):
    print("Splitting documents into chunks...")
    docs = spliter.split_documents(documents)
    return docs


def load_docs_from_pickle(filename):
    if exists(filename):
        with open(filename, "rb") as f:
            docs = pickle.load(f)
            print(f"a total of {len(docs)} documents loaded from {filename}")
            return docs
    return []


def index_docs_category(category):
    team_ai_embeddings = Embeddings(ConfigService.load_embedding_model("config.yaml"))
    spliter = team_ai_embeddings._load_text_splitter()

    pickles = [
        f"knowledge_scripts/mfcom/mfcom-{category}.pickle",
    ]

    print("Loading extracted documents...")
    documents = sum(map(load_docs_from_pickle, pickles), [])
    print(f"Found {len(documents)} documents")
    splitted_documents = split_docs(documents, spliter)
    print(f"Number of chunks: {len(splitted_documents)}")

    print("Setting up embedder...")
    embeddings = team_ai_embeddings._get_embeddings_provider()

    n = 4  # Example value, adjust based on requirements
    document_collections = [splitted_documents[i::n] for i in range(n)]

    dbs = []

    for index, documents in enumerate(document_collections, start=1):
        print(
            f"Setting up FAISS vector store and calculating embeddings for collection {index}..."
        )
        dbs.append(FAISS.from_documents(documents, embeddings))

    merged_db = dbs[0]
    for db in dbs[1:]:
        print("Merging dbs...")
        merged_db.merge_from(db)

    print(f"Persisting faiss_index for category {category} to disk...")
    merged_db.save_local(f"knowledge_scripts/mfcom/embeddings/mfcom-{category}.kb")

    print("Done!")


def index_docs():
    index_docs_category("all")
    # index_docs_category("technical")
    # index_docs_category("agile")


if __name__ == "__main__":
    load_dotenv()
    index_docs()
