// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

import React, { useState } from "react";
import { Input, Modal } from "antd";
import { toast } from "react-toastify";
import { saveContext } from "../app/_local_store";
import ConfirmClose from "./_confirm_close";

const AddContextModal = ({
  isAddingContext,
  setIsAddingContext,
  reloadContexts = () => {},
}) => {
  const [contextTitle, setContextTitle] = useState("");
  const [contextDescription, setContextDescription] = useState("");
  const [isCloseConfirmationModalVisible, setIsCloseConfirmationModalVisible] =
    useState(false);

  const closeModal = () => {
    setContextTitle("");
    setContextDescription("");
    setIsAddingContext(false);
  };

  const addContext = () => {
    if (!contextTitle.trim()) {
      toast.error("Please enter some title");
      return;
    }
    if (!contextDescription.trim()) {
      toast.error("Please enter some description");
      return;
    }

    saveContext(contextTitle, contextDescription);
    closeModal();
    reloadContexts();
    toast.success("Context added successfully!");
  };

  return (
    <>
      <Modal
        title="Add new context"
        open={isAddingContext}
        onCancel={() => {
          setIsCloseConfirmationModalVisible(true);
        }}
        onOk={addContext}
        okText="Save"
        className="add-context-modal"
      >
        <span className="label">Title</span>
        <Input
          value={contextTitle}
          onChange={(e) => setContextTitle(e.target.value)}
          placeholder="Enter the title of your context"
          rows={1}
          className="title-input"
        />
        <span className="label">Description</span>
        <Input.TextArea
          value={contextDescription}
          onChange={(e) => setContextDescription(e.target.value)}
          placeholder="Enter the description of your context, e.g. a description of your domain or architecture that you frequently need"
          autoSize={{ minRows: 10, maxRows: 15 }}
          className="description-input"
        />
      </Modal>

      <ConfirmClose
        isVisible={isCloseConfirmationModalVisible}
        onForceClose={() => {
          closeModal();
          setIsCloseConfirmationModalVisible(false);
        }}
        onReturnBack={() => {
          setIsCloseConfirmationModalVisible(false);
        }}
      />
    </>
  );
};

export default AddContextModal;
