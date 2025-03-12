// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { describe, it, expect, vi } from "vitest";
import { isFeatureEnabled, FEATURES } from "../app/feature_toggle";
import { getFeatureTogglesAsJson } from "../app/_local_store";

beforeEach(() => {
  vi.mock("../app/_local_store", () => ({
    getFeatureTogglesAsJson: vi.fn(),
  }));
});

afterEach(() => {
  vi.resetAllMocks();
});

describe("isFeatureEnabled", () => {
  it("should return true if the feature is enabled", () => {
    getFeatureTogglesAsJson.mockReturnValue({
      add_context_from_ui: true,
    });

    const result = isFeatureEnabled(FEATURES.ADD_CONTEXT_FROM_UI);
    expect(result).toBe(true);
  });

  it("should return false if the feature is disabled", () => {
    getFeatureTogglesAsJson.mockReturnValue({
      [FEATURES.ADD_CONTEXT_FROM_UI]: false,
    });

    const result = isFeatureEnabled(FEATURES.ADD_CONTEXT_FROM_UI);
    expect(result).toBe(false);
  });

  it("should return false if the feature is not present in the configuration", () => {
    getFeatureTogglesAsJson.mockReturnValue({});

    const result = isFeatureEnabled(FEATURES.ADD_CONTEXT_FROM_UI);
    expect(result).toBe(false);
  });
});
