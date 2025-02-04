// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React from "react";
import DisclaimerPopup from "./DisclaimerPopup";

const Layout = ({ children, disclaimerMessage }) => {
  return (
    <>
      <DisclaimerPopup disclaimerConfig={disclaimerMessage} />
      {children}
    </>
  );
};

export default Layout;
