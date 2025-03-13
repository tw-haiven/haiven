// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { addToPinboard } from "../app/_local_store";
import { RiFileCopyLine, RiChat2Line, RiPushpinLine } from "react-icons/ri";
import { Button, Tooltip } from "antd";
import { toast } from "react-toastify";
import { scenarioToText } from "./_dynamic_data_renderer";

export default function CardActions({ scenario, onExploreHandler }) {
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

  return (
    <div className="card-actions-footer">
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
