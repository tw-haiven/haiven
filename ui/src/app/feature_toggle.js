// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

export const FEATURES = {
  THOUGHTWORKS: "THOUGHTWORKS",
  LLM_TOKEN_USAGE: "LLM_TOKEN_USAGE",
};

const fetchServerToggles = async () => {
  try {
    const response = await fetch("/api/features");
    if (!response.ok) {
      console.error("Failed to fetch server toggles:", response.status);
      return {};
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching server toggles:", error);
    return {};
  }
};

export const getFeatureTogglesAsJson = async () => {
  const localToggles = JSON.parse(localStorage.getItem("toggles")) || {};
  const serverToggles = await fetchServerToggles();

  // Merge toggles, with user toggles taking precedence
  const mergedToggles = { ...serverToggles, ...localToggles };
  return mergedToggles;
};
