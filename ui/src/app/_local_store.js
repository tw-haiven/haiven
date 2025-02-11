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
