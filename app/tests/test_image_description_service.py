# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from unittest.mock import MagicMock, patch
from PIL import Image
from io import BytesIO

from llms.image_description_service import ImageDescriptionService
from llms.model import Model


class TestImageDescriptionService:
    @staticmethod
    def get_test_image():
        # Create a simple image for testing
        image = Image.new("RGB", (100, 100), color="red")
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        buffered.seek(0)
        return Image.open(buffered)

    @patch("llms.image_description_service.AzureOpenAI")
    def test_describe_with_azure(
        self,
        mock_azure_openai,
    ):
        model = Model(
            provider="azure",
            id="some-image-model",
            name="Some image model",
            config={
                "azure_endpoint": "https://example.com",
                "api_key": "test_api_key",
                "azure_deployment": "test_deployment",
                "api_version": "v1",
            },
        )

        image_description_service = ImageDescriptionService(model=model)
        test_image = self.get_test_image()
        user_input = "Describe this image"

        mock_azure_openai_instance = mock_azure_openai.return_value

        mock_response = [
            MagicMock(choices=[MagicMock(delta=MagicMock(content="Test "))]),
            MagicMock(choices=[MagicMock(delta=MagicMock(content="description"))]),
        ]

        mock_azure_openai_instance.chat.completions.create.return_value = iter(
            mock_response
        )

        result = image_description_service._describe_image_with_azure(
            image=test_image, user_input=user_input
        )

        assert next(result) == "Test "
        assert next(result) == "description"
        mock_azure_openai_instance.chat.completions.create.assert_called_once()
        args, kwargs = mock_azure_openai_instance.chat.completions.create.call_args

        kwargs["model"] == "some-image-model"
        assert len(kwargs["messages"]) == 2
        print("Actual value:", kwargs["messages"][1]["content"][0]["text"])
        assert kwargs["messages"][1]["content"][0]["text"] == "Describe this image"

        assert image_description_service.model_client is not None
