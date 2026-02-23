// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useState } from "react";
import { Modal, Tooltip, message } from "antd";
import { RiEyeLine } from "react-icons/ri";
import { fetchPromptContent } from "./utils/promptDownloadUtils";

const PromptOverviewPreview = ({ prompt }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [previewContent, setPreviewContent] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handlePreview = async (event) => {
    event.stopPropagation();
    if (!prompt) return;

    setIsOpen(true);

    if (previewContent) return;

    setIsLoading(true);
    try {
      const downloadablePrompt = await fetchPromptContent(prompt);
      setPreviewContent(downloadablePrompt.content);
    } catch (error) {
      console.error("Error previewing prompt:", error);
      setPreviewContent("Preview is not available for this prompt.");
      message.error("Failed to load prompt preview.");
    } finally {
      setIsLoading(false);
    }
  };

  if (!prompt) {
    return null;
  }

  return (
    <>
      <Tooltip title="Preview Prompt" placement="bottom">
        <button
          className="download-prompt-button"
          data-testid="prompt-preview-button"
          onClick={handlePreview}
          type="button"
        >
          <RiEyeLine />
        </button>
      </Tooltip>
      <Modal
        title={prompt.title || "Prompt Preview"}
        open={isOpen}
        onCancel={() => setIsOpen(false)}
        footer={null}
      >
        <div className="snippet">
          {isLoading ? (
            <p>Loading prompt preview...</p>
          ) : (
            <pre>{previewContent}</pre>
          )}
        </div>
      </Modal>
    </>
  );
};

export default PromptOverviewPreview;
