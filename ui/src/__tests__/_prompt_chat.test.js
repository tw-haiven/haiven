// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { render, screen, fireEvent } from "@testing-library/react";
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
});

describe("PromptChat Component", () => {
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

  it("should render chat page Header with correct page title, disclaimer and prompt decsription tooltip", async () => {
    vitest.mock("@ant-design/pro-chat", () => ({
      __esModule: true,
      ProChat: () => {
        return <div></div>;
      },
      ProChatProvider: () => {
        return <div></div>;
      },
    }));

    render(
      <PromptChat
        promptId="1"
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

    expect(
      screen.getByRole("heading", { name: /User person creation/i }),
    ).toBeInTheDocument();
    expect(screen.getByText(/AI model/i)).toHaveTextContent(
      "AI model: c1 model | AI-generated content can be inaccurate—validate all important information. Do not include client confidential information or personal data in your inputs. Review our guidelines here.",
    );
    const pageTitleTooltip = screen.getByTestId("page-title-tooltip");
    expect(pageTitleTooltip).toBeInTheDocument();
    fireEvent.mouseOver(pageTitleTooltip.firstChild);
    expect(
      await screen.findByText(/This is prompt description tooltip/i),
    ).toBeInTheDocument();
  });

  it("should render chat area with all default elements", () => {
    vitest.mock("@ant-design/pro-chat", async (importOriginal) => {
      const actual = await importOriginal();
      return {
        ...actual,

        useProChat: vi.fn().mockReturnValue({
          clearMessage: vi.fn(),
          sendMessage: vi.fn(),
          resendMessage: vi.fn(),
          deleteMessage: vi.fn(),
          setMessageContent: vi.fn(),
          stopGenerateMessage: vi.fn(),
          getChatMessages: vi.fn().mockReturnValue([]),
        }),
      };
    });

    render(
      <PromptChat
        promptId="1"
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
    expect(
      screen.getByPlaceholderText("Help text for user person creation"),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Let me help you with your task!"),
    ).toBeInTheDocument();
    expect(screen.getByText("Attach more context")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "SEND" })).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "View/Edit Prompt" }),
    ).toBeInTheDocument();
    expect(screen.getByTestId("pin-action")).toBeInTheDocument();
    expect(screen.getByTestId("copy-action")).toBeInTheDocument();
    expect(screen.getByTestId("regenerate-action")).toBeInTheDocument();
    expect(screen.getByTestId("delete-action")).toBeInTheDocument();
  });

  //TODO:
  //test for checking chat actions are working correctly
  //test to check if llm response is rendered correctly
  //test if advanced prompting works correctly
});
