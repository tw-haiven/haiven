// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useState } from "react";
import { addToPinboard } from "../app/_local_store";
import { RiFileCopyLine, RiChat2Line, RiPushpinLine } from "react-icons/ri";
import { Button, Drawer, Tooltip, message } from "antd";
import ChatExploration from "../pages/_chat_exploration";

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

export default function CardActions({
  scenario,
  prompt,
  scenarioQueries,
  chatExploreTitle,
  selectedContext,
  previousFraming,
}) {
  const [drawerTitle, setDrawerTitle] = useState(chatExploreTitle);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [chatContext, setChatContext] = useState({});

  const copySuccess = () => {
    message.success("Content copied successfully!");
  };

  const onCopyOne = (scenario) => {
    navigator.clipboard.writeText(scenarioToText(scenario));
    copySuccess();
  };

  const onPin = (id) => {
    const timestamp = Math.floor(Date.now()).toString();
    addToPinboard(timestamp, scenarioToText(scenario));
  };

  const onExplore = () => {
    setDrawerTitle(chatExploreTitle + ": " + scenario.title);
    setChatContext({
      id: scenario.id,
      firstStepInput: prompt,
      previousFraming: previousFraming,
      context: selectedContext,
      itemSummary: scenarioToText(scenario),
      ...scenario,
    });
    setDrawerOpen(true);
  };

  return (
    <>
      <Drawer
        title={drawerTitle}
        mask={false}
        open={drawerOpen}
        destroyOnClose={true}
        onClose={() => setDrawerOpen(false)}
        size={"large"}
      >
        <ChatExploration
          context={chatContext}
          user={{ name: "User", avatar: "/boba/user-5-fill-dark-blue.svg" }}
          scenarioQueries={scenarioQueries}
        />
      </Drawer>
      <div className="card-actions-footer">
        <Tooltip title="Chat With Haiven" key="chat">
          <Button type="link" onClick={() => onExplore()}>
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
    </>
  );
}
