// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { addToPinboard } from "../app/_local_store";
import { RiFileCopyLine, RiChat2Line, RiPushpinLine } from "react-icons/ri";
import { Button, Tooltip, Checkbox } from "antd";
import { useState } from "react";
import { toast } from "react-toastify";

export const scenarioToText = (scenario) => {
  let markdown = `## ${scenario.title}\n\n`;
  Object.keys(scenario).map((key) => {
    if (
      key !== "title" &&
      key !== "hidden" &&
      key !== "exclude" &&
      key !== "id"
    ) {
      const value = scenario[key];
      if (Array.isArray(value)) {
        markdown += `**${key.charAt(0).toUpperCase() + key.slice(1)}:**\n${value.map((item) => `- ${item}`).join("\n")}\n\n`;
      } else {
        markdown += `**${key.charAt(0).toUpperCase() + key.slice(1)}:**\n${value}\n\n`;
      }
    }
  });
  return markdown;
};

export default function CardActions({
  scenario,
  onExploreHandler,
  onScenarioSelectionHandler,
}) {
  const [selected, setSelected] = useState(true);

  const copySuccess = () => {
    toast.success("Content copied successfully!");
  };

  const onCopyOne = (scenario) => {
    navigator.clipboard.writeText(scenarioToText(scenario));
    copySuccess();
  };

  const onPin = () => {
    const timestamp = Math.floor(Date.now()).toString();
    addToPinboard(timestamp, scenarioToText(scenario));
  };

  const onSelectionChanged = (e) => {
    setSelected(e.target.checked);
    onScenarioSelectionHandler(e);
  };

  return (
    <div className="card-actions-footer">
      <div className="selection-container">
        {onScenarioSelectionHandler !== undefined && (
          <Checkbox
            onChange={onSelectionChanged}
            className="include-action"
            checked={selected}
            data-testid="scenario-include-checkbox"
          >
            Include
          </Checkbox>
        )}
      </div>
      <div className="actions-container">
        {onExploreHandler && (
          <Tooltip title="Chat with Haiven" key="chat">
            <Button type="link" onClick={() => onExploreHandler(scenario)}>
              <RiChat2Line fontSize="large" />
            </Button>
          </Tooltip>
        )}
        <Tooltip title="Copy" key="copy">
          <Button type="link" onClick={() => onCopyOne(scenario)}>
            <RiFileCopyLine fontSize="large" />
          </Button>
        </Tooltip>
        <Tooltip title="Pin to pinboard" key="pin">
          <Button
            type="link"
            onClick={() => onPin()}
            style={{ paddingRight: "0" }}
          >
            <RiPushpinLine fontSize="large" />
          </Button>
        </Tooltip>
      </div>
    </div>
  );
}
