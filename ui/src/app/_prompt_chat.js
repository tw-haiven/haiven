// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
"use client";
import { ProChatProvider } from "@ant-design/pro-chat";
import { useEffect, useState, useRef } from "react";
import { Input, Select, Button, message, Collapse } from "antd";
import { MenuFoldOutlined } from "@ant-design/icons";

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
  headerTooltip = true,
  inputTooltip = true,
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
  const [isExpanded, setIsExpanded] = useState(true);
  const [usePromptId, setUsePromptId] = useState(true);
  const [placeholder, setPlaceholder] = useState("");

  useEffect(() => {
    setUsePromptId(true);
  });

  const buildUserInput = () => {
    let userInput = promptInput;
    if (imageDescription && imageDescription !== "") {
      userInput += "\n\n" + imageDescription;
    }
    return userInput;
  };

  const buildRequestBody = (userInput) => {
    return {
      userinput: userInput,
      promptid: usePromptId ? selectedPrompt?.identifier : undefined,
      chatSessionId: chatSessionId,
      ...(selectedContext !== "base" && { context: selectedContext }),
      ...(selectedDocument !== "base" && { document: selectedDocument }),
    };
  };

  const startNewChat = async (userInput = null) => {
    if (chatRef.current) {
      // the ProChat controls the flow - let it know we have a new message,
      // the ultimate request will come back to "submitPromptToBackend" function here
      setChatSessionId(undefined);
      setConversationStarted(false);
      if (!userInput) {
        userInput = buildUserInput();
      }
      chatRef.current.startNewConversation(userInput);
      setIsExpanded(false);
    }
  };

  const submitPromptToBackend = async (messages) => {
    const lastMessage = messages[messages.length - 1];
    let requestData;
    if (!conversationStarted) {
      requestData = buildRequestBody(lastMessage?.content);
    } else {
      requestData = {
        userinput: lastMessage?.content,
        chatSessionId: chatSessionId,
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
        const errorMessage = `ERROR: ${detailedErrorMessage}`;

        throw new Error(errorMessage);
      }

      const chatId = response.headers.get("X-Chat-ID");
      setPlaceholder("");

      if (!conversationStarted) {
        setConversationStarted(true);
        setChatSessionId(chatId);
      }

      return response;
    } catch (error) {
      message.error(error.message);
    }
  };

  function handlePromptSelection(value) {
    const selectedPrompt = prompts.find(
      (prompt) => prompt.identifier === value,
    );
    setPromptSelection(selectedPrompt);
    setPlaceholder(selectedPrompt?.help_user_input || pageIntro);
  }

  const handleContextSelection = (value) => {
    setSelectedContext(value);
  };

  const buildRenderPromptRequest = () => {
    return buildRequestBody(buildUserInput());
  };

  const onCollapsibleIconClick = (e) => {
    setIsExpanded(!isExpanded);
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
      <DescribeImage onImageDescriptionChange={setImageDescription} />
      {imageDescription && <TextArea value={imageDescription} rows={6} />}
    </div>
  ) : (
    <></>
  );

  const documentChoiceUserInput =
    showDocuments && documents ? (
      <div className="user-input">
        <label>
          Document
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

  const textSnippetsUserInput = showTextSnippets ? (
    <ContextChoice
      onChange={handleContextSelection}
      contexts={contexts}
      value={selectedContext?.key}
    />
  ) : (
    <></>
  );

  const contextSection =
    showTextSnippets || showDocuments ? (
      <div className="prompt-chat-options-section">
        <div>
          {textSnippetsUserInput}
          {documentChoiceUserInput}
        </div>
      </div>
    ) : (
      <></>
    );

  const promptMenu = (
    <div>
      <div className="prompt-chat-options-section">
        <h1>
          {selectedPrompt?.title || pageTitle}
          {headerTooltip && (
            <HelpTooltip text="This prompt comes from the connected knowledge pack, where you can customize it if you don't like the results." />
          )}
        </h1>
        <div className={headerTooltip ? "" : "prompt-chat-description"}>
          {selectedPrompt?.help_prompt_description ||
            "Ask general questions & document based queries"}
        </div>
      </div>

      <div className="prompt-chat-options-section">
        <div>
          <div className="user-input">
            <label>
              Your input
              {inputTooltip && (
                <HelpTooltip
                  text={selectedPrompt?.help_user_input || pageIntro}
                />
              )}
            </label>

            <TextArea
              value={promptInput}
              style={{ width: "100%" }}
              placeholder={selectedPrompt?.help_user_input || pageIntro}
              rows={10}
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
        {showTextSnippets && (
          <PromptPreview
            buildRenderPromptRequest={buildRenderPromptRequest}
            startNewChat={startNewChat}
            setUsePromptId={setUsePromptId}
          />
        )}
        <Button onClick={() => startNewChat(null)} className="go-button">
          START CHAT
        </Button>
      </div>
    </div>
  );

  const collapseItem = [
    {
      key: "1",
      children: promptMenu,
    },
  ];

  return (
    <>
      <div className={`prompt-chat-container ${isExpanded ? "" : "collapsed"}`}>
        <Collapse
          className="prompt-chat-options-container"
          items={collapseItem}
          defaultActiveKey={["1"]}
          ghost={isExpanded}
          activeKey={isExpanded ? "1" : ""}
          onChange={onCollapsibleIconClick}
          expandIcon={() => <MenuFoldOutlined rotate={isExpanded ? 0 : 180} />}
        />
        <div className="chat-container-wrapper">
          <ChatHeader models={models} />
          <div className="chat-container">
            <h1 className="title-for-collapsed-panel">
              {selectedPrompt?.title || pageTitle}
            </h1>
            <div className="chat-widget-container">
              <ProChatProvider>
                <ChatWidget
                  onSubmitMessage={submitPromptToBackend}
                  ref={chatRef}
                  helloMessage={
                    "Fill in some input on the left and hit 'Generate'"
                  }
                  placeholder={placeholder}
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
