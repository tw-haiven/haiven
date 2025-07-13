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

      // Skip if no value to decode
      if (!value) continue;

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
            // Skip empty chunks
            if (!value || !value.trim()) return;

            // Check if this is an SSE event (starts with "event:")
            if (value.trim().startsWith("event:")) {
              // Handle SSE events
              const lines = value.trim().split("\n");
              let eventType = null;
              let eventData = null;

              for (const line of lines) {
                if (line.startsWith("event:")) {
                  eventType = line.substring(6).trim();
                } else if (line.startsWith("data:")) {
                  eventData = line.substring(5).trim();
                }
              }

              if (eventType === "token_usage" && eventData) {
                try {
                  const tokenUsageData = JSON.parse(eventData);
                  // Call onMessageHandle with a structured token usage object
                  options.onMessageHandle?.(
                    {
                      type: "token_usage",
                      data: tokenUsageData,
                    },
                    response,
                  );
                } catch (parseError) {
                  console.log(
                    "Failed to parse token usage data:",
                    eventData,
                    parseError,
                  );
                }
              }
            } else {
              // Handle regular JSON chunks
              try {
                const data = JSON.parse(value);
                // Only check for error messages on string data, not objects
                if (typeof data.data === "string") {
                  checkIsErrorMessage(data.data || "");
                }
                options.onMessageHandle?.(data, response);
              } catch (parseError) {
                console.log("Failed to parse JSON chunk:", value, parseError);
              }
            }
          });
        }
      } else if (options.text === true) {
        // Handle SSE format for text streams
        if (chunkValue !== "") {
          const lines = chunkValue.split("\n");
          let eventType = "message";

          for (const line of lines) {
            if (line.startsWith("event: ")) {
              eventType = line.substring(7).trim();
            } else if (line.startsWith("data: ")) {
              const data = line.substring(6);

              if (eventType === "token_usage") {
                try {
                  const tokenUsageData = JSON.parse(data);
                  options.onTokenUsage?.(tokenUsageData);
                } catch (parseError) {
                  console.log(
                    "Failed to parse token usage data:",
                    data,
                    parseError,
                  );
                }
                eventType = "message"; // Reset for next event
              } else {
                // Regular text content - check for errors and pass through
                checkIsErrorMessage(data);
                options.onMessageHandle?.(data, response);
              }
            } else if (line === "") {
              // End of event, reset type
              eventType = "message";
            }
          }
        }
      } else {
        // Ensure chunkValue is a string before checking for error messages
        if (typeof chunkValue === "string") {
          checkIsErrorMessage(chunkValue);
        }
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
