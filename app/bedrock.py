# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from litellm import completion
from dotenv import load_dotenv

load_dotenv()

# https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/model-catalog
# Access is granted to these models in us-east-1:
# anthropic.claude-3-7-sonnet-20250219-v1:0
# anthropic.claude-3-5-sonnet-20241022-v2:0

response = completion(
    # Without region in front of model ID
    ## litellm.exceptions.APIConnectionError: litellm.APIConnectionError: BedrockException - {"message":"You don't have access to the model with the specified model ID."}
    model="bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0",
    # With region in front of model ID
    ## AttributeError: 'AmazonAnthropicConfig' object has no attribute 'aws_authentication_params'
    #   model="bedrock/us-east-1.anthropic.claude-3-5-sonnet-20241022-v2:0",
    # Tried with and without adding these explicitly (they should be pulled anyway from the .env), both with same results
    #   aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    #     aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    #     aws_region_name=os.environ.get("AWS_REGION_NAME"),
    messages=[{"content": "Who is Elvis?", "role": "user"}],
)
