// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
export const framePromptContent = (promptData) => {
  let textContent = `DESCRIPTION:\n\n${promptData.help_prompt_description || ""}`;

  if (promptData.help_sample_input) {
    textContent += `\n\nSAMPLE INPUT:\n\n${promptData.help_sample_input}`;
  }

  if (promptData.follow_ups && promptData.follow_ups.length > 0) {
    textContent += "\n\nFOLLOW_UP PROMPTS:";
    promptData.follow_ups.forEach((followUp, index) => {
      textContent += `\n\n${index + 1}. ${followUp.title}`;
      if (followUp.help_prompt_description) {
        textContent += `\n\nDescription: ${followUp.help_prompt_description}`;
      }
    });
  }

  textContent += `\n\n\n\n\n\n\nPROMPT:\n\n${promptData.content || ""}`;
  return textContent;
};

const promptToDownload = (promptData) => {
  return {
    filename: getFileName(promptData),
    content: framePromptContent(promptData),
  };
};

export const fetchPromptContent = async (prompt) => {
  const response = await fetch(
    `/api/download-prompt?prompt_id=${prompt.identifier}`,
    {
      method: "GET",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    },
  );

  if (!response.ok) {
    if (response.status === 403) {
      throw new Error("This prompt is not available for download");
    }
    throw new Error("Failed to fetch prompt data");
  }

  const responseArray = await response.json();
  const promptData = responseArray[0];
  return promptToDownload(promptData);
};

export const fetchAllPromptsContents = async (category = "") => {
  const response = await fetch(`/api/download-prompt?category=${category}`, {
    method: "GET",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error("Failed to fetch prompt data");
  }

  const promptDataArray = await response.json();
  const promptContents = promptDataArray.map((promptData) => {
    return promptToDownload(promptData);
  });
  return promptContents;
};

export const getFileName = (prompt) => {
  console.log(prompt);
  const date = new Date();
  const month = date.toLocaleString("en-US", { month: "short" });
  const day = date.getDate();
  const year = date.getFullYear();
  return `${prompt.filename}_prompt_${day}_${month}_${year}.txt`;
};
