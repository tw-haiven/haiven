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
        // Handle the new backend format that mixes JSON objects and SSE events
        if (chunkValue !== "") {
          // Split by double newlines to separate different messages
          const messages = chunkValue.split(/\n\n+/);

          messages.forEach((message) => {
            // Skip empty messages
            if (!message || !message.trim()) return;

            const trimmedMessage = message.trim();

            // Check if this is an SSE event (starts with "event:")
            if (trimmedMessage.startsWith("event:")) {
              // Handle SSE events
              const lines = trimmedMessage.split("\n");
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
                const data = JSON.parse(trimmedMessage);
                // Only check for error messages on string data, not objects
                if (typeof data.data === "string") {
                  checkIsErrorMessage(data.data || "");
                }
                // Handle metadata objects that don't have a data property
                if (data.metadata && !data.data) {
                  options.onMessageHandle?.(data, response);
                } else if (data.data) {
                  options.onMessageHandle?.(data, response);
                }
              } catch (parseError) {
                console.log(
                  "Failed to parse JSON chunk:",
                  trimmedMessage,
                  parseError,
                );
              }
            }
          });
        }
      } else if (options.text === true) {
        // Handle SSE format for text streams with mixed JSON and SSE events
        if (chunkValue !== "") {
          // Split by double newlines to separate different messages
          const messages = chunkValue.split(/\n\n+/);

          messages.forEach((message) => {
            // Skip empty messages
            if (!message || !message.trim()) return;

            const trimmedMessage = message.trim();

            // Check if this is an SSE event (starts with "event:")
            if (trimmedMessage.startsWith("event:")) {
              // Handle SSE events
              const lines = trimmedMessage.split("\n");
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
                  options.onTokenUsage?.(tokenUsageData);
                } catch (parseError) {
                  console.log(
                    "Failed to parse token usage data:",
                    eventData,
                    parseError,
                  );
                }
              }
            } else {
              // Handle regular text content or JSON objects
              try {
                // Try to parse as JSON first
                const jsonData = JSON.parse(trimmedMessage);
                // If it's a JSON object with data property, extract the text
                if (jsonData.data && typeof jsonData.data === "string") {
                  checkIsErrorMessage(jsonData.data);
                  options.onMessageHandle?.(jsonData.data, response);
                } else if (jsonData.metadata) {
                  // Handle metadata objects
                  options.onMessageHandle?.(jsonData, response);
                }
              } catch (parseError) {
                // Not JSON, treat as plain text
                checkIsErrorMessage(trimmedMessage);
                options.onMessageHandle?.(trimmedMessage, response);
              }
            }
          });
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
