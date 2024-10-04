// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { fetchSSE } from "../app/_fetch_sse";
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
  const [modelOutputFailed, setModelOutputFailed] = useState(false);
  const router = useRouter();

  function abortLoad() {
    ctrl && ctrl.abort("User aborted");
    setLoading(false);
  }

  function formatModel(model) {
    if (model === "azure-gpt4") {
      return "GPT-4";
    }
    return model;
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
    setModelOutputFailed(false);
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
            setModelOutputFailed(true);
            console.log("response is not parseable into an array");
          }
        },
      },
    );
  };

  const placeholderHelp =
    "Describe who the users are, what assets you need to protect, and how data flows through your system";

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
        <div className="prompt-chat-container">
          <div className="prompt-chat-options-container">
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
                  rows={18}
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

              {modelOutputFailed && (
                <Space
                  direction="vertical"
                  style={{ width: "100%", marginTop: "5px" }}
                >
                  <Alert
                    message="Model failed to respond rightly"
                    description="Please rewrite your message and try again"
                    type="warning"
                  />
                </Space>
              )}
            </div>
          </div>

          <div
            style={{ height: "100%", display: "flex", flexDirection: "column" }}
          >
            <div className="disclaimer" style={{ color: "#" }}>
              AI model: <b>{formatModel(models.chat)}</b>
              &nbsp;|&nbsp;AI-generated content may be incorrect. Validate
              important information.
            </div>
            <div
              className={"scenarios-collection " + displayMode + "-display"}
              style={{ height: "95%", background: "#F5F5F5" }}
            >
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
