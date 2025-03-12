// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useState } from "react";
import { Modal, Button } from "antd";
import { toast } from "react-toastify";
import { RiClipboardLine, RiBookOpenLine } from "react-icons/ri";

import MarkdownRenderer from "./_markdown_renderer";

export default function PromptSampleInput({ sampleInput }) {
  const [enableSampleInputModal, setEnableSampleInputModal] = useState(false);

  const showSampleInputModal = () => {
    setEnableSampleInputModal(true);
  };

  const hideSampleInputModal = () => {
    setEnableSampleInputModal(false);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(sampleInput);
    toast.success("Content copied successfully!");
  };

  return (
    sampleInput && (
      <div className="prompt-sample-input-container">
        <Button
          className="prompt-sample-input-link"
          type="link"
          onClick={showSampleInputModal}
        >
          <RiBookOpenLine className="prompt-sample-input-icon" />
          Sample Input
        </Button>

        <Modal
          className="view-or-edit-details-modal"
          title="Sample Input"
          open={enableSampleInputModal}
          closable={false}
          onOk={hideSampleInputModal}
          onCancel={hideSampleInputModal}
        >
          <div className="metadata-header">
            <p>
              This is a sample input for reference. It demonstrates the expected
              format and structure for your input.
            </p>
            <div className="actions">
              <Button className="copy-action-link" onClick={handleCopy}>
                <RiClipboardLine
                  style={{
                    fontSize: "large",
                  }}
                />{" "}
                COPY
              </Button>
            </div>
          </div>
          <MarkdownRenderer className="content-viewer" content={sampleInput} />
          <div className="modal-footer">
            <Button
              className="close-modal-link"
              key="Ok"
              onClick={hideSampleInputModal}
            >
              OK
            </Button>
          </div>
        </Modal>
      </div>
    )
  );
}
