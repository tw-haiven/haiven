# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from unittest import mock
from llms.model import Model
from ui.ui import UIBaseComponents


@mock.patch("config_service.ConfigService")
def test_get_services(mock_config_service):
    # given an LLMConfig object initialised with a config file containing azure services
    first_model_id = "azure-gpt35"
    first_model_provider = "azure"
    first_model_name = "GPT-3.5 on Azure"
    first_model = Model(first_model_id, first_model_provider, first_model_name, [], {})

    second_model_id = "azure-gpt4"
    second_model_provider = "azure"
    second_model_name = "GPT-4 on AWS"
    second_model = Model(
        second_model_id, second_model_provider, second_model_name, [], {}
    )

    models = [first_model, second_model]

    mock_config_service.load_enabled_models.return_value = models

    ui = UIBaseComponents(mock_config_service)

    # when trying to get valid service values
    valid_service_values = ui._get_model_service_choices([])
    # then the services defined in the config file should be returned
    assert valid_service_values == [
        (first_model_name, first_model_id),
        (second_model_name, second_model_id),
    ]
