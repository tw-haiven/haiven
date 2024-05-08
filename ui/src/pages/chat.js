"use client";
import {
  ProChat,
  ProChatProvider,
  useProChat,
  Avatar,
} from "@ant-design/pro-chat";
import { useTheme } from "antd-style";
import { useEffect, useState, useRef } from "react";
import { Input, Select, Space, Button } from "antd";
const { TextArea } = Input;

const Home = () => {
  const PromptChat = () => {
    const theme = useTheme();
    const proChat = useProChat();

    const [prompts, setPrompts] = useState([]);
    const [promptInput, setPromptInput] = useState("");
    const [selectedPrompt, setPromptSelection] = useState("");
    const [showComponent, setShowComponent] = useState(false);
    const [promptStarted, setPromptStarted] = useState(false);
    const [chatSessionId, setChatSessionId] = useState();

    useEffect(() => setShowComponent(true), []);

    const onSubmitMessage = async (messages) => {
      // console.log("messages", messages)

      if (promptStarted !== true) {
        const lastMessage = messages[messages.length - 1];
        const response = await fetch("/api/prompt", {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            userinput: lastMessage?.content,
            promptid: selectedPrompt.identifier,
            chatSessionId: chatSessionId,
          }),
        });
        setPromptStarted(true);
        setChatSessionId(response.headers.get("X-Chat-ID"));
        return response;
      } else {
        console.log("Continuing conversation...");
        const lastMessage = messages[messages.length - 1];
        const response = await fetch("/api/prompt", {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            userinput: lastMessage?.content,
            promptid: selectedPrompt.identifier,
            chatSessionId: chatSessionId,
          }),
        });
        return response;
      }
    };

    function handlePromptChange(value) {
      const selectedPrompt = prompts.find(
        (prompt) => prompt.identifier === value,
      );
      setPromptSelection(selectedPrompt);
    }

    useEffect(() => {
      fetch("/api/prompts", {
        method: "GET",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
      }).then((response) => {
        response.json().then((data) => {
          const formattedPrompts = data.map((item) => ({
            ...item,
            value: item.identifier,
            label: item.title,
          }));
          setPrompts(formattedPrompts);
        });
      });
    }, []);

    const onSubmitPrompt = async () => {
      console.log("promptInput", promptInput);
      proChat.sendMessage(promptInput);
    };

    return (
      <div>
        <div id="prompt-center">
          <h2>Prompting Center</h2>
          What do you want to do?{" "}
          <Select
            onChange={handlePromptChange}
            style={{ width: 300 }}
            options={prompts}
          ></Select>
          <div>
            {selectedPrompt && (
              <div>
                <p>
                  <b>Description: </b>
                  {selectedPrompt.help_prompt_description}
                </p>
                <p>
                  <b>User input: </b>
                  {selectedPrompt.help_user_input}
                </p>
                <p>
                  <b>Sample input: </b>
                  {selectedPrompt.help_sample_input}
                </p>
              </div>
            )}
          </div>
          <br />
          <br />
          <Space.Compact style={{ width: "100%" }}>
            Your user input:{" "}
            <TextArea
              value={promptInput}
              onChange={(e, v) => {
                setPromptInput(e.target.value);
              }}
            />
            <Button type="primary" onClick={onSubmitPrompt}>
              Go
            </Button>
          </Space.Compact>
        </div>
        {showComponent && (
          <ProChat
            style={{
              height: "100vh",
              backgroundColor: theme.colorBgContainer,
            }}
            locale="en-US"
            helloMessage={
              <div>
                {
                  "Welcome! To get started, choose a prompt from the dropdown and give me your input."
                }
              </div>
            }
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
        )}
      </div>
    );
  };

  return (
    <ProChatProvider>
      <PromptChat />
    </ProChatProvider>
  );
};
export default Home;
