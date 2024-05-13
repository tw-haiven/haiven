export const getMessageError = async (response) => {
  let chatMessageError = {
    message: `response error, status: ${response.statusText}`,
    type: response.status,
  };

  return chatMessageError;
};

/*
 Attempt to implement a fetch SSE variant that is more flexible in terms
 of taking different HTTP methods, headers etc - basically the full power of fetch()
 Original code copied from https://github.com/ant-design/pro-chat
 https://github.com/ant-design/pro-chat/blob/371bc6580d684575d84a89ee5e149f751334c456/src/ProChat/utils/fetch.ts

 options:
   onErrorHandle?: (error: {"message", "type"})
   onMessageHandle?: (text: string, response: Response)
   onFinish?: (text: string)
   json?: boolean; if true, will process '{ "data": "some partial token of a JSON string" }' chunks and pass on as JSON object
*/
export const fetchSSE2 = async (fetchFn, options) => {
  options = options || {};
  const response = await fetchFn();

  if (!response.ok) {
    // TODO: need a message error custom parser
    const chatMessageError = await getMessageError(response);

    options.onErrorHandle?.(chatMessageError);
    return;
  }

  const returnRes = response.clone();

  const data = response.body;

  if (!data) return;

  const reader = data.getReader();
  const decoder = new TextDecoder();

  let done = false;

  while (!done) {
    const { value, done: doneReading } = await reader.read();
    done = doneReading;
    const chunkValue = decoder.decode(value, { stream: !doneReading });

    console.log("reading", chunkValue);

    if (options.json === true) {
      // - expectation from backend: '{ "data": "some partial token of a JSON string" }'
      // - chunkValue is sometimes multiple messages
      // - make an assumption about API endpoints' message delimiters (\n\n)
      // - Split into multiple "messages" with JSON data tokens
      if (chunkValue !== "") {
        const SPLIT_DELIMITER = "|SPLIT|";
        const chunkable = chunkValue.replace(
          /}\n\n{/g,
          "}" + SPLIT_DELIMITER + "{",
        );
        const chunks = chunkable.split(SPLIT_DELIMITER);
        chunks.forEach((value) => {
          const data = JSON.parse(value);
          options.onMessageHandle?.(data, returnRes);
        });
      }
    } else {
      options.onMessageHandle?.(chunkValue, returnRes);
    }
  }

  options.onFinish?.("finish");

  return returnRes;
};

export function fetchSSE(options) {
  const { url, onData, onStop } = options;
  try {
    const sse = new EventSource(url, { withCredentials: true });
    sse.onmessage = (event) => {
      // if(!isLoadingXhr) {
      //   console.log("is loading xhr", isLoadingXhr);
      //   return;
      // }
      if (event.data == "[DONE]") {
        onStop();
        sse.close();
        return;
      }
      onData(event, sse);
    };
    sse.onerror = (error) => {
      console.log("error", error);
      onStop();
    };
    sse.onopen = (event) => {};
    return sse;
  } catch (error) {
    console.log("error", error);
    onStop();
  }
}
