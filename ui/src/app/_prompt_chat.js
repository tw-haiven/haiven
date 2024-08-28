// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
"use client";
import { ProChatProvider } from "@ant-design/pro-chat";
import { useEffect, useState, useRef } from "react";
import { Input, Select, Button } from "antd";

const { TextArea } = Input;
import ChatWidget from "./_chat";
import DescribeImage from "./_image_description";
import HelpTooltip from "./_help_tooltip";

const PromptChat = ({
  promptId,
  prompts,
  contexts,
  documents,
  showImageDescription = true,
  showTextSnippets = true,
  showDocuments = true,
  pageTitle,
  pageIntro,
}) => {
  const chatRef = useRef();

  // User inputs
  const [selectedPrompt, setPromptSelection] = useState(promptId); // via query parameter
  const [selectedContext, setSelectedContext] = useState("");
  const [selectedDocument, setSelectedDocument] = useState("");
  const [promptInput, setPromptInput] = useState("");
  const [imageDescription, setImageDescription] = useState("");

  // Chat state
  const [conversationStarted, setConversationStarted] = useState(false);
  const [chatSessionId, setChatSessionId] = useState();
  const [showChat, setShowChat] = useState(false);

  useEffect(() => setShowChat(false), []);

  const submitPromptToBackend = async (messages) => {
    if (conversationStarted !== true) {
      // start a new chat session with the selected prompt

      const userInput = messages[messages.length - 1];

      const requestData = {
        userinput: userInput?.content,
        promptid: selectedPrompt?.identifier,
        chatSessionId: chatSessionId,
        document: selectedDocument,
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
      setConversationStarted(true);
      setChatSessionId(response.headers.get("X-Chat-ID"));
      setShowChat(true);
      return response;
    } else {
      // continue chat session
      const lastMessage = messages[messages.length - 1];
      const response = await fetch("/api/prompt", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          userinput: lastMessage?.content,
          chatSessionId: chatSessionId,
        }),
      });
      return response;
    }
  };

  function handlePromptSelection(value) {
    const selectedPrompt = prompts.find(
      (prompt) => prompt.identifier === value,
    );
    setPromptSelection(selectedPrompt);
  }

  const handleContextSelection = (value) => {
    setSelectedContext(value);
  };

  useEffect(() => {
    handlePromptSelection(promptId);
  }, [promptId, prompts]);

  const startNewChat = async () => {
    if (chatRef.current) {
      // the ProChat controls the flow - let it know we have a new message,
      // the ultimate request will come back to "onSubmitPrompt" function here
      setChatSessionId(undefined);
      setConversationStarted(false);

      let userInput = promptInput;
      if (imageDescription && imageDescription !== "") {
        userInput += "\n\n" + imageDescription;
      }
      chatRef.current.startNewConversation(userInput);
    }
  };

  const imageDescriptionUserInput = showImageDescription ? (
    <div className="user-input">
      <p>
        Add image description
        <HelpTooltip text="Get an AI diagram description to help with your input. You can edit this description before you start the chat." />
      </p>
      <DescribeImage onImageDescriptionChange={setImageDescription} />
      {imageDescription && <TextArea value={imageDescription} rows={6} />}
    </div>
  ) : (
    <></>
  );

  const documentChoiceUserInput =
    showDocuments && documents ? (
      <div className="user-input">
        <p>
          Document
          <HelpTooltip text="Select a document from your knowledge pack that might have useful information for your context. Haiven will try to find useful information in this document during the first chat interaction." />
        </p>
        <Select
          onChange={setSelectedDocument}
          style={{ width: 300 }}
          options={documents}
          value={selectedDocument?.key}
        ></Select>
      </div>
    ) : (
      <></>
    );

  const textSnippetsUserInput =
    showTextSnippets && contexts ? (
      <div className="user-input">
        <p>
          Text snippets
          <HelpTooltip text="You can define text snippets describing your domain and architecture in your knowledge pack, and pull them into the prompt here." />
        </p>
        <Select
          onChange={handleContextSelection}
          style={{ width: 300 }}
          options={contexts}
          value={selectedContext?.key}
          defaultValue="base"
        ></Select>
      </div>
    ) : (
      <></>
    );

  const contextSection =
    showTextSnippets || showDocuments ? (
      <div className="prompt-chat-options-section">
        <div>
          <h2>{selectedPrompt ? "Add context" : ""}</h2>
        </div>
        <div>
          {textSnippetsUserInput}
          {documentChoiceUserInput}
        </div>
      </div>
    ) : (
      <></>
    );

  const prompt_options = (
    <div className="prompt-chat-options-container">
      <div className="prompt-chat-options-section">
        <h1>
          {selectedPrompt?.title || pageTitle}
          <HelpTooltip text="This prompt comes from the connected knowledge pack, where you can customize it if you don't like the results." />
        </h1>

        <p>{selectedPrompt?.help_prompt_description || pageIntro}</p>
      </div>

      <div className="prompt-chat-options-section">
        <div>
          <h2>{selectedPrompt ? "Your input" : "What is your question?"}</h2>
          <div className="user-input">{selectedPrompt?.help_user_input}</div>

          <div className="user-input">
            <TextArea
              value={promptInput}
              rows={4}
              onChange={(e, v) => {
                setPromptInput(e.target.value);
              }}
            />
          </div>
          {imageDescriptionUserInput}
        </div>
      </div>
      {contextSection}
      <div className="prompt-chat-options-section">
        <Button type="primary" onClick={startNewChat} className="go-button">
          START CHAT
        </Button>
      </div>
    </div>
  );

  return (
    <>
      <div className="prompt-chat-container">
        {prompt_options}

        <ProChatProvider>
          <ChatWidget
            onSubmitMessage={submitPromptToBackend}
            ref={chatRef}
            visible={showChat}
            helloMessage={"Fill in some input on the left and hit 'Generate'"}
          />
        </ProChatProvider>
      </div>
    </>
  );
};

export default PromptChat;
