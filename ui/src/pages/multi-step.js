// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState, useEffect } from "react";
import { fetchSSE } from "../app/_fetch_sse";
import {
  Drawer,
  Card,
  Spin,
  Button,
  Input,
  Collapse,
  Tooltip,
  message,
} from "antd";
const { TextArea } = Input;
import ChatExploration from "./_chat_exploration";
import { parse } from "best-effort-json-parser";
import { RiFileCopyLine, RiChat2Line, RiPushpinLine } from "react-icons/ri";
import { MenuFoldOutlined } from "@ant-design/icons";
import ReactMarkdown from "react-markdown";
import ContextChoice from "../app/_context_choice";
import PromptPreview from "../app/_prompt_preview";
import HelpTooltip from "../app/_help_tooltip";
import Disclaimer from "./_disclaimer";
import { addToPinboard } from "../app/_local_store";
import { getPromptsGuided } from "../app/_boba_api";

let ctrl;

const MultiStep = ({ contexts, models }) => {
  const [scenarios, setScenarios] = useState([]);
  const [isLoading, setLoading] = useState(false);
  const [selectedContext, setSelectedContext] = useState("");
  const [promptInput, setPromptInput] = useState("");
  const [promptConfiguration, setPromptConfiguration] = useState({});

  const [cardExplorationDrawerOpen, setCardExplorationDrawerOpen] =
    useState(false);
  const [cardExplorationDrawerTitle, setCardExplorationDrawerTitle] =
    useState("Explore");

  const [currentAbortController, setCurrentAbortController] = useState();

  const [followUpResults, setFollowUpResults] = useState({});
  const [chatContext, setChatContext] = useState({});
  const [isExpanded, setIsExpanded] = useState(true);

  useEffect(() => {
    const firstStepPrompt = "guided-story-validation";
    getPromptsGuided((data) => {
      const firstStepEntry = data.find(
        (entry) => entry.value === firstStepPrompt,
      );
      firstStepEntry.followUps.forEach((followUp) => {
        followUpResults[followUp.identifier] = "";
      });
      setFollowUpResults(followUpResults);
      setPromptConfiguration(firstStepEntry);
    });
  }, []);

  const onCollapsibleIconClick = (e) => {
    setIsExpanded(!isExpanded);
  };

  function abortLoad() {
    ctrl && ctrl.abort("User aborted");
    setLoading(false);
  }

  function abortCurrentLoad() {
    setLoading(false);
    currentAbortController && currentAbortController.abort("User aborted");
  }

  const handleContextSelection = (value) => {
    setSelectedContext(value);
  };

  const onExplore = (id) => {
    setCardExplorationDrawerTitle("Explore scenario: " + scenarios[id].title);
    setChatContext({
      id: id,
      originalPrompt: promptInput,
      type: "explore-endpoint-doesnt-exist-yet", // TODO: Exploration will not work yet, no specific endpoint for it yet
      ...scenarios[id],
    });
    setCardExplorationDrawerOpen(true);
  };

  const scenarioToText = (scenario) => {
    return "# Title: " + scenario.title + "\nDescription: " + scenario.summary;
  };

  const scenarioToJson = (scenario) => {
    return { title: scenario.title, content: scenario.summary };
  };

  const copySuccess = () => {
    message.success("Content copied successfully!");
  };

  const onCopyAll = () => {
    const allScenarios = scenarios.map(scenarioToText);
    navigator.clipboard.writeText(allScenarios.join("\n\n"));
    copySuccess();
  };

  const onCopy = (id) => {
    navigator.clipboard.writeText(scenarioToText(scenarios[id]));

    copySuccess();
  };

  const onPin = (id) => {
    const timestamp = Math.floor(Date.now()).toString();
    addToPinboard(
      timestamp,
      "## " + scenarios[id].title + "\n\n" + scenarios[id].summary,
    );
  };

  const onCopyFollowUp = (id) => {
    navigator.clipboard.writeText(followUpResults[id]);
    copySuccess();
  };

  const buildRequestDataFirstStep = () => {
    return {
      userinput: promptInput,
      context: selectedContext,
      promptid: promptConfiguration.identifier,
    };
  };

  const buildRequestDataSecondStep = (followUpId) => {
    return {
      userinput: promptInput,
      context: selectedContext,
      promptid: followUpId,

      scenarios: scenarios.map(scenarioToJson), // title, content
      previous_promptid: promptConfiguration.identifier,
    };
  };

  const sendFirstStepPrompt = () => {
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
        body: JSON.stringify(buildRequestDataFirstStep()),
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
            if (ms.includes("Error code:")) {
              message.error(ms);
            } else {
              message.warning(
                "Model failed to respond rightly, please rewrite your message and try again",
              );
            }
            console.log("response is not parseable into an array");
          }
        },
      },
    );
  };

  const sendFollowUpPrompt = (apiEndpoint, onData, followUpId) => {
    abortCurrentLoad();
    const ctrl = new AbortController();
    setCurrentAbortController(ctrl);
    setLoading(true);

    let ms = "";

    fetchSSE(
      apiEndpoint,
      {
        body: JSON.stringify(buildRequestDataSecondStep(followUpId)),
        signal: ctrl.signal,
      },
      {
        onErrorHandle: () => {
          abortLoad(ctrl);
        },
        onMessageHandle: (data) => {
          try {
            ms += data;

            onData(ms);
          } catch (error) {
            console.log("error", error, "data received", "'" + data + "'");
          }
        },
        onFinish: () => {
          setLoading(false);
        },
      },
    );
  };

  const onFollowUp = (followUpId) => {
    sendFollowUpPrompt(
      "/api/prompt/follow-up",
      (result) => {
        console.log("updating follow up result", followUpId);
        followUpResults[followUpId] = result;
        setFollowUpResults(followUpResults);
      },
      followUpId,
    );
  };

  const placeholderHelp =
    "Describe who the users are, what assets you need to protect, and how data flows through your system";

  const followUpCollapseItems = promptConfiguration.followUps?.map(
    (followUp, i) => {
      return {
        key: followUp.identifier,
        label: followUp.title,
        children: (
          <div className="second-step-section">
            <p>{followUp.help_prompt_description}</p>
            <Button
              onClick={() => onFollowUp(followUp.identifier)}
              size="small"
              className="go-button"
            >
              GENERATE
            </Button>
            {followUpResults[followUp.identifier] && (
              <>
                <div className="generated-text-results">
                  <Button
                    type="link"
                    onClick={() => {
                      onCopyFollowUp(followUp.identifier);
                    }}
                    className="icon-button"
                  >
                    <RiFileCopyLine fontSize="large" />
                  </Button>
                  <ReactMarkdown>
                    {followUpResults[followUp.identifier]}
                  </ReactMarkdown>
                </div>
              </>
            )}
          </div>
        ),
      };
    },
  );

  const promptMenu = (
    <div>
      <div className="prompt-chat-options-section">
        <h1>{promptConfiguration.title}</h1>
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
          <PromptPreview buildRenderPromptRequest={buildRequestDataFirstStep} />
          <Button
            onClick={sendFirstStepPrompt}
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
      label: isExpanded ? "Hide Prompt Panel" : "Show Prompt Panel",
      children: promptMenu,
    },
  ];

  return (
    <>
      <Drawer
        title={cardExplorationDrawerTitle}
        mask={false}
        open={cardExplorationDrawerOpen}
        destroyOnClose={true}
        onClose={() => setCardExplorationDrawerOpen(false)}
        size={"large"}
      >
        <ChatExploration
          context={chatContext}
          user={{
            name: "User",
            avatar: "/boba/user-5-fill-dark-blue.svg",
          }}
          scenarioQueries={[]}
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
          <Disclaimer models={models} />
          <h1 className="title-for-collapsed-panel">
            {promptConfiguration.title}
          </h1>
          <div className={"scenarios-collection grid-display"}>
            {scenarios && scenarios.length > 0 && (
              <Button type="link" className="copy-all" onClick={onCopyAll}>
                <RiFileCopyLine fontSize="large" /> COPY ALL
              </Button>
            )}
            <div className="cards-container">
              {scenarios.map((scenario, i) => {
                return (
                  <Card
                    title={scenario.title}
                    key={i}
                    className="scenario"
                    actions={[
                      <Tooltip title="Chat With Haiven">
                        <Button type="link" onClick={() => onExplore(i)}>
                          <RiChat2Line fontSize="large" />
                        </Button>
                      </Tooltip>,
                      <Tooltip title="Copy">
                        <Button type="link" onClick={() => onCopy(i)}>
                          <RiFileCopyLine fontSize="large" />
                        </Button>
                      </Tooltip>,
                      <Tooltip title="Pin to pinboard">
                        <Button type="link" onClick={() => onPin(i)}>
                          <RiPushpinLine fontSize="large" />
                        </Button>
                      </Tooltip>,
                    ]}
                  >
                    <div className="scenario-card-content">
                      <ReactMarkdown className="scenario-summary">
                        {scenario.summary}
                      </ReactMarkdown>
                    </div>
                  </Card>
                );
              })}
            </div>
            {scenarios.length > 0 && (
              <div className="follow-up-container">
                <div style={{ marginTop: "1em" }}>
                  <h3>What you can do next</h3>
                </div>
                <Collapse
                  items={followUpCollapseItems}
                  className="second-step-collapsable"
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default MultiStep;
