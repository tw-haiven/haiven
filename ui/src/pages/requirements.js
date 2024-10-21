// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { fetchSSE } from "../app/_fetch_sse";
import { parse } from "best-effort-json-parser";
import {
  Alert,
  Button,
  Card,
  Drawer,
  Input,
  Space,
  Spin,
  Select,
  message,
} from "antd";
const { TextArea } = Input;
import { RiChat2Line, RiCheckboxMultipleBlankFill } from "react-icons/ri";
import ReactMarkdown from "react-markdown";
import { RiPushpin2Line } from "react-icons/ri";

import ChatExploration from "./_chat_exploration";
import ContextChoice from "../app/_context_choice";
import PromptPreview from "../app/_prompt_preview";
import HelpTooltip from "../app/_help_tooltip";
import Disclaimer from "./_disclaimer";
import { addToPinboard } from "../app/_pinboard";

let ctrl;

const RequirementsBreakdown = ({ contexts, models }) => {
  const [scenarios, setScenarios] = useState([]);
  const [isLoading, setLoading] = useState(false);
  const [selectedContext, setSelectedContext] = useState("");
  const [promptInput, setPromptInput] = useState("");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerTitle, setDrawerTitle] = useState("Explore requirement");
  const [chatContext, setChatContext] = useState({});
  const [variations, setVariations] = useState([
    { value: "workflow", label: "By workflow" },
    { value: "timeline", label: "By timeline" },
    { value: "data-boundaries", label: "By data boundaries" },
    { value: "operational-boundaries", label: "By operational boundaries" },
  ]);
  const [selectedVariation, setSelectedVariation] = useState(variations[0]);
  const placeholderHelp = "Describe the high level requirements to break down";

  const router = useRouter();

  function abortLoad() {
    ctrl && ctrl.abort();
    setLoading(false);
  }

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

  const onPin = (id) => {
    const timestamp = Math.floor(Date.now()).toString();
    addToPinboard(
      timestamp,
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

  const onSubmitPrompt = () => {
    abortLoad();
    ctrl = new AbortController();
    setLoading(true);

    const uri = "/api/requirements?variation=" + selectedVariation;

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
            message.warning(
              "Model failed to respond rightly, please rewrite your message and try again",
            );
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
              <h1>Requirements Breakdown</h1>
              <p>
                Haiven will help you break down your requirement into multiple
                work packages.
              </p>
            </div>
            <div className="prompt-chat-options-section">
              <div className="user-input">
                <label>
                  High level description of your requirement
                  <HelpTooltip text={placeholderHelp} />
                </label>
                <TextArea
                  placeholder={placeholderHelp}
                  value={promptInput}
                  onChange={(e, v) => {
                    setPromptInput(e.target.value);
                  }}
                  rows={20}
                />
              </div>
              <ContextChoice
                onChange={setSelectedContext}
                contexts={contexts}
                value={selectedContext?.key}
              />
              <div className="user-input">
                {/* <PromptPreview buildRenderPromptRequest={buildRequestData} /> */}
                <label>
                  Style of breakdown
                  <HelpTooltip text="There are different approaches to breaking down a requirement into smaller work packages, try different ones and see which one fits your situation best." />
                </label>
                <Select
                  onChange={setSelectedVariation}
                  style={{ marginBottom: "1em" }}
                  options={variations}
                  value={selectedVariation}
                  defaultValue="workflow"
                />
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
          </div>
          <div
            style={{ height: "100%", display: "flex", flexDirection: "column" }}
          >
            <Disclaimer models={models} />
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
                        <Button
                          type="link"
                          key="explore"
                          onClick={() => onPin(i)}
                        >
                          <RiPushpin2Line style={{ fontSize: "large" }} />
                        </Button>,
                      ]}
                    >
                      <div className="scenario-card-content">
                        <h3>{scenario.title}</h3>
                        <ReactMarkdown className="scenario-summary">
                          {scenario.summary}
                        </ReactMarkdown>
                      </div>
                    </Card>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default RequirementsBreakdown;
