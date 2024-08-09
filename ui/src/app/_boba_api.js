// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
export const getPrompts = async (onSuccess) => {
  fetch("/api/prompts", {
    method: "GET",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
  }).then((response) => {
    response.json().then((data) => {
      const formattedPrompts = data.map((item) => ({
        ...item,
        value: item.identifier,
        label: item.title,
      }));
      onSuccess(formattedPrompts);
    });
  });
};

export const getContexts = async (onSuccess) => {
  fetch("/api/knowledge/snippets", {
    method: "GET",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
  }).then((response) => {
    response.json().then((data) => {
      onSuccess(data);
    });
  });
};
