// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { fetchSSE } from "../app/_fetch_sse";
import { parse } from "best-effort-json-parser";
import { Alert, Button, Card, Drawer, Input, Space, Spin, Select } from "antd";
const { TextArea } = Input;
import { RiChat2Line, RiCheckboxMultipleBlankFill } from "react-icons/ri";

import ChatExploration from "./_chat_exploration";
import ContextChoice from "../app/_context_choice";
import PromptPreview from "../app/_prompt_preview";

let ctrl;

const RequirementsBreakdown = ({ contexts }) => {
  const [scenarios, setScenarios] = useState([]);
  const [isLoading, setLoading] = useState(false);
  const [selectedContext, setSelectedContext] = useState("");
  const [promptInput, setPromptInput] = useState("");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerTitle, setDrawerTitle] = useState("Explore requirement");
  const [chatContext, setChatContext] = useState({});
  const [modelOutputFailed, setModelOutputFailed] = useState(false);
  const router = useRouter();

  function abortLoad() {
    ctrl && ctrl.abort();
    setLoading(false);
  }

  const handleContextSelection = (value) => {
    setSelectedContext(value);
  };

  const onExplore = (id) => {
    setDrawerTitle("Explore requirement: " + scenarios[id].title);
    setChatContext({
      id: id,
      originalPrompt: promptInput,
      type: "requirements",
      ...scenarios[id],
    });
    setDrawerOpen(true);
  };

  const onCopy = (id) => {
    navigator.clipboard.writeText(
      "## " + scenarios[id].title + "\n\n" + scenarios[id].summary,
    );
  };

  const buildRequestData = () => {
    return {
      userinput: promptInput,
      context: selectedContext,
      promptid: "guided-requirements",
    };
  };

  const onSubmitPrompt = (event) => {
    setModelOutputFailed(false);
    abortLoad();
    ctrl = new AbortController();
    setLoading(true);

    const uri = "/api/prompt";

    const requestData = buildRequestData();

    let ms = "";
    let output = [];

    fetchSSE(
      uri,
      {
        method: "POST",
        credentials: "include",
        signal: ctrl.signal,
        body: JSON.stringify(requestData),
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
            "Write behavior-driven development scenarios for this requirement",
            "Break down this requirement into smaller requirements",
            "What could potentially go wrong?",
          ]}
        />
      </Drawer>

      <div id="canvas">
        <div className="prompt-chat-container">
          <div className="prompt-chat-options-container">
            <div className="prompt-chat-options-section">
              <h1>Requirements breakdown</h1>
              <p>
                Haiven will help you break down your requirement into multiple
                scenarios.
              </p>
            </div>
            <div className="prompt-chat-options-section">
              <div className="user-input">
                <label>High level description of your requirement</label>
                <TextArea
                  placeholder="Describe the high level requirements to break down"
                  value={promptInput}
                  onChange={(e, v) => {
                    setPromptInput(e.target.value);
                  }}
                  rows={20}
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
                  <div style={{ marginTop: 10 }}>
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

          <div className={"scenarios-collection grid-display"}>
            <div className="cards-container">
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
                        onClick={() => onCopy(i)}
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
                      <div className="scenario-summary">{scenario.summary}</div>
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
                          <div className="card-prop-name">Potential impact</div>
                          <div className="card-prop-value">
                            {scenario.impact}
                          </div>
                        </div>
                      )}
                    </div>
                  </Card>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default RequirementsBreakdown;
