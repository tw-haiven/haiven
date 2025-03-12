// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

import React from "react";
import AddUserContent from "./_add_user_content";

const AddNote = ({ isAddingNote, setIsAddingNote, saveNewNote }) => {
  const submitNewNote = (title, description) => {
    const noteContent = "# " + title + "\n\n" + description;
    saveNewNote(noteContent);
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
