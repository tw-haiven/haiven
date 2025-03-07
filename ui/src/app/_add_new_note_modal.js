// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

import React, { useState } from "react";
import { Input, Modal } from "antd";
import { toast } from "react-toastify";
import ConfirmClose from "./_confirm_close";

const AddNewNoteModal = ({ isAddingNote, setIsAddingNote, callBack }) => {
  const [newNoteTitle, setNewNoteTitle] = useState("");
  const [newNoteDescription, setNewNoteDescription] = useState("");
  const [isCloseConfirmationModalVisible, setIsCloseConfirmationModalVisible] =
    useState(false);

  const closeModal = () => {
    setNewNoteTitle("");
    setNewNoteDescription("");
    setIsAddingNote(false);
  };

  const addNote = () => {
    if (!newNoteTitle.trim()) {
      toast.error("Please enter some title");
      return;
    }
    if (!newNoteDescription.trim()) {
      toast.error("Please enter some description");
      return;
    }

    const noteContent = "# " + newNoteTitle + "\n\n" + newNoteDescription;
    callBack(noteContent);
    closeModal();
    toast.success("Note added successfully!");
  };

  return (
    <>
      <Modal
        title="Add new note"
        open={isAddingNote}
        onCancel={() => {
          setIsCloseConfirmationModalVisible(true);
        }}
        onOk={addNote}
        okText="Save"
        className="add-note-modal"
      >
        <span className="label">Title</span>
        <Input
          value={newNoteTitle}
          onChange={(e) => setNewNoteTitle(e.target.value)}
          placeholder="Enter the title of your note"
          rows={1}
          className="title-input"
        />
        <span className="label">Description</span>
        <Input.TextArea
          value={newNoteDescription}
          onChange={(e) => setNewNoteDescription(e.target.value)}
          placeholder="Enter the description of your note, e.g. a description of your domain or architecture that you frequently need"
          autoSize={{ minRows: 10, maxRows: 15 }}
          className="description-input"
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

export default AddNewNoteModal;
