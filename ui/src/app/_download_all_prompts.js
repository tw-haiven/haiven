// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useEffect, useState } from "react";
import { RiDownload2Line } from "react-icons/ri";
import { Dropdown } from "antd";
import JSZip from "jszip";
import { fetchAllPromptsContents } from "./utils/promptDownloadUtils";

const DownloadAllPrompts = ({ prompts }) => {
  const handleMultiplePromptsDownload = async (category = "") => {
    var folderName = category
      ? category.toLowerCase().replace(/\s+/g, "-") + "-prompts"
      : "all-prompts";
    try {
      const zip = new JSZip();

      const allPromptsFolder = zip.folder(folderName);

      const allPromptsContents = await fetchAllPromptsContents(
        (category = category),
      );

      allPromptsContents.forEach((prompt) => {
        allPromptsFolder.file(prompt.filename, prompt.content);
      });

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

    // Filter out restricted prompts
    const downloadablePrompts = prompts.filter(
      (prompt) => !prompt.download_restricted,
    );

    // Get categories that have at least one downloadable prompt
    const categories = [
      ...new Set(
        downloadablePrompts.flatMap((prompt) => prompt.categories || []),
      ),
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
