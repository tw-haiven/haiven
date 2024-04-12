# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import os
import unittest
from teamai_cli.services.cli_config_service import CliConfigService

TEST_CLI_CONFIG_PATH = "test-cli-config"


class TestCliConfigService(unittest.TestCase):
    def tearDown(self):
        if os.path.exists(TEST_CLI_CONFIG_PATH):
            os.remove(TEST_CLI_CONFIG_PATH)

    def test_initialize_config(self):
        cli_config_service = CliConfigService(TEST_CLI_CONFIG_PATH)

        config_path = "test-config"
        env_path = "test-env"
        cli_config_service.initialize_config(config_path, env_path)

        assert os.path.exists(TEST_CLI_CONFIG_PATH)

        file_content = None
        with open(TEST_CLI_CONFIG_PATH, "r") as file:
            file_content = file.read()

        assert file_content == f"config_path: {config_path}\nenv_path: {env_path}"
        assert cli_config_service.get_config_path() == config_path
        assert cli_config_service.get_env_path() == env_path

    def test_set_config_path_creates_cli_config_file_if_not_exists(self):
        cli_config_service = CliConfigService(TEST_CLI_CONFIG_PATH)

        new_config_path = "new-test-config"
        cli_config_service.set_config_path(new_config_path)

        assert os.path.exists(TEST_CLI_CONFIG_PATH)

        file_content = None
        with open(TEST_CLI_CONFIG_PATH, "r") as file:
            file_content = file.read()

        assert file_content == f"config_path: {new_config_path}\nenv_path: "
        assert cli_config_service.get_config_path() == new_config_path

    def test_set_config_path_update_config_path_value_if_cli_config_file_exists(self):
        cli_config_service = CliConfigService(TEST_CLI_CONFIG_PATH)

        config_path = "test-config"
        env_path = "test-env"
        cli_config_service.initialize_config(config_path, env_path)

        new_config_path = "new-test-config"
        cli_config_service.set_config_path(new_config_path)

        file_content = None
        with open(TEST_CLI_CONFIG_PATH, "r") as file:
            file_content = file.read()

        assert file_content == f"config_path: {new_config_path}\nenv_path: {env_path}\n"
        assert cli_config_service.get_config_path() == new_config_path

    def test_set_env_path_creates_cli_config_file_if_not_exists(self):
        cli_config_service = CliConfigService(TEST_CLI_CONFIG_PATH)

        new_env_path = "new-env"
        cli_config_service.set_env_path(new_env_path)

        assert os.path.exists(TEST_CLI_CONFIG_PATH)

        file_content = None
        with open(TEST_CLI_CONFIG_PATH, "r") as file:
            file_content = file.read()

        assert file_content == f"config_path: \nenv_path: {new_env_path}"
        assert cli_config_service.get_env_path() == new_env_path

    def test_set_env_path_update_env_path_value_if_cli_config_file_exists(self):
        cli_config_service = CliConfigService(TEST_CLI_CONFIG_PATH)

        config_path = "test-config"
        env_path = "test-env"
        cli_config_service.initialize_config(config_path, env_path)

        new_env_path = "new-test-config"
        cli_config_service.set_env_path(new_env_path)

        file_content = None
        with open(TEST_CLI_CONFIG_PATH, "r") as file:
            file_content = file.read()

        assert file_content == f"config_path: {config_path}\nenv_path: {new_env_path}\n"
        assert cli_config_service.get_env_path() == new_env_path
