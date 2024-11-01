// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { addToPinboard } from "../app/_local_store";
import { RiFileCopyLine, RiChat2Line, RiPushpinLine } from "react-icons/ri";
import { Button, Tooltip, message } from "antd";

export const scenarioToText = (scenario) => {
  let markdown = `## ${scenario.title}\n\n`;
  Object.keys(scenario).map((key) => {
    if (key !== "title") {
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

export default function CardActions({ scenario, onExploreHandler }) {
  const copySuccess = () => {
    message.success("Content copied successfully!");
  };

  const onCopyOne = (scenario) => {
    navigator.clipboard.writeText(scenarioToText(scenario));
    copySuccess();
  };

  const onPin = () => {
    const timestamp = Math.floor(Date.now()).toString();
    addToPinboard(timestamp, scenarioToText(scenario));
  };

  return (
    <div className="card-actions-footer">
      <Tooltip title="Chat With Haiven" key="chat">
        <Button type="link" onClick={() => onExploreHandler(scenario)}>
          <RiChat2Line fontSize="large" />
        </Button>
      </Tooltip>
      <Tooltip title="Copy" key="copy">
        <Button type="link" onClick={() => onCopyOne(scenario)}>
          <RiFileCopyLine fontSize="large" />
        </Button>
      </Tooltip>
      <Tooltip title="Pin to pinboard" key="pin">
        <Button type="link" onClick={() => onPin()}>
          <RiPushpinLine fontSize="large" />
        </Button>
      </Tooltip>
    </div>
  );
}
