// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { Button } from "antd";
import { RiClipboardLine } from "react-icons/ri";

const ClipboardButton = ({ toggleClipboardDrawer }) => {
  return (
    <Button
      onClick={() => toggleClipboardDrawer(true)}
      className="btn-clipboard"
    >
      <RiClipboardLine
        style={{
          display: "inline-block",
          verticalAlign: "middle",
          height: 14,
        }}
      />
    </Button>
  );
};

export default ClipboardButton;
