// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useState } from "react";
import { Modal, Button } from "antd";
import { HiBookOpen } from "react-icons/hi";
import MarkdownRenderer from "./_markdown_renderer";

export default function PromptSampleInput({ sampleInput }) {
  const [enableSampleInputModal, setEnableSampleInputModal] = useState(false);

  const showSampleInputModal = () => {
    setEnableSampleInputModal(true);
  };

  const hideSampleInputModal = () => {
    setEnableSampleInputModal(false);
  };

  return (
    sampleInput && (
      <div className="prompt-example-container">
        <Button
          className="show-prompt-example-icon"
          type="link"
          onClick={showSampleInputModal}
        >
          <HiBookOpen />
        </Button>

        <Modal
          className="prompt-example-modal"
          title="Sample Input"
          open={enableSampleInputModal}
          closable={false}
          onOk={hideSampleInputModal}
          onCancel={hideSampleInputModal}
          footer={[
            <Button key="Ok" onClick={hideSampleInputModal}>
              Ok
            </Button>,
          ]}
        >
          <MarkdownRenderer content={sampleInput} />
        </Modal>
      </div>
    )
  );
}
