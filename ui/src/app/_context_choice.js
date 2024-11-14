// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { Select } from "antd";
import HelpTooltip from "./_help_tooltip";

function ContextChoice({ contexts, value, onChange }) {
  return (
    <div className="user-input">
      <label>
        Your context
        <HelpTooltip text="Choose a context that is relevant to your domain / industry / situation / organisation." />
      </label>
      <Select
        onChange={onChange}
        options={contexts}
        value={value}
        defaultValue="base"
        data-testid="context-select"
      />
    </div>
  );
}

export default ContextChoice;
