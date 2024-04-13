# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.

import os
import pickle

from langchain_core.documents import Document
from pypdf import PdfReader
from typing import List


class FileService:
    def get_text_and_metadata_from_pdf(self, pdf_file):
        text = []
        metadatas = []
        pdf_reader = PdfReader(pdf_file)
        page_number = 1
        for page in pdf_reader.pages:
            text.append(page.extract_text())
            metadatas.append({"page": page_number, "file": pdf_file.name})
            page_number += 1
        return text, metadatas

    def write_pickles(
        self, documents: List[Document], output_dir: str, pickle_file_path: str
    ):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(f"{output_dir}/{pickle_file_path}", "wb") as f:
            pickle.dump(documents, f)

    def get_files_path_from_directory(self, source_dir: str):
        files = []
        for root, _, filenames in os.walk(source_dir):
            for filename in filenames:
                files.append(os.path.join(root, filename))
        return files

    def write_metadata_file(self, metadata: List[dict], output_path: str):
        metadata_file_content = "---\n"
        for metadata_item in metadata:
            metadata_file_content += f"{metadata_item}: {metadata[metadata_item]}\n"
        metadata_file_content += "---\n"
        with open(output_path, "w") as f:
            f.write(str(metadata_file_content))
