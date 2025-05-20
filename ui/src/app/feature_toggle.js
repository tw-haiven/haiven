// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

export const FEATURES = {
  FEATURE_DELIVERY_MANAGEMENT: "FEATURE_DELIVERY_MANAGEMENT",
  DOWNLOAD_PROMPTS: "DOWNLOAD_PROMPTS",
};

export const getFeatureTogglesAsJson = () => {
  return JSON.parse(localStorage.getItem("toggles")) || {};
};
