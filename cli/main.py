# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import typer

from app.app import App
from services.config_service import ConfigService
from services.file_service import FileService
from services.knowledge_service import KnowledgeService
from services.token_service import TokenService

CONFIG_FILE_PATH = "../app/config.yaml"
ENCODING = "cl100k_base"

cli = typer.Typer()


@cli.command()
def index_file(
    source_path: str = "",
    destination_dir="new_knowledge_base.kb",
    embedding_model="openai",
    config_path: str = CONFIG_FILE_PATH,
):
    tiktoken_service = TokenService(ENCODING)
    knowledge_service = KnowledgeService(destination_dir, tiktoken_service)
    config_service = ConfigService()
    file_service = FileService()
    app = App(config_service, file_service, knowledge_service)
    app.index_individual_file(source_path, embedding_model, config_path)


@cli.command()
def index_all_files(
    source_dir: str = "",
    destination_dir="new_knowledge_base.kb",
    embedding_model="openai",
    config_path: str = CONFIG_FILE_PATH,
):
    token_service = TokenService(ENCODING)
    knowledge_service = KnowledgeService(destination_dir, token_service)
    config_service = ConfigService()
    file_service = FileService()
    app = App(config_service, file_service, knowledge_service)
    app.index_all_files(source_dir, embedding_model, config_path)


if __name__ == "__main__":
    cli()
