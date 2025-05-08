// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, beforeEach, vi } from "vitest";
import DownloadPrompt from "../app/_download_prompt";
import "@testing-library/jest-dom";

// Set up a test environment with a DOM
const setup = () => {
  const container = document.createElement("div");
  document.body.appendChild(container);
  return container;
};

describe.skip("DownloadPrompt", () => {
  const mockPrompt = {
    identifier: "test-prompt",
    title: "Test Prompt Title",
    help_prompt_description: "Test description",
    content: "Test prompt content",
  };

  beforeEach(() => {
    // Clear all mocks before each test
    vi.clearAllMocks();

    // Mock fetch
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            help_prompt_description: "Test description",
            content: "Test prompt content",
            help_sample_input: "Test sample input",
            follow_ups: [
              {
                title: "Follow Up 1",
                help_prompt_description: "Follow up description 1",
              },
            ],
          }),
      }),
    );

    // Mock URL and Blob
    global.URL.createObjectURL = vi.fn(() => "mock-url");
    global.URL.revokeObjectURL = vi.fn();
    global.Blob = vi.fn();

    // Mock document methods
    const mockLink = {
      href: "",
      download: "",
      click: vi.fn(),
    };
    document.createElement = vi.fn(() => mockLink);
    document.body.appendChild = vi.fn();
    document.body.removeChild = vi.fn();
  });

  it("renders download button with tooltip", () => {
    const { container } = render(<DownloadPrompt prompt={mockPrompt} />);
    expect(
      container.querySelector('[data-testid="download-prompt-button"]'),
    ).toBeTruthy();
  });

  it("handles download with all prompt data", async () => {
    const { container } = render(<DownloadPrompt prompt={mockPrompt} />);

    const downloadButton = container.querySelector(
      '[data-testid="download-prompt-button"]',
    );
    await fireEvent.click(downloadButton);

    // Wait for all promises to resolve
    await vi.waitFor(() => {
      // Verify fetch was called with correct parameters
      expect(global.fetch).toHaveBeenCalledWith(
        "/api/prompt/test-prompt",
        expect.objectContaining({
          method: "GET",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
        }),
      );
    });

    // Wait for blob creation and download
    await vi.waitFor(
      () => {
        // Verify blob creation with correct content
        expect(global.Blob).toHaveBeenCalledWith(
          [expect.stringContaining("Test description")],
          { type: "text/plain" },
        );

        // Verify URL creation and cleanup
        expect(global.URL.createObjectURL).toHaveBeenCalled();
        expect(document.createElement).toHaveBeenCalledWith("a");
        expect(document.body.appendChild).toHaveBeenCalled();
        expect(document.body.removeChild).toHaveBeenCalled();
        expect(global.URL.revokeObjectURL).toHaveBeenCalledWith("mock-url");
      },
      { timeout: 1000 },
    );
  });

  it("handles download with sample input", async () => {
    const { container } = render(<DownloadPrompt prompt={mockPrompt} />);

    const downloadButton = container.querySelector(
      '[data-testid="download-prompt-button"]',
    );
    await fireEvent.click(downloadButton);

    // Verify blob content includes sample input
    await vi.waitFor(() => {
      expect(global.Blob).toHaveBeenCalledWith(
        [expect.stringContaining("Sample Input: Test sample input")],
        { type: "text/plain" },
      );
    });
  });

  it("handles download with follow-up prompts", async () => {
    const { container } = render(<DownloadPrompt prompt={mockPrompt} />);

    const downloadButton = container.querySelector(
      '[data-testid="download-prompt-button"]',
    );
    await fireEvent.click(downloadButton);

    // Verify blob content includes follow-up prompts
    await vi.waitFor(() => {
      expect(global.Blob).toHaveBeenCalledWith(
        [expect.stringContaining("Follow-up Prompts")],
        { type: "text/plain" },
      );
      expect(global.Blob).toHaveBeenCalledWith(
        [expect.stringContaining("1. Follow Up 1")],
        { type: "text/plain" },
      );
    });
  });

  it("handles fetch error gracefully", async () => {
    // Mock fetch to fail
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: false,
      }),
    );

    // Mock console.error
    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    const { container } = render(<DownloadPrompt prompt={mockPrompt} />);

    const downloadButton = container.querySelector(
      '[data-testid="download-prompt-button"]',
    );
    await fireEvent.click(downloadButton);

    await vi.waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith(
        "Error downloading prompt:",
        expect.any(Error),
      );
    });

    consoleSpy.mockRestore();
  });

  it("does nothing when prompt is not provided", async () => {
    const { container } = render(<DownloadPrompt prompt={null} />);

    const downloadButton = container.querySelector(
      '[data-testid="download-prompt-button"]',
    );
    await fireEvent.click(downloadButton);

    await vi.waitFor(() => {
      expect(global.fetch).not.toHaveBeenCalled();
      expect(global.Blob).not.toHaveBeenCalled();
    });
  });
});
