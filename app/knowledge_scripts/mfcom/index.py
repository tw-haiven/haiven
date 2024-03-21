# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import pickle
import os
from os.path import exists
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS


def split_docs(documents, chunk_size=600, chunk_overlap=20):
    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    docs = text_splitter.split_documents(documents)

    return docs


def load_docs_from_pickle(filename):
    if exists(filename):
        with open(filename, "rb") as f:
            docs = pickle.load(f)
            print(f"a total of {len(docs)} documents loaded from {filename}")
            return docs
    return []


def index_docs_category(category):
    pickles = [
        f"knowledge_scripts/mfcom/mfcom-{category}.pickle",
    ]

    print("Loading extracted documents...")
    documents = sum(map(load_docs_from_pickle, pickles), [])
    print(f"Found {len(documents)} documents")
    splitted_documents = split_docs(documents)
    print(f"Number of chunks: {len(splitted_documents)}")

    print("Setting up embedder...")
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])

    print("Setting up FAISS vector store and calculating embeddings...")
    db = FAISS.from_documents(splitted_documents, embeddings)

    print("Persisting faiss_index to disk...")
    db.save_local(f"teams/team_demo/knowledge/documents/mfcom-{category}.kb")

    print("Done!")


def index_docs():
    index_docs_category("all")
    # index_docs_category("technical")
    # index_docs_category("agile")


if __name__ == "__main__":
    load_dotenv()
    index_docs()
