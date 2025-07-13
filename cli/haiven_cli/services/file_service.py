# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os
import csv
import re

from pypdf import PdfReader
from typing import List


class FileService:
    def clean_text_with_spaces_between_characters(self, text: str):
        # Replace two spaces with one space, then remove spaces between characters and specified punctuation
        text = re.sub(r"(?<=[\w,.’\-():]) (?=[\w,.’\-():])", "", text)
        text = re.sub(r"  ", " ", text)
        return text

    def get_text_and_metadata_from_pdf(self, pdf_file, pdf_source_link=None):
        text = []
        metadatas = []
        pdf_reader = PdfReader(pdf_file)
        pdf_file_base_name = os.path.basename(pdf_file.name)

        page_number = 1
        pdf_title = _get_pdf_title(pdf_reader, pdf_file_base_name)
        pdf_authors = _get_pdf_authors(pdf_reader)
        pdf_source = pdf_source_link or pdf_file_base_name

        for page in pdf_reader.pages:
            text.append(page.extract_text())
            metadata_for_page = {
                "page": page_number,
                "source": pdf_source,
                "title": pdf_title,
                "authors": pdf_authors,
            }
            metadatas.append(metadata_for_page)
            page_number += 1
        return text, metadatas

    def get_text_and_metadata_from_csv(self, csv_file):
        text = []
        metadatas = []

        with open(csv_file, "r") as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                text.append(row["content"])
                metadatas.append(
                    {
                        "source": row["metadata.source"],
                        "title": row["metadata.title"],
                        "authors": row["metadata.authors"],
                    }
                )
        return text, metadatas

    def get_text_and_metadata_from_txts(self, txt_file_directory, authors="Unknown"):
        text = []
        metadatas = []
        txt_files = self.get_files_path_from_directory(txt_file_directory, ".txt")
        for txt_file in txt_files:
            with open(txt_file, "r") as file:
                text.append(file.read())
            metadatas.append(
                {
                    "source": txt_file,
                    "title": os.path.basename(txt_file),
                    "authors": authors,
                }
            )
        return text, metadatas

    def get_files_path_from_directory(self, source_dir: str, file_extension=None):
        files = []
        for root, _, filenames in os.walk(source_dir):
            for filename in filenames:
                if file_extension:
                    if filename.endswith(file_extension):
                        files.append(os.path.join(root, filename))
                else:
                    files.append(os.path.join(root, filename))
        return files

    def write_metadata_file(self, metadata: List[dict], output_path: str):
        metadata_file_content = "---\n"
        for metadata_item in metadata:
            metadata_file_content += f"{metadata_item}: {metadata[metadata_item]}\n"
        metadata_file_content += "---\n"
        with open(output_path, "w") as f:
            f.write(str(metadata_file_content))


def _get_pdf_title(pdf_reader, source):
    if not pdf_reader.metadata or not pdf_reader.metadata.title:
        source_name = os.path.basename(source)
        return source_name.replace(".pdf", "").replace("_", " ").title()
    else:
        return pdf_reader.metadata.title


def _get_pdf_authors(pdf_reader):
    if not pdf_reader.metadata or not pdf_reader.metadata.author:
        return []
    else:
        return [pdf_reader.metadata.author]
