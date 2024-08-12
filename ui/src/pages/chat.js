// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
"use client";
import { ProChatProvider } from "@ant-design/pro-chat";
import { useEffect, useState, useRef } from "react";
import { Input, Select, Button, Tooltip, Radio } from "antd";
import { RiQuestionLine } from "react-icons/ri";

const { TextArea } = Input;
import ChatWidget from "../app/_chat";
import Clipboard from "../app/_clipboard";
import ClipboardButton from "../app/_clipboard_button";
import { getPrompts, getContexts } from "../app/_boba_api";

const PromptChat = () => {
  const chatRef = useRef();

  const [prompts, setPrompts] = useState([]);
  const [contexts, setContexts] = useState([]);
  const [selectedContext, setSelectedContext] = useState("");
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
      const requestData = {
        userinput: lastMessage?.content,
        promptid: selectedPrompt.identifier,
        chatSessionId: chatSessionId,
      };
      if (selectedContext !== "base") {
        requestData.context = selectedContext;
      }
      const response = await fetch("/api/prompt", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
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

  const handleContextChange = ({ target: { value } }) => {
    console.log("Context radio checked", value);
    setSelectedContext(value);
  };

  useEffect(() => {
    getPrompts(setPrompts);
    getContexts((data) => {
      const labelValuePairs = data.map((context) => {
        if (context.context === "base") {
          console.log("context is base!");
          return {
            label: "none",
            value: "base",
          };
        } else {
          return {
            label: context.context,
            value: context.context,
          };
        }
      });
      setContexts(labelValuePairs);
    });
  }, []);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const prompt = params.get("prompt");
    if (prompt) {
      handlePromptChange(prompt);
    }
  }, [prompts]);

  const addMessageToChatWidget = async () => {
    if (chatRef.current) {
      chatRef.current.sendMessage(promptInput);
    }
  };

  return (
    <>
      {/* <Clipboard
        toggleClipboardDrawer={setClipboardDrawerOpen}
        isOpen={clipboardDrawerOpen}
        contexts={contexts}
      /> */}

      <div className="prompt-chat-container">
        <div id="prompt-center">
          {/* <ClipboardButton toggleClipboardDrawer={setClipboardDrawerOpen} /> */}
          <h2>Prompting Center</h2>
          <div className="user-inputs">
            <div className="prompt-center-section">
              <div className="section-header">
                What do you want to do?
                <Tooltip
                  className="tooltip-help"
                  title="Choose a task from the dropdown to get more info about what each of them can do"
                >
                  <RiQuestionLine />
                </Tooltip>
              </div>

              <div className="section-inputs">
                <div className="user-input">
                  <Select
                    onChange={handlePromptChange}
                    style={{ width: 300 }}
                    options={prompts}
                    value={selectedPrompt?.identifier}
                  ></Select>
                </div>

                {selectedPrompt && (
                  <div className="user-input">
                    <p>
                      <b>Description: </b>
                      {selectedPrompt.help_prompt_description}
                    </p>
                    <p>
                      <b>Your input: </b>
                      {selectedPrompt.help_user_input}
                    </p>
                    <p>
                      <b>Sample input: </b>
                      {selectedPrompt.help_sample_input}
                    </p>
                  </div>
                )}
              </div>
            </div>

            <div className="prompt-center-section">
              <div className="section-header">
                Add your input
                <Tooltip
                  className="tooltip-help"
                  title="Provide the input based on the description of the chosen task. Optionally, you can choose to add one of the available contexts from your knowledge pack."
                >
                  <RiQuestionLine />
                </Tooltip>
              </div>

              <div className="section-inputs">
                <div className="user-input">
                  <label>Your input:</label>
                  <TextArea
                    value={promptInput}
                    rows={4}
                    onChange={(e, v) => {
                      setPromptInput(e.target.value);
                    }}
                  />
                </div>

                {contexts && (
                  <div className="context-list">
                    <b>Add a context</b> <br />
                    <Radio.Group
                      optionType="button"
                      buttonStyle="solid"
                      options={contexts}
                      defaultValue="base"
                      onChange={handleContextChange}
                    />
                  </div>
                )}
              </div>
            </div>
            <div className="prompt-center-section">
              <Button type="primary" onClick={addMessageToChatWidget}>
                Go
              </Button>
            </div>
          </div>
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
