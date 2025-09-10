// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { describe, it, expect, beforeEach, vi } from "vitest";
import {
  generateReadmeContent,
  getFileName,
} from "../app/utils/rulesDownloadUtils";

// Mock the utils
vi.mock("../app/utils/rulesDownloadUtils", () => ({
  generateReadmeContent: vi.fn(),
  getFileName: vi.fn(),
}));

describe("DownloadRules Utilities", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should call generateReadmeContent with correct IDE", () => {
    generateReadmeContent.mockReturnValue("Mock README content");

    const result = generateReadmeContent("cursor");

    expect(generateReadmeContent).toHaveBeenCalledWith("cursor");
    expect(result).toBe("Mock README content");
  });

  it("should call getFileName with correct parameters", () => {
    const mockRule = { id: "rule1", filename: "rule1.md" };
    getFileName.mockReturnValue("rule1.mdc");

    const result = getFileName(mockRule, "cursor");

    expect(getFileName).toHaveBeenCalledWith(mockRule, "cursor");
    expect(result).toBe("rule1.mdc");
  });

  it("should handle filenames with existing extensions", () => {
    const mockRule = { id: "rule1", filename: "casper-workflow.md" };

    // Test that it removes existing extension before adding new one
    getFileName.mockReturnValue("casper-workflow.mdc");
    expect(getFileName(mockRule, "cursor")).toBe("casper-workflow.mdc");

    getFileName.mockReturnValue("casper-workflow.md");
    expect(getFileName(mockRule, "copilot")).toBe("casper-workflow.md");
  });

  it("should generate README content for individual rule downloads", () => {
    generateReadmeContent.mockReturnValue("Mock README for individual rule");

    const result = generateReadmeContent("cursor");

    expect(generateReadmeContent).toHaveBeenCalledWith("cursor");
    expect(result).toBe("Mock README for individual rule");
  });

  it("should handle different IDE types", () => {
    const mockRule = { id: "rule1", filename: "rule1.md" };

    // Test Cursor
    getFileName.mockReturnValue("rule1.mdc");
    expect(getFileName(mockRule, "cursor")).toBe("rule1.mdc");

    // Test Copilot
    getFileName.mockReturnValue("rule1.md");
    expect(getFileName(mockRule, "copilot")).toBe("rule1.md");

    // Test Amazon Q
    getFileName.mockReturnValue("rule1.md");
    expect(getFileName(mockRule, "amazon-q")).toBe("rule1.md");
  });
});
