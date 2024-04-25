# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import typer

from teamai_cli.app.app import App
from teamai_cli.services.config_service import ConfigService
from teamai_cli.services.cli_config_service import CliConfigService
from teamai_cli.services.embedding_service import EmbeddingService
from teamai_cli.services.file_service import FileService
from teamai_cli.services.knowledge_service import KnowledgeService
from teamai_cli.services.token_service import TokenService
from teamai_cli.services.metadata_service import MetadataService

ENCODING = "cl100k_base"

cli = typer.Typer(no_args_is_help=True)


@cli.command(no_args_is_help=True)
def index_file(
    source_path: str,
    embedding_model="openai",
    config_path: str = "",
    description: str = "",
    output_dir: str = "new_knowledge_base",
):
    """Index single file to a given destination directory."""

    cli_config_service = CliConfigService()
    if cli_config_service.get_config_path() and config_path == "":
        config_path = cli_config_service.get_config_path()

    env_path_file = cli_config_service.get_env_path()

    config_service = ConfigService(env_file_path=env_path_file)

    app = create_app(config_service)
    app.index_individual_file(
        source_path, embedding_model, config_path, output_dir, description
    )


@cli.command(no_args_is_help=True)
def index_all_files(
    source_dir: str,
    output_dir="new_knowledge_base",
    embedding_model="openai",
    description: str = "",
    config_path: str = "",
):
    """Index all files in a directory to a given destination directory."""
    cli_config_service = CliConfigService()
    if cli_config_service.get_config_path() and config_path == "":
        config_path = cli_config_service.get_config_path()

    env_path_file = cli_config_service.get_env_path()

    config_service = ConfigService(env_file_path=env_path_file)
    app = create_app(config_service)
    print("Indexing all files")
    app.index_all_files(
        source_dir, embedding_model, config_path, output_dir, description
    )


@cli.command(no_args_is_help=True)
def create_context(
    context_name: str = "",
    kp_root: str = "",
):
    """Create a context package base structure."""
    file_service = FileService()
    file_service.create_context_structure(context_name, kp_root)
    file_service.write_architecture_file(
        f"{kp_root}/contexts/{context_name}/architecture.md"
    )
    file_service.write_business_context_file(
        f"{kp_root}/contexts/{context_name}/business_context.md"
    )


@cli.command(no_args_is_help=True)
def init(
    config_path: str = "",
    env_path: str = "",
):
    """Initialize the config file with the given config and env paths."""
    config_service = CliConfigService()
    config_service.initialize_config(config_path=config_path, env_path=env_path)
    print(f"Config file initialized at {config_service.cli_config_path}")


@cli.command(no_args_is_help=True)
def set_config_path(
    config_path: str = "",
):
    """Set the config path in the config file."""
    config_service = CliConfigService()
    config_service.set_config_path(config_path)
    print(f"Config path set to {config_path}")


@cli.command(no_args_is_help=True)
def set_env_path(
    env_path: str = "",
):
    """Set the env path in the config file."""
    config_service = CliConfigService()
    config_service.set_env_path(env_path)
    print(f"Env path set to {env_path}")


def create_app(config_service: ConfigService):
    token_service = TokenService(ENCODING)
    knowledge_service = KnowledgeService(token_service, EmbeddingService)
    app = App(
        config_service,
        FileService(),
        knowledge_service,
        MetadataService,
    )
    return app


if __name__ == "__main__":
    cli()
