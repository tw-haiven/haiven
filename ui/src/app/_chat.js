// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { ProChat, useProChat } from "@ant-design/pro-chat";
import { css, cx, useTheme } from "antd-style";
import React, { forwardRef, useImperativeHandle, useState } from "react";
import { ProChatProvider } from "@ant-design/pro-chat";

const ChatWidget = forwardRef(
  ({ onSubmitMessage, helloMessage, visible }, ref) => {
    const proChat = useProChat();

    const [chatIsVisible, setChatIsVisible] = useState(visible);

    const theme = useTheme();
    const ChatStylingClass = cx(
      css(`
          .ant-pro-chat-list-item-message-content {
            background-color: #ffffff;
          }
      `),
    );

    const userProfile = {
      name: "User",
      avatar: "/boba/user-5-fill-dark-blue.svg",
    };

    const onSubmit = async (messages) => {
      console.log("onSubmit");
      return await onSubmitMessage(messages);
    };

    useImperativeHandle(ref, () => ({
      async sendMessage(message) {
        setChatIsVisible(true);
        return await proChat.sendMessage(message);
      },
    }));

    return (
      <div
        style={{ background: theme.colorBgLayout }}
        className={ChatStylingClass}
      >
        {chatIsVisible && (
          <ProChat
            style={{
              backgroundColor: theme.colorBgContainer,
              height: "100vh", // this is important for the chat_exploration styling!
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
            helloMessage={helloMessage}
            request={onSubmit}
          />
        )}
      </div>
    );
  },
);

export default ChatWidget;
