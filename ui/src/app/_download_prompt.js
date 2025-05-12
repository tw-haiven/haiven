// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { RiDownload2Line } from "react-icons/ri";
import { Tooltip } from "antd";
import { isFeatureEnabled, FEATURES } from "./feature_toggle";

const DownloadPrompt = ({ prompt }) => {
  const prompt_file_content = async (prompt) => {
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

    let textContent = `Description: ${promptData.help_prompt_description || ""}
Prompt: ${promptData.content || ""}`;

    if (promptData.help_sample_input) {
      textContent += `\nSample Input: ${promptData.help_sample_input}`;
    }
    if (promptData.follow_ups && promptData.follow_ups.length > 0) {
      textContent += "\n\nFollow-up Prompts:";
      promptData.follow_ups.forEach((followUp, index) => {
        textContent += `\n\n${index + 1}. ${followUp.title}`;
        if (followUp.help_prompt_description) {
          textContent += `\n   Description: ${followUp.help_prompt_description}`;
        }
      });
    }
    return textContent;
  };

  const handleDownload = async () => {
    if (!prompt) return;

    try {
      var textContent = await prompt_file_content(prompt);

      const blob = new Blob([textContent], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;

      // Convert title to hyphenated format and create filename
      const hyphenatedTitle = prompt.title.toLowerCase().replace(/\s+/g, "-");
      link.download = `${hyphenatedTitle}-prompt.txt`;

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading prompt:", error);
    }
  };

  return (
    isFeatureEnabled(FEATURES.DOWNLOAD_PROMPTS) && (
      <Tooltip title="Download Prompt" placement="bottom">
        <button
          onClick={handleDownload}
          className="download-prompt-button"
          data-testid="download-prompt-button"
        >
          <RiDownload2Line />
        </button>
      </Tooltip>
    )
  );
};

export default DownloadPrompt;
