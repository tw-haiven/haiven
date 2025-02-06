// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import PromptChat from "../app/_prompt_chat";

describe("PromptChat Component", () => {
  const mockPrompts = [
    {
      identifier: "1",
      title: "User person creation",
      help_user_input: "Help text for user person creation",
      help_prompt_description: "This is prompt decription tooltip",
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
      await screen.findByText(/This is prompt decription tooltip/i),
    ).toBeInTheDocument();
  });
});
