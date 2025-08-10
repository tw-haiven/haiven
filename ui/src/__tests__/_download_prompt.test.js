// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, beforeEach, vi } from "vitest";
import DownloadPrompt from "../app/_download_prompt";
import "@testing-library/jest-dom";

// Mock the fetchPromptContent function
vi.mock("../app/utils/promptDownloadUtils", () => ({
  fetchPromptContent: vi.fn(),
}));

describe("DownloadPrompt", () => {
  const mockPrompt = {
    identifier: "test-prompt",
    title: "Test Prompt Title",
    help_prompt_description: "Test description",
    content: "Test prompt content",
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders download button when prompt is not download restricted", () => {
    const unrestrictedPrompt = {
      ...mockPrompt,
      download_restricted: false,
    };

    render(<DownloadPrompt prompt={unrestrictedPrompt} />);

    expect(screen.getByTestId("download-prompt-button")).toBeInTheDocument();
  });

  it("hides download button when prompt is download restricted", () => {
    const restrictedPrompt = {
      ...mockPrompt,
      download_restricted: true,
    };

    const { container } = render(<DownloadPrompt prompt={restrictedPrompt} />);

    expect(container.firstChild).toBeNull();
  });

  it("shows download button when download_restricted field is not present", () => {
    const promptWithoutRestrictionField = {
      ...mockPrompt,
      // No download_restricted field
    };

    render(<DownloadPrompt prompt={promptWithoutRestrictionField} />);

    expect(screen.getByTestId("download-prompt-button")).toBeInTheDocument();
  });

  it("returns null when prompt is null", () => {
    const { container } = render(<DownloadPrompt prompt={null} />);

    expect(container.firstChild).toBeNull();
  });

  // Test that the download button is clickable (basic functionality test)
  it("download button is clickable", () => {
    const unrestrictedPrompt = {
      ...mockPrompt,
      download_restricted: false,
    };

    render(<DownloadPrompt prompt={unrestrictedPrompt} />);

    const downloadButton = screen.getByTestId("download-prompt-button");
    expect(downloadButton).toBeInTheDocument();

    // Verify the button is clickable
    fireEvent.click(downloadButton);
    // If we get here without errors, the button is clickable
  });
});
