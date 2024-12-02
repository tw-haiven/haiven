// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState } from "react";
import { useRouter } from "next/router";
import { fetchSSE } from "../app/_fetch_sse";
import { parse } from "best-effort-json-parser";
import { MenuFoldOutlined } from "@ant-design/icons";
import { Button, Drawer, Input, Select, message, Collapse } from "antd";
const { TextArea } = Input;

import ContextChoice from "../app/_context_choice";
import HelpTooltip from "../app/_help_tooltip";
import ChatHeader from "./_chat_header";
import { scenarioToText } from "../app/_card_actions";
import ChatExploration from "./_chat_exploration";
import CardsList from "../app/_cards-list";
import useLoader from "../hooks/useLoader";

const RequirementsBreakdown = ({ contexts, models }) => {
  const [scenarios, setScenarios] = useState([]);
  const { loading, abortLoad, startLoad, StopLoad } = useLoader();
  const [selectedContext, setSelectedContext] = useState("");
  const [promptInput, setPromptInput] = useState("");
  const [variations, setVariations] = useState([
    { value: "workflow", label: "By workflow" },
    { value: "timeline", label: "By timeline" },
    { value: "data-boundaries", label: "By data boundaries" },
    {
      value: "operational-boundaries",
      label: "By operational boundaries",
    },
  ]);
  const [selectedVariation, setSelectedVariation] = useState(variations[0]);
  const [isExpanded, setIsExpanded] = useState(true);
  const [drawerTitle, setDrawerTitle] = useState("");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [chatContext, setChatContext] = useState({});

  const placeholderHelp =
    "Describe the requirements that you'd like to break down";

  const router = useRouter();

  const onCopyAll = () => {
    const allScenarios = scenarios.map(scenarioToText);
    navigator.clipboard.writeText(allScenarios.join("\n\n"));

    message.success("Content copied successfully!");
  };

  const buildRequestData = () => {
    return {
      userinput: promptInput,
      context: selectedContext,
      promptid: "guided-requirements",
    };
  };

  const onCollapsibleIconClick = (e) => {
    setIsExpanded(!isExpanded);
  };

  const onExplore = (scenario) => {
    setDrawerTitle("Explore requirement: " + scenario.title);
    setChatContext({
      id: scenario.id,
      firstStepInput: promptInput,
      previousFraming:
        "We are breaking down a software requirement into smaller parts.",
      context: selectedContext,
      itemSummary: scenarioToText(scenario),
      ...scenario,
    });
    setDrawerOpen(true);
  };

  const onSubmitPrompt = () => {
    setIsExpanded(false);

    const uri = "/api/requirements?variation=" + selectedVariation;

    const requestData = buildRequestData();

    let ms = "";
    let output = [];

    fetchSSE(
      uri,
      {
        method: "POST",
        credentials: "include",
        signal: startLoad(),
        body: JSON.stringify(requestData),
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

  const promptTitle = "Requirements Breakdown";

  const promptMenu = (
    <div>
      <div className="prompt-chat-options-section">
        <h1>{promptTitle}</h1>
        <p>
          Haiven will help you break down your requirement into multiple work
          packages.
        </p>
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
          onChange={setSelectedContext}
          contexts={contexts}
          value={selectedContext?.key}
        />
        <div className="user-input">
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
            "Write behavior-driven development scenarios for this requirement",
            "Break down this requirement into smaller requirements",
            "What could potentially go wrong?",
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
            <ChatHeader models={models} />
            <CardsList
              scenarios={scenarios}
              title={promptTitle}
              onExplore={onExplore}
              stopLoadComponent={<StopLoad />}
            />
          </div>
        </div>
      </div>
    </>
  );
};

export default RequirementsBreakdown;
