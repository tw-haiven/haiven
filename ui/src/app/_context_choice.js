// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useState } from "react";
import { Select, Tooltip, Button } from "antd";
import { RiAddBoxLine } from "react-icons/ri";
import HelpTooltip from "./_help_tooltip";
import AddContext from "../app/_add_context";

function ContextChoice({ contexts, onChange }) {
  const [isAddingContext, setIsAddingContext] = useState(false);

  const tooltipMessage =
    contexts.length === 1
      ? "There are no contexts configured in the knowledge pack. Contexts can provide project-specific information about domain and architecture that Haiven can reuse across prompts."
      : "Choose a context from your knowledge pack that is relevant to the domain, architecture, or team you are working on.";
  return (
    <div className="user-input">
      <div className="input-context-label">
        <label>
          Select your context
          <HelpTooltip
            text={tooltipMessage}
            testid="context-selection-tooltip"
          />
        </label>
        <Tooltip title="Add your project context to be reused in your Haiven inputs. This will be included in the context dropdown.">
          <Button
            type="link"
            className="add-context-icon-button"
            onClick={() => setIsAddingContext(true)}
          >
            <RiAddBoxLine fontSize="large" />
            Add Context
          </Button>
        </Tooltip>
      </div>

      <Select
        onChange={onChange}
        options={contexts}
        data-testid="context-select"
        mode="multiple"
        placeholder="Please select the context(s)"
        maxCount="3"
      />
      <AddContext
        isAddingContext={isAddingContext}
        setIsAddingContext={setIsAddingContext}
      />
    </div>
  );
}

export default ContextChoice;
