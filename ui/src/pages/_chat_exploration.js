import { useState, useEffect } from "react";
import { ProChat, ProChatProvider, useProChat } from "@ant-design/pro-chat";
import { Button, Flex } from "antd";
import { useTheme } from "antd-style";

export default function ChatExploration({
  context,
  user,
  scenarioQueries = [],
}) {
  const item = context || {};
  const userProfile = user || {
    name: "User",
    avatar: "/boba/user-5-fill-dark-blue.svg",
  };
  const theme = useTheme();
  const [promptStarted, setPromptStarted] = useState(false);
  const [chatSessionId, setChatSessionId] = useState();

  const onSubmitMessage = async (messages) => {
    console.log("Submitting message: ", messages);
    const uri = "/api/" + item.type + "/explore",
      context = item.summary;

    if (promptStarted !== true) {
      const lastMessage = messages[messages.length - 1];
      const response = await fetch(uri, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          input: lastMessage?.content,
          context: context,
          chatSessionId: chatSessionId,
        }),
      });
      setPromptStarted(true);
      setChatSessionId(response.headers.get("X-Chat-ID"));
      return response;
    } else {
      console.log("Continuing conversation...");
      const lastMessage = messages[messages.length - 1];
      const response = await fetch(uri, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          input: lastMessage?.content,
          context: context,
          chatSessionId: chatSessionId,
        }),
      });
      return response;
    }
  };

  const PossibilityPanel = () => {
    const proChat = useProChat();

    return (
      <Flex marginBottom="2px" style={{ width: "100%" }}>
        <Flex
          align="flex-start"
          gap="middle"
          vertical
          style={{ width: "100%" }}
        >
          {scenarioQueries.map((text, i) => (
            <Button
              key={i}
              onClick={() => {
                proChat.sendMessage(text);
              }}
              style={{
                width: "100%", // Ensure button width is 100%
                backgroundColor: theme.colorBgContainer,
                color: theme.colorText,
                border: "1px solid " + theme.colorBorder,
                marginBottom: "2px",
                overflow: "hidden",
                textOverflow: "clip",
                whiteSpace: "normal",
                minHeight: "40px",
                height: "auto",
              }}
            >
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
