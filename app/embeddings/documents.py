# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from langchain_community.vectorstores import FAISS
from typing import List
from langchain.docstore.document import Document


class KnowledgeDocument:
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


class DocumentsUtils:
    @staticmethod
    def get_unique_sources(
        documents: List[Document],
    ) -> List[dict[str, str]]:
        unique_sources = []
        unique_keys = []
        for doc in documents:
            key = f"{doc.metadata.get('source', 'unkown source')}#{doc.metadata.get('page', '')}"
            if key not in unique_keys:
                unique_keys.append(key)
                unique_sources.append(doc)

        return unique_sources

    @staticmethod
    def get_source_title_link(document_metadata: dict) -> str:
        page_anchor = (
            f"#page={DocumentsUtils.get_source_page(document_metadata)}"
            if DocumentsUtils.get_source_page(document_metadata)
            else ""
        )
        if "source" in document_metadata:
            source_link = document_metadata["source"]
            if (
                source_link
                and not source_link.startswith("http")
                and "kp-static" not in source_link
            ):
                source_link = "/kp-static/" + source_link

            if "title" in document_metadata:
                return (
                    f"[{document_metadata['title']}]({source_link}{page_anchor})"
                    if source_link
                    else document_metadata["title"]
                )
            else:
                return (
                    f"[{document_metadata['source']}]({source_link}{page_anchor})"
                    if source_link
                    else "unkown"
                )
        else:
            return "unknown"

    @staticmethod
    def get_source_page(document_metadata: dict) -> str:
        if "page" in document_metadata:
            return document_metadata["page"]
        else:
            return None

    @staticmethod
    def get_source_authors(document_metadata: dict) -> str:
        if "authors" in document_metadata:
            # Depending on how something was indexed, this value can have a few different shapes
            # Trying to be tolerant of different formats here and display them nicely
            if isinstance(document_metadata["authors"], list):
                return ", ".join(document_metadata["authors"])
            elif (
                isinstance(document_metadata["authors"], str)
                and document_metadata["authors"].startswith("[")
                and document_metadata["authors"].endswith("]")
            ):
                authors_string = document_metadata["authors"]
                if "'" in authors_string:
                    authors_string = authors_string.replace("'", "")

                return ", ".join(authors_string[1:-1].split(","))
            else:
                return document_metadata["authors"]
        else:
            return None

    @staticmethod
    def get_extra_metadata(source_metadata: dict) -> str:
        page_metadata = (
            f"Page {DocumentsUtils.get_source_page(source_metadata)}"
            if DocumentsUtils.get_source_page(source_metadata)
            else ""
        )
        authors_metadata = (
            f"Authors: {DocumentsUtils.get_source_authors(source_metadata)}"
            if DocumentsUtils.get_source_authors(source_metadata)
            else ""
        )
        return f"{page_metadata} {authors_metadata}"

    @staticmethod
    def get_search_result_item(document_metadata: dict) -> str:
        return f"{DocumentsUtils.get_source_title_link(document_metadata)} {f'({DocumentsUtils.get_extra_metadata(document_metadata).strip()})' if DocumentsUtils.get_extra_metadata(document_metadata) else ''}"
