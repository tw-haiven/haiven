// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState } from "react";
import { fetchSSE } from "../app/_fetch_sse";
import { MenuFoldOutlined } from "@ant-design/icons";

import { Drawer, Button, Input, message, Collapse } from "antd";
const { TextArea } = Input;
import { parse } from "best-effort-json-parser";
import Disclaimer from "./_disclaimer";
import ContextChoice from "../app/_context_choice";
import PromptPreview from "../app/_prompt_preview";
import HelpTooltip from "../app/_help_tooltip";
import CardsList from "../app/_cards-list";
import { scenarioToText } from "../app/_card_actions";
import ChatExploration from "./_chat_exploration";

import useLoader from "../hooks/useLoader";

const ThreatModelling = ({ contexts, models }) => {
  const [scenarios, setScenarios] = useState([]);
  const { loading, abortLoad, startLoad, StopLoad } = useLoader();
  const [selectedContext, setSelectedContext] = useState("");
  const [promptInput, setPromptInput] = useState("");
  const [isExpanded, setIsExpanded] = useState(true);
  const [drawerTitle, setDrawerTitle] = useState("");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [chatContext, setChatContext] = useState({});

  const handleContextSelection = (value) => {
    setSelectedContext(value);
  };

  const onCollapsibleIconClick = (e) => {
    setIsExpanded(!isExpanded);
  };

  const onExplore = (scenario) => {
    setDrawerTitle("Explore Scenario: " + scenario.title);
    setChatContext({
      id: scenario.id,
      firstStepInput: promptInput,
      previousFraming:
        "We are brainstorming security threat scenarios for our application.",
      context: selectedContext,
      itemSummary: scenarioToText(scenario),
      ...scenario,
    });
    setDrawerOpen(true);
  };

  const buildRequestData = () => {
    return {
      userinput: promptInput,
      context: selectedContext,
      promptid: "guided-threat-modelling",
    };
  };

  const onSubmitPrompt = (event) => {
    setIsExpanded(false);

    const uri = "/api/prompt";

    let ms = "";
    let output = [];

    fetchSSE(
      uri,
      {
        method: "POST",
        signal: startLoad(),
        body: JSON.stringify(buildRequestData()),
      },
      {
        json: true,
        onErrorHandle: () => {
          abortLoad();
        },
        onFinish: () => {
          if (ms == "") {
            message.warning(
              "Model failed to respond rightly, please rewrite your message and try again",
            );
          }
          abortLoad();
        },
        onMessageHandle: (data) => {
          ms += data.data;
          ms = ms.trim().replace(/^[^[]+/, "");
          if (ms.startsWith("[")) {
            try {
              output = parse(ms || "[]");
            } catch (error) {
              console.log("ms", ms);
              console.log("error", error);
            }
            if (Array.isArray(output)) {
              setScenarios(output);
            } else {
              abortLoad();
              message.warning(
                "Model failed to respond rightly, please rewrite your message and try again",
              );
              console.log("response is not parseable into an array");
            }
          }
        },
      },
    );
  };

  const placeholderHelp =
    "Describe your users, the assets to protect, and how data flows through your system.";

  const promptPanel = (
    <div>
      <div className="prompt-chat-options-section">
        <h1>Threat Modelling</h1>
      </div>

      <div className="prompt-chat-options-section">
        <div className="user-input">
          <label>
            Your input
            <HelpTooltip text={placeholderHelp} />
          </label>
          <TextArea
            placeholder={placeholderHelp}
            value={promptInput}
            onChange={(e, v) => {
              setPromptInput(e.target.value);
            }}
            rows={10}
          />
        </div>
        <ContextChoice
          onChange={handleContextSelection}
          contexts={contexts}
          value={selectedContext?.key}
        />
        <div className="user-input">
          <PromptPreview buildRenderPromptRequest={buildRequestData} />
          <Button
            onClick={onSubmitPrompt}
            className="go-button"
            disabled={loading}
          >
            GENERATE
          </Button>
        </div>
      </div>
    </div>
  );

  const collapseItem = [
    {
      key: "1",
      label: isExpanded ? "Hide Prompt Panel" : "Show Prompt Panel",
      children: promptPanel,
    },
  ];

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
          user={{
            name: "User",
            avatar: "/boba/user-5-fill-dark-blue.svg",
          }}
          scenarioQueries={[
            "How could this scenario be prevented?",
            "Elaborate how you chose the probability for this scenario",
            "Elaborate how you chose the impact for this scenario",
          ]}
        />
      </Drawer>
      <div id="canvas">
        <div
          className={`prompt-chat-container ${isExpanded ? "" : "collapsed"}`}
        >
          <Collapse
            className="prompt-chat-options-container"
            items={collapseItem}
            defaultActiveKey={["1"]}
            ghost={isExpanded}
            activeKey={isExpanded ? "1" : ""}
            onChange={onCollapsibleIconClick}
            expandIcon={() => (
              <MenuFoldOutlined rotate={isExpanded ? 0 : 180} />
            )}
          />
          <div className="chat-container-wrapper">
            <Disclaimer models={models} />
            <CardsList
              scenarios={scenarios}
              title="Threat Modelling"
              matrixMode={true}
              onExplore={onExplore}
              stopLoadComponent={<StopLoad />}
            />
          </div>
        </div>
      </div>
    </>
  );
};

export default ThreatModelling;
