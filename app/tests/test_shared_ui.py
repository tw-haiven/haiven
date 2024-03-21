# © 2024 Thoughtworks, Inc. | Thoughtworks Pre-Existing Intellectual Property | See License file for permissions.
from unittest import mock
from shared.models.model import Model
from shared.ui import _get_valid_tone_values, _get_default_temperature, _get_services


def test_get_valid_tone_values():
    expected_tone_values = [
        ("More creative (0.8)", 0.8),
        ("Balanced (0.5)", 0.5),
        ("More precise (0.2)", 0.2),
    ]
    actual_tone_values = _get_valid_tone_values()
    assert (
        actual_tone_values == expected_tone_values
    ), f"Expected tone values do not match. Expected: {expected_tone_values}, Got: {actual_tone_values}"


def test_get_default_tone():
    expected_default_tone = 0.2
    actual_default_tone = _get_default_temperature()
    assert (
        actual_default_tone == expected_default_tone
    ), f"Expected default tone does not match. Expected: {expected_default_tone}, Got: {actual_default_tone}"


@mock.patch("shared.ui.ModelsService.get_models")
@mock.patch("shared.ui.ConfigService.load_enabled_providers")
def test_get_services(load_enabled_providers, models_service_get_models_mock):
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

    load_enabled_providers.return_value = ["azure"]
    models_service_get_models_mock.return_value = models

    # when trying to get valid service values
    valid_service_values = _get_services([])
    # then the services defined in the config file should be returned
    assert valid_service_values == [
        (first_model_name, first_model_id),
        (second_model_name, second_model_id),
    ]
