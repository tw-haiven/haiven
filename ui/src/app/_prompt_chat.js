// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
"use client";
import { ProChatProvider } from "@ant-design/pro-chat";
import { useEffect, useState, useRef } from "react";
import { Input, Select, Button, message, Collapse } from "antd";

const { TextArea } = Input;
import ChatWidget from "./_chat";
import DescribeImage from "./_image_description";
import HelpTooltip from "./_help_tooltip";
import ContextChoice from "./_context_choice";
import ChatHeader from "../pages/_chat_header";
import PromptPreview from "./_prompt_preview";

const PromptChat = ({
  promptId,
  prompts,
  contexts,
  documents,
  models,
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
  const [imageDescription, setImageDescription] = useState("");

  // Chat state
  const [conversationStarted, setConversationStarted] = useState(false);
  const [chatSessionId, setChatSessionId] = useState(undefined);
  const [usePromptId, setUsePromptId] = useState(true);
  const [placeholder, setPlaceholder] = useState("");

  useEffect(() => {
    setUsePromptId(true);
  });

  const appendImageDescription = (userInput) => {
    if (imageDescription && imageDescription !== "") {
      userInput += "\n\n" + imageDescription;
    }
    return userInput;
  };

  const buildFirstChatRequestBody = (userInput) => {
    return {
      userinput: usePromptId ? appendImageDescription(userInput) : userInput,
      promptid: usePromptId ? selectedPrompt?.identifier : undefined,
      chatSessionId: chatSessionId,
      ...(selectedContext !== "base" && { context: selectedContext }),
      ...(selectedDocument !== "base" && { document: selectedDocument }),
    };
  };

  const startNewChat = async (userInput) => {
    if (chatRef.current) {
      setChatSessionId(undefined);
      setConversationStarted(false);
      chatRef.current.startNewConversation(userInput);
    }
  };

  const renderPromptRequest = () => {
    if (chatRef.current) {
      return buildFirstChatRequestBody(chatRef.current.prompt);
    }
  };

  const submitPromptToBackend = async (messages) => {
    const lastMessage = messages[messages.length - 1];
    let requestData;
    if (!conversationStarted) {
      requestData = buildFirstChatRequestBody(lastMessage?.content);
    } else {
      requestData = {
        userinput: lastMessage?.content,
        chatSessionId: chatSessionId,
        ...(selectedDocument !== "base" && { document: selectedDocument }),
      };
    }

    try {
      const response = await fetch("/api/prompt", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        const errorBody = await response.json();
        const detailedErrorMessage =
          errorBody.detail || "An unknown error occurred.";
        // Return error in the format that ChatWidget expects
        return `[ERROR]: ${detailedErrorMessage}`;
      }

      const chatId = response.headers.get("X-Chat-ID");
      setPlaceholder("");

      if (!conversationStarted) {
        setConversationStarted(true);
        setChatSessionId(chatId);
      }

      return response;
    } catch (error) {
      // Return error in the format that ChatWidget expects
      return `[ERROR]: ${error.message}`;
    }
  };

  function handlePromptSelection(value) {
    const selectedPrompt = prompts.find(
      (prompt) => prompt.identifier === value,
    );
    setPromptSelection(selectedPrompt);
    setPlaceholder(
      selectedPrompt && selectedPrompt.help_user_input
        ? selectedPrompt.help_user_input
        : pageIntro,
    );
  }

  const handleContextSelection = (value) => {
    setSelectedContext(value);
  };

  useEffect(() => {
    handlePromptSelection(promptId);
  }, [promptId, prompts]);

  const imageDescriptionUserInput = showImageDescription ? (
    <div className="user-input">
      <label>
        Upload image
        <HelpTooltip text="Get AI to describe an image (e.g. a diagram) to help with your input. You can edit this description before you start the chat." />
      </label>
      <DescribeImage
        onImageDescriptionChange={setImageDescription}
        imageDescription={imageDescription}
      />
    </div>
  ) : (
    <></>
  );

  const documentsMenu =
    showDocuments && documents ? (
      <div className="user-input">
        <label>
          Select document
          <HelpTooltip text="Select a document from your knowledge pack that might have useful information for your context. Haiven will try to find useful information in this document during the first chat interaction." />
        </label>
        <Select
          onChange={setSelectedDocument}
          options={documents}
          value={selectedDocument?.key}
          defaultValue={"base"}
        ></Select>
      </div>
    ) : (
      <></>
    );

  const contextsMenu = showTextSnippets ? (
    <ContextChoice
      onChange={handleContextSelection}
      contexts={contexts}
      value={selectedContext?.key}
    />
  ) : (
    <></>
  );

  const title = (
    <div className="title">
      <h3>
        {selectedPrompt?.title || pageTitle}
        <HelpTooltip
          text={
            selectedPrompt?.help_prompt_description ||
            "Ask general questions & document based queries"
          }
        />
      </h3>
    </div>
  );

  const promptPreview = showTextSnippets ? (
    <PromptPreview
      renderPromptRequest={renderPromptRequest}
      startNewChat={startNewChat}
      setUsePromptId={setUsePromptId}
    />
  ) : null;

  const advancedPromptingMenu = (
    <div className="prompting-dropdown-menu">
      {contextsMenu}
      {documentsMenu}
      {imageDescriptionUserInput}
    </div>
  );

  return (
    <>
      <div className="prompt-chat-container">
        <div className="chat-container-wrapper">
          <ChatHeader models={models} titleComponent={title} />
          <div className="chat-container">
            <h1 className="title-for-collapsed-panel">
              {selectedPrompt?.title || pageTitle}
            </h1>
            <div className="chat-widget-container">
              <ProChatProvider>
                <ChatWidget
                  onSubmitMessage={submitPromptToBackend}
                  ref={chatRef}
                  placeholder={placeholder}
                  promptPreviewComponent={promptPreview}
                  advancedPromptingMenu={advancedPromptingMenu}
                  conversationStarted={conversationStarted}
                />
              </ProChatProvider>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default PromptChat;
