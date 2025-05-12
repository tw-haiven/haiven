// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { getFeatureTogglesAsJson } from "../app/_local_store";

export const FEATURES = {
  FEATURE_DELIVERY_MANAGEMENT: "FEATURE_DELIVERY_MANAGEMENT",
};

export const isFeatureEnabled = (featureName) => {
  const allFeatureToggles = getFeatureTogglesAsJson();
  return allFeatureToggles[featureName] === true;
};
