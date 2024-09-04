// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { Select } from "antd";
import HelpTooltip from "./_help_tooltip";

function ContextChoice({ contexts, value, onChange }) {
  return (
    <div className="user-input">
      <label>
        Contexts
        <HelpTooltip text="You can define reusable descriptions of your domain and architecture in your knowledge pack, and pull them into the prompt here." />
      </label>
      <Select
        onChange={onChange}
        style={{ width: 300 }}
        options={contexts}
        value={value}
        defaultValue="base"
      />
    </div>
  );
}

export default ContextChoice;
