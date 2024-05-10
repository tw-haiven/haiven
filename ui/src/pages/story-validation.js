import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { fetchSSE, fetchSSE2 } from "../app/_fetch_sse";
import { Card, Spin, Button, Input } from "antd";
const { TextArea } = Input;
import { parse } from "best-effort-json-parser";

let ctrl;

const Home = () => {
  const [scenarios, setScenarios] = useState([]);
  const [selections, setSelections] = useState([]);
  const [isLoading, setLoading] = useState(false);
  const [promptInput, setPromptInput] = useState("");
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

  const onQuestionSelectionChanged = (index) => {
    return (event) => {
      if (event.target.checked && selections.indexOf(index) == -1)
        setSelections([...selections, index]);
      else setSelections(selections.filter((s) => s != index));
    };
  };

  const onGenerateScenarios = () => {
    const selectedClarifications = selections.map((selectedIndex) => {
      const scenario = scenarios[selectedIndex];
      return scenario;
    });
    console.log(selectedClarifications);
  };

  const onSubmitPrompt = (event) => {
    abortLoad();
    ctrl = new AbortController();
    setLoading(true);

    const uri =
      "/api/story-validation" + "?input=" + encodeURIComponent(promptInput);

    let ms = "";
    let output = [];

    fetchSSE2(
      () => {
        const response = fetch(uri, {
          method: "GET",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          // body: JSON.stringify({
          //   userinput: lastMessage?.content,
          //   promptid: selectedPrompt.identifier,
          //   chatSessionId: chatSessionId,
          // }),
        });

        return response;
      },
      {
        onErrorHandle: () => {
          setLoading(false);
          abortLoad();
        },
        onMessageHandle: (rawData) => {
          // console.log("Data received", rawData);
          try {
            // let jsonString = '{ "data": " {\n" }';  // This string is how you might receive it.
            // let correctedJsonString = jsonString.replace(/\n/g, "\\n");
            // let parsedData = JSON.parse(correctedJsonString);
            // console.log(parsedData);

            // const data = JSON.parse(rawData.replace(/\\/g, "\\\\"));
            // const data = JSON.parse(rawData);
            // console.log(data);

            // ms += data.data;
            console.log("RAW", rawData);
            ms += rawData;

            console.log("MS", ms);
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
          } catch (error) {
            console.log("error", error, "rawData", "'" + rawData + "'");
          }
        },
        onAbort: () => {
          setLoading(false);
          abortLoad();
        },
        onFinish: () => {},
      },
    );

    // let sse = fetchSSE({
    //   url: uri,
    //   onData: (event, sse) => {
    //     const data = JSON.parse(event.data);
    //     ms += data.data;
    //     try {
    //       output = parse(ms || "[]");
    //     } catch (error) {
    //       console.log("error", error);
    //     }
    //     if (Array.isArray(output)) {
    //       setScenarios(output);
    //     } else {
    //       console.log("response is not parseable into an array");
    //     }
    //   },
    //   onStop: () => {
    //     setLoading(false);
    //     abortLoad();
    //   },
    // });
    // setCurrentSSE(sse);
  };

  const query = router.query;
  const params = query;
  const initialStrategicPrompt = params.strategic_prompt;
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
      <div id="canvas">
        <div id="prompt-center">
          <b style={{ fontSize: 20, display: "inline-block" }}>
            Validate and refine a user story
          </b>
          &nbsp;
          <div className="scenario-inputs">
            <div className="scenario-input">
              <label>High level requirements</label>
              <TextArea
                placeholder="What do you have so far?"
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
            {scenarios.length > 0 && (
              <div className="generate-instructions">
                Go through the questions, select the ones that are relevant and
                refine the answers.
                <br />
                Once you're happy with the selected answers, you can generate
                given/when/then scenarios for this story <br />
                <Button type="primary" onClick={onGenerateScenarios}>
                  Generate
                </Button>
              </div>
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

        <div className={"scenarios-collection cards-display"}>
          {scenarios.map((scenario, i) => {
            return (
              <Card
                key={i}
                className="scenario"
                title={<>{scenario.question}</>}
                actions={[
                  <input
                    key={"cb" + i}
                    type="checkbox"
                    className="select-scenario"
                    onChange={onQuestionSelectionChanged(i)}
                  />,
                ]}
              >
                <div className="q-a-card-content">
                  {scenario.question && (
                    <div className="card-prop stackable">
                      <div className="card-prop-name">Suggested answer</div>
                      <div>
                        <TextArea
                          className="answer-overwrite"
                          value={scenario.answer}
                          onChange={(e) => {
                            console.log("changing", e.target.value);
                            scenario.answer = e.target.value;
                            setScenarios(scenarios);
                          }}
                          rows={8}
                        ></TextArea>
                      </div>
                    </div>
                  )}
                </div>
              </Card>
            );
          })}
        </div>
      </div>
    </>
  );
};

export default Home;
