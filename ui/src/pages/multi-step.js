// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState, useEffect } from "react";
import { fetchSSE } from "../app/_fetch_sse";
import { Drawer, Card, Spin, Button, Input, Collapse } from "antd";
const { TextArea } = Input;
import ChatExploration from "./_chat_exploration";
import { parse } from "best-effort-json-parser";
import {
  RiFileCopyLine,
  RiChat2Line,
  RiCheckboxMultipleBlankLine,
  RiCheckboxMultipleBlankFill,
} from "react-icons/ri";
import ReactMarkdown from "react-markdown";
import ContextChoice from "../app/_context_choice";
import PromptPreview from "../app/_prompt_preview";
import HelpTooltip from "../app/_help_tooltip";
import Disclaimer from "./_disclaimer";

let ctrl;

const MultiStep = ({ contexts, models }) => {
  const [scenarios, setScenarios] = useState([]);
  const [isLoading, setLoading] = useState(false);
  const [displayMode, setDisplayMode] = useState("grid");
  const [selectedContext, setSelectedContext] = useState("");
  const [promptInput, setPromptInput] = useState("");

  const [cardExplorationDrawerOpen, setCardExplorationDrawerOpen] =
    useState(false);
  const [cardExplorationDrawerTitle, setCardExplorationDrawerTitle] =
    useState("Explore");

  const [currentAbortController, setCurrentAbortController] = useState();

  const [followUpResults, setFollowUpResults] = useState({});
  const [chatContext, setChatContext] = useState({});

  // hard coding a "workflow" for the purpose of the spike
  // This would ultimately come from the backend
  const workflowStoryValidation = {
    workflowId: "story-validation",
    firstStep: {
      id: "guided-story-validation",
      title: "Story validation",
      description: "Guide the user through the story validation process",
    },
    followUps: [
      {
        id: "guided-story-validation-01-summary",
        description: "Create a summary",
      },
    ],
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

  const onCopyAll = () => {
    const allScenarios = scenarios.map(scenarioToText);
    navigator.clipboard.writeText(allScenarios.join("\n\n"));
  };

  const onCopyOne = (id) => {
    navigator.clipboard.writeText(scenarioToText(scenarios[id]));
  };

  const onCopyFollowUp = (id) => {
    navigator.clipboard.writeText(followUpResults[id]);
  };

  const buildRequestDataFirstStep = () => {
    return {
      userinput: promptInput,
      context: selectedContext,
      promptid: workflowStoryValidation.firstStep.id,
    };
  };

  const buildRequestDataSecondStep = (followUpId) => {
    return {
      userinput: promptInput,
      context: selectedContext,
      promptid: followUpId,

      scenarios: scenarios.map(scenarioToJson), // title, content
      previous_promptid: workflowStoryValidation.firstStep.id,
    };
  };

  useEffect(() => {
    workflowStoryValidation.followUps.forEach((followUp) => {
      followUpResults[followUp.id] = "";
    });
    setFollowUpResults(followUpResults);
  }, []);

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

  const followUpButtons = (
    <>
      {workflowStoryValidation.followUps.map((followUp, i) => {
        return (
          <Button
            className="prompt-preview-copy-btn"
            onClick={() => onFollowUp(followUp.id)}
            size="small"
          >
            <RiCheckboxMultipleBlankLine />
            {followUp.description}
          </Button>
        );
      })}
    </>
  );

  const followUpCollapseItems = workflowStoryValidation.followUps.map(
    (followUp, i) => {
      return {
        key: followUp.id,
        label: followUp.title,
        children: (
          <div className="second-step-section">
            <p>{followUp.description}</p>
            {followUpResults[followUp.id] && (
              <>
                <div className="generated-text-results">
                  <Button
                    onClick={onCopyFollowUp(followUp.id)}
                    className="icon-button"
                  >
                    <RiFileCopyLine />
                  </Button>
                  <ReactMarkdown>{followUpResults[followUp.id]}</ReactMarkdown>
                </div>
              </>
            )}
          </div>
        ),
      };
    },
  );

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
              <h1>{workflowStoryValidation.firstStep.title}</h1>
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
                <PromptPreview
                  buildRenderPromptRequest={buildRequestDataFirstStep}
                />
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

          <div
            style={{ height: "100%", display: "flex", flexDirection: "column" }}
          >
            <Disclaimer models={models} />
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
                  {followUpButtons}
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
                        <div className="card-prop-name">Description</div>
                        <div className="scenario-summary">
                          {scenario.summary}
                        </div>
                      </div>
                    </Card>
                  );
                })}
                <Collapse
                  items={followUpCollapseItems}
                  className="second-step-collapsable"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default MultiStep;
