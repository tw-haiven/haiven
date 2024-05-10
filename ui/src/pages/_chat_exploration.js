import { useState } from "react";
import { ProChat } from "@ant-design/pro-chat";
import { useTheme } from "antd-style";

export default function ChatExploration({ context, user }) {
  const item = context || {};
  const userProfile = user || { name: "User" , avatar: "👤" };
  const theme = useTheme();
  const [promptStarted, setPromptStarted] = useState(false);
  const [chatSessionId, setChatSessionId] = useState();

  const onSubmitMessage = async (messages) => {
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

  return (
    <div className="chat-exploration">
      <ProChat
        style={{
          height: "100%",
          backgroundColor: theme.colorBgContainer,
        }}
        showTitle
        assistantMeta={{
          avatar: "/boba/haiven-chat-avatar.png",
          title: "Haiven",
          backgroundColor: "#003d4f",
        }}
        userMeta={{
          avatar: userProfile.avatar ?? userProfile.name,
          title: userProfile.name,
          backgroundColor: "#ffffff",
        }}
        locale="en-US"
        helloMessage={
          "In this " +
          item.type +
          ", " +
          item.summary +
          " What do you want to explore next?"
        }
        request={onSubmitMessage}
      />
    </div>
  );
}
