// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
"use client";
import { ProChatProvider } from "@ant-design/pro-chat";
import { useEffect, useState, useRef } from "react";
import { Input, Select } from "antd";
import { toast } from "react-toastify";
import { DownOutlined } from "@ant-design/icons";

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
import DownloadPrompt from "./_download_prompt";
import LLMTokenUsage from "./_llm_token_usage";
import { formattedUsage } from "../app/utils/tokenUtils";

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
  featureToggleConfig = {},
}) => {
  const chatRef = useRef();

  // User inputs
  const [selectedPrompt, setPromptSelection] = useState(promptId); // via query parameter
  const [selectedContexts, setSelectedContexts] = useState([]);
  const [selectedDocuments, setSelectedDocuments] = useState([]);
  const [imageDescription, setImageDescription] = useState("");
  const [userInput, setUserInput] = useState(initialInput);

  // Chat state
  const [conversationStarted, setConversationStarted] = useState(false);
  const [chatSessionId, setChatSessionId] = useState(undefined);
  const [usePromptId, setUsePromptId] = useState(true);
  const [placeholder, setPlaceholder] = useState("");
  const [allContexts, setAllContexts] = useState([]);
  const [tokenUsage, setTokenUsage] = useState(null);

  const MAX_COUNT = 3;
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

    const handleStorageChange = () => {
      combineAllContexts(contexts);
    };

    window.addEventListener("update-context", handleStorageChange);

    return () => {
      window.removeEventListener("update-context", handleStorageChange);
    };
  }, [initialInput, contexts]);

  const appendImageDescription = (userInput) => {
    if (imageDescription && imageDescription !== "") {
      userInput += "\n\n" + imageDescription;
    }
    return userInput;
  };

  const attachContextsToRequestBody = (requestBody) => {
    const userContextsSummary = selectedContexts
      .filter((context) => context.isUserDefined)
      .map((context) => getSummaryForTheUserContext(context.value))
      .join("\n\n");

    const knowledgePackContexts = selectedContexts
      .map((context) => (!context.isUserDefined ? context.value : null))
      .filter((value) => value !== null);

    if (userContextsSummary !== "") {
      requestBody.userContext = userContextsSummary;
    }
    if (knowledgePackContexts.length > 0) {
      requestBody.contexts = knowledgePackContexts;
    }
    return requestBody;
  };

  const buildFirstChatRequestBody = (userInput) => {
    const requestBody = {
      userinput: usePromptId ? appendImageDescription(userInput) : userInput,
      promptid: usePromptId ? selectedPrompt?.identifier : undefined,
      chatSessionId: chatSessionId,
      document: selectedDocuments,
    };
    attachContextsToRequestBody(requestBody);
    return requestBody;
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

    // Reset token usage when starting new request
    setTokenUsage(null);

    let requestBody;
    if (!conversationStarted) {
      requestBody = buildFirstChatRequestBody(lastMessage?.content);
    } else {
      requestBody = {
        userinput: lastMessage?.content,
        chatSessionId: chatSessionId,
        ...(selectedDocuments !== "base" && { document: selectedDocuments }),
      };
    }

    try {
      const response = await fetch("/api/prompt", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorBody = await response.json();
        const detailedErrorMessage =
          errorBody.detail || "An unknown error occurred.";
        throw new Error(`ERROR: ${detailedErrorMessage}`);
      }

      const chatId = response.headers.get("X-Chat-ID");
      setPlaceholder("");

      if (!conversationStarted) {
        setConversationStarted(true);
        setChatSessionId(chatId);
      }

      // Create a stream that filters out token usage events and extracts clean content for ProChat
      const sseStream = new ReadableStream({
        start(controller) {
          const reader = response.body.getReader();
          const decoder = new TextDecoder();
          let buffer = "";

          function pump() {
            return reader.read().then(({ done, value }) => {
              if (done) {
                controller.close();
                return;
              }

              const chunk = decoder.decode(value, { stream: true });
              buffer += chunk;

              // Check if this chunk contains SSE token usage event
              if (buffer.includes("event: token_usage")) {
                // Split at the SSE event boundary
                const parts = buffer.split("event: token_usage");
                const contentPart = parts[0];
                const sseEventPart = "event: token_usage" + parts[1];

                // Send content part to ProChat
                if (contentPart) {
                  controller.enqueue(new TextEncoder().encode(contentPart));
                }

                // Parse token usage from SSE event
                const lines = sseEventPart.split("\n");
                for (const line of lines) {
                  if (line.startsWith("data: ")) {
                    const data = line.substring(6);

                    // Handle token usage
                    try {
                      const tokenUsageData = JSON.parse(data);
                      setTokenUsage(formattedUsage(tokenUsageData));
                    } catch (parseError) {
                      console.log(
                        "Failed to parse token usage data:",
                        data,
                        parseError,
                      );
                    }
                    break;
                  }
                }

                buffer = "";
              } else {
                // Regular content - stream directly to ProChat
                controller.enqueue(new TextEncoder().encode(chunk));
                buffer = "";
              }

              return pump();
            });
          }

          return pump();
        },
      });

      // Return new response with filtered stream
      return new Response(sseStream, {
        status: response.status,
        statusText: response.statusText,
        headers: response.headers,
      });
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

  const handleContextSelection = (values) => {
    const userSelectedContexts = allContexts.filter((context) =>
      values.includes(context.value),
    );
    setSelectedContexts(userSelectedContexts);
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

  const dropdownSuffix = (
    <>
      <span>
        {selectedDocuments.length} / {MAX_COUNT}
      </span>
      <DownOutlined />
    </>
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
          onChange={setSelectedDocuments}
          options={documents}
          mode="multiple"
          maxCount={MAX_COUNT}
          placeholder="Please select the document(s)"
          suffixIcon={dropdownSuffix}
          data-testid="document-select"
        ></Select>
      </div>
    ) : (
      <></>
    );

  const contextsMenu = showTextSnippets ? (
    <ContextChoice
      onChange={handleContextSelection}
      selectedContexts={selectedContexts}
      contexts={allContexts}
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
          testid="page-title-tooltip"
        />
      </h3>
      {selectedPrompt && <DownloadPrompt prompt={selectedPrompt} />}
      <LLMTokenUsage
        tokenUsage={tokenUsage}
        featureToggleConfig={featureToggleConfig}
      />
    </div>
  );

  const promptPreview = showTextSnippets ? (
    <PromptPreview
      selectedContexts={selectedContexts}
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
