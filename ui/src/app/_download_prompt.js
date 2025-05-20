// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useEffect, useState } from "react";
import { RiDownload2Line } from "react-icons/ri";
import { Tooltip } from "antd";
import { fetchPromptContent } from "./utils/promptDownloadUtils";

const DownloadPrompt = ({ prompt }) => {
  const handleDownload = async () => {
    if (!prompt) return;

    try {
      var downloadablePrompt = await fetchPromptContent(prompt);

      const blob = new Blob([downloadablePrompt.content], {
        type: "text/plain",
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;

      link.download = downloadablePrompt.filename;

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading prompt:", error);
    }
  };

  return (
    <Tooltip title="Download Prompt" placement="bottom">
      <button
        onClick={handleDownload}
        className="download-prompt-button"
        data-testid="download-prompt-button"
      >
        <RiDownload2Line />
      </button>
    </Tooltip>
  );
};

export default DownloadPrompt;
