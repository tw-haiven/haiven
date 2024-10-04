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
      const formattedForDropdown = data.map((item) => ({
        ...item,
        value: item.identifier,
        label: item.title,
      }));
      onSuccess(formattedForDropdown);
    });
  });
};

export const getModels = async (onSuccess) => {
  fetch("/api/models", {
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

export const getContextSnippets = async (onSuccess) => {
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

export const getDocuments = async (onSuccess) => {
  fetch("/api/knowledge/documents", {
    method: "GET",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
  }).then((response) => {
    response.json().then((data) => {
      const formattedForDropdown = data.map((item) => ({
        ...item,
        value: item.key,
        label: item.title,
      }));
      onSuccess(formattedForDropdown);
    });
  });
};

export const getRenderedPrompt = async (body, onSuccess) => {
  fetch("/api/prompt/render", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  }).then((response) => {
    response.json().then((data) => {
      onSuccess(data);
    });
  });
};
