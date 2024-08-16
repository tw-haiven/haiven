// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState } from "react";
import { fetchSSE } from "../app/_fetch_sse";
import { Alert, Button, Card, Input, Space, Spin } from "antd";
const { TextArea } = Input;
import { parse } from "best-effort-json-parser";
import ReactMarkdown from "react-markdown";
import { RiFileCopyLine } from "react-icons/ri";

const Home = () => {
  const [questions, setQuestions] = useState([]);
  const [storyScenarios, setStoryScenarios] = useState();
  const [isLoading, setLoading] = useState(false);
  const [promptInput, setPromptInput] = useState("");
  const [modelOutputFailed, setModelOutputFailed] = useState(false);
  const [currentAbortController, setCurrentAbortController] = useState();

  function abortLoad(abortController) {
    setLoading(false);
    abortController && abortController.abort("User aborted");
  }

  function abortCurrentLoad() {
    setLoading(false);
    currentAbortController && currentAbortController.abort("User aborted");
  }

  const onSubmitPrompt = () => {
    setModelOutputFailed(false);
    abortCurrentLoad();

    const ctrl = new AbortController();
    setCurrentAbortController(ctrl);
    setLoading(true);

    const uri = "/api/story-validation/questions";

    let ms = "";
    let output = [];

    fetchSSE(
      uri,
      {
        body: JSON.stringify({
          input: promptInput,
        }),
        signal: ctrl.signal,
      },
      {
        json: true,
        onErrorHandle: () => {
          abortLoad(ctrl);
        },
        onFinish: () => {
          setLoading(false);
        },
        onMessageHandle: (data, response) => {
          try {
            ms += data.data;

            try {
              output = parse(ms || "[]");
            } catch (error) {
              console.log("error", error);
            }
            if (Array.isArray(output)) {
              setQuestions(output);
            } else {
              setModelOutputFailed(true);
              console.log("response is not parseable into an array");
            }
          } catch (error) {
            console.log("error", error, "data received", "'" + data + "'");
          }
        },
      },
    );
  };

  const onGenerateScenarios = () => {
    abortCurrentLoad();
    const ctrl = new AbortController();
    setCurrentAbortController(ctrl);
    setLoading(true);

    const uri = "/api/story-validation/scenarios";

    let ms = "";

    fetchSSE(
      uri,
      {
        body: JSON.stringify({
          input: promptInput,
          answers: questions,
        }),
        signal: ctrl.signal,
      },
      {
        onErrorHandle: () => {
          abortLoad(ctrl);
        },
        onMessageHandle: (data) => {
          try {
            ms += data;

            setStoryScenarios(ms);
          } catch (error) {
            console.log("error", error, "data received", "'" + data + "'");
          }
        },
        onFinish: () => {
          setLoading(false);
        },
      },
    );
  };

  const copyScenarios = () => {
    navigator.clipboard.writeText(storyScenarios);
  };

  return (
    <>
      <div id="canvas">
        <div id="prompt-center">
          <h2>Validate and refine a user story</h2>
          <h3>Step 1: Discover gaps in your story</h3>
          <div className="user-inputs">
            <div className="user-input">
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
            {modelOutputFailed && (
              <Space direction="vertical" style={{ width: "100%" }}>
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

              <Button type="primary" danger onClick={abortCurrentLoad}>
                Stop
              </Button>
            </div>
          )}
        </div>

        <div className={"scenarios-collection cards-display"}>
          {questions.map((question, i) => {
            return (
              <Card
                key={i}
                className="scenario"
                title={<>{question.question}</>}
              >
                <div className="q-a-card-content">
                  {question.question && (
                    <div className="card-prop stackable">
                      <div className="card-prop-name">Suggested answer</div>
                      <div>
                        <TextArea
                          className="answer-overwrite"
                          value={question.answer}
                          onChange={(e) => {
                            const updatedQuestions = [...questions];
                            updatedQuestions[i].answer = e.target.value;
                            setQuestions(updatedQuestions);
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

        {questions.length > 0 && (
          <div className="generate-instructions">
            <h3>Step 2: Generate scenarios</h3>
            Go through the questions and refine the answers.
            <br />
            Once you're happy with the selected answers, you can generate
            given/when/then scenarios for this story <br />
            <Button type="primary" onClick={onGenerateScenarios}>
              Generate
            </Button>
          </div>
        )}
        {storyScenarios && (
          <div className="generated-text-results">
            <Button onClick={copyScenarios} className="icon-button">
              <RiFileCopyLine />
            </Button>
            <ReactMarkdown>{storyScenarios}</ReactMarkdown>
          </div>
        )}
      </div>
    </>
  );
};

export default Home;
