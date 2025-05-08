// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { RiDownload2Line } from "react-icons/ri";
import { Dropdown } from "antd";
import JSZip from "jszip";

const DownloadAllPrompts = ({ prompts }) => {
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

  const handleDownloadAll = async () => {
    if (!prompts || prompts.length === 0) return;

    try {
      const zip = new JSZip();

      const allPromptsFolder = zip.folder("all-prompts");

      for (const prompt of prompts) {
        const fileName = `${prompt.title.toLowerCase().replace(/\s+/g, "-")}.txt`;
        allPromptsFolder.file(fileName, prompt_file_content(prompt));
      }

      const content = await zip.generateAsync({ type: "blob" });

      const url = URL.createObjectURL(content);
      const link = document.createElement("a");
      link.href = url;
      link.download = "all-prompts.zip";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading prompts:", error);
    }
  };

  const handleDownloadByCategory = async (category) => {
    if (!prompts || prompts.length === 0) return;

    try {
      const categoryPrompts = prompts.filter(
        (prompt) => prompt.categories && prompt.categories.includes(category),
      );

      if (categoryPrompts.length === 0) return;

      const zip = new JSZip();

      const categoryFolder = zip.folder(
        category.toLowerCase().replace(/\s+/g, "-"),
      );

      for (const prompt of categoryPrompts) {
        const fileName = `${prompt.title.toLowerCase().replace(/\s+/g, "-")}.txt`;
        categoryFolder.file(fileName, prompt_file_content(prompt));
      }

      const content = await zip.generateAsync({ type: "blob" });

      const url = URL.createObjectURL(content);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${category.toLowerCase().replace(/\s+/g, "-")}-prompts.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading category prompts:", error);
    }
  };

  const getCategoryItems = () => {
    if (!prompts) return [];

    const categories = [
      ...new Set(prompts.flatMap((prompt) => prompt.categories || [])),
    ];
    return categories.map((category) => ({
      key: category,
      label: category.charAt(0).toUpperCase() + category.slice(1),
      onClick: () => handleDownloadByCategory(category),
    }));
  };

  const items = [
    {
      key: "all",
      label: "All Prompts",
      onClick: handleDownloadAll,
    },
    {
      type: "divider",
    },
    ...getCategoryItems(),
  ];

  return (
    <div>
      <Dropdown menu={{ items }} trigger={["click"]} placement="bottomRight">
        <button
          className="download-prompt-button"
          data-testid="download-all-prompts-button"
        >
          <span>Download prompts</span>
          <RiDownload2Line />
        </button>
      </Dropdown>
    </div>
  );
};

export default DownloadAllPrompts;
