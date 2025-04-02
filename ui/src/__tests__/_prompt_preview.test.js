// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { render, screen, fireEvent } from "@testing-library/react";
import PromptPreview from "../app/_prompt_preview";
import { vi } from "vitest";

vi.mock("../app/_boba_api", () => ({
  getRenderedPrompt: vi.fn((requestData, callback) => {
    callback({ prompt: "Mock Rendered Prompt", template: "Mock Template" });
  }),
}));

beforeAll(() => {
  global.getComputedStyle = vi.fn(() => ({}));
});

describe("PromptPreview Component", () => {
  let mockRenderPromptRequest;

  beforeEach(() => {
    mockRenderPromptRequest = vi.fn(() => ({ mockData: true }));
  });

  it("displays 'No contexts selected.' when no contexts are chosen", async () => {
    render(
      <PromptPreview
        selectedContexts={[]}
        renderPromptRequest={mockRenderPromptRequest}
      />,
    );

    fireEvent.click(screen.getByTestId("prompt-preview-btn"));

    const textElement = await screen.findByText("No contexts selected.");
    expect(textElement).toBeInTheDocument();
  });

  it("displays selected contexts correctly when contexts are provided", () => {
    const mockContexts = [
      { label: "Context A" },
      { label: "Context B" },
      { label: "Context C" },
    ];

    render(
      <PromptPreview
        selectedContexts={mockContexts}
        renderPromptRequest={mockRenderPromptRequest} // Mocked function
      />,
    );

    fireEvent.click(screen.getByTestId("prompt-preview-btn"));

    expect(
      screen.getByText("Contexts selected: Context A, Context B, Context C"),
    ).toBeInTheDocument();
  });
});
