// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { describe, it, expect, vi } from "vitest";
import {
  getFeatureTogglesAsJson,
  getFeatureToggleConfiguration,
} from "../app/feature_toggle";

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
  });
});
