// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { isFeatureEnabled, FEATURES } from "../app/feature_toggle";

describe("Feature Toggles", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  function setFeatureToggle(name, value) {
    const toggles = JSON.parse(localStorage.getItem("toggles")) || {};
    toggles[name] = value;
    localStorage.setItem("toggles", JSON.stringify(toggles));
  }

  Object.values(FEATURES).forEach((featureName) => {
    it(`should return true when ${featureName} is enabled`, () => {
      setFeatureToggle(featureName, true);
      expect(isFeatureEnabled(featureName)).toBe(true);
    });

    it(`should return false when ${featureName} is disabled`, () => {
      setFeatureToggle(featureName, false);
      expect(isFeatureEnabled(featureName)).toBe(false);
    });

    it(`should return false when ${featureName} is not present`, () => {
      // not setting anything
      expect(isFeatureEnabled(featureName)).toBe(false);
    });
  });
});
