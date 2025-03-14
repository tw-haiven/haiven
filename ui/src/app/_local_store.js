// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { toast } from "react-toastify";

export const initializeLocalStorage = () => {
  if (!localStorage.getItem("pinboard")) {
    localStorage.setItem("pinboard", JSON.stringify({}));
  }
  if (!localStorage.getItem("toggles")) {
    localStorage.setItem("toggles", JSON.stringify({}));
  }
};

export const addToPinboard = (key, content, isUserDefined = false) => {
  try {
    var pinboard = localStorage.getItem("pinboard");
    var pinboardMap = pinboard ? JSON.parse(pinboard) : {};
    var pinboardEntries = Object.entries(pinboardMap);
    if (pinboardMap.hasOwnProperty(key)) {
      toast.warning("This content is already pinned.");
      return;
    }

    const value = isUserDefined ? { content, isUserDefined: true } : content;
    pinboardEntries.unshift([key.toString(), value]);
    pinboardMap = Object.fromEntries(pinboardEntries);
    localStorage.setItem("pinboard", JSON.stringify(pinboardMap));
    toast.success("Text pinned successfully! You can view it on the Pinboard.");
  } catch (error) {
    console.log(error.message);
    toast.error("Failed to pin the content");
  }
};

const transformPinboardEntry = (value, timestamp) => {
  const isObject = typeof value === "object";
  return {
    timestamp,
    summary: isObject ? value.content : value,
    isUserDefined: isObject ? value.isUserDefined : false,
  };
};

export const saveNote = (newNote) => {
  const timestamp = Date.now().toString();
  const pinboardData = JSON.parse(localStorage.getItem("pinboard")) || {};
  pinboardData[timestamp] = { content: newNote, isUserDefined: true };
  localStorage.setItem("pinboard", JSON.stringify(pinboardData));
};

export const getPinboardData = () => {
  const pinboardData = JSON.parse(localStorage.getItem("pinboard")) || {};
  if (!pinboardData || Array.isArray(pinboardData)) {
    return [];
  }

  const entries = Object.entries(pinboardData).map(([timestamp, value]) =>
    transformPinboardEntry(value, timestamp),
  );

  return entries.sort((a, b) => b.isUserDefined - a.isUserDefined);
};

export const getFeatureToggleConfiguration = () => {
  return localStorage.getItem("toggles");
};

export const getFeatureTogglesAsJson = () => {
  return JSON.parse(localStorage.getItem("toggles")) || {};
};

const getContexts = () => {
  return JSON.parse(localStorage.getItem("context")) || [];
};

export const getSortedUserContexts = () => {
  let contexts = getContexts();
  contexts.sort((a, b) => b.timestamp - a.timestamp);
  return contexts;
};

export const saveContext = (title, description) => {
  const timestamp = Date.now();
  const contextData = getContexts();
  contextData.push({
    title,
    summary: description,
    timestamp,
    isUserDefined: true,
  });
  localStorage.setItem("context", JSON.stringify(contextData));
};

export const deleteContextByTimestamp = (timestamp) => {
  const contextData = getContexts();
  const updatedContextData = contextData.filter(
    (context) => context.timestamp !== timestamp,
  );

  localStorage.setItem("context", JSON.stringify(updatedContextData));
};

export const deletePinOrNoteByTimestamp = (timestamp) => {
  const pinboardData = JSON.parse(localStorage.getItem("pinboard")) || {};
  delete pinboardData[timestamp];
  localStorage.setItem("pinboard", JSON.stringify(pinboardData));
};

export const getSummaryForTheUserContext = (contextTitle) => {
  const userContexts = getSortedUserContexts();
  const context = userContexts.find(
    (context) => context.title === contextTitle,
  );
  return context ? context.summary : "";
};
