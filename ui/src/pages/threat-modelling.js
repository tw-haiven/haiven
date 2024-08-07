// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { fetchSSE } from "../app/_fetch_sse";
import { Alert, Drawer, Card, Space, Spin, Button, Radio, Input } from "antd";
const { TextArea } = Input;
import ScenariosPlotProbabilityImpact from "./_plot_prob_impact";
import ChatExploration from "./_chat_exploration";
import Clipboard from "./_clipboard";
import { parse } from "best-effort-json-parser";
import { RiStackLine, RiGridLine, RiClipboardLine } from "react-icons/ri";

let ctrl;

const Home = () => {
  const [scenarios, setScenarios] = useState([]);
  const [isLoading, setLoading] = useState(false);
  const [displayMode, setDisplayMode] = useState("grid");
  const [promptDataFlow, setPromptDataFlow] = useState("");
  const [promptUserBase, setPromptUserBase] = useState("");
  const [promptAssets, setPromptAssets] = useState("");
  const [explorationDrawerOpen, setExplorationDrawerOpen] = useState(false);
  const [explorationDrawerTitle, setExplorationDrawerTitle] =
    useState("Explore scenario");
  const [explorationDrawerHeader, setExplorationDrawerHeader] = useState("");
  const [clipboardDrawerOpen, setClipboardDrawerOpen] = useState(false);
  const [chatContext, setChatContext] = useState({});
  const [savedIdeas, setSavedIdeas] = useState([]);
  const [currentSSE, setCurrentSSE] = useState(null);
  const [modelOutputFailed, setModelOutputFailed] = useState(false);
  const router = useRouter();

  function abortLoad() {
    ctrl && ctrl.abort();
    setLoading(false);
    if (currentSSE && currentSSE.readyState == 1) {
      currentSSE.close();
      setCurrentSSE(null);
    }
  }

  function concatUserInput() {
    return (
      "**Userbase:** " +
      promptUserBase +
      "|| **Assets:** " +
      promptAssets +
      "|| **Dataflow:** " +
      promptDataFlow
    );
  }

  const onExplore = (id) => {
    setExplorationDrawerTitle("Explore scenario: " + scenarios[id].title);
    setExplorationDrawerHeader(scenarios[id].summary);
    setChatContext({
      id: id,
      originalPrompt: concatUserInput(),
      type: "threat-modelling",
      ...scenarios[id],
    });
    setExplorationDrawerOpen(true);
    setExplorationDrawerOpen(true);
  };

  const onSelectDisplayMode = (event) => {
    setDisplayMode(event.target.value);
  };

  const onSubmitPrompt = (event) => {
    setModelOutputFailed(false);
    abortLoad();
    ctrl = new AbortController();
    setLoading(true);

    const uri =
      "/api/threat-modelling" +
      "?dataFlow=" +
      encodeURIComponent(promptDataFlow) +
      "?assets=" +
      encodeURIComponent(promptAssets) +
      "?userBase=" +
      encodeURIComponent(promptUserBase);

    let ms = "";
    let output = [];

    let sse = fetchSSE({
      url: uri,
      onData: (event, sse) => {
        const data = JSON.parse(event.data);
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
      onStop: () => {
        setLoading(false);
        abortLoad();
      },
    });
    setCurrentSSE(sse);
  };

  const query = router.query;
  const params = query;
  const initialStrategicPrompt = params.strategic_prompt;
  // const promptRef = useRef();
  const [initialLoadDone, setInitialLoad] = useState(false);

  useEffect(() => {
    if (!initialStrategicPrompt) return;
    if (!router.isReady) return;
    if (initialLoadDone) return;
    setPromptDataFlow(initialStrategicPrompt);
    setInitialLoad(true);
  });

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
      <Drawer
        title="Clipboard"
        mask={false}
        open={clipboardDrawerOpen}
        destroyOnClose={true}
        onClose={() => setClipboardDrawerOpen(false)}
        size={"large"}
      >
        <Clipboard />
      </Drawer>
      <div id="canvas">
        <div id="prompt-center">
          <b style={{ fontSize: 20, display: "inline-block" }}>
            Threat Modelling
          </b>
          &nbsp;
          {/* <Button
            onClick={() => setClipboardDrawerOpen(true)}
            className="btn-clipboard"
          ><RiClipboardLine
          style={{
            display: "inline-block",
            verticalAlign: "middle",
            height: 14,
          }}
        /></Button> */}
          <Radio.Group
            className="display-mode"
            onChange={onSelectDisplayMode}
            defaultValue="grid"
            style={{ float: "right" }}
          >
            <Radio.Button value="grid">
              <RiStackLine /> Cards
            </Radio.Button>
            <Radio.Button value="plot">
              <RiGridLine /> Matrix
            </Radio.Button>
          </Radio.Group>
          <br />
          <br />
          <div className="scenario-inputs">
            <div className="scenario-input">
              <label>Users</label>{" "}
              <Input
                placeholder="Describe the user base, e.g. if it's B2C, B2B, internal, ..."
                value={promptUserBase}
                onChange={(e, v) => {
                  setPromptUserBase(e.target.value);
                }}
              />
            </div>
            <div className="scenario-input">
              <label>Assets</label>{" "}
              <Input
                placeholder="Describe any important assets that need to be protected"
                value={promptAssets}
                onChange={(e, v) => {
                  setPromptAssets(e.target.value);
                }}
              />
            </div>
            <div className="scenario-input">
              <label>Data flow</label>
              <TextArea
                placeholder="Describe how data flows through your system"
                value={promptDataFlow}
                onChange={(e, v) => {
                  setPromptDataFlow(e.target.value);
                }}
                rows={5}
              />
            </div>
            <Button type="primary" onClick={onSubmitPrompt}>
              Go
            </Button>
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
          &nbsp;
          {isLoading && (
            <div style={{ marginTop: 10 }}>
              <Spin />
              <div style={{ marginLeft: 105, display: "inline-block" }}>
                &nbsp;
              </div>

              <Button type="primary" danger onClick={abortLoad}>
                Stop
              </Button>
            </div>
          )}
        </div>

        <div className={"scenarios-collection " + displayMode + "-display"}>
          {scenarios.map((scenario, i) => {
            return (
              <Card
                key={i}
                className="scenario"
                title={<>{scenario.title}</>}
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
                <div className="scenario-card-content large">
                  {scenario.category && (
                    <div className="card-prop stackable">
                      <div className="card-prop-name">Category</div>
                      <div className="card-prop-value">{scenario.category}</div>
                    </div>
                  )}
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
                      <div className="card-prop-value">{scenario.impact}</div>
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
          <ScenariosPlotProbabilityImpact
            scenarios={scenarios}
            visible={displayMode == "plot"}
          />
        </div>
      </div>
    </>
  );
};

export default Home;
