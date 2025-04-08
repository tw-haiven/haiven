// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useState, useRef, useEffect } from "react";
import { ProChatProvider } from "@ant-design/pro-chat";
import ChatWidget from "../app/_chat";
import VerticalPossibilityPanel from "./_vertical-possibility-panel";

export default function ChatExploration({ context, scenarioQueries = [] }) {
  const [promptStarted, setPromptStarted] = useState(false);
  const [chatSessionId, setChatSessionId] = useState();
  const [previousContext, setPreviousContext] = useState(context);

  const chatRef = useRef();

  useEffect(() => {
    if (previousContext !== context) {
      setPreviousContext(context);
      setPromptStarted(false);
      chatRef.current.startNewConversation();
    }
  }, [context, previousContext]);

  const submitPromptToBackend = async (messages) => {
    const exploreUri = "/api/prompt/explore";

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
      return response;
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
      return response;
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
      </ProChatProvider>
    </div>
  );
}
