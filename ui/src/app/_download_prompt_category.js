// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { Tooltip } from "antd";
import { RiDownload2Line } from "react-icons/ri";
import JSZip from "jszip";
import { fetchAllPromptsContents } from "./utils/promptDownloadUtils";

const DownloadPromptCategory = ({ category, label }) => {
  const handleCategoryDownload = async (event) => {
    event.stopPropagation();
    if (!category) return;

    const folderName =
      category.toLowerCase().replace(/\s+/g, "-") + "-prompts";

    try {
      const zip = new JSZip();
      const categoryFolder = zip.folder(folderName);
      const promptContents = await fetchAllPromptsContents(category);

      promptContents.forEach((prompt) => {
        categoryFolder.file(prompt.filename, prompt.content);
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
      console.error("Error downloading prompt category:", error);
    }
  };

  if (!category) {
    return null;
  }

  const displayLabel =
    typeof label === "string" && label.trim().length > 0 ? label : category;

  return (
    <Tooltip title={`Download ${displayLabel} prompts`} placement="bottom">
      <button
        className="download-prompt-button"
        data-testid={`download-category-${category}`}
        onClick={handleCategoryDownload}
        type="button"
      >
        <RiDownload2Line />
      </button>
    </Tooltip>
  );
};

export default DownloadPromptCategory;
