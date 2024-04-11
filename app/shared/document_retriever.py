# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from typing import List, Tuple

from langchain.docstore.document import Document


class DocumentRetrieval:
    @staticmethod
    def get_unique_sources(
        documents: List[Tuple[Document, float]],
    ) -> Tuple[List[str], List[dict[str, str]]]:
        unique_sources = []
        metadata = []
        for doc, score in documents:
            print(
                f"@debug DocumentRetrieval.get_unique_sources: doc={doc}, score={score}"
            )
            source = doc.metadata.get("source", "unkown source")
            if source not in unique_sources:
                unique_sources.append(source)
                metadata.append(
                    {
                        "source": source,
                        "title": doc.metadata.get("title", "unknown title"),
                    }
                )

        return metadata
