// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { Select } from "antd";
import HelpTooltip from "./_help_tooltip";

function ContextChoice({ contexts, value, onChange }) {
  const tooltipMessage =
    contexts.length === 1
      ? "There are no contexts configured in the knowledge pack. Contexts can provide project-specific information about domain and architecture that Haiven can reuse across prompts."
      : "Choose a context from your knowledge pack that is relevant to the domain, architecture, or team you are working on.";
  return (
    <div className="user-input">
      <label>
        Add your context
        <HelpTooltip text={tooltipMessage} />
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
