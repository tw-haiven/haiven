// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React from "react";
import WelcomePopup from "./WelcomePopup";

const Layout = ({ children, welcomeMessage }) => {
  return (
    <>
      <WelcomePopup welcomeConfig={welcomeMessage} />
      {children}
    </>
  );
};

export default Layout;
