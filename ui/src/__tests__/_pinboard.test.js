// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { describe, it, expect, vi, beforeEach } from "vitest";
import { addToPinboard, getPinboardData } from "../app/_local_store";
import { toast } from "react-toastify";

const localStorageMock = (() => {
  let store = {};
  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => {
      store[key] = value.toString();
    },
    clear: () => {
      store = {};
    },
  };
})();

Object.defineProperty(window, "localStorage", {
  value: localStorageMock,
});

vi.mock("react-toastify", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

describe("addToPinboard", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it("should add content to pinboard and show success message", () => {
    const content = "Test content";
    const key = Date.now();

    addToPinboard(key, content);

    const pinboard = JSON.parse(localStorage.getItem("pinboard"));
    expect(Object.values(pinboard)).toContain(content);
    expect(toast.success).toHaveBeenCalledWith(
      "Text pinned successfully! You can view it on the Pinboard.",
    );
  });

  it("should handle errors and show error message", () => {
    const content = "Test content";
    const key = Date.now();
    const errorMessage = "Failed to pin the content";
    const newLocal = vi.spyOn(localStorage, "setItem");
    newLocal.mockImplementation(() => {
      throw new Error("Storage error");
    });

    addToPinboard(key, content);

    expect(toast.error).toHaveBeenCalledWith(errorMessage);
    newLocal.mockRestore();
  });

  it("should initialize pinboard if it does not exist", () => {
    const content = "Test content";
    const timestamp = 1729881106012;

    addToPinboard(timestamp, content);

    const pinboard = JSON.parse(localStorage.getItem("pinboard"));
    expect(pinboard).toBeDefined();
    expect(Object.entries(pinboard)[0]).toEqual([
      timestamp.toString(),
      content,
    ]);
  });

  it("should add new content to the top of pinboard", () => {
    const content1 = "Test content 1";
    const timestamp1 = 1729881106013;

    const content2 = "Test content 2";
    const timestamp2 = 1729881106014;

    addToPinboard(timestamp1, content1);
    addToPinboard(timestamp2, content2);

    const pinboard = JSON.parse(localStorage.getItem("pinboard"));
    expect(Object.entries(pinboard)[0]).toContain(content2);
    expect(Object.entries(pinboard)[1]).toContain(content1);
  });
});

describe("getPinboardData", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it("should return empty array for empty pinboard", () => {
    const result = getPinboardData();
    expect(result).toEqual([]);
  });

  it("should transform regular pinned content correctly", () => {
    const content = "Regular content";
    const timestamp = "1234";

    addToPinboard(timestamp, content);

    const result = getPinboardData();
    expect(result).toEqual([
      {
        timestamp: timestamp,
        summary: content,
        isUserDefined: false,
      },
    ]);
  });

  it("should transform user-defined content correctly", () => {
    const content = "User content";
    const timestamp = "1234";

    addToPinboard(timestamp, content, true);

    const result = getPinboardData();
    expect(result).toEqual([
      {
        timestamp: timestamp,
        summary: content,
        isUserDefined: true,
      },
    ]);
  });

  it("should sort user-defined content to the top", () => {
    addToPinboard("1", "Regular content");
    addToPinboard("2", "User content", true);
    addToPinboard("3", "Another regular content");

    const result = getPinboardData();
    expect(result[0].isUserDefined).toBe(true);
    expect(result[0].summary).toBe("User content");
    expect(result.length).toBe(3);
  });
});
