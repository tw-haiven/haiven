// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { describe, it, expect, vi, beforeEach } from "vitest";
import { addToPinboard } from "../app/_local_store";
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
