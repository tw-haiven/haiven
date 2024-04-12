# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import os

CONFIG_PATH_KEY = "config_path"
ENV_PATH_KEY = "env_path"


class CliConfigService:
    def __init__(self, cli_config_path: str = "~/.teamai/config"):
        self.cli_config_path = cli_config_path

    def initialize_config(self, config_path: str = "", env_path: str = ""):
        with open(self.cli_config_path, "w") as f:
            f.write(f"{CONFIG_PATH_KEY}: {config_path}\n{ENV_PATH_KEY}: {env_path}")

    def get_config_path(self):
        return self._get_value_from_file(self.cli_config_path, CONFIG_PATH_KEY)

    def set_config_path(self, config_path: str):
        if os.path.exists(self.cli_config_path):
            new_content = ""
            with open(self.cli_config_path, "r") as f:
                content = f.read()
                lines = content.split("\n")
                for line in lines:
                    print(f"DEBUG a line {line}")
                    if line.startswith(CONFIG_PATH_KEY):
                        new_content += f"{CONFIG_PATH_KEY}: {config_path}\n"
                    else:
                        new_content += f"{line}\n"
            with open(self.cli_config_path, "w") as f:
                f.write(new_content)
        else:
            self.initialize_config(config_path)

    def get_env_path(self):
        return self._get_value_from_file(self.cli_config_path, ENV_PATH_KEY)

    def set_env_path(self, env_path: str):
        pass

    def _get_value_from_file(self, config_path: str, key: str):
        with open(config_path, "r") as f:
            content = f.read()
            lines = content.split("\n")
            for line in lines:
                if line.startswith(key):
                    value = line.split(": ")[1]
                    return value
        return None
