from haiven_cli.models.page_data import PageData
from haiven_cli.models.html_filter import HtmlFilter
from langchain_core.documents import Document


class PageHelper:
    def get_article(self, page_data: PageData, html_filter: HtmlFilter) -> Document:
        page_content = self.find_text(page_data, html_filter)
        metadata = {
            "title": self.find_title(page_data),
            "url": page_data.url,
        }
        return Document(page_content=page_content, metadata=metadata)

    def find_title(self, page_data: PageData) -> str:
        title = ""
        title_header = page_data.content.find("h1")
        if title_header is not None:
            title = title_header.get_text(strip=True)

        return title

    def find_text(self, page_data: PageData, html_filter: HtmlFilter) -> str:
        main_content = page_data.content.find_all(html_filter.type)
        return " ".join([section.get_text() for section in main_content])
