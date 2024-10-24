// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState } from "react";
import { fetchSSE } from "../app/_fetch_sse";
import { MenuFoldOutlined } from "@ant-design/icons";
import {
  Alert,
  Button,
  Card,
  Checkbox,
  Drawer,
  Input,
  Select,
  Space,
  Spin,
  Radio,
  message,
  Collapse,
} from "antd";
import ScenariosPlot from "./_plot";
import ChatExploration from "./_chat_exploration";
import { parse } from "best-effort-json-parser";
const { TextArea } = Input;

import {
  RiStackLine,
  RiGridLine,
  RiThumbDownLine,
  RiThumbUpLine,
  RiRocket2Line,
  RiFileImageLine,
  RiAliensLine,
} from "react-icons/ri";
import Disclaimer from "./_disclaimer";

let ctrl;

const Home = ({ models }) => {
  const [numOfScenarios, setNumOfScenarios] = useState("6");
  const [scenarios, setScenarios] = useState([]);
  const [isLoading, setLoading] = useState(false);
  const [isDetailed, setDetailed] = useState(false);
  const [displayMode, setDisplayMode] = useState("grid");
  const [prompt, setPrompt] = useState("");
  const [timeHorizon, setTimeHorizon] = useState("5 years");
  const [optimism, setOptimism] = useState("optimistic");
  const [realism, setRealism] = useState("scifi");
  const [strangeness, setStrangeness] = useState("neutral");
  const [voice, setVoice] = useState("serious");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerTitle, setDrawerTitle] = useState("Explore scenario");
  const [chatContext, setChatContext] = useState({});
  const [isExpanded, setIsExpanded] = useState(true);

  function abortLoad() {
    ctrl && ctrl.abort("User aborted");
    setLoading(false);
  }

  function handleSelectChange(value) {
    setNumOfScenarios(value);
    setLoading(false);
  }

  function handleSelectTimeHorizonChange(value) {
    setTimeHorizon(value);
    setLoading(false);
  }

  function handleSelectOptimismChange(value) {
    setOptimism(value);
    setLoading(false);
  }

  function handleSelectRealismChange(value) {
    setRealism(value);
    setLoading(false);
  }

  const onExplore = (id) => {
    setDrawerTitle("Explore scenario: " + scenarios[id].title);
    setChatContext({
      id: id,
      originalPrompt: prompt,
      type: "scenario",
      ...scenarios[id],
    });
    setDrawerOpen(true);
  };

  const handleDetailCheck = (event) => {
    setDetailed(event.target.checked);
    if (event.target.checked) setDisplayMode("list");
    else setDisplayMode("grid");
  };

  const onSelectDisplayMode = (event) => {
    setDisplayMode(event.target.value);
  };

  const onCollapsibleIconClick = (e) => {
    setIsExpanded(!isExpanded);
  };

  const onSubmitPrompt = async () => {
    abortLoad();
    ctrl = new AbortController();
    setLoading(true);
    setIsExpanded(false);
    // setPrompt(value);

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
      encodeURIComponent(realism) +
      "&strangeness=" +
      encodeURIComponent(strangeness) +
      "&voice=" +
      encodeURIComponent(voice);

    let ms = "";
    let output = [];

    fetchSSE(
      uri,
      { method: "GET", signal: ctrl.signal },
      {
        json: true,
        onErrorHandle: () => {
          abortLoad(ctrl);
        },
        onFinish: () => {
          setLoading(false);
        },
        onMessageHandle: (data) => {
          try {
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
          } catch (error) {
            console.log("error", error, "data received", "'" + data + "'");
          }
        },
      },
    );
  };

  const promptMenu = (
    <div>
      <div className="prompt-chat-options-section">
        <h1>Scenarios</h1>
      </div>
      <div className="prompt-chat-options-section">
        <div className="user-input">
          <label>Generate</label>
          <Select
            defaultValue={"5"}
            onChange={handleSelectChange}
            disabled={isLoading}
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
            disabled={isLoading}
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
            disabled={isLoading}
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
            disabled={isLoading}
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
          <Checkbox onChange={handleDetailCheck} disabled={isLoading}>
            Add details (signals, threats, opportunties)
          </Checkbox>
        </div>

        <div className="user-input">
          <label>Strategic prompt</label>
          <TextArea
            disabled={isLoading}
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
            disabled={isLoading}
          >
            GENERATE
          </Button>
        </div>
        <div className="user-input">
          {isLoading ? <Spin /> : <></>}
          {isLoading && (
            <Button
              type="primary"
              danger
              onClick={abortLoad}
              style={{ marginLeft: "1em" }}
            >
              Stop
            </Button>
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
        title={drawerTitle}
        mask={false}
        open={drawerOpen}
        destroyOnClose={true}
        onClose={() => setDrawerOpen(false)}
        size={"large"}
      >
        <ChatExploration
          context={chatContext}
          user={{ name: "User", avatar: "/boba/user-5-fill-dark-blue.svg" }}
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
          <Disclaimer models={models} />
          <h1 className="title-for-collapsed-panel">Scenarios</h1>
          <div className={"scenarios-collection " + displayMode + "-display"}>
            <div>
              <Radio.Group
                className="display-mode-choice"
                onChange={onSelectDisplayMode}
                defaultValue="grid"
                style={{ float: "right" }}
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
            <div className="cards-container with-display-mode">
              {scenarios.map((scenario, i) => {
                return (
                  <Card
                    hoverable
                    key={i}
                    className="scenario"
                    // title={<>{}</>}
                    actions={[
                      <Button
                        type="link"
                        key="explore"
                        onClick={() => onExplore(i)}
                      >
                        Explore
                      </Button>,
                    ]}
                  >
                    <div className="scenario-card-content">
                      <h3>{scenario.title}</h3>
                      <div className="scenario-summary">{scenario.summary}</div>
                      {scenario.horizon && (
                        <div className="card-prop stackable">
                          <div className="card-prop-name">Horizon</div>
                          <div className="card-prop-value">
                            {scenario.horizon}
                          </div>
                        </div>
                      )}
                      {scenario.plausibility && (
                        <div className="card-prop stackable">
                          <div className="card-prop-name">Plausibility</div>
                          <div className="card-prop-value">
                            {scenario.plausibility}
                          </div>
                        </div>
                      )}
                      {scenario.probability && (
                        <div className="card-prop stackable">
                          <div className="card-prop-name">Probability</div>
                          <div className="card-prop-value">
                            {scenario.probability}
                          </div>
                        </div>
                      )}
                      {scenario.signals && (
                        <div className="card-prop">
                          <div className="card-prop-name">
                            Signals/Driving Forces
                          </div>
                          <div className="card-prop-value">
                            {(scenario.signals || []).join(", ")}
                          </div>
                        </div>
                      )}
                      {scenario.threats && (
                        <div className="card-prop">
                          <div className="card-prop-name">Threats</div>
                          <div className="card-prop-value">
                            {(scenario.threats || []).join(", ")}
                          </div>
                        </div>
                      )}
                      {scenario.opportunities && (
                        <div className="card-prop">
                          <div className="card-prop-name">Opportunities</div>
                          <div className="card-prop-value">
                            {(scenario.opportunities || []).join(", ")}
                          </div>
                        </div>
                      )}
                    </div>
                  </Card>
                );
              })}
            </div>
            <div
              className="scenarios-plot-container"
              style={{ display: displayMode == "plot" ? "block" : "none" }}
            >
              <ScenariosPlot
                scenarios={scenarios}
                visible={displayMode == "plot"}
              />
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Home;
