# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.

from models.page_data import PageData
from models.html_filter import HtmlFilter
from langchain_core.documents import Document


class PageHelper:
    def get_article(self, page_data: PageData) -> Document:
        pass

    def find_title(self, page_data: PageData) -> str:
        title = ""
        title_header = page_data.content.find("h1")
        if title_header is not None:
            title = title_header.get_text(strip=True)

        return title

    def find_text(self, page_data: PageData, html_filter: HtmlFilter) -> str:
        main_content = page_data.content.find_all(html_filter)
        return " ".join([section.get_text() for section in main_content])
