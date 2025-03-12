// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { getFeatureTogglesAsJson } from "../app/_local_store";

export const FEATURES = {
  ADD_CONTEXT_FROM_UI: "add_context_from_ui",
};

export const isFeatureEnabled = (featureName) => {
  const allFeatureToggles = getFeatureTogglesAsJson();
  return allFeatureToggles[featureName] === true;
};
