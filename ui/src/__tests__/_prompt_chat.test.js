// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import {
  render,
  screen,
  fireEvent,
  waitFor,
  within,
} from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import PromptChat from "../app/_prompt_chat";
import { fetchSSE } from "../app/_fetch_sse";
import { saveContext } from "../app/_local_store";
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => {
      store[key] = value.toString();
    },
    clear: () => {
      store = {};
    },
  };
})();

Object.defineProperty(window, "localStorage", {
  value: localStorageMock,
});

vi.mock("../app/_fetch_sse");

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
  const imageText = "Mocked image description";

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
    { value: "context1", label: "Context 1" },
    { value: "context2", label: "Context 2" },
  ];

  const mockDocuments = [
    { value: "document1", label: "Document 1" },
    { value: "document2", label: "Document 2" },
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
    expect(screen.getByTestId("context-select")).toBeInTheDocument();

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

  async function selectDocument() {
    const documentDropdown = screen.getByTestId("document-select").firstChild;
    fireEvent.mouseDown(documentDropdown);
    const selectedDocument = await screen.findByText("Document 1");
    fireEvent.click(selectedDocument);
  }

  async function selectContext(contextTitle) {
    const contextDropdown = screen.getByTestId("context-select").firstChild;
    fireEvent.mouseDown(contextDropdown);
    const selectedContext = await screen.findByText(contextTitle);
    fireEvent.click(selectedContext);
  }

  function clickAdvancedPrompt() {
    const advancedPromptLink = screen.getByText("Attach more context");
    fireEvent.click(advancedPromptLink);
  }

  async function uploadImage() {
    const file = new File([imageText], "test-image.png", { type: "image/png" });

    const input = screen
      .getByRole("button", {
        name: /upload/i,
      })
      .parentNode.querySelector("input");
    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() =>
      expect(screen.queryByText("View/Edit Description")).not.toBeNull(),
    );
  }

  function verifyPromptPreview() {
    const promptPreviewLink = screen.getByText("View/Edit Prompt");
    expect(promptPreviewLink).toBeInTheDocument();
  }

  function verifySampleInput() {
    const sampleInputLink = screen.getByText("Sample Input");
    expect(sampleInputLink).toBeInTheDocument();
    fireEvent.click(sampleInputLink);
    expect(
      screen.getByText(mockPrompts[0].help_sample_input),
    ).toBeInTheDocument();
  }

  function setUpUserContexts() {
    vi.useFakeTimers();

    vi.setSystemTime(new Date("2025-03-28T12:00:00.000Z"));
    saveContext("User Context 1", "User Context 1 description");

    vi.setSystemTime(new Date("2025-03-28T12:00:00.005Z"));
    saveContext("User Context 2", "User Context 2 description");

    vi.useRealTimers();
  }

  it("should render chat area with initial components", async () => {
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
    verifySampleInput();
    verifyPromptPreview();
  });

  it("should fetch prompt response for given user input with the selected options", async () => {
    const mockResponse = "Sample response from LLM";
    const fetchMock = setupFetchMock(mockResponse);

    fetchSSE.mockImplementation((url, options, eventHandlers) => {
      expect(url).toBe("/api/prompt/image");
      eventHandlers.onMessageHandle(imageText);
      eventHandlers.onFinish();
    });

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

    clickAdvancedPrompt();
    await selectContext("Context 1");
    await selectContext("Context 2");
    await selectDocument();
    uploadImage();
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
          userinput: "Here is my prompt input\n\nMocked image description",
          promptid: "1",
          chatSessionId: undefined,
          document: "document1",
          contexts: ["context1", "context2"],
        }),
      );
      expect(screen.getByText(mockResponse)).toBeInTheDocument();
    });
  });

  it("should fetch chat response for multiple contexts which includes knowledge pack contexts and user contexts", async () => {
    setUpUserContexts();
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

    clickAdvancedPrompt();
    const contextDropdown = screen.getByTestId("context-select").firstChild;
    fireEvent.mouseDown(contextDropdown);

    await selectContext("User Context 1");
    await selectContext("User Context 2");
    await selectContext("Context 1");
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
          document: "",
          userContext:
            "User Context 2 description\n\nUser Context 1 description",
          contexts: ["context1"],
        }),
      );
      expect(screen.getByText(mockResponse)).toBeInTheDocument();
    });
  });

  //TODO:
  //test for checking chat actions are working correctly
  //test edit prompt
});
