# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import base64
import json
from io import BytesIO

import boto3
from botocore.exceptions import ClientError
from openai import AzureOpenAI, OpenAI
from PIL import Image
from llms.model import Model
from vertexai.preview.generative_models import GenerativeModel, Part
import ollama

DEFAULT_PROMPT = "I am a member of a software development team. This image is part of our documentation, please describe the image to me."


class ImageDescriptionService:
    """
    Provides a unified interface for generating descriptions of images using AI services from various cloud providers.


    Attributes:
        model (Model): Configuration of the model to be used for generating image descriptions. This includes the provider (GCP, Azure, AWS Anthropic) and necessary credentials and endpoints.

    Methods:
        prompt_with_image(image_from_gradio: Image, prompt: str) -> str:
            A static method that serves as the entry point for clients to get descriptions of images. It delegates the actual processing to an instance method.

        _prompt_with_image(image_from_gradio: Image, user_input: str) -> str:
            Determines the appropriate cloud provider based on the `model_definition` and forwards the request to the corresponding method for processing.

        _describe_with_gcp(image: Image.Image, user_input: str) -> str:
            Generates a description of the given image using Google Cloud Platform's AI service.

        _describe_image_with_azure(image: Image.Image, user_input: str) -> str:
            Generates a description of the given image using Azure's AI service.

        _describe_image_with_aws_anthropic(image: Image.Image, user_input: str) -> str:
            Generates a description of the given image using AWS Anthropic's AI service.

        _get_image_bytes(image: Image) -> bytes:
            Helper method to convert an image to its byte representation.

        _encode_image_base64(image: Image) -> str:
            Helper method to encode an image to a base64 string, facilitating its transmission over networks.
    """

    def __init__(self, model: Model):
        """
        Initializes the ImageDescriptionService with a specific model configuration.

        Args:
            model_id (str): The identifier of the model configuration to use for image descriptions. If `None` or an empty string, the default model will be used.

        Raises:
            ValueError: If `model_id` is None or an empty string.
        """

        self.model_definition = model
        self.model_client = None  # will be instantiated based on the provider

    def prompt_with_image(self, image_from_gradio: Image, user_input: str) -> str:
        if image_from_gradio is None:
            return ""

        if user_input == "":
            user_input = DEFAULT_PROMPT

        match self.model_definition.provider.lower():
            case "gcp":
                return self._describe_with_gcp(image_from_gradio, user_input)
            case "azure":
                return self._describe_image_with_azure(image_from_gradio, user_input)
            case "aws":
                return self._describe_image_with_aws_anthropic(
                    image_from_gradio, user_input
                )
            case "ollama":
                return self._describe_image_with_ollama(image_from_gradio, user_input)
            case "openai":
                return self._describe_image_with_openai(image_from_gradio, user_input)
            case _:
                return "Provider not supported"

    def _describe_with_gcp(self, image: Image.Image, user_input: str) -> str:
        if self.model_client is None:
            self.model_client = GenerativeModel(
                self.model_definition.config.get("model")
            )

        image = Part.from_data(self._get_image_bytes(image), mime_type="image/png")

        model_response = self.model_client.generate_content(
            [
                user_input,
                image,
            ]
        )
        return model_response.text

    def _describe_image_with_openai(self, image: Image.Image, user_input: str) -> str:
        if self.model_client is None:
            api_key = self.model_definition.config.get("api_key")
            if not api_key.strip():
                return "Error: Missing Open AI Vision configuration. Please check your environment variables."
            self.model_client = OpenAI(api_key=api_key)

        response = self.model_client.chat.completions.create(
            model=self.model_definition.config.get("model_name"),
            messages=[
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
            ],
            max_tokens=2000,
        )

        return response.choices[0].message.content

    def _describe_image_with_azure(self, image: Image.Image, user_input: str) -> str:
        if self.model_client is None:
            azure_endpoint = self.model_definition.config.get("azure_endpoint")
            api_key = self.model_definition.config.get("api_key")
            azure_deployment = self.model_definition.config.get("azure_deployment")
            api_version = self.model_definition.config.get("api_version")

            if not all(
                [
                    azure_endpoint.strip(),
                    api_key.strip(),
                    azure_deployment.strip(),
                    api_version.strip(),
                ]
            ):
                return "Error: Missing Azure AI Vision configuration. Please check your environment variables."

            self.model_client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                base_url=f"{azure_endpoint}/openai/deployments/{azure_deployment}",
            )

        response = self.model_client.chat.completions.create(
            model=self.model_definition.config.get("azure_deployment"),
            messages=[
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
            ],
            max_tokens=2000,
        )

        return response.choices[0].message.content

    def _describe_image_with_aws_anthropic(
        self, image: Image.Image, user_input: str
    ) -> str:
        try:
            if self.model_client is None:
                self.model_client = boto3.client(
                    service_name="bedrock-runtime",
                    region_name=self.model_definition.config.get("region_name"),
                )

            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": self._encode_image_base64(image),
                            },
                        }
                    ],
                }
            ]

            if len(user_input) > 0:
                messages[0]["content"].append(
                    {
                        "type": "text",
                        "text": user_input,
                    }
                )

            body = json.dumps(
                {
                    "anthropic_version": self.model_definition.config.get(
                        "anthropic_version"
                    ),
                    "max_tokens": 5000,
                    "messages": messages,
                }
            )

            response = self.model_client.invoke_model(
                body=body, modelId=self.model_definition.config.get("model_id")
            )
            response = json.loads(response.get("body").read())
            return response["content"][0]["text"]

        except ClientError as err:
            message = err.response["Error"]["Message"]
            print("A client error occured: " + format(message))
            return "Error: " + message

    def _describe_image_with_ollama(
        self, gradio_image: Image.Image, user_input: str
    ) -> str:
        res = ollama.chat(
            model=self.model_definition.config.get("model"),
            messages=[
                {
                    "role": "user",
                    "content": user_input,
                    "images": [self._get_image_bytes(gradio_image)],
                }
            ],
        )

        print(res["message"]["content"])
        return res["message"]["content"]

    def _get_image_bytes(self, image):
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return buffered.getvalue()

    def _encode_image_base64(self, image: Image):
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")
