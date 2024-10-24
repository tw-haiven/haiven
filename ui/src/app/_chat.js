// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { ActionIconGroup, ProChat, useProChat } from "@ant-design/pro-chat";
import { css, cx, useTheme } from "antd-style";
import { message } from "antd";
import { PinIcon, RotateCw, Trash, Copy } from "lucide-react";
import React, { forwardRef, useImperativeHandle, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { addToPinboard } from "./_pinboard";

const ChatWidget = forwardRef(
  ({ onSubmitMessage, helloMessage, visible }, ref) => {
    const proChat = useProChat();

    const [chatIsVisible, setChatIsVisible] = useState(visible);
    const pin = {
      icon: PinIcon,
      key: "pin",
      label: "Pin",
      execute: (props) => {
        addToPinboard(props.time, props.message);
      },
    };
    const regenerate = {
      key: "regenerate",
      label: "Regenerate",
      icon: RotateCw,
      execute: (props) => {
        proChat.resendMessage(props["data-id"]);
      },
    };
    const del = {
      key: "del",
      label: "Delete",
      icon: Trash,
      execute: (props) => {
        proChat.deleteMessage(props["data-id"]);
      },
    };
    const copy = {
      key: "copy",
      label: "copy",
      icon: Copy,
      execute: (props) => {
        navigator.clipboard.writeText(props.message);
        message.success("Copy Success");
      },
    };

    const defaultActions = [copy, pin, regenerate];
    const extendedActions = [del];

    const theme = useTheme();
    const ChatStylingClass = cx(
      css(`
          .ant-pro-chat-list-item-message-content {
            background-color: #ffffff;
          }
          .ant-pro-chat-list-item-message-content h1, h2, h3, h4 {
            font-weight: 630;
          }
          .ant-pro-chat-list-item-message-content h1 {
            font-size: 1.7em;
          }
          .ant-pro-chat-list-item-message-content h2 {
            font-size: 1.5em;
          }
          .ant-pro-chat-list-item-message-content h3 {
            font-size: 1.3em;
          }
          .ant-pro-chat-list-item-message-content h4, h5 {
            font-size: 1.1em;
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
      async startNewConversation(message) {
        setChatIsVisible(true);
        proChat.clearMessage();
        return await proChat.sendMessage(message);
      },
    }));

    return (
      <div style={{ height: "100%" }} className={ChatStylingClass}>
        {chatIsVisible && (
          <ProChat
            style={{
              height: "100%", // this is important for the chat_exploration styling!
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
            chatItemRenderConfig={{
              contentRender: (props, _defaultDom) => {
                const isError = props.message.startsWith("[ERROR]: ")
                  ? props.message.replace("[ERROR]: ", "")
                  : null;
                return (
                  <div
                    className={`chat-message ${props.primary ? "user" : "assistant"}`}
                  >
                    {isError ? (
                      <p style={{ color: "red" }}>{isError}</p>
                    ) : (
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {props.message}
                      </ReactMarkdown>
                    )}
                  </div>
                );
              },
              actionsRender: (props, _defaultDom) => {
                return (
                  <ActionIconGroup
                    items={defaultActions}
                    dropdownMenu={extendedActions}
                    onActionClick={(action) => {
                      action.item.execute(props);
                    }}
                    type="ghost"
                  />
                );
              },
            }}
          />
        )}
      </div>
    );
  },
);

export default ChatWidget;
