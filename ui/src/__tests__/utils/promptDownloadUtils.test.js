// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  framePromptContent,
  fetchPromptContent,
  fetchAllPromptsContents,
  getFileName,
} from "../../app/utils/promptDownloadUtils";

describe("promptDownloadUtils", () => {
  describe("framePromptContent", () => {
    it("should format prompt data with all fields", () => {
      const mockPromptData = {
        help_prompt_description: "Test description",
        help_sample_input: "Test sample input",
        follow_ups: [
          {
            title: "Follow Up 1",
            help_prompt_description: "Follow up 1 description",
          },
          {
            title: "Follow Up 2",
            help_prompt_description: "Follow up 2 description",
          },
        ],
        content: "Test prompt content",
      };

      const result = framePromptContent(mockPromptData);

      expect(result).toContain("DESCRIPTION:\n\nTest description");
      expect(result).toContain("SAMPLE INPUT:\n\nTest sample input");
      expect(result).toContain("FOLLOW_UP PROMPTS:");
      expect(result).toContain("1. Follow Up 1");
      expect(result).toContain("Description: Follow up 1 description");
      expect(result).toContain("2. Follow Up 2");
      expect(result).toContain("Description: Follow up 2 description");
      expect(result).toContain("PROMPT:\n\nTest prompt content");
    });

    it("should handle missing fields", () => {
      const mockPromptData = {
        help_prompt_description: "Test description",
        content: "Test prompt content",
      };

      const result = framePromptContent(mockPromptData);

      expect(result).toContain("DESCRIPTION:\n\nTest description");
      expect(result).not.toContain("SAMPLE INPUT:");
      expect(result).not.toContain("FOLLOW_UP PROMPTS:");
      expect(result).toContain("PROMPT:\n\nTest prompt content");
    });

    it("should handle missing content", () => {
      const mockPromptData = {
        help_prompt_description: "Test description",
      };

      const result = framePromptContent(mockPromptData);

      expect(result).toContain("DESCRIPTION:\n\nTest description");
      expect(result).toContain("PROMPT:\n\n");
    });

    it("should handle follow-ups without descriptions", () => {
      const mockPromptData = {
        help_prompt_description: "Test description",
        follow_ups: [{ title: "Follow Up 1" }],
        content: "Test prompt content",
      };

      const result = framePromptContent(mockPromptData);

      expect(result).toContain("FOLLOW_UP PROMPTS:");
      expect(result).toContain("1. Follow Up 1");
      expect(result).not.toContain("Description:");
    });
  });

  describe("getFileName", () => {
    beforeEach(() => {
      // Mock the Date constructor
      vi.useFakeTimers();
      vi.setSystemTime(new Date(2024, 5, 15)); // June 15, 2024
    });

    afterEach(() => {
      vi.useRealTimers();
    });

    it("should generate the correct filename format", () => {
      const mockPrompt = {
        filename: "test_prompt",
      };

      const result = getFileName(mockPrompt);

      expect(result).toBe("test_prompt_prompt_15_Jun_2024.txt");
    });
  });

  describe("fetchPromptContent", () => {
    beforeEach(() => {
      global.fetch = vi.fn();
    });

    afterEach(() => {
      vi.restoreAllMocks();
    });

    it("should fetch a single prompt content and format it correctly", async () => {
      const mockPrompt = {
        identifier: "test-id",
      };

      const mockResponseData = [
        {
          help_prompt_description: "Test description",
          content: "Test content",
          filename: "test_filename",
        },
      ];

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponseData,
      });

      const result = await fetchPromptContent(mockPrompt);

      expect(fetch).toHaveBeenCalledWith(
        "/api/prompts-content?prompt_id=test-id",
        {
          method: "GET",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
        },
      );

      expect(result).toHaveProperty("filename");
      expect(result).toHaveProperty("content");
      expect(result.content).toContain("Test description");
      expect(result.content).toContain("Test content");
    });

    it("should throw an error if the fetch fails", async () => {
      const mockPrompt = {
        identifier: "test-id",
      };

      global.fetch.mockResolvedValueOnce({
        ok: false,
      });

      await expect(fetchPromptContent(mockPrompt)).rejects.toThrow(
        "Failed to fetch prompt data",
      );
    });
  });

  describe("fetchAllPromptsContents", () => {
    beforeEach(() => {
      global.fetch = vi.fn();
    });

    afterEach(() => {
      vi.restoreAllMocks();
    });

    it("should fetch all prompts without a category", async () => {
      const mockResponseData = [
        {
          help_prompt_description: "Test description 1",
          content: "Test content 1",
          filename: "test_filename_1",
        },
        {
          help_prompt_description: "Test description 2",
          content: "Test content 2",
          filename: "test_filename_2",
        },
      ];

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponseData,
      });

      const result = await fetchAllPromptsContents();

      expect(fetch).toHaveBeenCalledWith("/api/prompts-content?category=", {
        method: "GET",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
      });

      expect(result).toEqual([
        {
          filename: expect.stringMatching(
            /test_filename_1_prompt_\d+_[A-Za-z]+_\d{4}\.txt/,
          ),
          content: expect.stringContaining(
            "DESCRIPTION:\n\nTest description 1\n\n\n\n\n\n\nPROMPT:\n\nTest content 1",
          ),
        },
        {
          filename: expect.stringMatching(
            /test_filename_2_prompt_\d+_[A-Za-z]+_\d{4}\.txt/,
          ),
          content: expect.stringContaining(
            "DESCRIPTION:\n\nTest description 2\n\n\n\n\n\n\nPROMPT:\n\nTest content 2",
          ),
        },
      ]);
    });

    it("should fetch prompts with a specific category", async () => {
      const mockResponseData = [
        {
          help_prompt_description: "Architecture description",
          content: "Architecture content",
          filename: "architecture_filename",
        },
      ];

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponseData,
      });

      const result = await fetchAllPromptsContents("architecture");

      expect(fetch).toHaveBeenCalledWith(
        "/api/prompts-content?category=architecture",
        {
          method: "GET",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
        },
      );
      expect(result).toEqual([
        {
          filename: expect.stringMatching(
            /architecture_filename_prompt_\d+_[A-Za-z]+_\d{4}\.txt/,
          ),
          content: expect.stringContaining(
            "DESCRIPTION:\n\nArchitecture description\n\n\n\n\n\n\nPROMPT:\n\nArchitecture content",
          ),
        },
      ]);
    });

    it("should throw an error if the fetch fails", async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
      });

      await expect(fetchAllPromptsContents()).rejects.toThrow(
        "Failed to fetch prompt data",
      );
    });
  });
});
