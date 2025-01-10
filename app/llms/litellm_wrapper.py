from litellm import completion
from tenacity import *
from litellm import RateLimitError
import datetime

@retry(stop=stop_after_attempt(2), wait=wait_fixed(60), retry=retry_if_exception_type(RateLimitError))
def llmCompletion(**kwargs):
    return completion(**kwargs)
