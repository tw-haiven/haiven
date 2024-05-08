import { useState } from "react";
import {
  ProChat,
  ProChatProvider,
  useProChat,
  Avatar,
} from "@ant-design/pro-chat";
import { useTheme } from "antd-style";

const ctrls = {};
export default function ChatExploration({ context }) {
  const item = context || {};
  const theme = useTheme();
  const [promptStarted, setPromptStarted] = useState(false);
  const [chatSessionId, setChatSessionId] = useState();

  const onSubmitMessage = async (messages) => {
    // console.log("messages", messages)

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
        locale="en-US"
        helloMessage={"In this " + item.type + ", " + item.summary + ". What do you want to explore next?"}
        request={onSubmitMessage}
        chatItemRenderConfig={{
          avatarRender: (item, dom, defaultDom) => {
            // const role = item.originData.role;
            // if (role === "user") { // also: "assistant", "hello"
            //   item.originData.meta.avatar = "🤷‍♀️"
            // }

            return defaultDom;
          },
        }}
      />
    </div>
  );
}
