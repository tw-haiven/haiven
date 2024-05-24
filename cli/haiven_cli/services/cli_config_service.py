import os
from pathlib import Path

DEFAULT_CLI_CONFIG_DIR = f"{Path.home()}/.teamai"
CONFIG_PATH_KEY = "config_path"
ENV_PATH_KEY = "env_path"


class CliConfigService:
    def __init__(self, cli_config_dir: str = DEFAULT_CLI_CONFIG_DIR):
        self.cli_config_dir = cli_config_dir
        self.cli_config_path = f"{cli_config_dir}/config"

    def initialize_config(self, config_path: str = "", env_path: str = ""):
        if not os.path.isabs(config_path) and config_path != "":
            config_path = os.path.abspath(config_path)

        if not os.path.isabs(env_path) and env_path != "":
            env_path = os.path.abspath(env_path)

        if not os.path.exists(os.path.expanduser(self.cli_config_dir)):
            os.makedirs(os.path.expanduser(self.cli_config_dir), exist_ok=True)
            file_path = os.path.expanduser(self.cli_config_path)
            with open(file_path, "w") as f:
                f.write(f"{CONFIG_PATH_KEY}: {config_path}\n{ENV_PATH_KEY}: {env_path}")
        else:
            if config_path:
                self.set_config_path(config_path)
            if env_path:
                self.set_env_path(env_path)

    def get_config_path(self):
        cli_config_path = os.path.expanduser(self.cli_config_path)
        return _get_value_from_file(cli_config_path, CONFIG_PATH_KEY)

    def set_config_path(self, config_path: str):
        config_path = os.path.abspath(config_path)
        print(config_path)
        if os.path.exists(self.cli_config_path):
            _update_value_in_file(self.cli_config_path, CONFIG_PATH_KEY, config_path)
        else:
            self.initialize_config(config_path=config_path)

    def get_env_path(self):
        return _get_value_from_file(self.cli_config_path, ENV_PATH_KEY)

    def set_env_path(self, env_path: str):
        config_path = os.path.abspath(self.cli_config_path)
        if os.path.exists(config_path):
            _update_value_in_file(config_path, ENV_PATH_KEY, env_path)
        else:
            self.initialize_config(env_path=env_path)


def _update_value_in_file(config_path: str, key: str, value: str):
    new_content = ""
    with open(config_path, "r") as f:
        content = f.read()
        lines = content.split("\n")
        for line in lines:
            if line.startswith(key):
                new_content += f"{key}: {value}\n"
            else:
                new_content += f"{line}\n"
    with open(config_path, "w") as f:
        f.write(new_content)


def _get_value_from_file(config_path: str, key: str):
    with open(config_path, "r") as f:
        content = f.read()
        lines = content.split("\n")
        for line in lines:
            if line.startswith(key):
                value = line.split(": ")[1]
                return value
    return None
