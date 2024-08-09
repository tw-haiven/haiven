// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
"use client";
import { ProChatProvider } from "@ant-design/pro-chat";
import { useEffect, useState, useRef } from "react";
import { Input, Select, Button } from "antd";
const { TextArea } = Input;
import ChatWidget from "../app/_chat";
import Clipboard from "../app/_clipboard";
import ClipboardButton from "../app/_clipboard_button";

const PromptChat = () => {
  const chatRef = useRef();

  const [prompts, setPrompts] = useState([]);
  const [promptInput, setPromptInput] = useState("");
  const [selectedPrompt, setPromptSelection] = useState("");
  const [showChat, setShowChat] = useState(false);
  const [promptStarted, setPromptStarted] = useState(false);
  const [chatSessionId, setChatSessionId] = useState();
  const [clipboardDrawerOpen, setClipboardDrawerOpen] = useState(false);

  useEffect(() => setShowChat(false), []);

  const submitPromptToBackend = async (messages) => {
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
      setShowChat(true);
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

  const addMessageToChatWidget = async () => {
    if (chatRef.current) {
      chatRef.current.sendMessage(promptInput);
    }
  };

  return (
    <>
      <Clipboard
        toggleClipboardDrawer={setClipboardDrawerOpen}
        isOpen={clipboardDrawerOpen}
      />

      <div className="prompt-chat-container">
        <div id="prompt-center">
          <ClipboardButton toggleClipboardDrawer={setClipboardDrawerOpen} />
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
          Your user input:{" "}
          <TextArea
            value={promptInput}
            rows={4}
            onChange={(e, v) => {
              setPromptInput(e.target.value);
            }}
          />
          <br />
          <br />
          <Button type="primary" onClick={addMessageToChatWidget}>
            Go
          </Button>
        </div>

        <ProChatProvider>
          <ChatWidget
            onSubmitMessage={submitPromptToBackend}
            ref={chatRef}
            visible={showChat}
          />
        </ProChatProvider>
      </div>
    </>
  );
};

export default PromptChat;
