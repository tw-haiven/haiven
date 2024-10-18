// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { message } from "antd";

export const addToPinboard = (content) => {
  try {
    var pinboard = localStorage.getItem("pinboard");
    var pinboardMap = pinboard ? JSON.parse(pinboard) : {};
    var pinboardEntries = Object.entries(pinboardMap);
    pinboardEntries.unshift([Date.now(), content]);
    pinboardMap = Object.fromEntries(pinboardEntries);
    localStorage.setItem("pinboard", JSON.stringify(pinboardMap));
  } catch (error) {
    console.log(error.message);
    message.error("Failed to pin the content");
  }
  message.success("Text pinned successfully! You can view it on the Pinboard.");
};
