// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useEffect, useState } from "react";
import { RiDownload2Line } from "react-icons/ri";
import { Dropdown } from "antd";
import JSZip from "jszip";
import { isFeatureEnabled, FEATURES } from "./feature_toggle";
import { fetchPromptContent, getFileName } from "./utils/promptDataUtils";

const DownloadAllPrompts = ({ prompts }) => {
  const [isDownloadPromptsEnabled, setIsDownloadPromptsEnabled] =
    useState(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      setIsDownloadPromptsEnabled(isFeatureEnabled(FEATURES.DOWNLOAD_PROMPTS));
    }
  }, []);

  const handleMultiplePromptsDownload = async (category = "") => {
    if (!prompts || prompts.length === 0) return;

    var folderName = "all-prompts";
    if (category !== "") {
      folderName = category.toLowerCase().replace(/\s+/g, "-") + "-prompts";
      const categoryPrompts = prompts.filter(
        (prompt) => prompt.categories && prompt.categories.includes(category),
      );
      if (categoryPrompts.length === 0) return;
      prompts = categoryPrompts;
    }
    try {
      const zip = new JSZip();

      const allPromptsFolder = zip.folder(folderName);

      for (const prompt of prompts) {
        const fileName = getFileName(prompt);
        allPromptsFolder.file(fileName, fetchPromptContent(prompt));
      }

      const content = await zip.generateAsync({ type: "blob" });

      const url = URL.createObjectURL(content);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${folderName}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading prompt:", error);
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
      onClick: () => handleMultiplePromptsDownload(category),
    }));
  };

  const items = [
    {
      key: "all",
      label: "All Prompts",
      onClick: () => handleMultiplePromptsDownload(),
    },
    {
      type: "divider",
    },
    ...getCategoryItems(),
  ];

  return (
    isDownloadPromptsEnabled && (
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
    )
  );
};

export default DownloadAllPrompts;
