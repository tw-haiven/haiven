import { useRouter } from "next/router";
import React, { useEffect, useState } from "react";
import { Tabs, Input, Spin, Button, Space, Row, Col } from "antd";
import EvalResults from "./_eval_results";
import partialParse from "partial-json-parser";
import {
  AiOutlinePlayCircle,
  AiOutlineDelete,
  AiOutlinePlusCircle,
  AiOutlineStop,
} from "react-icons/ai";
const { TextArea } = Input;

function callback(key) {
  console.log(key);
}

let ctrls = [];
let cachedResults = {};

const TestIdeas = () => {
  const [initialLoadDone, setInitialLoad] = useState(false);
  const [strategyPrompts, setStrategyPrompts] = useState([]);
  const [scenarioPrompts, setScenarioPrompts] = useState([]);
  const [dimensionPrompts, setDimensionPrompts] = useState([]);
  const [strategies, setStrategies] = useState([]);
  const [scenarios, setScenarios] = useState([]);
  const [isLoading, setLoading] = useState(false);
  const [results, setResults] = useState({}); //[{strat: ..., scenario: ...}, ...]

  const router = useRouter();
  const query = router.query;
  const params = query;
  let initialScenarios;
  let initialStrategies;

  if (router.isReady && !initialLoadDone) {
    console.log("loading initial strategies and scenarios");
    //parse strategies
    try {
      initialStrategies = params.strategies || [];
    } catch (error) {
      console.log("error", error);
    }

    if (
      !Array.isArray(initialStrategies) &&
      typeof initialStrategies === "string"
    )
      initialStrategies = [initialStrategies];

    initialStrategies = initialStrategies.map((s) => {
      try {
        return JSON.parse(s);
      } catch (error) {
        console.log("error", error);
      }
    });

    if (initialStrategies) {
      const parsedInitialStrategies = initialStrategies.map((s) => {
        return {
          title: s.title,
          description:
            s.summary +
            "\nWinning aspiration: " +
            s.winning_aspiration +
            "\nProblem diagnosis: " +
            s.problem_diagnosis +
            "\nWhere to play: " +
            s.where_to_play +
            "\n\nHow to win: " +
            s.how_to_win +
            "\n\nWhat would have to be true: " +
            s.what_would_have_to_be_true,
        };
      });
      setStrategies(parsedInitialStrategies);
      console.log(
        "setting strat prompts to ",
        parsedInitialStrategies.map((s) => s.title + ": " + s.description),
      );
      setStrategyPrompts(
        parsedInitialStrategies.map((s) => s.title + ": " + s.description),
      );
    }

    //parse scenarios
    try {
      initialScenarios = params.scenarios || [];
    } catch (error) {
      console.log("error", error);
    }

    if (
      !Array.isArray(initialScenarios) &&
      typeof initialScenarios === "string"
    )
      initialScenarios = [initialScenarios];

    initialScenarios = initialScenarios.map((s) => {
      try {
        return JSON.parse(s);
      } catch (error) {
        console.log("error", error);
      }
    });

    if (initialScenarios) {
      console.log("initialscenarios", initialScenarios);
      const parsedInitialScenarios = initialScenarios.map((s) => {
        const title = s.title.split(":")[0];
        const description = s.title.split(title)[1];
        return { title: title, description: s.title };
      });
      setScenarios(parsedInitialScenarios);
      setScenarioPrompts(
        parsedInitialScenarios.map((s) => s.title + ": " + s.description),
      );
    }

    setInitialLoad(true);
  }

  function abortEval() {
    ctrls.forEach((ctrl) => ctrl.abort());
    ctrls = [];
    setLoading(false);
  }

  const fetchEvaluation = (
    strategyIndex,
    scenarioIndex,
    ctrl,
    key,
    onAbort,
  ) => {
    const scenario = scenarioPrompts[scenarioIndex];
    const strategy = strategyPrompts[strategyIndex];
    const encodedScenario = `scenario=${encodeURIComponent(scenario)}`;
    const encodedStrategy = `strategy=${encodeURIComponent(strategy)}`;
    const encodedDimensions = `dimensions=${encodeURIComponent(JSON.stringify(dimensionPrompts))}`;
    const uri =
      "/api/evaluate-strategy?" +
      encodedStrategy +
      "&" +
      encodedScenario +
      "&" +
      encodedDimensions;

    let ms = "";
    let isLoadingXhr = true;
    let output = [];
    try {
      fetchEventSource(uri, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
        openWhenHidden: true,
        signal: ctrl.signal,
        onmessage: (event) => {
          if (!isLoadingXhr) {
            console.log("is loading xhr", isLoadingXhr);
            return;
          }
          if (event.data == "[DONE]") {
            isLoadingXhr = false;
            onAbort();
            return;
          }
          const data = JSON.parse(event.data);
          ms += data.data;
          try {
            output = partialParse(ms || "[]");
          } catch (error) {
            console.log("error", error);
          }
          const result = {
            strategyIndex: strategyIndex,
            scenarioIndex: scenarioIndex,
            strategy: strategy,
            scenario: scenario,
            results: output,
          };

          cachedResults[key] = result;
          setResults([...Object.values(cachedResults)]);
        },
        onerror: (error) => {
          console.log("error", error);
          onAbort();
          isLoadingXhr = false;
        },
      });
    } catch (error) {
      onAbort();
      console.log("error", error);
      isLoadingXhr = false;
    }
  };

  const runEvaluation = () => {
    abortEval();
    setLoading(true);
    ctrls = [];
    for (let i = 0; i < strategyPrompts.length; i++) {
      for (let j = 0; j < scenarioPrompts.length; j++) {
        const ctrl = new AbortController();
        ctrls.push(ctrl);
        fetchEvaluation(i, j, ctrl, i + "-" + j, (key) => {
          ctrl.abort();
          ctrls = ctrls.filter((c) => c != ctrl);
          if (ctrls.length == 0) setLoading(false);
        });
      }
    }
  };

  const setFocus = (id) => {
    document.getElementById(id)?.focus();
  };

  useEffect(() => {
    if (strategyPrompts.length == 0) {
      setStrategyPrompts([""]);
      return;
    }
    setStrategies(
      strategyPrompts.map((p) => {
        return {
          title: p.split(":")[0],
          description: p.split(p.split(":")[0])[1],
        };
      }),
    );
  }, [strategyPrompts]);

  useEffect(() => {
    if (scenarioPrompts.length == 0) {
      setScenarioPrompts([""]);
      return;
    }
    setScenarios(
      scenarioPrompts.map((p) => {
        return {
          title: p.split(":")[0],
          description: p.split(p.split(":")[0])[1],
        };
      }),
    );
  }, [scenarioPrompts]);

  useEffect(() => {
    if (dimensionPrompts.length == 0) {
      setDimensionPrompts([
        "Market Demand",
        "Business Viability",
        "Technical Feasilbility",
      ]);
    }
  }, [dimensionPrompts]);

  const generateDimensions = () => {};

  const isValid = () => {
    const s = strategyPrompts.filter(
      (s) => s && s.length > 0 && s.trim().length > 0,
    );
    const sc = scenarioPrompts.filter(
      (s) => s && s.length > 0 && s.trim().length > 0,
    );
    const d = dimensionPrompts.filter(
      (s) => s && s.length > 0 && s.trim().length > 0,
    );
    return s.length > 0 && sc.length > 0 && d.length > 0;
  };

  return (
    <div>
      <div id="prompt-center" style={{ marginTop: 10 }}>
        <img
          src="/boba/popping-boba.png"
          style={{ height: 25, display: "inline-block", verticalAlign: "top" }}
        />{" "}
        <b style={{ fontSize: 20, display: "inline-block" }}>
          Popping Boba: Strategy Evaluation
        </b>
        &nbsp;
        <Space defaultValue="grid" style={{ float: "right" }}>
          {!isLoading && (
            <Button onClick={generateDimensions} value="gendims">
              <AiOutlinePlusCircle
                style={{
                  display: "inline-block",
                  verticalAlign: "middle",
                  height: 14,
                  marginRight: 5,
                }}
              />{" "}
              Generate Evaluation Dimensions
            </Button>
          )}
          {!isLoading && (
            <Button
              type="primary"
              disabled={!isValid()}
              onClick={runEvaluation}
              value="run"
            >
              <AiOutlinePlayCircle
                style={{
                  display: "inline-block",
                  verticalAlign: "middle",
                  height: 14,
                  marginRight: 5,
                }}
              />{" "}
              Run Evaluation
            </Button>
          )}
          {isLoading && (
            <Button type="primary" danger onClick={abortEval}>
              <AiOutlineStop
                style={{
                  display: "inline-block",
                  verticalAlign: "middle",
                  height: 14,
                  marginRight: 5,
                }}
              />{" "}
              Stop Evaluation
            </Button>
          )}
          &nbsp;
          {isLoading ? <Spin /> : <></>}
        </Space>
      </div>
      <div id="canvas">
        <Row>
          <Col span={10} className="prompt-list-section">
            <Space>
              <Button
                size="small"
                onClick={() => {
                  setStrategyPrompts([...strategyPrompts, ""]);
                  setTimeout(
                    () => setFocus("strategy-" + strategyPrompts.length),
                    100,
                  );
                }}
                value="add-strategy"
              >
                <AiOutlinePlusCircle /> &nbsp;Add strategy
              </Button>
              <Button
                size="small"
                onClick={() => {
                  setScenarioPrompts([...scenarioPrompts, ""]);
                  setTimeout(
                    () => setFocus("scenario-" + scenarioPrompts.length),
                    100,
                  );
                }}
                value="add-scenario"
              >
                <AiOutlinePlusCircle /> &nbsp;Add scenario
              </Button>
              <Button
                size="small"
                onClick={() => {
                  setDimensionPrompts([...dimensionPrompts, ""]);
                  setTimeout(
                    () => setFocus("dimension-" + dimensionPrompts.length),
                    100,
                  );
                }}
                value="add-dimension"
              >
                <AiOutlinePlusCircle /> &nbsp;Add evaluation dimension
              </Button>
            </Space>
            <br />
            <br />

            <div>
              {strategyPrompts.map((prompt, i) => {
                return (
                  <div className="subprompt-entry" key={"strategy-" + i}>
                    <div className="subprompt-entry-label">
                      <b>Strategy {i + 1}:</b>
                      {strategyPrompts.length > 1 && (
                        <Button
                          type="text"
                          style={{ float: "right" }}
                          danger
                          size="small"
                          icon={<AiOutlineDelete />}
                          onClick={() => {
                            const newPrompts = [...strategyPrompts];
                            newPrompts.splice(i, 1);
                            setStrategyPrompts(newPrompts);
                          }}
                        />
                      )}
                    </div>
                    <TextArea
                      id={"strategy-" + i}
                      value={prompt}
                      autoSize={{
                        minRows: 1,
                        maxRows: 3,
                      }}
                      style={{ width: "100%" }}
                      placeholder="Name: Description of strategy"
                      disabled={isLoading}
                      onChange={(e) => {
                        const newPrompts = [...strategyPrompts];
                        newPrompts[i] = e.target.value;
                        setStrategyPrompts(newPrompts);
                      }}
                    />
                  </div>
                );
              })}
            </div>

            {scenarioPrompts.map((prompt, i) => {
              return (
                <div className="subprompt-entry" key={i}>
                  <div className="subprompt-entry-label">
                    <b>Scenario {i + 1}:</b>
                    {scenarioPrompts.length > 1 && (
                      <Button
                        type="text"
                        style={{ float: "right" }}
                        danger
                        size="small"
                        icon={<AiOutlineDelete />}
                        onClick={() => {
                          const newPrompts = [...scenarioPrompts];
                          newPrompts.splice(i, 1);
                          setScenarioPrompts(newPrompts);
                        }}
                      />
                    )}
                  </div>
                  <TextArea
                    id={"scenario-" + i}
                    value={prompt}
                    autoSize={{
                      minRows: 1,
                      maxRows: 3,
                    }}
                    style={{ width: "100%" }}
                    placeholder="Name: Description of future scenario"
                    disabled={isLoading}
                    onChange={(e) => {
                      const newPrompts = [...scenarioPrompts];
                      newPrompts[i] = e.target.value;
                      setScenarioPrompts(newPrompts);
                    }}
                  />
                </div>
              );
            })}

            {dimensionPrompts.map((prompt, i) => {
              return (
                <div className="subprompt-entry" key={i}>
                  <div className="subprompt-entry-label">
                    <b>Evaluation dimension {i + 1}:</b>
                    {dimensionPrompts.length > 1 && (
                      <Button
                        type="text"
                        style={{ float: "right" }}
                        danger
                        size="small"
                        icon={<AiOutlineDelete />}
                        onClick={() => {
                          const newPrompts = [...dimensionPrompts];
                          newPrompts.splice(i, 1);
                          setDimensionPrompts(newPrompts);
                        }}
                      />
                    )}
                  </div>
                  <TextArea
                    id={"dimension-" + i}
                    focus
                    value={prompt}
                    autoSize={{
                      minRows: 1,
                      maxRows: 3,
                    }}
                    style={{ width: "100%" }}
                    placeholder="Name: Description of evaluation dimension/objective"
                    disabled={isLoading}
                    onChange={(e) => {
                      const newPrompts = [...dimensionPrompts];
                      newPrompts[i] = e.target.value;
                      setDimensionPrompts(newPrompts);
                    }}
                  />
                </div>
              );
            })}
          </Col>
          <Col span={14} className="results-section">
            <Tabs
              type="card"
              items={[
                {
                  label: `Evaluation Framework`,
                  key: "eval-results",
                  children: (
                    <div style={{ marginLeft: 15 }}>
                      <EvalResults
                        results={Object.values(results)}
                        scenarios={scenarioPrompts}
                        strategies={strategyPrompts}
                        dimensions={dimensionPrompts}
                      />
                    </div>
                  ),
                },
                // {
                //   label: `Evaluation Results`,
                //   key: 'eval-framework',
                //   children: <div style={{marginLeft: 15}}>
                //     {(Object.values(results)||[]).map((result, i) => {
                //       return <div key={i}>
                //         <b>Strategy: {result.strategy}</b><br/>
                //         <b style={{marginLeft: 20}}>Scenario: {result.scenario}</b><br/>
                //         {result.dimensions?.map((dim, j) => {
                //           return <div style={{marginBottom: 20, marginLeft: 40}} key={j}>
                //             <b>Evaluation dimension: {dim.name}:</b> <br/>
                //             {dim.questions?.map((question) => {
                //               return <>
                //                 <b>Q:</b> {question.question}<br/>
                //                 <b>A:</b> {question.answer}<br/>
                //               </>
                //             })}
                //             <b>Score: {dim.score}</b> {dim.rationale && <>({dim.rationale})</>}
                //           </div>
                //         })}
                //       </div>
                //     })}
                //   </div>
                // },
              ]}
            />
          </Col>
        </Row>
      </div>
    </div>
  );
};

export default TestIdeas;
