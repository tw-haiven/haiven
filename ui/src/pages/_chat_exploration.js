import { useState, useEffect } from "react";
import { ProChat, ProChatProvider, useProChat } from "@ant-design/pro-chat";
import { Button, Flex } from "antd";
import { useTheme } from "antd-style";
import { RiLightbulbLine } from "react-icons/ri";

export default function ChatExploration({
  context,
  user,
  scenarioQueries = [],
}) {
  const item = context || {};
  console.log("ITEM:", item);
  const userProfile = user || {
    name: "User",
    avatar: "/boba/user-5-fill-dark-blue.svg",
  };
  const theme = useTheme();
  const [promptStarted, setPromptStarted] = useState(false);
  const [chatSessionId, setChatSessionId] = useState();

  function itemToString(item) {
    let result = "";
    for (const key in item) {
      result += `**${key}:** ${item[key]} || `;
    }
    return result;
  }

  const onSubmitMessage = async (messages) => {
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

  const PossibilityPanel = () => {
    const proChat = useProChat();

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
                proChat.sendMessage(text);
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

  const Chat = () => {
    return (
      <ProChat
        style={{
          height: "100%",
          width: "100%",
          backgroundColor: theme.colorBgContainer,
          marginTop: "5px",
        }}
        showTitle
        assistantMeta={{
          avatar: "/boba/shining-fill-white.svg",
          title: "Haiven",
          backgroundColor: "#003d4f",
        }}
        userMeta={{
          avatar: userProfile.avatar ?? userProfile.name,
          title: userProfile.name,
          backgroundColor: "#47a1ad",
        }}
        locale="en-US"
        helloMessage={"What do you want to explore?"}
        request={onSubmitMessage}
      />
    );
  };

  return (
    <div className="chat-exploration">
      <div className="chat-exploration__header">
        <p>{item.summary}</p>
      </div>
      <ProChatProvider>
        <PossibilityPanel />
        <Chat />
      </ProChatProvider>
    </div>
  );
}
