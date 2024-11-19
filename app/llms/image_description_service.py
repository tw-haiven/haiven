# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import base64
from io import BytesIO
from PIL import Image
from litellm import completion

from llms.model_config import ModelConfig

DEFAULT_PROMPT = "I am a member of a software development team. This image is part of our documentation, please describe the image to me."


class ImageDescriptionService:
    """
    Provides a unified interface for generating descriptions of images using AI services from various cloud providers.

    Attributes:
        model (Model): Configuration of the model to be used for generating image descriptions. This includes the provider and necessary credentials and endpoints.

    Methods:
        prompt_with_image(image: Image, prompt: str) -> str:
            A method that serves as the entry point for clients to get descriptions of images. It uses the litellm library to call models and get descriptions of images.

        _get_image_bytes(image: Image) -> bytes:
            Helper method to convert an image to its byte representation.

        _encode_image_base64(image: Image) -> str:
            Helper method to encode an image to a base64 string, facilitating its transmission over networks.

        _messages_for_lite_api(image: Image.Image, user_input: str) -> list:
            Helper method to create the message payload for the litellm API.
    """

    def __init__(self, model: ModelConfig):
        """
        Initializes the ImageDescriptionService with a specific model configuration.

        Args:
            model_id (str): The identifier of the model configuration to use for image descriptions. If `None` or an empty string, the default model will be used.

        Raises:
            ValueError: If `model_id` is None or an empty string.
        """

        self.model_definition = model
        self.model_client = None  # will be instantiated based on the provider

    def prompt_with_image(self, image: Image, user_input: str):
        if image is None:
            return ""

        if user_input == "":
            user_input = DEFAULT_PROMPT

        try:
            response = completion(
                model=self.model_definition.lite_id,
                messages=self._messages_for_lite_api(image, user_input),
                max_tokens=2000,
                stream=True,
            )

            for chunk in response:
                if len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield delta.content

        except Exception as error:
            if not str(error).strip():
                error = "Error while the model was processing the input"
            yield f"[ERROR]: {str(error)}"

    def _get_image_bytes(self, image):
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return buffered.getvalue()

    def _encode_image_base64(self, image: Image):
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def _messages_for_lite_api(self, image: Image.Image, user_input: str):
        return [
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_input,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "data:image/png;base64,"
                            + self._encode_image_base64(image)
                        },
                    },
                ],
            },
        ]
