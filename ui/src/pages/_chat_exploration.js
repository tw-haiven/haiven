// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useState, useRef } from "react";
import { ProChatProvider } from "@ant-design/pro-chat";
import { Button, Flex } from "antd";
import { RiLightbulbLine } from "react-icons/ri";
import ChatWidget from "../app/_chat";

export default function ChatExploration({
  context,
  user,
  scenarioQueries = [],
}) {
  const item = context || {};
  // console.log("ITEM:", item);

  const [promptStarted, setPromptStarted] = useState(false);
  const [chatSessionId, setChatSessionId] = useState();

  const chatRef = useRef();

  function itemToString(item) {
    let result = "";
    for (const key in item) {
      result += `**${key}:** ${item[key]} || `;
    }
    return result;
  }

  const submitPromptToBackend = async (messages) => {
    const exploreUri = "/api/" + item.type + "/explore",
      itemSummary = itemToString(item);

    if (promptStarted !== true) {
      const lastMessage = messages[messages.length - 1];
      const response = await fetch(exploreUri, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          userMessage: lastMessage?.content,
          item: itemSummary,
          originalInput: item?.originalPrompt || "",
          chatSessionId: chatSessionId,
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
          userMessage: lastMessage?.content,
          item: itemSummary,
          originalInput: item?.originalPrompt || "",
          chatSessionId: chatSessionId,
        }),
      });
      return response;
    }
  };

  const addMessageToChatWidget = async (prompt) => {
    if (chatRef.current) {
      chatRef.current.sendMessage(prompt);
    }
  };

  const PossibilityPanel = () => {
    return (
      <Flex
        marginBottom="1em"
        style={{ width: "100%" }}
        className="suggestions-list"
      >
        <Flex align="flex-start" gap="small" vertical style={{ width: "100%" }}>
          <div className="suggestions-title">Suggestions:</div>
          {scenarioQueries.map((text, i) => (
            <Button
              key={i}
              onClick={() => {
                addMessageToChatWidget(text);
              }}
              className="suggestion"
            >
              <RiLightbulbLine />
              {text}
            </Button>
          ))}
        </Flex>
      </Flex>
    );
  };

  return (
    <div className="chat-exploration">
      <div className="chat-exploration__header">
        <p>{item.summary}</p>
      </div>
      <PossibilityPanel />
      <ProChatProvider>
        <ChatWidget
          onSubmitMessage={submitPromptToBackend}
          ref={chatRef}
          visible={true}
          helloMessage={
            "Chat with me! Click on one of the suggested questions, or type your own below."
          }
        />
      </ProChatProvider>
    </div>
  );
}
