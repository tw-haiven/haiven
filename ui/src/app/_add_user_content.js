// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

import React, { useState } from "react";
import { Input, Modal } from "antd";
import { toast } from "react-toastify";
import ConfirmClose from "./_confirm_close";

const AddUserContent = ({
  isOpen,
  setIsOpen,
  contentType = "Content",
  handleSubmit,
}) => {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [isCloseConfirmationModalVisible, setIsCloseConfirmationModalVisible] =
    useState(false);

  const closeModal = () => {
    setTitle("");
    setDescription("");
    setIsOpen(false);
  };

  const submitContent = () => {
    if (!title.trim()) {
      toast.error("Please enter some title");
      return;
    }
    if (!description.trim()) {
      toast.error("Please enter some description");
      return;
    }

    handleSubmit(title, description);
    closeModal();
    toast.success("Content added successfully!");
  };

  return (
    <>
      <Modal
        title={`Add new ${contentType}`}
        open={isOpen}
        onCancel={() => {
          setIsCloseConfirmationModalVisible(true);
        }}
        onOk={submitContent}
        okText="Save"
        className="add-content-modal"
      >
        <label className="label">Title</label>
        <Input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          rows={1}
          className="title-input"
          data-testid="add-content-title"
        />
        <span className="label">Description</span>
        <Input.TextArea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          autoSize={{ minRows: 10, maxRows: 15 }}
          className="description-input"
          data-testid="add-content-description"
        />
      </Modal>
      <ConfirmClose
        isVisible={isCloseConfirmationModalVisible}
        onForceClose={() => {
          closeModal(false);
          setIsCloseConfirmationModalVisible(false);
        }}
        onReturnBack={() => {
          setIsCloseConfirmationModalVisible(false);
        }}
      />
    </>
  );
};

export default AddUserContent;
