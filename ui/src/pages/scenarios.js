// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState } from "react";
import { fetchSSE } from "../app/_fetch_sse";
import { MenuFoldOutlined } from "@ant-design/icons";
import {
  Button,
  Drawer,
  Checkbox,
  Input,
  Select,
  message,
  Collapse,
} from "antd";
import { parse } from "best-effort-json-parser";
const { TextArea } = Input;

import {
  RiThumbDownLine,
  RiThumbUpLine,
  RiRocket2Line,
  RiFileImageLine,
  RiAliensLine,
} from "react-icons/ri";
import Disclaimer from "./_disclaimer";
import { scenarioToText } from "../app/_card_actions";
import useLoader from "../hooks/useLoader";
import ChatExploration from "./_chat_exploration";
import CardsList from "../app/_cards-list";

const Home = ({ models }) => {
  const [numOfScenarios, setNumOfScenarios] = useState("6");
  const [scenarios, setScenarios] = useState([]);
  const { loading, abortLoad, startLoad, StopLoad } = useLoader();
  const [isDetailed, setDetailed] = useState(false);
  const [prompt, setPrompt] = useState("");
  const [timeHorizon, setTimeHorizon] = useState("5 years");
  const [optimism, setOptimism] = useState("optimistic");
  const [realism, setRealism] = useState("scifi");
  const [isExpanded, setIsExpanded] = useState(true);
  const [drawerTitle, setDrawerTitle] = useState("");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [chatContext, setChatContext] = useState({});

  function handleSelectChange(value) {
    setNumOfScenarios(value);
    abortLoad();
  }

  function handleSelectTimeHorizonChange(value) {
    setTimeHorizon(value);
    abortLoad();
  }

  function handleSelectOptimismChange(value) {
    setOptimism(value);
    abortLoad();
  }

  function handleSelectRealismChange(value) {
    setRealism(value);
    abortLoad();
  }

  const onCopyAll = () => {
    const allScenarios = scenarios.map(scenarioToText);
    navigator.clipboard.writeText(allScenarios.join("\n\n\n"));
    message.success("Content copied successfully!");
  };

  const handleDetailCheck = (event) => {
    setDetailed(event.target.checked);
    if (event.target.checked) setDisplayMode("list");
    else setDisplayMode("grid");
  };

  const onCollapsibleIconClick = (e) => {
    setIsExpanded(!isExpanded);
  };

  const onExplore = (scenario) => {
    setDrawerTitle("Explore Scenario: " + scenario.title);
    setChatContext({
      id: scenario.id,
      firstStepInput: prompt,
      previousFraming:
        "You are a visionary futurist. We're brainstorming scenarios.",
      itemSummary: scenarioToText(scenario),
      ...scenario,
    });
    setDrawerOpen(true);
  };

  const onSubmitPrompt = async () => {
    setIsExpanded(false);

    const uri =
      "/api/make-scenario" +
      "?input=" +
      encodeURIComponent(prompt) +
      "&num_scenarios=" +
      encodeURIComponent(numOfScenarios) +
      "&detail=" +
      encodeURIComponent(isDetailed) +
      "&time_horizon=" +
      encodeURIComponent(timeHorizon) +
      "&optimism=" +
      encodeURIComponent(optimism) +
      "&realism=" +
      encodeURIComponent(realism);

    let ms = "";
    let output = [];

    fetchSSE(
      uri,
      { method: "GET", signal: startLoad() },
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
          try {
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
          } catch (error) {
            console.log("error", error, "data received", "'" + data + "'");
          }
        },
      },
    );
  };

  const promptTitle = "Scenario Design";

  const promptMenu = (
    <div>
      <div className="prompt-chat-options-section">
        <h1>{promptTitle}</h1>
        <p>
          Brainstorm a range of scenarios for your product domain based on
          criteria like time horizon, realism, and optimism.
        </p>
      </div>
      <div className="prompt-chat-options-section">
        <div className="user-input">
          <label>Generate</label>
          <Select
            defaultValue={"5"}
            onChange={handleSelectChange}
            disabled={loading}
            options={[
              { value: "1", label: "1 scenario" },
              { value: "3", label: "3 scenarios" },
              { value: "5", label: "5 scenarios" },
              { value: "10", label: "10 scenarios" },
            ]}
          ></Select>
        </div>
        <div className="user-input">
          <Select
            defaultValue={"10-year"}
            onChange={handleSelectTimeHorizonChange}
            disabled={loading}
            options={[
              { value: "5-year", label: "5-year horizon" },
              { value: "10-year", label: "10-year horizon" },
              { value: "100-year", label: "100-year horizon" },
            ]}
          ></Select>
        </div>
        <div className="user-input">
          <Select
            defaultValue={"optimistic"}
            onChange={handleSelectOptimismChange}
            disabled={loading}
            options={[
              {
                value: "optimistic",
                label: (
                  <div>
                    <span className="config-icon">
                      <RiThumbUpLine />
                    </span>{" "}
                    Optimistic
                  </div>
                ),
              },
              {
                value: "pessimistic",
                label: (
                  <div>
                    <span className="config-icon">
                      <RiThumbDownLine />
                    </span>{" "}
                    Pessimistic
                  </div>
                ),
              },
            ]}
          ></Select>
        </div>
        <div className="user-input">
          <Select
            defaultValue={"futuristic sci-fi"}
            onChange={handleSelectRealismChange}
            disabled={loading}
            options={[
              {
                value: "realistic",
                label: (
                  <div>
                    <span className="config-icon">
                      <RiFileImageLine />
                    </span>{" "}
                    Realistic
                  </div>
                ),
              },
              {
                value: "futuristic sci-fi",
                label: (
                  <div>
                    <span className="config-icon">
                      <RiRocket2Line />
                    </span>{" "}
                    Sci-fi Future
                  </div>
                ),
              },
              {
                value: "bizarre",
                label: (
                  <div>
                    <span className="config-icon">
                      <RiAliensLine />
                    </span>{" "}
                    Bizarre
                  </div>
                ),
              },
            ]}
          ></Select>
        </div>
        <div className="user-input">
          <Checkbox onChange={handleDetailCheck} disabled={loading}>
            Add details (signals, threats, opportunties)
          </Checkbox>
        </div>

        <div className="user-input">
          <label>Strategic prompt</label>
          <TextArea
            disabled={loading}
            value={prompt}
            onChange={(e, v) => {
              setPrompt(e.target.value);
            }}
            rows="4"
          />
        </div>
        <div className="user-input">
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
            "What are the key drivers for this scenario?",
            "What are the key uncertainties?",
            "What business opportunities could this trigger?",
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

export default Home;
