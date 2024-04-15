# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import typer

from teamai_cli.app.app import App
from teamai_cli.services.client import Client
from teamai_cli.services.config_service import ConfigService
from teamai_cli.services.cli_config_service import CliConfigService
from teamai_cli.services.embedding_service import EmbeddingService
from teamai_cli.services.file_service import FileService
from teamai_cli.services.knowledge_service import KnowledgeService
from teamai_cli.services.page_helper import PageHelper
from teamai_cli.services.token_service import TokenService
from teamai_cli.services.web_page_service import WebPageService

CONFIG_FILE_PATH = "config.yaml"
ENCODING = "cl100k_base"

cli = typer.Typer(no_args_is_help=True)


@cli.command()
def index_file(
    source_path: str,
    embedding_model="openai",
    config_path: str = CONFIG_FILE_PATH,
    description: str = "",
    output_dir: str = "new_knowledge_base",
):
    """Index single pdf or text file to a given destination directory."""

    cli_config_service = CliConfigService()
    env_path_file = cli_config_service.get_env_path()
    target_config_path = cli_config_service.get_config_path()
    if not target_config_path:
        target_config_path = config_path

    config_service = ConfigService(env_file_path=env_path_file)
    embeddings = config_service.load_embeddings(target_config_path)
    provider = ""
    for embedding in embeddings:
        if embedding.id == embedding_model:
            provider = embedding.provider
            break

    metadata = _get_single_file_metadata(source_path, description, provider)
    app = create_app(config_service)
    app.index_individual_file(
        source_path, embedding_model, config_path, output_dir, metadata
    )


@cli.command()
def index_all_files(
    source_dir: str,
    output_dir="new_knowledge_base",
    embedding_model="openai",
    config_path: str = CONFIG_FILE_PATH,
):
    """Index all pdf or text files in a directory to a given destination directory."""
    cli_config_service = CliConfigService()
    env_path_file = cli_config_service.get_env_path()

    config_service = ConfigService(env_file_path=env_path_file)
    app = create_app(config_service)
    print("Indexing all files")
    app.index_all_files(source_dir, embedding_model, config_path, output_dir, {})


@cli.command()
def pickle_web_page(
    url: str,
    destination_path="web_page.pickle",
    html_filter="p",
):
    """Index a web page to a given destination path."""
    cli_config_service = CliConfigService()
    env_path_file = cli_config_service.get_env_path()

    config_service = ConfigService(env_file_path=env_path_file)
    app = create_app(config_service)
    app.index_web_page(
        url=url, html_filter=html_filter, destination_path=destination_path
    )


@cli.command()
def init(
    config_path: str = CONFIG_FILE_PATH,
    env_path: str = "",
):
    """Initialize the config file with the given config and env paths."""
    config_service = CliConfigService()
    config_service.initialize_config(config_path=config_path, env_path=env_path)
    print(f"Config file initialized at {config_service.cli_config_path}")


@cli.command()
def set_config_path(
    config_path: str,
):
    """Set the config path in the config file."""
    config_service = CliConfigService()
    config_service.set_config_path(config_path)
    print(f"Config path set to {config_path}")


@cli.command()
def set_env_path(
    env_path: str,
):
    """Set the env path in the config file."""
    config_service = CliConfigService()
    config_service.set_env_path(env_path)
    print(f"Env path set to {env_path}")


def create_app(config_service: ConfigService):
    token_service = TokenService(ENCODING)
    knowledge_service = KnowledgeService(token_service, EmbeddingService)
    file_service = FileService()
    client = Client()
    page_helper = PageHelper()
    web_page_service = WebPageService(client, page_helper)
    app = App(config_service, file_service, knowledge_service, web_page_service)
    return app


def _get_single_file_metadata(
    source_path: str, description: str, provider: str
) -> dict:
    title = f"{source_path.split('.')[0]}"
    return {
        "title": title,
        "description": description,
        "source": source_path,
        "path": f"{title}.kb",
        "provider": provider,
    }


if __name__ == "__main__":
    cli()
