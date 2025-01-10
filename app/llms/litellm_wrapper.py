# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
from litellm import completion
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from litellm import RateLimitError


@retry(
    stop=stop_after_attempt(2),
    wait=wait_fixed(60),
    retry=retry_if_exception_type(RateLimitError),
)
def llmCompletion(**kwargs):
    return completion(**kwargs)
