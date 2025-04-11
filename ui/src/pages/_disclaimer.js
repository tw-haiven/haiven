// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React from "react";
import { Alert } from "antd";

const Disclaimer = ({ message }) => {
  return <Alert message={message} type="warning" showIcon />;
};

export default Disclaimer;
