import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { fetchSSE } from "../app/_fetch_sse";
import { Drawer, Card, Space, Spin, Button, Radio, Input } from "antd";
const { TextArea } = Input;
import ScenariosPlotProbabilityImpact from "./_plot_prob_impact";
import ChatExploration from "./_chat_exploration";
import { parse } from "best-effort-json-parser";

let ctrl;

const Home = () => {
  const [scenarios, setScenarios] = useState([]);
  const [isLoading, setLoading] = useState(false);
  const [displayMode, setDisplayMode] = useState("grid");
  const [promptInput, setPromptInput] = useState("");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerTitle, setDrawerTitle] = useState("Explore requirement");
  const [drawerHeader, setDrawerHeader] = useState("Explore scenario");
  const [chatContext, setChatContext] = useState({});
  const [currentSSE, setCurrentSSE] = useState(null);
  const router = useRouter();

  function abortLoad() {
    ctrl && ctrl.abort();
    setLoading(false);
    if (currentSSE && currentSSE.readyState == 1) {
      currentSSE.close();
      setCurrentSSE(null);
    }
  }

  const onExplore = (id) => {
    setDrawerTitle("Explore requirement: " + scenarios[id].title);
    setDrawerHeader(scenarios[id].summary);
    setChatContext({
      id: id,
      originalPrompt: promptInput,
      type: "requirements",
      ...scenarios[id],
    });
    setDrawerOpen(true);
  };

  const onSelectDisplayMode = (event) => {
    setDisplayMode(event.target.value);
  };

  const onSubmitPrompt = (event) => {
    abortLoad();
    ctrl = new AbortController();
    setLoading(true);

    const uri =
      "/api/requirements" + "?input=" + encodeURIComponent(promptInput);

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
    setPromptInput(initialStrategicPrompt);
    setInitialLoad(true);
  });

  return (
    <>
      <Drawer
        title={drawerTitle}
        mask={false}
        open={drawerOpen}
        size="large"
        destroyOnClose={true}
        onClose={() => setDrawerOpen(false)}
      >
        <ChatExploration
          context={chatContext}
          user={{
            name: "User",
            avatar: "/boba/user-5-fill-dark-blue.svg",
          }}
          scenarioQueries={[
            "Write behavior-driven development scenarios for this requirement",
            "What could potentially go wrong?",
          ]}
        />
      </Drawer>
      <div id="canvas">
        <div id="prompt-center">
          <b style={{ fontSize: 20, display: "inline-block" }}>
            Requirements breakdown
          </b>
          &nbsp;
          {/* <Radio.Group
            onChange={onSelectDisplayMode}
            defaultValue="grid"
            style={{ float: "right" }}
          >
            <Radio.Button value="grid">
              <AiOutlineGroup
                style={{
                  display: "inline-block",
                  verticalAlign: "middle",
                  height: 14,
                }}
              />{" "}
              Cards
            </Radio.Button>
            <Radio.Button value="plot">
              <AiOutlineBorderInner
                style={{
                  display: "inline-block",
                  verticalAlign: "middle",
                  height: 14,
                }}
              />{" "}
              Matrix
            </Radio.Button>
          </Radio.Group>
          <br />
          <br /> */}
          <div className="scenario-inputs">
            <div className="scenario-input">
              <label>High level requirements</label>
              <TextArea
                placeholder="Describe the high level requirements to break down"
                value={promptInput}
                onChange={(e, v) => {
                  setPromptInput(e.target.value);
                }}
                rows={5}
              />
            </div>
            <Button type="primary" onClick={onSubmitPrompt}>
              Go
            </Button>
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
                <div className="scenario-card-content">
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
