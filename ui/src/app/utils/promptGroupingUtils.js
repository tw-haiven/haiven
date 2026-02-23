// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import {
  initialiseMenuCategoriesForSidebar,
  THOUGHTWORKS_ONLY_CATEGORIES,
} from "../_navigation_items";
import { FEATURES } from "../feature_toggle";

const isThoughtworksPrompt = (prompt) =>
  prompt.categories?.some((category) =>
    THOUGHTWORKS_ONLY_CATEGORIES.includes(category),
  );

export const buildPromptCategories = (prompts = [], featureToggleConfig = {}) => {
  const isThoughtworksInstance =
    featureToggleConfig?.[FEATURES.THOUGHTWORKS] === true;
  const menuCategories = initialiseMenuCategoriesForSidebar(
    isThoughtworksInstance,
  );

  const promptsByCategory = {};

  prompts
    .filter((prompt) => prompt.show !== false)
    .filter((prompt) => {
      if (isThoughtworksPrompt(prompt)) {
        return isThoughtworksInstance;
      }
      return true;
    })
    .forEach((prompt) => {
      const promptCategories =
        prompt.categories && prompt.categories.length > 0
          ? prompt.categories
          : ["other"];

      promptCategories.forEach((category) => {
        if (
          THOUGHTWORKS_ONLY_CATEGORIES.includes(category) &&
          !isThoughtworksInstance
        ) {
          return;
        }

        const categoryKey = menuCategories[category] ? category : "other";
        if (!promptsByCategory[categoryKey]) {
          promptsByCategory[categoryKey] = [];
        }
        promptsByCategory[categoryKey].push(prompt);
      });
    });

  return Object.keys(menuCategories)
    .filter((key) => {
      const menuCategory = menuCategories[key];
      if (menuCategory.type === "divider" || menuCategory.type === "group") {
        return false;
      }
      return promptsByCategory[key] && promptsByCategory[key].length > 0;
    })
    .map((key) => ({
      key,
      label: menuCategories[key].label,
      prompts: promptsByCategory[key].slice().sort((a, b) => {
        return (a.title || "").localeCompare(b.title || "");
      }),
    }));
};
