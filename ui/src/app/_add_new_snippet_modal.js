// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

import React, { useState } from "react";
import { Input, Modal } from "antd";
import { toast } from "react-toastify";

const AddNewSnippetModal = ({
  isAddingSnippet,
  setIsAddingSnippet,
  callBack,
}) => {
  const [newSnippet, setNewSnippet] = useState("");

  const addSnippet = () => {
    if (!newSnippet.trim()) {
      toast.error("Please enter some content for your snippet");
      return;
    }

    callBack(newSnippet);
    setNewSnippet("");
    setIsAddingSnippet(false);
    toast.success("Snippet added successfully!");
  };

  return (
    <Modal
      title="Add new snippet"
      open={isAddingSnippet}
      onCancel={() => {
        setIsAddingSnippet(false);
        setNewSnippet("");
      }}
      onOk={addSnippet}
      okText="Save"
    >
      <Input.TextArea
        value={newSnippet}
        onChange={(e) => setNewSnippet(e.target.value)}
        placeholder="Enter your reusable snippet here, e.g. a description of your domain or architecture that you frequently need"
        rows={15}
      />
    </Modal>
  );
};

export default AddNewSnippetModal;
