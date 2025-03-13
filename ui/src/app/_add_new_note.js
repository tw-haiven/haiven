// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

import React from "react";
import AddUserContent from "./_add_user_content";
import { saveNote } from "../app/_local_store";

const AddNote = ({ isAddingNote, setIsAddingNote, reloadData }) => {
  const submitNewNote = (title, description) => {
    const noteContent = "# " + title + "\n\n" + description;
    saveNote(noteContent);
    reloadData();
  };

  return (
    <AddUserContent
      isOpen={isAddingNote}
      setIsOpen={setIsAddingNote}
      handleSubmit={submitNewNote}
      contentType="Note"
    ></AddUserContent>
  );
};

export default AddNote;
