// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
"use client";
import { ProChatProvider } from "@ant-design/pro-chat";
import { useEffect, useState, useRef } from "react";
import { Input, Select, Button } from "antd";
import { toast } from "react-toastify";

const { TextArea } = Input;
import ChatWidget from "./_chat";
import DescribeImage from "./_image_description";
import HelpTooltip from "./_help_tooltip";
import ContextChoice from "./_context_choice";
import ChatHeader from "../pages/_chat_header";
import PromptPreview from "./_prompt_preview";
import {
  getSortedUserContexts,
  getSummaryForTheUserContext,
} from "./_local_store";

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
  initialInput = "",
}) => {
  const chatRef = useRef();

  // User inputs
  const [selectedPrompt, setPromptSelection] = useState(promptId); // via query parameter
  const [selectedContext, setSelectedContext] = useState("");
  const [selectedDocument, setSelectedDocument] = useState("");
  const [imageDescription, setImageDescription] = useState("");
  const [userInput, setUserInput] = useState(initialInput);

  // Chat state
  const [conversationStarted, setConversationStarted] = useState(false);
  const [chatSessionId, setChatSessionId] = useState(undefined);
  const [usePromptId, setUsePromptId] = useState(true);
  const [placeholder, setPlaceholder] = useState("");
  const [allContexts, setAllContexts] = useState([]);

  function combineAllContexts(contexts) {
    const userContexts = getSortedUserContexts();
    const userContextsForDropdown = userContexts.map((context) => ({
      value: context.title,
      label: context.title,
      isUserDefined: true,
    }));
    if (contexts !== undefined && contexts.length > 0) {
      setAllContexts(contexts.concat(userContextsForDropdown));
    } else {
      setAllContexts(userContextsForDropdown);
    }
  }

  useEffect(() => {
    if (initialInput && chatRef.current) {
      chatRef.current.setPromptValue(initialInput);
    }
    combineAllContexts(contexts);

    const handleStorageChange = (event) => {
      combineAllContexts(contexts);
    };

    window.addEventListener("new-context", handleStorageChange);

    return () => {
      window.removeEventListener("new-context", handleStorageChange);
    };
  }, [
    initialInput,
    contexts,
    typeof window !== "undefined"
      ? window.localStorage.getItem("context")
      : null,
  ]);

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
      ...(selectedContext.value !== "base" &&
        selectedContext.isUserDefined && {
          userContext: getSummaryForTheUserContext(selectedContext.value),
        }),
      ...(selectedContext.value !== "base" &&
        !selectedContext.isUserDefined && { context: selectedContext.value }),
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
      toast.error(error.message);
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
    setSelectedContext(allContexts.find((context) => context.value === value));
  };

  useEffect(() => {
    handlePromptSelection(promptId);
  }, [promptId, prompts]);

  const imageDescriptionUserInput = showImageDescription ? (
    <div className="user-input">
      <label>
        Upload image
        <HelpTooltip
          text={
            <>
              <div>
                Get AI to describe an image (e.g. a diagram) to help with your
                input. You can edit this description before you start the chat.
              </div>
              Only JPEG/JPG/PNG types are allowed.
            </>
          }
          testid="upload-image-tooltip"
        />
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
          <HelpTooltip
            text="Select a document from your knowledge pack that might have useful information for your context. Haiven will try to find useful information in this document during the first chat interaction."
            testid="document-selection-tooltip"
          />
        </label>
        <Select
          onChange={setSelectedDocument}
          options={documents}
          value={selectedDocument?.key}
          defaultValue={"base"}
          data-testid="document-select"
        ></Select>
      </div>
    ) : (
      <></>
    );

  const contextsMenu = showTextSnippets ? (
    <ContextChoice onChange={handleContextSelection} contexts={allContexts} />
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
          testid="page-title-tooltip"
        />
      </h3>
    </div>
  );

  const promptPreview = showTextSnippets ? (
    <PromptPreview
      renderPromptRequest={renderPromptRequest}
      startNewChat={startNewChat}
      setUsePromptId={setUsePromptId}
      sampleInput={selectedPrompt?.help_sample_input}
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
