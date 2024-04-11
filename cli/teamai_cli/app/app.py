# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from teamai_cli.models.embedding_model import EmbeddingModel
from teamai_cli.services.config_service import ConfigService
from teamai_cli.services.file_service import FileService
from teamai_cli.models.html_filter import HtmlFilter
from teamai_cli.services.knowledge_service import KnowledgeService
from teamai_cli.services.web_page_service import WebPageService
from typing import List


class App:
    def __init__(
        self,
        config_service: ConfigService,
        file_service: FileService,
        knowledge_service: KnowledgeService,
        web_page_service: WebPageService,
    ):
        self.config_service = config_service
        self.file_service = file_service
        self.knowledge_service = knowledge_service
        self.web_page_service = web_page_service

    def index_individual_file(
        self, source_path: str, embedding_model: str, config_path: str
    ):
        if not source_path:
            raise ValueError("please provide file path for source_path option")

        if not (source_path.endswith(".txt") or source_path.endswith(".pdf")):
            raise ValueError("source file needs to be .txt or .pdf file")

        embedding_models = self.config_service.load_embeddings(config_path)
        model = self._get_embedding(embedding_model, embedding_models)
        if model is None:
            current_models = self._get_defined_embedding_models_ids(embedding_models)
            raise ValueError(
                f"embeddings are not defined in {config_path}\n{current_models}"
            )

        file_content = None
        metadata = None
        if source_path.endswith(".txt"):
            file_content, metadata = self._get_txt_file_text_and_metadata(source_path)
        else:
            file_content, metadata = self._get_pdf_file_text_and_metadata(source_path)

        self.knowledge_service.index(file_content, metadata, model)

    def index_all_files(self, source_dir: str, embedding_model: str, config_path: str):
        if not source_dir:
            raise ValueError("please provide directory path for source_dir option")

        embedding_models = self.config_service.load_embeddings(config_path)
        model = self._get_embedding(embedding_model, embedding_models)
        if model is None:
            current_models = self._get_defined_embedding_models_ids(embedding_models)
            raise ValueError(
                f"embeddings are not defined in {config_path}\n{current_models}"
            )

        files = self.file_service.get_files_path_from_directory(source_dir)
        for file in files:
            file_content = None
            metadata = None
            if file.endswith(".txt"):
                file_content, metadata = self._get_txt_file_text_and_metadata(file)
            else:
                file_content, metadata = self._get_pdf_file_text_and_metadata(file)

            self.knowledge_service.index(file_content, metadata, model)

    def index_web_page(self, url: str, html_filter: str, destination_path: str):
        if not url:
            raise ValueError("please provide url for url option")

        web_page_article = self.web_page_service.get_single_page(
            url, HtmlFilter(html_filter)
        )
        self.knowledge_service.pickle_documents(web_page_article, destination_path)

    def _get_txt_file_text_and_metadata(self, source_path: str):
        with open(source_path, "r") as file:
            return [file.read()], [{"file": source_path}]

    def _get_pdf_file_text_and_metadata(self, source_path: str):
        with open(source_path, "rb") as pdf_file:
            return self.file_service.get_text_and_metadata_from_pdf(pdf_file)

    def _get_embedding(
        self, embedding_model: str, embedding_models: List[EmbeddingModel]
    ) -> EmbeddingModel:
        for model in embedding_models:
            if embedding_model == model.id:
                return model
        return None

    def _get_defined_embedding_models_ids(
        self, embedding_models: List[EmbeddingModel]
    ) -> str:
        models_ids = "Usable models according to config file:"
        for model in embedding_models:
            models_ids = f"{models_ids}\n- {model.id}"
        return models_ids
