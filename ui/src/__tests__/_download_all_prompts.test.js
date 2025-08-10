// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, beforeEach, vi } from "vitest";
import DownloadAllPrompts from "../app/_download_all_prompts";
import "@testing-library/jest-dom";

// Mock the fetchAllPromptsContents function
vi.mock("../app/utils/promptDownloadUtils", () => ({
  fetchAllPromptsContents: vi.fn(),
}));

describe("DownloadAllPrompts", () => {
  const mockPrompts = [
    {
      identifier: "prompt-1",
      title: "Prompt 1",
      categories: ["architecture"],
      download_restricted: false,
    },
    {
      identifier: "prompt-2",
      title: "Prompt 2",
      categories: ["architecture"],
      download_restricted: true, // This should be filtered out
    },
    {
      identifier: "prompt-3",
      title: "Prompt 3",
      categories: ["coding"],
      download_restricted: false,
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders download all prompts button", () => {
    render(<DownloadAllPrompts prompts={mockPrompts} />);

    expect(
      screen.getByTestId("download-all-prompts-button"),
    ).toBeInTheDocument();
  });

  it("download button is clickable", () => {
    render(<DownloadAllPrompts prompts={mockPrompts} />);

    const downloadButton = screen.getByTestId("download-all-prompts-button");
    expect(downloadButton).toBeInTheDocument();

    // Verify the button is clickable
    fireEvent.click(downloadButton);
    // If we get here without errors, the button is clickable
  });

  it("shows categories in dropdown when clicked", () => {
    render(<DownloadAllPrompts prompts={mockPrompts} />);

    const downloadButton = screen.getByTestId("download-all-prompts-button");
    fireEvent.click(downloadButton);

    // Should show categories that have downloadable prompts (with proper capitalization)
    expect(screen.getByText("Architecture")).toBeInTheDocument();
    expect(screen.getByText("Coding")).toBeInTheDocument();
  });

  it("shows download all prompts option", () => {
    render(<DownloadAllPrompts prompts={mockPrompts} />);

    const downloadButton = screen.getByTestId("download-all-prompts-button");
    fireEvent.click(downloadButton);

    // Should show the "All Prompts" option (not "Download All Prompts")
    expect(screen.getByText("All Prompts")).toBeInTheDocument();
  });
});
