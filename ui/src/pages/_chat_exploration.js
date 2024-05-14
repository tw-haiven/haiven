import { useState } from "react";
import { ProChat, ProChatProvider, useProChat } from "@ant-design/pro-chat";
import { Button, Divider, Flex } from "antd";
import { useTheme } from "antd-style";
import { create } from "domain";

export default function ChatExploration({ context, user }) {
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

  const getQuestions = () => {
    return [
      "What could go wrong?",
      "What business opportunities could this offer?",
    ];
  };
  const possibilities = getQuestions();

  const PossibilityPanel = () => {
    const proChat = useProChat();

    return (
      <Flex style={{ padding: 24 }} gap={8} justify={"space-between"}>
        <Flex gap={8}>
          {possibilities.map((text, i) => (
            <Button
              key={i}
              type="primary"
              onClick={() => {
                console.log("submitting this: ", text);
                proChat.sendMessage(text);
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
          backgroundColor: theme.colorBgContainer,
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
