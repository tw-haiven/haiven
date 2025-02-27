// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import PromptChat from "../app/_prompt_chat";

beforeEach(() => {
  vitest.clearAllMocks();

  Object.defineProperty(window, "matchMedia", {
    writable: true,
    value: vi.fn().mockImplementation((query) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });
  Element.prototype.scrollTo = () => {};
});

describe("PromptChat Component", () => {
  const verifyTooltip = async (testId, tooltipText) => {
    const tooltipElement = screen.getByTestId(testId);
    expect(tooltipElement).toBeInTheDocument();
    fireEvent.mouseOver(tooltipElement.firstChild);
    expect(await screen.findByText(tooltipText)).toBeInTheDocument();
  };

  const someUserInput = "Here is my prompt input";

  const givenUserInput = () => {
    const inputField = screen.getByTestId("chat-user-input");
    fireEvent.change(inputField, { target: { value: someUserInput } });
  };

  const mockPrompts = [
    {
      identifier: "1",
      title: "User person creation",
      help_user_input: "Help text for user person creation",
      help_sample_input: "Sample input for the prompt",
      help_prompt_description: "This is prompt description tooltip",
    },
    { identifier: "2", title: "Contract Test Generation" },
  ];

  const mockContexts = [
    { key: "base", label: "Base Context" },
    { key: "context1", label: "Context 1" },
    { key: "context2", label: "Context 2" },
  ];

  const mockDocuments = [
    { key: "doc1", label: "Document 1" },
    { key: "doc2", label: "Document 2" },
  ];

  const mockModels = {
    chat: {
      id: "c1",
      name: "c1 model",
    },
    vision: {
      id: "v1",
      name: "v1 model ",
    },
    embeddings: {
      id: "e1",
      name: "e1 model",
    },
  };

  const verifyChatAreaHeader = async () => {
    expect(
      screen.getByRole("heading", { name: /User person creation/i }),
    ).toBeInTheDocument();
    expect(screen.getByText(/AI model/i)).toHaveTextContent(
      "AI model: c1 model | AI-generated content can be inaccurate—validate all important information. Do not include client confidential information or personal data in your inputs. Review our guidelines here.",
    );
    await verifyTooltip(
      "page-title-tooltip",
      "This is prompt description tooltip",
    );
  };

  const verifyChatAreaDefaultComponents = () => {
    expect(
      screen.getByText("Let me help you with your task!"),
    ).toBeInTheDocument();
    expect(screen.getByTestId("pin-action")).toBeInTheDocument();
    expect(screen.getByTestId("copy-action")).toBeInTheDocument();
    expect(screen.getByTestId("regenerate-action")).toBeInTheDocument();
    expect(screen.getByTestId("delete-action")).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText("Help text for user person creation"),
    ).toBeInTheDocument();
    expect(screen.getByText("Attach more context")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "SEND" })).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "View/Edit Prompt" }),
    ).toBeInTheDocument();
  };

  const verifyAdvancedPromptOptions = async () => {
    const advancedPromptLink = screen.getByText("Attach more context");
    fireEvent.click(advancedPromptLink);

    //context
    expect(screen.getByText("Add your context")).toBeInTheDocument();
    expect(screen.getByTestId("context-select")).toBeInTheDocument();
    await verifyTooltip(
      "context-selection-tooltip",
      "Choose a context from your knowledge pack that is relevant to the domain, architecture, or team you are working on.",
    );

    //document
    expect(screen.getByText("Select document")).toBeInTheDocument();
    await verifyTooltip(
      "document-selection-tooltip",
      "Select a document from your knowledge pack that might have useful information for your context. Haiven will try to find useful information in this document during the first chat interaction.",
    );

    //image description
    expect(screen.getByText("Upload image")).toBeInTheDocument();
    await verifyTooltip(
      "upload-image-tooltip",
      "Get AI to describe an image (e.g. a diagram) to help with your input. You can edit this description before you start the chat.",
    );
    screen.getByText("Only JPEG/JPG/PNG types are allowed.");
  };

  const setupFetchMock = (mockResponse = "sample response") => {
    function createMockStream(data) {
      const encoder = new TextEncoder();
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(encoder.encode(data));
          controller.close();
        },
      });
      return stream;
    }

    const fetchMock = vi.fn(async (url, options) =>
      Promise.resolve({
        ok: true,
        status: 200,
        statusText: "OK",
        body: createMockStream(mockResponse),
        headers: {
          get: (header) => (header === "X-Chat-Id" ? "c1" : null),
        },
        clone: () => ({
          json: async () => mockResponse,
        }),
      }),
    );

    vi.stubGlobal("fetch", fetchMock);
    return fetchMock;
  };

  it("should render chat area Header with correct page title, disclaimer and prompt description tooltip", async () => {
    render(
      <PromptChat
        promptId={mockPrompts[0].identifier}
        prompts={mockPrompts}
        contexts={mockContexts}
        documents={mockDocuments}
        showImageDescription={true}
        showTextSnippets={true}
        showDocuments={true}
        models={mockModels}
        pageTitle="Test Page Title"
        pageIntro="Test Page Intro"
      />,
    );

    await verifyChatAreaHeader(verifyTooltip);
    verifyChatAreaDefaultComponents();
    await verifyAdvancedPromptOptions(verifyTooltip);
  });

  it("should fetch prompt response for given user input with the selected options", async () => {
    const mockResponse = "Sample response from LLM";
    const fetchMock = setupFetchMock(mockResponse);

    render(
      <PromptChat
        promptId={mockPrompts[0].identifier}
        prompts={mockPrompts}
        contexts={mockContexts}
        documents={mockDocuments}
        showImageDescription={true}
        showTextSnippets={true}
        showDocuments={true}
        models={mockModels}
        pageTitle="Test Page Title"
        pageIntro="Test Page Intro"
      />,
    );

    const advancedPromptLink = screen.getByText("Attach more context");
    fireEvent.click(advancedPromptLink);

    givenUserInput();

    const sendButton = screen.getByRole("button", { name: "SEND" });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith("/api/prompt", expect.any(Object));
      const fetchOptions = fetchMock.mock.calls[0][1];
      expect(fetchOptions.method).toBe("POST");
      expect(fetchOptions.headers["Content-Type"]).toBe("application/json");
      expect(fetchOptions.body).toBe(
        JSON.stringify({
          userinput: "Here is my prompt input",
          promptid: "1",
          chatSessionId: undefined,
          context: "",
          document: "",
        }),
      );
      expect(screen.getByText(mockResponse)).toBeInTheDocument();
    });
  });

  //TODO:
  //test for checking chat actions are working correctly
  //select the context, document and image description and fetch response accordingly
});
