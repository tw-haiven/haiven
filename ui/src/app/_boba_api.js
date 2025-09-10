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
      const formattedForDropdown = data
        .filter((item) => {
          return item.identifier !== "journey-to-stories-d6de9661d893";
        })
        .map((item) => ({
          ...item,
          value: item.identifier,
          label: item.title,
          followUps: item.follow_ups,
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

export const getDisclaimerAndGuidelines = async (onSuccess) => {
  fetch("/api/disclaimer-guidelines", {
    method: "GET",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
  }).then((response) => {
    response.json().then((data) => {
      if (data.enabled) {
        onSuccess(data);
      } else {
        onSuccess(null);
      }
    });
  });
};

export const getInspirations = async (onSuccess) => {
  fetch("/api/inspirations", {
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

export const getInspirationById = async (inspirationId, onSuccess) => {
  fetch(`/api/inspirations/${inspirationId}`, {
    method: "GET",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
  }).then((response) => {
    if (!response.ok) {
      throw new Error("Failed to fetch inspiration");
    }
    response.json().then((data) => {
      onSuccess(data);
    });
  });
};

export const getRules = async (onSuccess) =>
  fetch("/api/rules/list", {
    method: "GET",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
  }).then((response) => {
    response.json().then((data) => {
      onSuccess(data.rules || []);
    });
  });

// API Key Management Functions
export const getApiKeys = async (onSuccess, onError) => {
  const response = await fetch("/api/apikeys", {
    method: "GET",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const error = new Error(`HTTP error! status: ${response.status}`);
    if (onError) {
      onError(error);
    } else {
      console.error("Error fetching API keys:", error);
    }
    return;
  }

  const data = await response.json();
  onSuccess(data);
};

export const generateApiKey = async (
  name,
  onSuccess,
  onError,
  expiresDays = 30,
) => {
  const response = await fetch("/api/apikeys/generate", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      name: name,
      expires_days: expiresDays,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    const error = new Error(
      errorData.detail || `HTTP error! status: ${response.status}`,
    );
    if (onError) {
      onError(error);
    } else {
      console.error("Error generating API key:", error);
    }
    return;
  }

  const data = await response.json();
  onSuccess(data);
};

export const revokeApiKey = async (keyHash, onSuccess, onError) => {
  const response = await fetch("/api/apikeys/revoke", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      key_hash: keyHash,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    const error = new Error(
      errorData.detail || `HTTP error! status: ${response.status}`,
    );
    if (onError) {
      onError(error);
    } else {
      console.error("Error revoking API key:", error);
    }
    return;
  }

  const data = await response.json();
  onSuccess(data);
};

export const getApiKeyUsage = async (onSuccess, onError) => {
  const response = await fetch("/api/apikeys/usage", {
    method: "GET",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    const error = new Error(`HTTP error! status: ${response.status}`);
    if (onError) {
      onError(error);
    } else {
      console.error("Error fetching API key usage:", error);
    }
    return;
  }
  const data = await response.json();
  onSuccess(data);
};
