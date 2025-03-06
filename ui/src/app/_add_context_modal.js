// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

import React, { useState } from "react";
import { Input, Modal } from "antd";
import { toast } from "react-toastify";
import { saveContext } from "../app/_local_store";

const AddContextModal = ({
  isAddingContext,
  setIsAddingContext,
  reloadPinboard,
}) => {
  const [contextTitle, setContextTitle] = useState("");
  const [contextDescription, setContextDescription] = useState("");

  const resetAddContextForm = () => {
    setContextTitle("");
    setContextDescription("");
    setIsAddingContext(false);
  };

  const addContext = () => {
    if (!contextTitle.trim()) {
      toast.error("Please enter some title for your context");
      return;
    }
    if (!contextDescription.trim()) {
      toast.error("Please enter some description for your context");
      return;
    }

    saveContext(contextTitle, contextDescription);
    resetAddContextForm();
    reloadPinboard();
    toast.success("Context added successfully!");
  };

  return (
    <Modal
      title="Add new context"
      open={isAddingContext}
      onCancel={() => {
        setIsAddingContext(false);
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
  );
};

export default AddContextModal;
