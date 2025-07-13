// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useState, useRef, useEffect } from "react";
import { ProChatProvider } from "@ant-design/pro-chat";
import ChatWidget from "../app/_chat";
import VerticalPossibilityPanel from "./_vertical-possibility-panel";
import LLMTokenUsage from "../app/_llm_token_usage";
import { formattedUsage } from "../app/utils/tokenUtils";

export default function ChatExploration({
  context,
  scenarioQueries = [],
  featureToggleConfig = {},
}) {
  const [promptStarted, setPromptStarted] = useState(false);
  const [chatSessionId, setChatSessionId] = useState();
  const [previousContext, setPreviousContext] = useState(context);
  const [tokenUsage, setTokenUsage] = useState(null);

  const chatRef = useRef();

  useEffect(() => {
    if (previousContext !== context) {
      setPreviousContext(context);
      setPromptStarted(false);
      setTokenUsage(null);
      chatRef.current.startNewConversation();
    }
  }, [context, previousContext]);

  const submitPromptToBackend = async (messages) => {
    const exploreUri = "/api/prompt/explore";

    // Reset token usage
    setTokenUsage(null);

    const processSSEResponse = (response) => {
      const sseStream = new ReadableStream({
        start(controller) {
          const reader = response.body.getReader();
          const decoder = new TextDecoder();
          let buffer = "";

          function pump() {
            return reader.read().then(({ done, value }) => {
              if (done) {
                controller.close();
                return;
              }

              const chunk = decoder.decode(value, { stream: true });
              buffer += chunk;
              // Check if this chunk contains SSE token usage event
              if (buffer.includes("event: token_usage")) {
                // Split at the SSE event boundary
                const parts = buffer.split("event: token_usage");
                const contentPart = parts[0];
                const sseEventPart = "event: token_usage" + parts[1];

                // Send content part to ProChat
                if (contentPart) {
                  controller.enqueue(new TextEncoder().encode(contentPart));
                }

                // Parse token usage from SSE event
                const lines = sseEventPart.split("\n");
                for (const line of lines) {
                  if (line.startsWith("data: ")) {
                    const data = line.substring(6);

                    // Process complete SSE events

                    try {
                      const tokenUsageData = JSON.parse(data);
                      setTokenUsage(formattedUsage(tokenUsageData));
                    } catch (parseError) {
                      console.log(
                        "Failed to parse token usage data:",
                        data,
                        parseError,
                      );
                    }
                    break;
                  }
                }

                buffer = "";
              } else {
                // Regular content - stream directly to ProChat
                controller.enqueue(new TextEncoder().encode(chunk));
                buffer = "";
              }

              return pump();
            });
          }

          return pump();
        },
      });

      // Create new response with filtered stream
      return new Response(sseStream, {
        status: response.status,
        statusText: response.statusText,
        headers: response.headers,
      });
    };

    if (promptStarted !== true) {
      const lastMessage = messages[messages.length - 1];
      const response = await fetch(exploreUri, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          userinput: lastMessage?.content,
          item: previousContext?.itemSummary,
          contexts: previousContext?.context || [],
          userContext: previousContext?.userContext || "",
          first_step_input: previousContext?.firstStepInput || "",
          previous_promptid: previousContext?.previousPromptId || "",
          previous_framing: previousContext?.previousFraming || "",
        }),
      });
      setPromptStarted(true);
      setChatSessionId(response.headers.get("X-Chat-ID"));
      return processSSEResponse(response);
    } else {
      console.log("Continuing conversation...");
      const lastMessage = messages[messages.length - 1];
      const response = await fetch(exploreUri, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          userinput: lastMessage?.content,
          chatSessionId: chatSessionId,
        }),
      });
      return processSSEResponse(response);
    }
  };

  const addMessageToChatWidget = async (prompt) => {
    if (chatRef.current) {
      chatRef.current.startNewConversation(prompt);
    }
  };

  return (
    <div className="chat-exploration">
      <div className="chat-exploration__header">
        <p>{previousContext?.summary || "No summary available"}</p>
      </div>
      {scenarioQueries.length > 0 ? (
        <VerticalPossibilityPanel
          scenarioQueries={scenarioQueries}
          onClick={addMessageToChatWidget}
        />
      ) : null}
      <ProChatProvider>
        <ChatWidget
          onSubmitMessage={submitPromptToBackend}
          ref={chatRef}
          visible={true}
          helloMessage={
            scenarioQueries.length > 0
              ? "Chat with me! Click on one of the suggested questions, or type your own below."
              : "Chat with me! Type your question below."
          }
        />
        <LLMTokenUsage
          tokenUsage={tokenUsage}
          featureToggleConfig={featureToggleConfig}
        />
      </ProChatProvider>
    </div>
  );
}
