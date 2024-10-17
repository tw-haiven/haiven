// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
"use client";
import { ProChatProvider } from "@ant-design/pro-chat";
import { useEffect, useState, useRef } from "react";
import { Input, Select, Button, message } from "antd";

const { TextArea } = Input;
import ChatWidget from "./_chat";
import DescribeImage from "./_image_description";
import HelpTooltip from "./_help_tooltip";
import ContextChoice from "./_context_choice";
import Disclaimer from "../pages/_disclaimer";
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
  const [promptInput, setPromptInput] = useState("");
  const [imageDescription, setImageDescription] = useState("");

  // Chat state
  const [conversationStarted, setConversationStarted] = useState(false);
  const [chatSessionId, setChatSessionId] = useState();
  const [showChat, setShowChat] = useState(false);

  // Rendered prompt
  const [renderedPromptData, setRenderedPromptData] = useState({});
  const [showRenderedPrompt, setShowRenderedPrompt] = useState(false);

  useEffect(() => setShowChat(false), []);

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
      promptid: selectedPrompt?.identifier,
      chatSessionId: chatSessionId,
      ...(selectedContext !== "base" && { context: selectedContext }),
      ...(selectedDocument !== "base" && { document: selectedDocument }),
    };
  };

  const startNewChat = async () => {
    if (chatRef.current) {
      // the ProChat controls the flow - let it know we have a new message,
      // the ultimate request will come back to "submitPromptToBackend" function here
      setChatSessionId(undefined);
      setConversationStarted(false);

      let userInput = buildUserInput();
      chatRef.current.startNewConversation(userInput);
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
        const errorMessage = `Error: ${response.status} - ${response.statusText}`;
        throw new Error(errorMessage);
      }

      const chatId = response.headers.get("X-Chat-ID");

      if (!conversationStarted) {
        setConversationStarted(true);
        setChatSessionId(chatId);
        setShowChat(true);
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
  }

  const handleContextSelection = (value) => {
    setSelectedContext(value);
  };

  const buildRenderPromptRequest = () => {
    return buildRequestBody(buildUserInput());
  };

  useEffect(() => {
    handlePromptSelection(promptId);
  }, [promptId, prompts]);

  const imageDescriptionUserInput = showImageDescription ? (
    <div className="user-input">
      <label>
        Upload an image
        <HelpTooltip text="Get an AI diagram description to help with your input. You can edit this description before you start the chat." />
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

  const prompt_options = (
    <div className="prompt-chat-options-container">
      <div className="prompt-chat-options-section">
        <h1>
          {selectedPrompt?.title || pageTitle}
          <HelpTooltip text="This prompt comes from the connected knowledge pack, where you can customize it if you don't like the results." />
        </h1>

        <div>{selectedPrompt?.help_prompt_description}</div>
      </div>

      <div className="prompt-chat-options-section">
        <div>
          <div className="user-input">
            <label>
              {selectedPrompt ? "Your input" : "What do you want help with?"}
              <HelpTooltip
                text={selectedPrompt?.help_user_input || pageIntro}
              />
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
          <PromptPreview buildRenderPromptRequest={buildRenderPromptRequest} />
        )}
        <Button onClick={startNewChat} className="go-button">
          START CHAT
        </Button>
      </div>
    </div>
  );

  return (
    <>
      <div className="prompt-chat-container">
        {prompt_options}
        <div
          style={{ height: "100%", display: "flex", flexDirection: "column" }}
        >
          <Disclaimer models={models} />
          <div style={{ height: "95%" }}>
            <ProChatProvider>
              <ChatWidget
                onSubmitMessage={submitPromptToBackend}
                ref={chatRef}
                visible={showChat}
                helloMessage={
                  "Fill in some input on the left and hit 'Generate'"
                }
              />
            </ProChatProvider>
          </div>
        </div>
      </div>
    </>
  );
};

export default PromptChat;
