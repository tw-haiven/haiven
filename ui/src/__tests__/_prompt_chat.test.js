// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { act } from "react";
import PromptChat from "../app/_prompt_chat";
import { describe, it, expect, vi, afterEach } from "vitest";

describe("PromptChat Component", () => {
  const mockPrompts = [
    {
      identifier: "1",
      title: "User person creation",
      help_prompt_description: "Help description",
      help_user_input: "Help input",
    },
    { identifier: "2", title: "Contract Test Generation" },
  ];
  const mockContexts = [
    { key: "base", label: "Base Context" },
    { key: "context1", label: "Context 1" },
  ];
  const mockDocuments = [
    { key: "doc1", label: "Document 1" },
    { key: "doc2", label: "Document 2" },
  ];
  const mockModels = [
    {
      chat: "Chat Model",
      vision: "Vision Model ",
      embeddings: "Embeddings Model",
    },
  ];

  // TODO: Write tests for the PromptChat component after refactoring
  it("should render the default user input fields and options when no prompt is selected", async () => {
    vitest.mock("@ant-design/pro-chat", () => ({
      __esModule: true,
      ProChat: () => {
        return <div></div>;
      },
      ProChatProvider: () => {
        return <div></div>;
      },
    }));

    await act(async () => {
      render(
        <PromptChat
          promptId=""
          prompts={mockPrompts}
          contexts={mockContexts}
          documents={mockDocuments}
          models={mockModels}
          pageTitle="Default Title"
          pageIntro="Default Intro"
          headerTooltip={true}
        />,
      );
    });

    // const startChatButton = screen.getByText(/SEND/i);

    // expect(screen.getAllByText(/Default Title/i)[0]).toBeInTheDocument();
    // expect(screen.getByPlaceholderText(/Default Intro/i)).toBeInTheDocument();
    // expect(screen.getByText(/Upload image/i)).toBeInTheDocument();
    // expect(startChatButton).toBeInTheDocument();
  });
});
