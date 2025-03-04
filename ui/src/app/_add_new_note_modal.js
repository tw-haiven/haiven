// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

import React, { useState } from "react";
import { Input, Modal } from "antd";
import { toast } from "react-toastify";

const AddNewNoteModal = ({ isAddingNote, setIsAddingNote, callBack }) => {
  const [newNoteTitle, setNewNoteTitle] = useState("");
  const [newNoteDescription, setNewNoteDescription] = useState("");

  const resetFormInputValues = () => {
    setNewNoteTitle("");
    setNewNoteDescription("");
    setIsAddingNote(false);
  };

  const addNote = () => {
    if (!newNoteTitle.trim()) {
      toast.error("Please enter some title for your note");
      return;
    }
    if (!newNoteDescription.trim()) {
      toast.error("Please enter some description for your note");
      return;
    }

    const noteContent = "# " + newNoteTitle + "\n\n" + newNoteDescription;
    callBack(noteContent);
    resetFormInputValues();
    toast.success("Note added successfully!");
  };

  return (
    <Modal
      title="Add new note"
      open={isAddingNote}
      onCancel={() => {
        setIsAddingNote(false);
      }}
      onOk={addNote}
      okText="Save"
    >
      <Input
        value={newNoteTitle}
        onChange={(e) => setNewNoteTitle(e.target.value)}
        placeholder="Enter the title of your note"
        rows={1}
      />
      <Input.TextArea
        style={{
          marginTop: "12px",
        }}
        value={newNoteDescription}
        onChange={(e) => setNewNoteDescription(e.target.value)}
        placeholder="Enter the description of your note, e.g. a description of your domain or architecture that you frequently need"
        rows={15}
      />
    </Modal>
  );
};

export default AddNewNoteModal;
