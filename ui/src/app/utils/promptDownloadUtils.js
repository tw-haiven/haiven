// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
export const fetchPromptContent = async (prompt) => {
  const response = await fetch(`/api/prompt/${prompt.identifier}`, {
    method: "GET",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error("Failed to fetch prompt data");
  }

  const promptData = await response.json();

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

export const getFileName = (prompt) => {
  const hyphenatedTitle = prompt.title.toLowerCase().replace(/\s+/g, "-");
  const date = new Date();
  const month = date.toLocaleString("en-US", { month: "short" });
  const day = date.getDate();
  const year = date.getFullYear();
  return `${hyphenatedTitle}-prompt-${day}-${month}-${year}.txt`;
};
