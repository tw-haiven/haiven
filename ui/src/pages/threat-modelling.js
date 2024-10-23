// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { fetchSSE } from "../app/_fetch_sse";
import { MenuFoldOutlined } from "@ant-design/icons";
import {
  Alert,
  Drawer,
  Card,
  Space,
  Spin,
  Button,
  Radio,
  Input,
  Select,
  message,
  Collapse,
} from "antd";
const { TextArea } = Input;
import ScenariosPlotProbabilityImpact from "./_plot_prob_impact";
import ChatExploration from "./_chat_exploration";
import { parse } from "best-effort-json-parser";
import {
  RiStackLine,
  RiGridLine,
  RiChat2Line,
  RiCheckboxMultipleBlankLine,
  RiCheckboxMultipleBlankFill,
} from "react-icons/ri";

import ContextChoice from "../app/_context_choice";
import PromptPreview from "../app/_prompt_preview";
import HelpTooltip from "../app/_help_tooltip";
import Disclaimer from "./_disclaimer";

let ctrl;

const ThreatModelling = ({ contexts, models }) => {
  const [scenarios, setScenarios] = useState([]);
  const [isLoading, setLoading] = useState(false);
  const [displayMode, setDisplayMode] = useState("grid");
  const [selectedContext, setSelectedContext] = useState("");
  const [promptInput, setPromptInput] = useState("");
  const [explorationDrawerOpen, setExplorationDrawerOpen] = useState(false);
  const [explorationDrawerTitle, setExplorationDrawerTitle] =
    useState("Explore scenario");
  const [chatContext, setChatContext] = useState({});
  const [isExpanded, setIsExpanded] = useState(true);

  const router = useRouter();

  function abortLoad() {
    ctrl && ctrl.abort("User aborted");
    setLoading(false);
  }

  const handleContextSelection = (value) => {
    setSelectedContext(value);
  };

  const onExplore = (id) => {
    setExplorationDrawerTitle("Explore scenario: " + scenarios[id].title);
    setChatContext({
      id: id,
      originalPrompt: promptInput,
      type: "threat-modelling",
      ...scenarios[id],
    });
    setExplorationDrawerOpen(true);
  };

  const onSelectDisplayMode = (event) => {
    setDisplayMode(event.target.value);
  };

  const onCollapsibleIconClick = (e) => {
    setIsExpanded(!isExpanded);
  };

  const scenarioToText = (scenario) => {
    return (
      "# Title: " +
      scenario.title +
      "\n\nCategory: " +
      scenario.category +
      "\nDescription: " +
      scenario.summary +
      "\nProbability: " +
      scenario.probability +
      "\nImpact: " +
      scenario.impact
    );
  };

  const onCopyAll = () => {
    const allScenarios = scenarios.map(scenarioToText);
    navigator.clipboard.writeText(allScenarios.join("\n\n"));
  };

  const onCopyOne = (id) => {
    navigator.clipboard.writeText(scenarioToText(scenarios[id]));
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
          setIsExpanded(false);
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
    "Describe who the users are, what assets you need to protect, and how data flows through your system";

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
        <div className="user-input">
          {isLoading && (
            <div>
              <Spin />
              <Button
                type="primary"
                danger
                onClick={abortLoad}
                style={{ marginLeft: "1em" }}
              >
                Stop
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const collapseItem = [
    {
      key: "1",
      label: isExpanded ? (
        <div>Hide Prompt Panel</div>
      ) : (
        <div className="prompt-options-panel-header">
          <div>Show Prompt Panel</div>
          <Disclaimer models={models} />
        </div>
      ),
      children: promptMenu,
    },
  ];

  return (
    <>
      <Drawer
        title={explorationDrawerTitle}
        mask={false}
        open={explorationDrawerOpen}
        destroyOnClose={true}
        onClose={() => setExplorationDrawerOpen(false)}
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
            className={`prompt-chat-options-container ${isExpanded ? "" : "collapsed"}`}
            items={collapseItem}
            defaultActiveKey={["1"]}
            ghost={isExpanded}
            activeKey={isExpanded ? "1" : ""}
            onChange={onCollapsibleIconClick}
            expandIcon={() => (
              <MenuFoldOutlined rotate={isExpanded ? 0 : 180} />
            )}
          />
          <div className="content-container">
            {isExpanded ? <Disclaimer models={models} /> : null}
            <h1
              className={`title-for-collapsed-panel ${isExpanded ? "hide" : "show"}`}
            >
              Threat Modelling
            </h1>
            <div className={"scenarios-collection " + displayMode + "-display"}>
              {scenarios && scenarios.length > 0 && (
                <div className="scenarios-actions">
                  <Button
                    className="prompt-preview-copy-btn"
                    onClick={onCopyAll}
                    size="small"
                  >
                    <RiCheckboxMultipleBlankLine /> COPY ALL
                  </Button>
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
              <div className="cards-container with-display-mode">
                {scenarios.map((scenario, i) => {
                  return (
                    <Card
                      hoverable
                      key={i}
                      className="scenario"
                      actions={[
                        <Button
                          type="link"
                          key="explore"
                          onClick={() => onExplore(i)}
                        >
                          <RiChat2Line style={{ fontSize: "large" }} />
                        </Button>,
                        <Button
                          type="link"
                          key="explore"
                          onClick={() => onCopyOne(i)}
                        >
                          <RiCheckboxMultipleBlankFill
                            style={{ fontSize: "large" }}
                          />
                        </Button>,
                      ]}
                    >
                      <div className="scenario-card-content">
                        <h3>{scenario.title}</h3>
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
