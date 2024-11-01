// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState } from "react";
import { fetchSSE } from "../app/_fetch_sse";
import { MenuFoldOutlined } from "@ant-design/icons";
import { RiStackLine, RiGridLine, RiFileCopyLine } from "react-icons/ri";

import {
  Card,
  Drawer,
  Spin,
  Button,
  Radio,
  Input,
  message,
  Collapse,
} from "antd";
const { TextArea } = Input;
import ScenariosPlotProbabilityImpact from "./_plot_prob_impact";
import { parse } from "best-effort-json-parser";
import { useRouter } from "next/router";
import ContextChoice from "../app/_context_choice";
import PromptPreview from "../app/_prompt_preview";
import HelpTooltip from "../app/_help_tooltip";
import Disclaimer from "./_disclaimer";
import CardActions, { scenarioToText } from "../app/_card_actions";
import ChatExploration from "./_chat_exploration";

let ctrl;

const ThreatModelling = ({ contexts, models }) => {
  const [scenarios, setScenarios] = useState([]);
  const [isLoading, setLoading] = useState(false);
  const [displayMode, setDisplayMode] = useState("grid");
  const [selectedContext, setSelectedContext] = useState("");
  const [promptInput, setPromptInput] = useState("");
  const [isExpanded, setIsExpanded] = useState(true);
  const [drawerTitle, setDrawerTitle] = useState("");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [chatContext, setChatContext] = useState({});

  const router = useRouter();

  function abortLoad() {
    ctrl && ctrl.abort("User aborted");
    setLoading(false);
  }

  const handleContextSelection = (value) => {
    setSelectedContext(value);
  };

  const onSelectDisplayMode = (event) => {
    setDisplayMode(event.target.value);
  };

  const onCollapsibleIconClick = (e) => {
    setIsExpanded(!isExpanded);
  };

  const onCopyAll = () => {
    const allScenarios = scenarios.map(scenarioToText);
    navigator.clipboard.writeText(allScenarios.join("\n\n\n"));
    message.success("Content copied successfully!");
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
    abortLoad();
    ctrl = new AbortController();
    setLoading(true);
    setIsExpanded(false);

    const uri = "/api/prompt";

    let ms = "";
    let output = [];

    fetchSSE(
      uri,
      {
        method: "POST",
        signal: ctrl.signal,
        body: JSON.stringify(buildRequestData()),
      },
      {
        json: true,
        onErrorHandle: () => {
          abortLoad(ctrl);
        },
        onFinish: () => {
          setLoading(false);
        },
        onMessageHandle: (data) => {
          ms += data.data;
          try {
            output = parse(ms || "[]");
          } catch (error) {
            console.log("error", error);
          }
          if (Array.isArray(output)) {
            setScenarios(output);
          } else {
            message.warning(
              "Model failed to respond rightly, please rewrite your message and try again",
            );
            console.log("response is not parseable into an array");
            abortLoad(ctrl);
          }
        },
      },
    );
  };

  const placeholderHelp =
    "Describe your users, the assets to protect, and how data flows through your system.";

  const promptMenu = (
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
            disabled={isLoading}
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
      children: promptMenu,
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
            <div className="prompt-chat-header">
              <h1 className="title-for-collapsed-panel">Threat Modelling</h1>
              {isLoading && (
                <div className="user-input">
                  <Spin />
                  <Button
                    type="secondary"
                    danger
                    onClick={abortLoad}
                    style={{ marginLeft: "1em" }}
                  >
                    Stop
                  </Button>
                </div>
              )}
              {scenarios && scenarios.length > 0 && (
                <Button type="link" className="copy-all" onClick={onCopyAll}>
                  <RiFileCopyLine fontSize="large" /> COPY ALL
                </Button>
              )}
              {scenarios && scenarios.length > 0 && (
                <div className="scenarios-actions">
                  <Radio.Group
                    className="display-mode-choice"
                    onChange={onSelectDisplayMode}
                    defaultValue="grid"
                    size="small"
                  >
                    <Radio.Button value="grid">
                      <RiStackLine /> CARD VIEW
                    </Radio.Button>
                    <Radio.Button value="plot">
                      <RiGridLine /> MATRIX VIEW
                    </Radio.Button>
                  </Radio.Group>
                </div>
              )}
            </div>
            <div className={"scenarios-collection " + displayMode + "-display"}>
              <div className="cards-container with-display-mode">
                {scenarios.map((scenario, i) => {
                  return (
                    <Card title={scenario.title} key={i} className="scenario">
                      <div className="scenario-card-content">
                        {scenario.category && (
                          <div className="card-prop stackable">
                            <div className="card-prop-name">Category</div>
                            <div className="card-prop-value">
                              {scenario.category}
                            </div>
                          </div>
                        )}
                        <div className="card-prop-name">Description</div>
                        <div className="scenario-summary">
                          {scenario.summary}
                        </div>
                        {scenario.probability && (
                          <div className="card-prop stackable">
                            <div className="card-prop-name">Probability</div>
                            <div className="card-prop-value">
                              {scenario.probability}
                            </div>
                          </div>
                        )}
                        {scenario.impact && (
                          <div className="card-prop stackable">
                            <div className="card-prop-name">
                              Potential impact
                            </div>
                            <div className="card-prop-value">
                              {scenario.impact}
                            </div>
                          </div>
                        )}
                      </div>
                      <CardActions
                        scenario={scenario}
                        prompt={promptInput}
                        scenarioQueries={scenarioQueries}
                        chatExploreTitle="Explore Scenario"
                        previousFraming="We are brainstorming security threat scenarios for our application."
                        selectedContext={selectedContext}
                      />
                    </Card>
                  );
                })}
                <div
                  className="scenarios-plot-container"
                  style={{ display: displayMode == "plot" ? "block" : "none" }}
                >
                  <ScenariosPlotProbabilityImpact
                    scenarios={scenarios}
                    visible={displayMode == "plot"}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default ThreatModelling;
