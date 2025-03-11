// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { describe, it, expect, vi } from "vitest";
import { isFeatureEnabled, FEATURES } from "../app/feature_toggle";
import { getFeatureToggleConfiguration } from "../app/_local_store";

beforeEach(() => {
  vi.mock("../app/_local_store", () => ({
    getFeatureToggleConfiguration: vi.fn(),
  }));
});

afterEach(() => {
  vi.resetAllMocks();
});

describe("isFeatureEnabled", () => {
  it("should return true if the feature is enabled", () => {
    getFeatureToggleConfiguration.mockReturnValue({
      [FEATURES.ADD_CONTEXT_FROM_UI]: "true",
    });

    const result = isFeatureEnabled(FEATURES.ADD_CONTEXT_FROM_UI);
    expect(result).toBe(true);
  });

  it("should return false if the feature is disabled", () => {
    getFeatureToggleConfiguration.mockReturnValue({
      [FEATURES.ADD_CONTEXT_FROM_UI]: "false",
    });

    const result = isFeatureEnabled(FEATURES.ADD_CONTEXT_FROM_UI);
    expect(result).toBe(false);
  });

  it("should return false if the feature is not present in the configuration", () => {
    getFeatureToggleConfiguration.mockReturnValue({});

    const result = isFeatureEnabled(FEATURES.ADD_CONTEXT_FROM_UI);
    expect(result).toBe(false);
  });
});
