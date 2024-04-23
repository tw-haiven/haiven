# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import os
from teamai_cli.models.embedding_model import EmbeddingModel
from teamai_cli.services.config_service import ConfigService
from teamai_cli.services.file_service import FileService
from teamai_cli.services.knowledge_service import KnowledgeService
from teamai_cli.services.metadata_service import MetadataService
from typing import List


class App:
    def __init__(
        self,
        config_service: ConfigService,
        file_service: FileService,
        knowledge_service: KnowledgeService,
        metadata_service: MetadataService,
    ):
        self.config_service = config_service
        self.file_service = file_service
        self.knowledge_service = knowledge_service
        self.metadata_service = metadata_service

    def index_individual_file(
        self,
        source_path: str,
        embedding_model: str,
        config_path: str,
        output_dir: str,
        description: str,
    ):
        if not source_path:
            raise ValueError("please provide file path for source_path option")

        if not (source_path.endswith(".pdf") or source_path.endswith(".csv")):
            raise ValueError("source file needs to be .pdf or .csv file")

        embedding_models = self.config_service.load_embeddings(config_path)
        model = _get_embedding(embedding_model, embedding_models)
        if model is None:
            current_models = _get_defined_embedding_models_ids(embedding_models)
            raise ValueError(
                f"embeddings are not defined in {config_path}\n{current_models}"
            )

        file_content = None
        file_metadata = None
        if source_path.endswith(".csv"):
            file_content, file_metadata = self._get_csv_file_text_and_metadata(
                source_path
            )
        elif source_path.endswith(".pdf"):
            file_content, file_metadata = self._get_pdf_file_text_and_metadata(
                source_path
            )
        else:
            raise ValueError("source file needs to be .pdf or .csv file")

        file_path_prefix = _format_file_name(source_path)
        output_kb_dir = f"{output_dir}/{file_path_prefix}.kb"
        self.knowledge_service.index(file_content, file_metadata, model, output_kb_dir)
        metadata = self.metadata_service.create_metadata(
            source_path, description, model.provider, output_dir
        )
        self.file_service.write_metadata_file(
            metadata, f"{output_dir}/{file_path_prefix}.md"
        )

    def index_all_files(
        self,
        source_dir: str,
        embedding_model: str,
        config_path: str,
        output_dir: str,
        description: str,
    ):
        if not source_dir:
            raise ValueError("please provide directory path for source_dir option")

        embedding_models = self.config_service.load_embeddings(config_path)
        model = _get_embedding(embedding_model, embedding_models)
        if model is None:
            current_models = _get_defined_embedding_models_ids(embedding_models)
            raise ValueError(
                f"embeddings are not defined in {config_path}\n{current_models}"
            )

        files = self.file_service.get_files_path_from_directory(source_dir)

        for file in files:
            print(f"creating knowledge for {file} in {output_dir}")
            file_content = None
            first_metadata = None
            if file.endswith(".csv"):
                file_content, first_metadata = self._get_csv_file_text_and_metadata(
                    file
                )
            elif file.endswith(".pdf"):
                file_content, first_metadata = self._get_pdf_file_text_and_metadata(
                    file
                )
            else:
                raise ValueError("source file needs to be .pdf or .csv file")

            output_kb_dir = f"{output_dir}/{_format_file_name(file)}.kb"
            self.knowledge_service.index(
                file_content, first_metadata, model, output_kb_dir
            )
            metadata = self.metadata_service.create_metadata(
                file, description, model.provider, output_dir
            )
            self.file_service.write_metadata_file(
                metadata, f"{output_dir}/{_format_file_name(file)}.md"
            )

    def create_domain_structure(self, domain_name: str, parent_dir: str = "./"):
        if not domain_name:
            raise ValueError("please provide domain name for domain_name option")

        if not os.path.exists(parent_dir):
            raise ValueError(f"parent directory {parent_dir} does not exist")

        self.file_service.create_domain_structure(domain_name, parent_dir)
        self.file_service.write_architecture_file(
            f"{parent_dir}/{domain_name}/architecture.md"
        )
        self.file_service.write_business_context_file(
            f"{parent_dir}/{domain_name}/business-context.md"
        )

    def _get_csv_file_text_and_metadata(self, source_path: str):
        return self.file_service.get_text_and_metadata_from_csv(source_path)

    def _get_pdf_file_text_and_metadata(self, source_path: str):
        with open(source_path, "rb") as pdf_file:
            return self.file_service.get_text_and_metadata_from_pdf(pdf_file)


def _get_embedding(
    embedding_model: str, embedding_models: List[EmbeddingModel]
) -> EmbeddingModel:
    for model in embedding_models:
        if embedding_model == model.id:
            return model
    return None


def _get_defined_embedding_models_ids(embedding_models: List[EmbeddingModel]) -> str:
    models_ids = "Usable models according to config file:"
    for model in embedding_models:
        models_ids = f"{models_ids}\n- {model.id}"
    return models_ids


def _format_file_name(file_path: str) -> str:
    split_file = file_path.split(".")
    file_prefix = split_file[-2]
    formatted_file = os.path.basename(os.path.normpath(file_prefix))
    return formatted_file
