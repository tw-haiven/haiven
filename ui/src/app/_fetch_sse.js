export const getMessageError = async (response) => {
  let chatMessageError = {
    message: `response error, status: ${response.statusText}`,
    type: response.status,
  };

  return chatMessageError;
};

// export interface FetchSSEOptions {
//   onErrorHandle?: (error: ChatMessageError) => void;
//   onMessageHandle?: (text: string, response: Response) => void;
//   onAbort?: (text: string) => Promise<void>;
//   onFinish?: (text: string, type: SSEFinishType) => Promise<void>;
// }

// Attempt to implement a fetch SSE variant that is more flexible in terms
// of taking different HTTP methods, headers etc - basically the full power of fetch()
// Copied from https://github.com/ant-design/pro-chat
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

    // TODO for backend: Backend shouldn't have the "data: " prefix for this client implementation
    // PROBLEM we stopped with: For some reason the chunkValue has lots of messed up escape characters
    /* Example
      ""[ {""\"title\": ""\"Hello scenario 1\""", \"description\": ""\"scenario description\"  }, { ""\"title\": ""\"Hello scenario 2\" }""]""
    */
    // console.log("reading", chunkValue);

    options.onMessageHandle?.(chunkValue.trim(), returnRes);
  }

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
