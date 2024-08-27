// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { Tooltip } from "antd";
import { RiInformationFill } from "react-icons/ri";

const HelpTooltip = ({ text }) => {
  return (
    <Tooltip className="tooltip-help" color="#003d4f" title={text}>
      <RiInformationFill />
    </Tooltip>
  );
};

export default HelpTooltip;
