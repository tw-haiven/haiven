import React, { useEffect, useState, useRef } from "react";
import { useRouter } from "next/router";
import { fetchSSE } from "../app/_fetch_sse";
import {
  Drawer,
  Card,
  Input,
  Select,
  Spin,
  Checkbox,
  Button,
  Radio,
  Space,
} from "antd";
import ScenariosPlot from "./_plot";
import ChatExploration from "./_chat_exploration";
import { parse } from "best-effort-json-parser";
const { Search } = Input;
import {
  AiOutlineBorderInner,
  AiOutlineGroup,
  AiOutlineLike,
  AiOutlineDislike,
  AiOutlineRocket,
  AiOutlinePicture,
  AiOutlineHeatMap,
} from "react-icons/ai";

const SelectedItemsMenu = ({
  selections,
  items,
  onClickBrainstormStrategies,
  onClickCreateStoryboard,
}) => {
  return (
    <div className="selected-items-menu">
      <span>
        {selections.length} of {items.length} scenarios selected:
      </span>
      &nbsp;
      <Space wrap>
        <Button type="primary" onClick={onClickBrainstormStrategies}>
          Brainstorm strategies and questions
        </Button>
        {selections.length == 1 && (
          <Button type="primary" onClick={onClickCreateStoryboard}>
            Create a storyboard for this scenario
          </Button>
        )}
      </Space>
    </div>
  );
};

let ctrl;

const Home = () => {
  const [numOfScenarios, setNumOfScenarios] = useState("5");
  const [scenarios, setScenarios] = useState([]);
  const [isLoading, setLoading] = useState(false);
  const [isDetailed, setDetailed] = useState(false);
  const [selections, setSelections] = useState([]);
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
  const [savedIdeas, setSavedIdeas] = useState([]);
  const router = useRouter();

  function abortLoad() {
    ctrl && ctrl.abort();
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

  const onSave = async (id) => {
    const scenario = scenarios[id];
    const body = scenario;
    body.prompt = prompt;
    body.type = "scenario";
    const resp = await fetch("/api/save-idea", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });
    const data = await resp.json();
    setSavedIdeas([...savedIdeas, id]);
    console.log("Saved idea", data);
  };

  const onClickBrainstormStrategies = () => {
    const scenariosParams = selections.map((selectedIndex) => {
      // console.log("i", selectedIndex);
      const scenario = scenarios[selectedIndex];
      // console.log("s", scenario);
      return (
        "scenarios=" +
        encodeURIComponent(scenario.title + ": " + scenario.summary)
      );
    });
    const url =
      "/strategies?strategic_prompt=" +
      encodeURIComponent(prompt) +
      "&" +
      scenariosParams.join("&");
    window.open(url, "_blank", "noreferrer");
  };

  const onClickCreateStoryboard = () => {
    const scenario = scenarios[selections[0]];
    const url =
      "/storyboard?prompt=" +
      encodeURIComponent(scenario.title + ": " + scenario.summary);
    window.open(url, "_blank", "noreferrer");
  };

  const handleDetailCheck = (event) => {
    setDetailed(event.target.checked);
    if (event.target.checked) setDisplayMode("list");
    else setDisplayMode("grid");
  };

  const onSelectDisplayMode = (event) => {
    setDisplayMode(event.target.value);
  };

  const onScenarioSelectChanged = (index) => {
    return (event) => {
      console.log("event for " + index, event);
      console.log(
        (event.target.checked ? "selected" : "deselected") + " scenario",
        scenarios[index],
      );
      if (event.target.checked && selections.indexOf(index) == -1)
        setSelections([...selections, index]);
      else setSelections(selections.filter((s) => s != index));
    };
  };

  const onSubmitPrompt = async (value, event) => {
    abortLoad();
    ctrl = new AbortController();
    setLoading(true);
    setPrompt(value);
    setSelections([]);

    const uri =
      "/api/make-scenario" +
      "?input=" +
      encodeURIComponent(value) +
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

    fetchSSE({
      url: uri,
      onData: (event) => {
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
      onOpen: () => {
        setLoading(true);
      },
    });
  };

  const query = router.query;
  const params = query;
  const initialStrategicPrompt = params.strategic_prompt;
  const promptRef = useRef();
  const [initialLoadDone, setInitialLoad] = useState(false);

  useEffect(() => {
    if (!initialStrategicPrompt) return;
    if (!router.isReady) return;
    if (initialLoadDone) return;
    setPrompt(initialStrategicPrompt);
    setInitialLoad(true);
  });

  return (
    <>
      <Drawer
        title={drawerTitle}
        mask={false}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      >
        <ChatExploration context={chatContext} />
      </Drawer>
      <div id="canvas">
        <div id="prompt-center">
          <b style={{ fontSize: 20, display: "inline-block" }}>Scenarios</b>
          &nbsp;
          <Radio.Group
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
          <br />
          Strategic prompt:&nbsp;
          <Search
            ref={promptRef}
            placeholder="enter a prompt and press enter to generate scenarios"
            className="fs-unmask"
            onSearch={onSubmitPrompt}
            style={{ width: 500, color: "white" }}
            disabled={isLoading}
            value={prompt}
            onChange={(e, v) => {
              setPrompt(e.target.value);
            }}
            enterButton={
              <div>
                <span>Go</span>
              </div>
            }
          />
          &nbsp; Generate{" "}
          <Select
            defaultValue={"5"}
            onChange={handleSelectChange}
            style={{ width: 150 }}
            disabled={isLoading}
            options={[
              { value: "1", label: "1 scenario" },
              { value: "3", label: "3 scenarios" },
              { value: "5", label: "5 scenarios" },
              { value: "10", label: "10 scenarios" },
            ]}
          ></Select>
          &nbsp;&nbsp;
          <Checkbox onChange={handleDetailCheck} disabled={isLoading} /> Add
          details (signals, threats, opportunties) &nbsp;
          {isLoading ? <Spin /> : <></>}
          <div style={{ marginTop: 10 }}>
            <div style={{ marginLeft: 105, display: "inline-block" }}>
              &nbsp;
            </div>
            <Select
              defaultValue={"10-year"}
              onChange={handleSelectTimeHorizonChange}
              style={{ width: 150 }}
              disabled={isLoading}
              options={[
                { value: "5-year", label: "5-year horizon" },
                { value: "10-year", label: "10-year horizon" },
                { value: "100-year", label: "100-year horizon" },
              ]}
            ></Select>
            &nbsp;&nbsp; &nbsp;
            <Select
              defaultValue={"optimistic"}
              onChange={handleSelectOptimismChange}
              style={{ width: 150 }}
              disabled={isLoading}
              options={[
                {
                  value: "optimistic",
                  label: (
                    <div>
                      <span className="config-icon">
                        <AiOutlineLike />
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
                        <AiOutlineDislike />
                      </span>{" "}
                      Pessimistic
                    </div>
                  ),
                },
              ]}
            ></Select>
            &nbsp;&nbsp;
            <Select
              defaultValue={"futuristic sci-fi"}
              onChange={handleSelectRealismChange}
              style={{ width: 150 }}
              disabled={isLoading}
              options={[
                {
                  value: "realistic",
                  label: (
                    <div>
                      <span className="config-icon">
                        <AiOutlinePicture />
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
                        <AiOutlineRocket />
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
                        <AiOutlineHeatMap />
                      </span>{" "}
                      Bizarre
                    </div>
                  ),
                },
              ]}
            ></Select>
            &nbsp;&nbsp;
            {isLoading && (
              <Button type="primary" danger onClick={abortLoad}>
                Stop
              </Button>
            )}
          </div>
          <br />
          <br />
          {selections.length > 0 && (
            <SelectedItemsMenu
              selections={selections}
              items={scenarios}
              onClickBrainstormStrategies={onClickBrainstormStrategies}
              onClickCreateStoryboard={onClickCreateStoryboard}
            />
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
                  <input
                    key={"cb" + i}
                    type="checkbox"
                    className="select-scenario"
                    onChange={onScenarioSelectChanged(i)}
                  />,
                  <Button
                    type="link"
                    key="explore"
                    onClick={() => onExplore(i)}
                  >
                    Explore
                  </Button>,
                  <>
                    {savedIdeas.includes(i) && (
                      <Button
                        type="link"
                        key="saved"
                        onClick={() => onSave(i)}
                        style={{ padding: 0 }}
                      >
                        Saved
                      </Button>
                    )}
                    {!savedIdeas.includes(i) && (
                      <Button
                        type="link"
                        key="save"
                        onClick={() => onSave(i)}
                        style={{ padding: 0 }}
                      >
                        Save
                      </Button>
                    )}
                  </>,
                ]}
              >
                <div className="scenario-card-content">
                  <div className="scenario-summary">{scenario.summary}</div>
                  {scenario.horizon && (
                    <div className="card-prop stackable">
                      <div className="card-prop-name">Horizon</div>
                      <div className="card-prop-value">{scenario.horizon}</div>
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
    </>
  );
};

export default Home;
