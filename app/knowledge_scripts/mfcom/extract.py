# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import pickle
from typing import List

from bs4 import BeautifulSoup
import yaml
import requests

from langchain_core.documents import Document

BLIKI_TAGS_BLACKLIST = [
    "agile",
    "conferences",
    "certification",
    "diversions",
    "thoughtworks",
    "agile adoption",
    "lean",
    "dictionary",
    "team environment",
    "projects",
    "computer history",
    "team organization",
    "collaboration",
    "recruiting",
    "retrospective",
    "academia",
    "microsoft",
    "language workbench",
    "travel",
    "gadgets",
    "diversity",
    "tools",
    "parser generators",
    "writing",
    "website",
    "presentations",
    "domestic",
    "photography",
    "internet culture",
    "legal",
    "infodecks",
    "attic",
    "ruby",
]

BLIKI_TECHNICAL_TAGS = [
    "continuous delivery",
    "build scripting",
    "testing",
    "test categories",
    "bad things",
    "technical debt",
    "application integration",
    "database",
    "noSQL",
    "version control",
    "evolutionary design",
    "technical leadership",
    "encapsulation",
    "language feature",
    "programming platforms",
    "domain driven design",
    "application architecture",
    "legacy rehab",
    "API design",
    "clean code",
    "object collaboration design",
    "web development",
    "domain specific language",
    "analysis patterns",
    "mobile",
    "big data",
    "expositional architectures",
    "refactoring",
    "refactoring boundary",
    "uml",
    "software craftsmanship",
    "microservices",
    "privacy",
    "event architectures",
    "front-end",
]


BLIKI_GENERAL_AGILE_TAGS = [
    "productivity",
    "metrics",
    "documentation",
    "extreme programming",
    "requirements analysis",
    "process theory",
    "project planning",
    "scrum",
    "estimation",
]


def mf_page_parser(content: BeautifulSoup) -> str:
    main_content = content.find_all("div", {"class": ["paperBody"]})
    main_content_text = " ".join([section.get_text() for section in main_content])
    try:
        return main_content_text
    except Exception as e:
        print(f"parser error: {e}")
        return ""


def find_title(content: BeautifulSoup) -> str:
    title = content.find("h1")
    if title is not None:
        return title.get_text(strip=True)


def find_tags_in_article(content: BeautifulSoup) -> List[str]:
    tag_section = content.find("div", {"class": ["tags"]})
    tag_links = tag_section.find_all("a")

    return [link.get_text() for link in tag_links]


def find_authors_in_article(content: BeautifulSoup) -> List[str]:
    try:
        authors = content.find_all("a", {"rel": "author"})
        return [link.get_text() for link in authors]
    except Exception as e:
        print(f"Error extracting authors, defaulting to Martin - {e}")
        return ["Martin Fowler"]


def load_urls(urls, blacklist_tags=None):
    articles = []

    for i in range(len(urls)):
        url = urls[i]
        # if i <= 5:
        if url.endswith("html"):
            print(f"{i} - Retrieving content from {url}")
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    content = response.text

                    soup = BeautifulSoup(content, "html.parser")

                    article_content = mf_page_parser(soup)
                    article_tags = find_tags_in_article(soup)
                    article_authors = find_authors_in_article(soup)

                    print(f"\tauthors: {article_authors} | tags: {article_tags}")

                    if blacklist_tags and all(
                        filter_tag in blacklist_tags for filter_tag in article_tags
                    ):
                        print(
                            f"\tNot loading, all tags {article_tags} are on the blacklist"
                        )
                    else:
                        metadata = {
                            "title": find_title(soup),
                            "source": url,
                            "authors": article_authors,
                            "tags": article_tags,
                        }
                        articles.append(
                            Document(page_content=article_content, metadata=metadata)
                        )
                else:
                    print(
                        f"\tFailed to retrieve content from {url}, {response.status_code}"
                    )
            except Exception as error:
                print(f"\tFailed to parse content from {url}: {error}")

        else:
            print(f"\tSkipping {url}, not an HTML page")

    return articles


def load_entries_from_bliki_tags_yaml(yaml_docs, tags):
    bliki_paths = []

    for doc in yaml_docs:
        if doc.get("name") in tags:
            bliki_paths.extend(doc.get("entries"))

    unique_bliki_identifiers = list(set(bliki_paths))
    urls = [
        f"https://martinfowler.com/bliki/{path}.html"
        for path in unique_bliki_identifiers
    ]

    return load_urls(urls)


def load_entries_from_articles_page(blacklist_tags=None):
    article_paths = []

    url = "https://martinfowler.com/tags"
    response = requests.get(url)
    if response.status_code == 200:
        content = response.text
        soup = BeautifulSoup(content, "html.parser")
        title_list = soup.find("div", {"class": ["title-list"]})
        all_links = title_list.find_all("a")
        for link in all_links:
            href = link.get("href")
            if href is not None and "article" in href:
                article_paths.append(f"https://martinfowler.com{href}")

    return load_urls(article_paths, blacklist_tags)


def extract_category(category, tags):
    file_path = "./knowledge_scripts/mfcom/data/tags_all.yaml"
    with open(file_path, "r") as file:
        docs = yaml.safe_load_all(file)
        articles = load_entries_from_bliki_tags_yaml(docs, tags)

    with open(f"knowledge_scripts/mfcom/mfcom_bliki_docs-{category}.pickle", "wb") as f:
        pickle.dump(articles, f)

    return articles


def extract_bliki():
    technical_articles = extract_category("technical", BLIKI_TECHNICAL_TAGS)
    agile_articles = extract_category("agile", BLIKI_GENERAL_AGILE_TAGS)
    all_articles = []
    all_articles.extend(technical_articles)
    all_articles.extend(agile_articles)
    return all_articles


def extract_articles():
    return load_entries_from_articles_page(BLIKI_TAGS_BLACKLIST)


def extract():
    all_articles = load_entries_from_articles_page(BLIKI_TAGS_BLACKLIST)
    all_articles.extend(extract_bliki())
    with open("knowledge_scripts/mfcom/mfcom-all.pickle", "wb") as f:
        pickle.dump(all_articles, f)


if __name__ == "__main__":
    extract()
