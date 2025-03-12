// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { describe, it, expect, vi } from "vitest";
import { getFeatureTogglesAsJson } from "../app/_local_store";

// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

beforeEach(() => {
  localStorage.clear();
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
