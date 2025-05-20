// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { describe, it, expect, vi } from "vitest";
import { getFeatureTogglesAsJson } from "../app/feature_toggle";

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

describe("Feature Toggle", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  describe("getFeatureTogglesAsJson", () => {
    beforeEach(() => {
      // Mock fetchServerToggles to return server toggles
      vi.spyOn(global, "fetch").mockImplementation(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ THOUGHTWORKS: true }),
        }),
      );
    });

    it("should merge local and server toggles", async () => {
      const localToggles = { feature1: true, feature2: false };
      localStorage.setItem("toggles", JSON.stringify(localToggles));

      const result = await getFeatureTogglesAsJson();
      expect(result).toEqual({ ...localToggles, THOUGHTWORKS: true });
    });

    it("should handle empty local toggles", async () => {
      const result = await getFeatureTogglesAsJson();
      expect(result).toEqual({ THOUGHTWORKS: true });
    });
  });
});
