// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState } from "react";
import { fetchSSE } from "../app/_fetch_sse";
import { Alert, Button, Card, Input, Space, Spin, Collapse } from "antd";
const { TextArea } = Input;
import { parse } from "best-effort-json-parser";
import ReactMarkdown from "react-markdown";
import { RiFileCopyLine } from "react-icons/ri";

import ContextChoice from "../app/_context_choice";
import PromptPreview from "../app/_prompt_preview";
import HelpTooltip from "../app/_help_tooltip";

const StoryValidation = ({ contexts, models }) => {
  const [questions, setQuestions] = useState([]);
  const [storyScenarios, setStoryScenarios] = useState();
  const [storySummary, setStorySummary] = useState();
  const [scopeCritique, setScopeCritique] = useState();
  const [isLoading, setLoading] = useState(false);
  const [selectedContext, setSelectedContext] = useState("");
  const [promptInput, setPromptInput] = useState("");
  const [modelOutputFailed, setModelOutputFailed] = useState(false);
  const [currentAbortController, setCurrentAbortController] = useState();
  const placeholderHelp = "What do you have so far?";

  function abortLoad(abortController) {
    setLoading(false);
    abortController && abortController.abort("User aborted");
  }

  function abortCurrentLoad() {
    setLoading(false);
    currentAbortController && currentAbortController.abort("User aborted");
  }

  function formatModel(model) {
    if (model === "azure-gpt4") {
      return "GPT-4";
    }
    return model;
  }

  const handleContextSelection = (value) => {
    setSelectedContext(value);
  };

  const clearAll = () => {
    setStoryScenarios("");
    setStorySummary("");
    setScopeCritique("");
    setQuestions([]);
  };

  const buildRequestData = () => {
    return {
      userinput: promptInput,
      context: selectedContext,
      promptid: "guided-story-validation",
    };
  };

  const onGenerateQuestions = () => {
    setModelOutputFailed(false);
    abortCurrentLoad();
    clearAll();

    const ctrl = new AbortController();
    setCurrentAbortController(ctrl);
    setLoading(true);

    const uri = "/api/prompt";

    let ms = "";
    let output = [];

    fetchSSE(
      uri,
      {
        body: JSON.stringify(buildRequestData()),
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

  const onSecondStep = (apiEndpoint, onData) => {
    abortCurrentLoad();
    const ctrl = new AbortController();
    setCurrentAbortController(ctrl);
    setLoading(true);

    let ms = "";

    fetchSSE(
      apiEndpoint,
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

            onData(ms);
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

  const onGenerateScenarios = () => {
    onSecondStep("/api/story-validation/scenarios", setStoryScenarios);
  };

  const onGenerateSummary = () => {
    onSecondStep("/api/story-validation/summary", setStorySummary);
  };

  const onGenerateScopeCritique = () => {
    onSecondStep("/api/story-validation/invest", setScopeCritique);
  };

  const copyScenarios = () => {
    navigator.clipboard.writeText(storyScenarios);
  };

  const copySummary = () => {
    navigator.clipboard.writeText(storySummary);
  };

  const copyScopeCritique = () => {
    navigator.clipboard.writeText(scopeCritique);
  };

  const secondStepItems = [
    {
      key: "summary",
      label: "Summary",
      children: (
        <div className="second-step-section">
          <p>
            Generate a high level summary of all the aspects of the story known
            based on the questions and answers.
          </p>
          <Button
            onClick={onGenerateSummary}
            className="go-button"
            disabled={isLoading}
          >
            GENERATE SUMMARY
          </Button>

          {storySummary && (
            <>
              <div className="generated-text-results">
                <Button onClick={copySummary} className="icon-button">
                  <RiFileCopyLine />
                </Button>
                <ReactMarkdown>{storySummary}</ReactMarkdown>
              </div>
            </>
          )}
        </div>
      ),
    },
    {
      key: "acceptance-criteria",
      label: "Acceptance criteria",
      children: (
        <div className="second-step-section">
          <p>
            Generate scenarios in given/when/then style, considering happy paths
            as well as failures and exceptions.
          </p>
          <Button
            onClick={onGenerateScenarios}
            className="go-button"
            disabled={isLoading}
          >
            GENERATE ACs
          </Button>

          {storyScenarios && (
            <div className="generated-text-results">
              <Button onClick={copyScenarios} className="icon-button">
                <RiFileCopyLine />
              </Button>
              <ReactMarkdown>{storyScenarios}</ReactMarkdown>
            </div>
          )}
        </div>
      ),
    },
    {
      key: "scope-check",
      label: "Is this a good scope for a user story?",
      children: (
        <div className="second-step-section">
          <p>
            Generate a critique of the size of these requirements, and their
            suitability for a thinly sliced user story.
          </p>
          <Button
            onClick={onGenerateScopeCritique}
            className="go-button"
            disabled={isLoading}
          >
            EVALUATE USER STORY SCOPE
          </Button>
          {scopeCritique && (
            <>
              <div className="generated-text-results">
                <Button onClick={copyScopeCritique} className="icon-button">
                  <RiFileCopyLine />
                </Button>
                <ReactMarkdown>{scopeCritique}</ReactMarkdown>
              </div>
            </>
          )}
        </div>
      ),
    },
  ];

  return (
    <>
      <div id="canvas">
        <div className="prompt-chat-container">
          <div className="prompt-chat-options-container">
            <div className="prompt-chat-options-section">
              <h1>Validate and refine a user story</h1>
              <p>
                Haiven will ask you questions about your requirement, so you can
                discover gaps you haven't thought about yet. In a second step,
                you can generate a draft for a user story.
              </p>
            </div>
            <div className="user-inputs">
              <div className="user-input">
                <label>
                  High level description of your requirement
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
                onChange={handleContextSelection}
                contexts={contexts}
                value={selectedContext?.key}
              />
              <PromptPreview buildRenderPromptRequest={buildRequestData} />
              <Button
                onClick={onGenerateQuestions}
                className="go-button"
                disabled={isLoading}
              >
                GENERATE QUESTIONS
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

            {isLoading && (
              <div style={{ marginTop: 10 }}>
                <Spin />
                <Button
                  type="primary"
                  danger
                  onClick={abortCurrentLoad}
                  style={{ marginLeft: "1em" }}
                >
                  Stop
                </Button>
              </div>
            )}
          </div>

          <div
            style={{ height: "100%", display: "flex", flexDirection: "column" }}
          >
            <div className="disclaimer">
              AI model: <b>{formatModel(models.chat)}</b>
              &nbsp;|&nbsp;AI-generated content may be incorrect. Validate
              important information.
            </div>
            <div
              className={"scenarios-collection cards-display"}
              style={{ height: "95%", background: "#F5F5F5" }}
            >
              {questions.length > 0 && <h2>Questions</h2>}
              <div className="cards-container">
                {questions.map((question, i) => {
                  return (
                    <Card
                      hoverable
                      key={i}
                      className="scenario"
                      title={<>{question.question}</>}
                    >
                      <div className="q-a-card-content">
                        {question.question && (
                          <div className="card-prop stackable">
                            <div className="card-prop-name">
                              Suggested answer
                            </div>
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
                <>
                  <div className="user-inputs" style={{ marginTop: "1em" }}>
                    <h3>What do you want to generate next?</h3>
                    <div>
                      Go through the questions and refine the answers.
                      <br />
                      Once you're happy with the selected answers, you can
                      generate different forms of summaries or further critique
                      for your story.
                      <br />
                      <br />
                    </div>
                  </div>
                  <Collapse
                    defaultActiveKey={[
                      "summary",
                      "acceptance-criteria",
                      "scope-check",
                    ]}
                    // defaultActiveKey={secondStepItems.map((i) => i.key)}
                    items={secondStepItems}
                    className="second-step-collapsable"
                  />
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default StoryValidation;
