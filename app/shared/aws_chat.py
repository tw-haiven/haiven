# This class overcomes the connection closing issues with BedrockChat by closing the connection after each call.
# It was observed that the BedrockChat class does not close the connection to AWS after a chat response is fully served.
# This results in multiple connections staying open in the background, and it is 'believed 'that this results in the
# below error message:
#       when calling the InvokeModelWithResponseStream operation: Too many requests,
#       please wait before trying again. You have sent too many requests. Wait before trying again.
#
# The AWSChat class simply overrides important methods from BedrockChat and ensures the underlying connection is closed
# before returning from the method.
# Note: It is important to call gc.collect() after closing the connection to ensure that the connection is closed.
#
# To test if connections are closed use the below command:
#       watch -n 1 'lsof -p <pid> | grep amazon'
# In the above command <pid> is the process id of the running application.


from typing import Any, Iterator, List, Optional
import gc

from langchain_community.chat_models import BedrockChat
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.outputs import GenerationChunk


class AWSChat(BedrockChat):
    def _stream(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        try:
            yield from super()._stream(prompt, stop, run_manager, **kwargs)
        finally:
            self.client.close()
            gc.collect()

    def _generate(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        try:
            return super()._generate(prompt, stop, run_manager, **kwargs)
        finally:
            self.client.close()
            gc.collect()

    def __call__(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        try:
            return super().__call__(prompt, stop, run_manager, **kwargs)
        finally:
            self.client.close()
            gc.collect()
