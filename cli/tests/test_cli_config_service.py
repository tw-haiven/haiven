# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
import os
import shutil
import unittest
from teamai_cli.services.cli_config_service import CliConfigService

TEST_CLI_CONFIG_DIR = "test-cli-config"


class TestCliConfigService(unittest.TestCase):
    def tearDown(self):
        if os.path.exists(TEST_CLI_CONFIG_DIR):
            shutil.rmtree(TEST_CLI_CONFIG_DIR)

    def test_initialize_config(self):
        cli_config_service = CliConfigService(TEST_CLI_CONFIG_DIR)
        config_path = "test-config"
        env_path = "test-env"
        cli_config_service.initialize_config(config_path, env_path)

        assert cli_config_service.cli_config_dir == TEST_CLI_CONFIG_DIR

        expected_cli_config_path = f"{TEST_CLI_CONFIG_DIR}/config"
        assert os.path.exists(TEST_CLI_CONFIG_DIR)

        file_content = None
        with open(expected_cli_config_path, "r") as file:
            file_content = file.read()

        assert file_content == f"config_path: {config_path}\nenv_path: {env_path}"
        assert cli_config_service.get_config_path() == config_path
        assert cli_config_service.get_env_path() == env_path

    def test_set_config_path_creates_cli_config_file_if_not_exists(self):
        cli_config_service = CliConfigService(TEST_CLI_CONFIG_DIR)

        new_config_path = "new-test-config"
        cli_config_service.set_config_path(new_config_path)

        expected_cli_config_path = f"{TEST_CLI_CONFIG_DIR}/config"
        assert os.path.exists(expected_cli_config_path)

        file_content = None
        with open(expected_cli_config_path, "r") as file:
            file_content = file.read()

        assert file_content == f"config_path: {new_config_path}\nenv_path: "
        assert cli_config_service.get_config_path() == new_config_path

    def test_set_config_path_update_config_path_value_if_cli_config_file_exists(self):
        cli_config_service = CliConfigService(TEST_CLI_CONFIG_DIR)

        config_path = "test-config"
        env_path = "test-env"
        cli_config_service.initialize_config(config_path, env_path)

        new_config_path = "new-test-config"
        cli_config_service.set_config_path(new_config_path)

        expected_cli_config_path = f"{TEST_CLI_CONFIG_DIR}/config"

        file_content = None
        with open(expected_cli_config_path, "r") as file:
            file_content = file.read()

        assert file_content == f"config_path: {new_config_path}\nenv_path: {env_path}\n"
        assert cli_config_service.get_config_path() == new_config_path

    def test_set_env_path_creates_cli_config_file_if_not_exists(self):
        cli_config_service = CliConfigService(TEST_CLI_CONFIG_DIR)

        new_env_path = "new-env"
        cli_config_service.set_env_path(new_env_path)

        expected_cli_config_path = f"{TEST_CLI_CONFIG_DIR}/config"
        assert os.path.exists(expected_cli_config_path)

        file_content = None
        with open(expected_cli_config_path, "r") as file:
            file_content = file.read()

        assert file_content == f"config_path: \nenv_path: {new_env_path}"
        assert cli_config_service.get_env_path() == new_env_path

    def test_set_env_path_update_env_path_value_if_cli_config_file_exists(self):
        cli_config_service = CliConfigService(TEST_CLI_CONFIG_DIR)

        config_path = "test-config"
        env_path = "test-env"
        cli_config_service.initialize_config(config_path, env_path)

        new_env_path = "new-test-config"
        cli_config_service.set_env_path(new_env_path)

        expected_cli_config_path = f"{TEST_CLI_CONFIG_DIR}/config"
        file_content = None
        with open(expected_cli_config_path, "r") as file:
            file_content = file.read()

        assert file_content == f"config_path: {config_path}\nenv_path: {new_env_path}\n"
        assert cli_config_service.get_env_path() == new_env_path
