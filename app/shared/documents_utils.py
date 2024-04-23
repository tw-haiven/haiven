# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from pypdf import PdfReader


def get_text_and_metadata_from_pdf(pdf_file):
    if pdf_file:
        text = []
        metadatas = []
        pdf_reader = PdfReader(pdf_file)
        page_number = 1
        for page in pdf_reader.pages:
            text.append(page.extract_text())
            metadatas.append(
                {
                    "page": page_number,
                    "source": pdf_file.name,
                    "title": pdf_reader.metadata.title,
                    "author": pdf_reader.metadata.author,
                }
            )
            page_number += 1
    return text, metadatas
