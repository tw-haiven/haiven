// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { describe, it, expect, vi } from "vitest";
import {
  getFeatureTogglesAsJson,
  addToPinboard,
  getPinboardData,
  getSortedContexts,
  deletePinOrNoteByTimestamp,
} from "../app/_local_store";
import { toast } from "react-toastify";

vi.mock("react-toastify", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

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

describe("Pinboard Component", () => {
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

  describe("getFeatureTogglesAsJson", () => {
    it("should return an empty object if no toggles are set", () => {
      const result = getFeatureTogglesAsJson();
      expect(result).toEqual({});
    });

    it("should return the feature toggles as a JSON object", () => {
      const toggles = { feature1: true, feature2: false };
      localStorage.setItem("toggles", JSON.stringify(toggles));

      const result = getFeatureTogglesAsJson();
      expect(result).toEqual(toggles);
    });

    describe("getSortedContexts", () => {
      beforeEach(() => {
        localStorage.clear();
        vi.clearAllMocks();
      });

      it("should return an empty array if no contexts are set", () => {
        const result = getSortedContexts();
        expect(result).toEqual([]);
      });

      it("should return contexts sorted by timestamp in descending order", () => {
        const context1 = {
          title: "Context 1",
          summary: "Summary 1",
          timestamp: 1,
        };
        const context2 = {
          title: "Context 2",
          summary: "Summary 2",
          timestamp: 2,
        };
        const context3 = {
          title: "Context 3",
          summary: "Summary 3",
          timestamp: 3,
        };

        localStorage.setItem(
          "context",
          JSON.stringify([context1, context2, context3]),
        );

        const result = getSortedContexts();
        expect(result).toEqual([context3, context2, context1]);
      });

      describe("deletePinOrNoteByTimestamp", () => {
        beforeEach(() => {
          localStorage.clear();
          vi.clearAllMocks();
        });

        it("should delete the pin or note by timestamp", () => {
          const timestamp1 = "1234";
          const timestamp2 = "5678";
          const content1 = "Content 1";
          const content2 = "Content 2";

          addToPinboard(timestamp1, content1);
          addToPinboard(timestamp2, content2);

          deletePinOrNoteByTimestamp(timestamp1);

          const pinboard = JSON.parse(localStorage.getItem("pinboard"));
          expect(pinboard[timestamp1]).toBeUndefined();
          expect(pinboard[timestamp2]).toBeDefined();
        });

        it("should do nothing if the timestamp does not exist", () => {
          const timestamp1 = "1234";
          const content1 = "Content 1";

          addToPinboard(timestamp1, content1);

          deletePinOrNoteByTimestamp("5678");

          const pinboard = JSON.parse(localStorage.getItem("pinboard"));
          expect(pinboard[timestamp1]).toBeDefined();
        });
      });
    });
  });
});
