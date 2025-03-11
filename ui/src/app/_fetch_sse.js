// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { toast } from "react-toastify";

export const getMessageError = async (response) => {
  let chatMessageError = {
    message: response.statusText,
    type: response.status,
  };

  return chatMessageError;
};

const checkIsErrorMessage = (response) => {
  const isError = response.startsWith("[ERROR]: ")
    ? response.replace("[ERROR]: ", "")
    : null;
  if (isError) {
    toast.error(isError);
    throw new Error(isError);
  }
};

const isAbortError = (error) => {
  return (
    error.name === "AbortError" &&
    error.message.includes("BodyStreamBuffer was aborted")
  );
};

/*
 Implementation of event stream client that is more flexible in terms
 of taking different HTTP methods, headers etc - basically the full power of fetch()
 Original code based on a copy from https://github.com/ant-design/pro-chat
 https://github.com/ant-design/pro-chat/blob/371bc6580d684575d84a89ee5e149f751334c456/src/ProChat/utils/fetch.ts

 options:
   onErrorHandle?: (error: {"message", "type"})
   onMessageHandle?: (text: string, response: Response)
   onFinish?: (text: string)
   json?: boolean; if true, will process '{ "data": "some partial token of a JSON string" }' chunks and pass on as JSON object
*/
export const fetchSSE = async (uri, fetchOptions, options) => {
  options = options || {};

  fetchOptions.credentials = fetchOptions.credentials || "include";
  fetchOptions.headers = fetchOptions.headers || {
    "Content-Type": "application/json",
  };
  fetchOptions.method = fetchOptions.method || "POST";
  const response = await fetch(uri, fetchOptions);

  if (!response.ok) {
    // TODO: need a message error custom parser
    const chatMessageError = await getMessageError(response);

    options.onErrorHandle?.(chatMessageError);
    const errorMessage = `Error: ${chatMessageError.type} - ${chatMessageError.message}`;
    toast.error(errorMessage);
    return;
  }

  const data = response.body;

  if (!data) return;

  const reader = data.getReader();
  const decoder = new TextDecoder();

  let done = false;

  try {
    while (!done) {
      const { value, done: doneReading } = await reader.read();
      done = doneReading;
      const chunkValue = decoder.decode(value, { stream: !doneReading });

      // console.log("reading", chunkValue);

      if (options.json === true) {
        // - expectation from backend: '{ "data": "some partial token of a JSON string" }'
        // - chunkValue is sometimes multiple messages
        // - make an assumption about API endpoints' message delimiters (\n\n)
        // - Split into multiple "messages" with JSON data tokens
        if (chunkValue !== "") {
          // LEARNING: Sending on just the JSON chunk directly, without {data: ...} wrapper, doesn't work, messes up character escaping
          // LEARNING: Using "data: " in front of the {data: ...} wrapper also breaks things, "Unexpected non-whitespace character" for the trailing line breaks?
          // LEARNING: Removing the trailing double line break from the API response a) doesn't seem to be the standard, EventStream tab doesn't show anything, and b) again seems to break the JSON.parse

          const SPLIT_DELIMITER = "|SPLIT|";
          const chunkable = chunkValue.replace(
            /}\n\n{/g,
            "}" + SPLIT_DELIMITER + "{",
          );
          const chunks = chunkable.split(SPLIT_DELIMITER);
          chunks.forEach((value) => {
            const data = JSON.parse(value);
            checkIsErrorMessage(data.data || "");
            options.onMessageHandle?.(data, response);
          });
        }
      } else {
        checkIsErrorMessage(chunkValue);
        options.onMessageHandle?.(chunkValue, response);
      }
    }

    options.onFinish?.("finish");
  } catch (error) {
    if (!isAbortError(error)) {
      console.log("error", error);
      options.onErrorHandle?.(error);
    }
  }
};
