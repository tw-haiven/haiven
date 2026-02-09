// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import KnowledgePackPage from "../pages/knowledge";
import "@testing-library/jest-dom";

describe("Knowledge overview prompts section", () => {
  const prompts = [
    {
      identifier: "architecture-prompt",
      title: "Architecture Prompt",
      categories: ["architecture"],
      help_prompt_description: "Architecture prompt description",
      download_restricted: false,
    },
    {
      identifier: "coding-prompt",
      title: "Coding Prompt",
      categories: ["coding"],
      help_prompt_description: "Coding prompt description",
      download_restricted: false,
    },
  ];

  const renderKnowledgePage = (featureToggleConfig = {}) =>
    render(
      <KnowledgePackPage
        contexts={[]}
        documents={[]}
        prompts={prompts}
        rules={[]}
        featureToggleConfig={featureToggleConfig}
      />,
    );

  it("shows prompt categories with per-prompt actions", async () => {
    renderKnowledgePage();

    expect(screen.getByText("Prompts")).toBeInTheDocument();
    expect(screen.getByText("Architecture")).toBeInTheDocument();
    expect(screen.getByText("Coding")).toBeInTheDocument();

    expect(
      screen.getByTestId("download-category-architecture"),
    ).toBeInTheDocument();
    expect(screen.getByTestId("download-category-coding")).toBeInTheDocument();

    fireEvent.click(screen.getByText("Architecture"));

    expect(screen.getByText("Architecture Prompt")).toBeInTheDocument();
    expect(screen.getByTestId("prompt-preview-button")).toBeInTheDocument();
    expect(screen.getByTestId("download-prompt-button")).toBeInTheDocument();
  });
});
