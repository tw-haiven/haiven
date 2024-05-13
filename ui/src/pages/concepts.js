import { useRouter } from "next/router";
import React, { useEffect, useState } from "react";
import { Drawer, Card, Input, Select, Spin, Button, Radio, Space } from "antd";
import ChatExploration from "./_chat_exploration";
import { parse } from "best-effort-json-parser";
const { Search } = Input;
import {
  AiOutlineBorderInner,
  AiOutlineGroup,
  AiOutlineDelete,
} from "react-icons/ai";

const SelectedItemsMenu = ({ selections, items, onClickCreateStoryboard }) => {
  return (
    <div className="selected-items-menu">
      <span>
        {selections.length} of {items.length} scenarios selected:
      </span>
      &nbsp;
      <Space wrap>
        {selections.length == 1 && (
          <Button type="primary" onClick={onClickCreateStoryboard}>
            Create a storyboard for this scenario
          </Button>
        )}
      </Space>
    </div>
  );
};

const SelectSubPrompt = () => {
  return (
    <Select defaultValue="scenario">
      <Select.Option value="scenario">Variations of</Select.Option>
    </Select>
  );
};

let ctrl;

const Home = () => {
  const [numOfScenarios, setNumOfScenarios] = useState("5");
  const [numOfQuestions, setNumOfQuestions] = useState("3");
  const [scenarios, setScenarios] = useState([]);
  const [isLoading, setLoading] = useState(false);
  const [isDetailed, setDetailed] = useState(false);
  const [selections, setSelections] = useState([]);
  const [displayMode, setDisplayMode] = useState("grid");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerTitle, setDrawerTitle] = useState("Explore scenario");
  const [chatContext, setChatContext] = useState({});
  const [prompt, setPrompt] = useState("");
  const [subprompts, setSubprompts] = useState([]);
  const [answersVisible, setAnswersVisible] = useState(true);
  const [savedIdeas, setSavedIdeas] = useState([]);

  function abortLoad() {
    ctrl && ctrl.abort();
    setLoading(false);
  }

  function handleSelectChange(value) {
    setNumOfScenarios(value);
    setLoading(false);
  }

  function handleSelectNumOfQuestionsChange(value) {
    setNumOfQuestions(value);
    setLoading(false);
  }

  const onExplore = (id) => {
    setDrawerTitle(
      "Explore concept: " +
        scenarios.concepts[id].title +
        ": " +
        scenarios.concepts[id].tagline,
    );
    setChatContext({
      id: id,
      originalPrompt: prompt,
      type: "concept",
      summary: scenarios.concepts[id].pitch,
      ...scenarios.concepts[id],
    });
    setDrawerOpen(true);
  };

  const onSave = async (id) => {
    const scenario = scenarios.concepts[id];
    const body = scenario;
    body.prompt = prompt;
    body.type = "concept";
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

  const onGenerateVariations = (id) => {
    // const scope = [id]
    // const subpromptsParam = scope.map((selectedIndex) => {
    //   const scenario = scenarios.concepts[selectedIndex];
    //   return {type: 'variations', prompt: scenario.title + ": " + scenario.pitch}
    // });
    const scenario = scenarios.concepts[id];
    const url =
      "/concepts?strategic_prompt=" +
      encodeURIComponent(
        'Explore variations of the concept "' +
          scenario.tagline +
          '": ' +
          scenario.pitch,
      );
    window.open(url, "_blank", "noreferrer");
  };

  const onClickCreateStoryboard = () => {
    const scenario = scenarios.concepts[selections[0]];
    const url =
      "/storyboard?prompt=" +
      encodeURIComponent(
        prompt +
          ":\n" +
          scenario.title +
          ": " +
          scenario.tagline +
          "\n" +
          scenario.pitch,
      );
    window.open(url, "_blank", "noreferrer");
  };

  const handleDetailCheck = (event) => {
    setDetailed(event.target.checked);
  };

  const onGenerateStoryboard = (id) => {
    const scenario = scenarios.concepts[id];
    const url =
      "/storyboard?prompt=" +
      encodeURIComponent(
        scenario.title + ": " + scenario.tagline + "\n" + scenario.pitch,
      );
    window.open(url, "_blank", "noreferrer");
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

  const onSubmitPrompt = (value, event) => {
    abortLoad();
    ctrl = new AbortController();
    setLoading(true);
    setPrompt(value);
    setSelections([]);
    setSavedIdeas([]);

    const uri =
      "/api/concepts?input=" +
      encodeURIComponent(value) +
      "&subprompts=" +
      encodeURIComponent(JSON.stringify(subprompts)) +
      "&num_concepts=" +
      encodeURIComponent(numOfScenarios) +
      "&num_questions=" +
      encodeURIComponent(numOfQuestions);

    console.log("uri", uri);

    let ms = "";
    let isLoadingXhr = true;
    let output = [];
    try {
      fetchEventSource(uri, {
        method: "GET",
        headers: {
          "Content-Type":
            "application/json" /*, 'Authorization': `Bearer ${session.accessToken}`*/,
        },
        openWhenHidden: true,
        signal: ctrl.signal,
        onmessage: (event) => {
          if (!isLoadingXhr) {
            console.log("is loading xhr", isLoadingXhr);
            return;
          }
          if (event.data == "[DONE]") {
            setLoading(false);
            isLoadingXhr = false;
            return;
          }
          const data = JSON.parse(event.data);
          ms += data.data;
          try {
            output = parse(ms || "[]");
          } catch (error) {
            console.log("error", error);
          }
          // if(!Array.isArray(output))
          //   output = [output]
          // console.log("setting output", output);
          setScenarios(output);
        },
        onerror: (error) => {
          console.log("error", error);
          setLoading(false);
          isLoadingXhr = false;
          ctrl.abort();
        },
      });
    } catch (error) {
      console.log("error", error);
      setLoading(false);
      isLoadingXhr = false;
      ctrl.abort();
    }
  };

  const deleteSubprompt = (index) => {
    return (event) => {
      console.log("delete subprompt #", index);
      let newSubprompts = subprompts.filter((s, i) => {
        console.log("filter", i);
        return i != index;
      });
      console.log("new subprompts", newSubprompts);
      setSubprompts(newSubprompts);
    };
  };

  const onSubpromptChanged = (index) => {
    return (event) => {
      console.log("subprompt changed", index);
      const newSubprompts = [...subprompts];
      newSubprompts[index].prompt = event.target.value;
      setSubprompts(newSubprompts);
    };
  };

  const onAddSubprompt = () => {
    setSubprompts([...subprompts, { type: "variations", text: "" }]);
  };

  const toggleAnswers = () => {
    setAnswersVisible(!answersVisible);
  };

  const router = useRouter();
  const query = router.query;
  const params = query;
  const initialStrategicPrompt = params.strategic_prompt;
  let initialSubprompts = params.subprompts;
  const [initialLoadDone, setInitialLoad] = useState(false);

  useEffect(() => {
    if (!router.isReady) return;
    if (initialLoadDone) return;
    if (initialStrategicPrompt) setPrompt(initialStrategicPrompt);
    if (initialSubprompts) {
      console.log("initialsubprompts", initialSubprompts);
      initialSubprompts = JSON.parse(initialSubprompts);
      setSubprompts(initialSubprompts);
    }
    setInitialLoad(true);
  });

  // console.log("scenarios", scenarios);

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
          <b style={{ fontSize: 20, display: "inline-block" }}>Concepts</b>
          &nbsp;
          <Radio.Group
            className="display-mode"
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
          <div style={{ display: "inline" }}>
            <Select
              defaultValue={"scenario"}
              style={{ width: 180 }}
              disabled={true}
              options={[
                { value: "scenario", label: "Concept prompt", disabled: true },
              ]}
            ></Select>
            <Search
              placeholder="enter a prompt (eg How might we...?) to generate concepts"
              value={prompt}
              onChange={(e, v) => {
                setPrompt(e.target.value);
              }}
              onSearch={onSubmitPrompt}
              style={{ width: 500, color: "white", marginLeft: 10 }}
              disabled={isLoading}
              enterButton={
                <div>
                  <span>Go</span>
                </div>
              }
            />
          </div>
          &nbsp; Generate{" "}
          <Select
            defaultValue={"3"}
            onChange={handleSelectNumOfQuestionsChange}
            style={{ width: 150 }}
            disabled={isLoading}
            options={[
              { value: "3", label: "3 questions" },
              { value: "5", label: "5 questions" },
              { value: "10", label: "10 questions" },
            ]}
          ></Select>
          &nbsp; and &nbsp;
          <Select
            defaultValue={"5"}
            onChange={handleSelectChange}
            style={{ width: 150 }}
            disabled={isLoading}
            options={[
              { value: "1", label: "1 concept" },
              { value: "3", label: "3 concepts" },
              { value: "5", label: "5 concepts" },
              { value: "10", label: "10 concepts" },
            ]}
          ></Select>
          &nbsp;&nbsp;
          {isLoading ? <Spin /> : <></>}
          <br />
          {subprompts.map((x, i) => {
            return (
              <div key={"subprompt-" + i} style={{ marginTop: 5 }}>
                <Select
                  key={"select-" + x}
                  defaultValue={"variations"}
                  value={x.type}
                  onChange={handleSelectChange}
                  style={{ width: 180 }}
                  disabled={isLoading}
                  options={[
                    { value: "variations", label: "Generate variations of" },
                  ]}
                ></Select>
                <Input
                  key={"input-" + x}
                  style={{ width: 500, marginLeft: 10 }}
                  placeholder="describe a concept you want variations of"
                  value={x.prompt}
                  onChange={onSubpromptChanged(i)}
                  disabled={isLoading}
                />
                &nbsp;
                <Button
                  key={"button-" + x}
                  type="text"
                  danger
                  onClick={deleteSubprompt(i)}
                  disabled={isLoading}
                >
                  <AiOutlineDelete
                    style={{ display: "inline-block", verticalAlign: "middle" }}
                  />
                </Button>
              </div>
            );
          })}
          {/* <Button style={{marginTop: 5, width: 200}} onClick={onAddSubprompt} disabled={isLoading}>Add subprompt</Button> */}
          {isLoading && (
            <Button
              type="primary"
              danger
              onClick={abortLoad}
              style={{ marginTop: 5, marginLeft: 10 }}
            >
              Stop
            </Button>
          )}
          <br />
          <br />
          {selections.length > 0 && (
            <SelectedItemsMenu
              selections={selections}
              items={scenarios}
              onClickCreateStoryboard={onClickCreateStoryboard}
            />
          )}
        </div>
        {/* END PROMPT CENTER */}

        {scenarios && scenarios.questions && (
          <div className={"scenarios-collection " + displayMode + "-display"}>
            <Card
              key={-1}
              className="scenario"
              title={<>Questions&nbsp;</>}
              actions={[]}
            >
              {scenarios?.questions?.map((scenario, i) => {
                return (
                  <div
                    key={i}
                    className="card-prop stackable"
                    style={{ marginBottom: 20, width: 200 }}
                  >
                    <div className="card-prop-value">
                      {i + 1}. <b>{scenario.question}</b>
                      <br />
                      <small>
                        <a
                          href={
                            "/concepts?strategic_prompt=" +
                            encodeURIComponent(scenario.question)
                          }
                          target="_blank"
                        >
                          Explore this question
                        </a>
                      </small>
                      {answersVisible &&
                        scenario.answer &&
                        scenario.answer.length > 0 && (
                          <small>({scenario.answer})</small>
                        )}
                    </div>
                  </div>
                );
              })}
            </Card>

            {scenarios?.concepts?.map((scenario, i) => {
              return (
                <Card
                  key={i}
                  className="scenario"
                  title={
                    <>
                      {scenario.title}: {scenario.tagline}
                    </>
                  }
                  actions={[
                    // <div style={{padding: 0}}><input key={'cb'+i} type="checkbox" className="select-scenario" onChange={onScenarioSelectChanged(i)} /></div>,
                    <Button
                      type="link"
                      key="storyboard"
                      onClick={() => onGenerateStoryboard(i)}
                      style={{ padding: 0 }}
                    >
                      Storyboard
                    </Button>,
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
                  <div
                    className="card-prop stackable"
                    style={{ marginTop: 10 }}
                  >
                    {/* <div className="card-prop-name">Pitch</div> */}
                    <div className="card-prop-value">
                      <b>{scenario.pitch}</b>
                    </div>
                  </div>
                  {scenario.hypothesis && (
                    <div
                      className="card-prop stackable"
                      style={{ marginTop: 10 }}
                    >
                      <div className="card-prop-name">Hypothesis</div>
                      <div className="card-prop-value">
                        {scenario.hypothesis}
                      </div>
                    </div>
                  )}
                  {/* <div className="card-prop stackable" style={{marginTop: 10}}>
                <div className="card-prop-name">Strategic prompts</div>
                <div className="card-prop-value">
                {scenario.questions?.map((question, j) => {
                  return <div key={j}>{question}</div>
                })}
                </div>
              </div> */}
                </Card>
              );
            })}
          </div>
        )}

        <div
          className="scenarios-plot-container"
          style={{ display: displayMode == "plot" ? "block" : "none" }}
        >
          {/* <ScenariosPlot scenarios={scenarios} visible={displayMode == 'plot'} /> */}
        </div>
      </div>
    </>
  );
};

export default Home;
