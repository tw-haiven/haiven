// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.

import React from "react";
import { saveContext } from "../app/_local_store";
import AddUserContent from "./_add_user_content";

const AddContext = ({
  isAddingContext,
  setIsAddingContext,
  reloadContexts = () => {},
}) => {
  const saveNewContext = (title, description) => {
    saveContext(title, description);
    reloadContexts();
  };

  return (
    <AddUserContent
      isOpen={isAddingContext}
      setIsOpen={setIsAddingContext}
      handleSubmit={saveNewContext}
      contentType="Context"
    ></AddUserContent>
  );
};

export default AddContext;
