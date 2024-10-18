// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { describe, it, expect, vi, beforeEach } from "vitest";
import { addToPinboard } from "../app/_pinboard";
import { message } from "antd";

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

vi.mock("antd", () => ({
  message: {
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
    expect(message.success).toHaveBeenCalledWith(
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

    expect(message.error).toHaveBeenCalledWith(errorMessage);
    newLocal.mockRestore();
  });

  it("should initialize pinboard if it does not exist", () => {
    const content = "Test content";
    const key = Date.now();

    addToPinboard(key, content);

    const pinboard = JSON.parse(localStorage.getItem("pinboard"));
    expect(pinboard).toBeDefined();
    expect(Object.values(pinboard)).toContain(content);
  });

  it("should add multiple contents to pinboard", () => {
    const content1 = "Test content 1";
    const content2 = "Test content 2";
    const originalDateNow = Date.now;

    addToPinboard(originalDateNow, content1);
    Date.now = vi.fn(() => 1234567891);
    addToPinboard(Date.now, content2);

    const pinboard = JSON.parse(localStorage.getItem("pinboard"));
    expect(Object.values(pinboard)).toContain(content1);
    expect(Object.values(pinboard)).toContain(content2);
  });
});
