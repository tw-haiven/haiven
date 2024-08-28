// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { Modal, Button } from "antd";
import { RiClipboardLine } from "react-icons/ri";

export default function RenderedPromptModal({ open, promptData, onClose }) {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const closeModal = () => {
    setIsModalOpen(false);
    onClose();
  };

  useEffect(() => {
    setIsModalOpen(open);
  }, [open]);

  const handleCopy = () => {
    navigator.clipboard.writeText(renderedPrompt);
  };

  return (
    <Modal
      title="Prompt preview"
      open={isModalOpen}
      onOk={closeModal}
      onCancel={closeModal}
      width={800}
      okButtonProps={{
        style: { display: "none" },
      }}
      cancelButtonProps={{
        style: { display: "none" },
      }}
    >
      <p>
        This is the text that will be sent to the AI model, based on your
        inputs.
      </p>

      <Button className="prompt-preview-copy-btn" onClick={handleCopy}>
        <RiClipboardLine
          style={{
            fontSize: "large",
          }}
        />{" "}
        COPY
      </Button>

      <ReactMarkdown className="prompt-preview">
        {promptData.renderedPrompt}
      </ReactMarkdown>
    </Modal>
  );
}
