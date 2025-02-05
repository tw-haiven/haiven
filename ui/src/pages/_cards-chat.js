// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState, useEffect } from "react";
import { fetchSSE } from "../app/_fetch_sse";
import { Drawer, Button, Input, Collapse, Form } from "antd";
import ChatExploration from "./_chat_exploration";
import { parse } from "best-effort-json-parser";
import { RiFileCopyLine, RiPushpinLine } from "react-icons/ri";
import { RiSendPlane2Line, RiStopCircleFill } from "react-icons/ri";
import { UpOutlined } from "@ant-design/icons";
import { GiSettingsKnobs } from "react-icons/gi";
import ReactMarkdown from "react-markdown";
import { toast } from "react-toastify";
import ChatHeader from "./_chat_header";
import ContextChoice from "../app/_context_choice";
import HelpTooltip from "../app/_help_tooltip";
import CardsList from "../app/_cards-list";
import useLoader from "../hooks/useLoader";
import { addToPinboard } from "../app/_local_store";
import PromptPreview from "../app/_prompt_preview";

const CardsChat = ({
  promptId,
  contexts,
  models,
  prompts,
  featureToggleConfig,
}) => {
  const [selectedPromptId, setSelectedPromptId] = useState(promptId); // via query parameter
  const [selectedPromptConfiguration, setSelectedPromptConfiguration] =
    useState({});

  const [scenarios, setScenarios] = useState([]);
  const { loading, abortLoad, startLoad, StopLoad } = useLoader();
  const [selectedContext, setSelectedContext] = useState("");
  const [promptInput, setPromptInput] = useState("");

  const [iterationPrompt, setIterationPrompt] = useState("");

  const [cardExplorationDrawerOpen, setCardExplorationDrawerOpen] =
    useState(false);
  const [cardExplorationDrawerTitle, setCardExplorationDrawerTitle] =
    useState("Explore");

  const [followUpResults, setFollowUpResults] = useState({});
  const [chatContext, setChatContext] = useState({});
  const [isPromptOptionsMenuExpanded, setPromptOptionsMenuExpanded] =
    useState(false);
  const [disableChatInput, setDisableChatInput] = useState(false);
  const [usePromptId, setUsePromptId] = useState(true);
  const [chatSessionIdCardBuilding, setChatSessionIdCardBuilding] = useState();

  useEffect(() => {
    if (selectedPromptId !== undefined && selectedPromptId !== null) {
      const firstStepEntry = prompts.find(
        (entry) => entry.value === selectedPromptId,
      );
      if (firstStepEntry) {
        firstStepEntry.followUps.forEach((followUp) => {
          followUpResults[followUp.identifier] = "";
        });
        setFollowUpResults(followUpResults);
        setSelectedPromptConfiguration(firstStepEntry);
      }
    }
    setUsePromptId(true);
  }, [promptId, prompts]);

  const onClickAdvancedPromptOptions = (e) => {
    setPromptOptionsMenuExpanded(!isPromptOptionsMenuExpanded);
  };

  const onExplore = (scenario) => {
    setCardExplorationDrawerTitle("Explore scenario: " + scenario.title);
    setChatContext({
      id: scenario.id,
      firstStepInput: promptInput,
      type: "prompt",
      previousPromptId: selectedPromptId,
      context: selectedContext,
      itemSummary: scenarioToText(scenario),
      ...scenario,
    });
    setCardExplorationDrawerOpen(true);
  };

  const scenarioToText = (scenario) => {
    return "# Title: " + scenario.title + "\nDescription: " + scenario.summary;
  };

  const scenarioToJson = (scenario) => {
    return { title: scenario.title, content: scenario.summary };
  };

  const copySuccess = () => {
    toast.success("Content copied successfully!");
  };

  const onCopyFollowUp = (id) => {
    navigator.clipboard.writeText(followUpResults[id]);
    copySuccess();
  };

  const onPinFollowUp = (id) => {
    const timestamp = Math.floor(Date.now()).toString();
    addToPinboard(timestamp, followUpResults[id]);
  };

  const buildRequestDataCardBuilding = () => {
    return {
      userinput: promptInput,
      context: selectedContext,
      promptid: usePromptId
        ? selectedPromptConfiguration?.identifier
        : undefined,
    };
  };

  const buildRequestDataGetMore = () => {
    const exampleScenario = scenarios.length > 0 ? scenarios[0] : undefined;
    return {
      userinput:
        "Give me some additional ones, in the same JSON format.\n\n" +
        exampleScenario
          ? "To recap, this is what the JSON structure of each one looks like right now, give me additional ones with all of these properties:\n" +
            JSON.stringify(exampleScenario)
          : "" +
            "To recap, this is what the structure of each one looks like right now, give me additional ones with all of these attributes:\n" +
            "\n\nOnly return JSON, nothing else.\n",
      context: selectedContext,
      promptid: undefined,
      chatSessionId: chatSessionIdCardBuilding,
      json: true,
    };
  };

  const buildRequestDataFollowUp = (followUpId) => {
    return {
      userinput: promptInput,
      context: selectedContext,
      promptid: followUpId,
      scenarios: scenarios
        .filter((scenario) => scenario.exclude !== true)
        .map(scenarioToJson),
      previous_promptid: selectedPromptConfiguration.identifier,
    };
  };

  const sendCardBuildingPrompt = (requestData) => {
    setDisableChatInput(true);
    const uri = "/api/prompt";

    let ms = "";
    let output = [];

    fetchSSE(
      uri,
      {
        method: "POST",
        signal: startLoad(),
        body: JSON.stringify(requestData),
      },
      {
        json: true,
        onErrorHandle: () => {
          abortLoad();
        },
        onFinish: () => {
          if (ms == "") {
            toast.warning(
              "Model failed to respond rightly, please rewrite your message and try again",
            );
          }
          abortLoad();
        },
        onMessageHandle: (data, response) => {
          const chatId = response.headers.get("X-Chat-ID");
          setChatSessionIdCardBuilding(chatId);

          const existingScenarios = scenarios.map((scenario) => ({
            ...scenario,
          }));

          ms += data.data;
          ms = ms.trim().replace(/^[^[]+/, "");
          if (ms.startsWith("[")) {
            try {
              output = parse(ms || "[]");
            } catch (error) {
              console.log("error", error);
            }
            if (Array.isArray(output)) {
              setScenarios([...existingScenarios, ...output]);
            } else {
              abortLoad();
              if (ms.includes("Error code:")) {
                toast.error(ms);
              } else {
                toast.warning(
                  "Model failed to respond rightly, please rewrite your message and try again",
                );
              }
              console.log("response is not parseable into an array");
            }
          }
        },
      },
    );
  };

  const sendFirstStepPrompt = () => {
    sendCardBuildingPrompt(buildRequestDataCardBuilding());
  };

  const sendGetMorePrompt = () => {
    sendCardBuildingPrompt(buildRequestDataGetMore());
  };

  /** ITERATION EXPERIMENT
   * (behind feature toggle, experimental implementation)
   *
   * Switch on with:
   * window.localStorage.setItem("toggles", '{ "cards_iteration": true }')
   * */
  const buildRequestDataIterate = () => {
    // add IDs to the scenarios
    scenarios.forEach((scenario, i) => {
      if (scenario.id === undefined) scenario.id = i + 1;
    });
    return {
      userinput: iterationPrompt,
      scenarios: JSON.stringify(
        scenarios
          .filter((scenario) => scenario.exclude !== true)
          .map(scenarioToJson),
      ),
      chatSessionId: chatSessionIdCardBuilding,
    };
  };

  const iterateScenarios = (partiallyParsed) => {
    partiallyParsed.forEach((parsedScenario) => {
      const existingScenario = scenarios.find(
        (scenario) => scenario.id === parsedScenario.id,
      );
      if (existingScenario) {
        Object.assign(existingScenario, parsedScenario);
        console.log(JSON.stringify(existingScenario));
        // Remove any empty properties (sometimes happens with partial parsing)
        Object.keys(existingScenario).forEach(
          (key) =>
            existingScenario[key] === "" ||
            (existingScenario[key] === undefined &&
              delete existingScenario[key]),
        );
      }
    });
    setScenarios([...scenarios]);
  };

  const sendIteration = () => {
    const uri = "/api/prompt/iterate";

    let ms = "";
    let output = [];

    fetchSSE(
      uri,
      {
        method: "POST",
        signal: startLoad(),
        body: JSON.stringify(buildRequestDataIterate()),
      },
      {
        json: true,
        onErrorHandle: () => {
          abortLoad();
        },
        onFinish: () => {
          if (ms == "") {
            toast.warning(
              "Model failed to respond rightly, please rewrite your message and try again",
            );
          }
          abortLoad();
        },
        onMessageHandle: (data) => {
          ms += data.data;
          ms = ms.trim().replace(/^[^[]+/, "");
          if (ms.startsWith("[")) {
            try {
              output = parse(ms || "[]");
            } catch (error) {
              console.log("error", error);
            }
            if (Array.isArray(output)) {
              iterateScenarios(output);
            } else {
              abortLoad();
              if (ms.includes("Error code:")) {
                toast.error(ms);
              } else {
                toast.warning(
                  "Model failed to respond rightly, please rewrite your message and try again",
                );
              }
              console.log("response is not parseable into an array");
            }
          }
        },
      },
    );
  };

  /** END ITERATION EXPERIMENT CODE */

  const sendFollowUpPrompt = (apiEndpoint, onData, followUpId) => {
    let ms = "";

    fetchSSE(
      apiEndpoint,
      {
        body: JSON.stringify(buildRequestDataFollowUp(followUpId)),
        signal: startLoad(),
      },
      {
        onErrorHandle: () => {
          abortLoad();
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
          abortLoad();
        },
      },
    );
  };

  const onFollowUp = (followUpId) => {
    sendFollowUpPrompt(
      "/api/prompt/follow-up",
      (result) => {
        setFollowUpResults((prevResults) => ({
          ...prevResults,
          [followUpId]: result,
        }));
      },
      followUpId,
    );
  };

  const followUpCollapseItems =
    selectedPromptConfiguration.followUps?.map((followUp, i) => {
      return {
        key: followUp.identifier,
        label: followUp.title,
        children: (
          <div className="second-step-section">
            <p>{followUp.help_prompt_description}</p>
            <Button
              onClick={() => onFollowUp(followUp.identifier)}
              className="go-button"
            >
              {followUpResults[followUp.identifier] ? "REGENERATE" : "GENERATE"}
            </Button>
            {followUpResults[followUp.identifier] && (
              <>
                <div className="generated-text-results">
                  <Button
                    type="link"
                    onClick={() => {
                      onPinFollowUp(followUp.identifier);
                    }}
                    className="icon-button"
                  >
                    <RiPushpinLine fontSize="large" />
                  </Button>
                  <Button
                    type="link"
                    onClick={() => {
                      onCopyFollowUp(followUp.identifier);
                    }}
                    className="icon-button"
                  >
                    <RiFileCopyLine fontSize="large" />
                  </Button>

                  <ReactMarkdown>
                    {followUpResults[followUp.identifier]}
                  </ReactMarkdown>
                </div>
              </>
            )}
          </div>
        ),
      };
    }) || [];

  const inputAreaRender = () => {
    const [form] = Form.useForm();

    const handleKeyDown = (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        form.submit();
      }
    };

    const items = [
      {
        key: "1",
        label: (
          <div className="advanced-prompting">
            <GiSettingsKnobs className="advanced-prompting-icon" />{" "}
            <span>Advanced Prompting</span>{" "}
            <UpOutlined
              className="advanced-prompting-collapse-icon"
              rotate={isPromptOptionsMenuExpanded ? 180 : 0}
            />
          </div>
        ),
        children: advancedPromptingMenu,
        extra: (
          <PromptPreview
            renderPromptRequest={buildRequestDataCardBuilding}
            disableEdit={true}
          />
        ),
        showArrow: false,
      },
    ];

    if (disableChatInput) {
      return null;
    }

    return (
      <div className="card-chat-input-container">
        <Collapse
          className="prompt-options-menu"
          items={items}
          defaultActiveKey={["1"]}
          ghost={isPromptOptionsMenuExpanded}
          activeKey={isPromptOptionsMenuExpanded ? "1" : ""}
          onChange={onClickAdvancedPromptOptions}
          collapsible="header"
        />
        <Form
          onFinish={async () => await sendFirstStepPrompt()}
          form={form}
          initialValues={{ question: "" }}
          className="chat-text-area-form"
        >
          <Form.Item
            name="question"
            rules={[{ required: true, message: "" }]}
            className="chat-text-area"
          >
            <Input.TextArea
              disabled={loading}
              required
              data-testid="user-input"
              value={promptInput}
              onChange={(e) => setPromptInput(e.target.value)}
              placeholder={selectedPromptConfiguration.help_user_input}
              autoSize={{ minRows: 1, maxRows: 4 }}
              onKeyDown={handleKeyDown}
            />
          </Form.Item>
          <Form.Item className="chat-text-area-submit">
            {loading ? (
              <Button
                type="secondary"
                icon={<RiStopCircleFill fontSize="large" />}
                onClick={() => abortLoad()}
              >
                STOP
              </Button>
            ) : (
              <Button
                htmlType="submit"
                icon={<RiSendPlane2Line fontSize="large" />}
              >
                SEND
              </Button>
            )}
          </Form.Item>
        </Form>
      </div>
    );
  };

  const advancedPromptingMenu = (
    <div className="prompt-chat-options-section">
      <div className="requirement-user-input">
        <ContextChoice
          onChange={setSelectedContext}
          contexts={contexts}
          value={selectedContext?.key}
        />
      </div>
    </div>
  );

  const title = (
    <div className="title">
      <h3>
        {selectedPromptConfiguration.title}
        <HelpTooltip
          text={selectedPromptConfiguration.help_prompt_description}
        />
      </h3>
    </div>
  );

  return (
    <>
      <Drawer
        title={cardExplorationDrawerTitle}
        mask={false}
        open={cardExplorationDrawerOpen}
        destroyOnClose={true}
        onClose={() => setCardExplorationDrawerOpen(false)}
        size={"large"}
      >
        <ChatExploration
          context={chatContext}
          user={{
            name: "User",
            avatar: "/boba/user-5-fill-dark-blue.svg",
          }}
          scenarioQueries={selectedPromptConfiguration.scenario_queries || []}
        />
      </Drawer>
      <div id="canvas">
        <div className="prompt-chat-container">
          <div className="chat-container-wrapper">
            <ChatHeader models={models} titleComponent={title} />
            <div className="card-chat-container card-chat-overflow">
              <CardsList
                title={selectedPromptConfiguration.title}
                scenarios={scenarios}
                setScenarios={setScenarios}
                editable={selectedPromptConfiguration.editable}
                selectable={
                  selectedPromptConfiguration.followUps !== undefined &&
                  selectedPromptConfiguration.followUps.length > 0
                }
                onExplore={onExplore}
                stopLoadComponent={<StopLoad />}
              />
              {inputAreaRender()}
              {scenarios.length > 0 && (
                <div className="generate-more">
                  <Button
                    onClick={sendGetMorePrompt}
                    className="go-button"
                    disabled={loading}
                  >
                    GENERATE MORE CARDS
                  </Button>
                </div>
              )}
              {/* Iteration experiment */}
              {featureToggleConfig["cards_iteration"] === true &&
                scenarios.length > 0 && (
                  <div style={{ width: "50%", paddingLeft: "2em" }}>
                    <p>
                      [EXPERIMENT] What else do you want to add to the cards?
                    </p>
                    <Input
                      value={iterationPrompt}
                      onChange={(e, v) => {
                        setIterationPrompt(e.target.value);
                      }}
                    />
                    <Button
                      onClick={sendIteration}
                      size="small"
                      className="go-button"
                    >
                      ENRICH CARDS
                    </Button>
                  </div>
                )}
              {/* / End iteration experiment */}
              {scenarios.length > 0 && followUpCollapseItems.length > 0 && (
                <div className="follow-up-container">
                  <div style={{ marginTop: "1em" }}>
                    <h3>What you can do next</h3>
                    <p>
                      Generate content based on the cards selected above.
                      Deselect cards to exclude them from the next step.
                    </p>
                  </div>
                  <Collapse
                    items={followUpCollapseItems}
                    className="second-step-collapsable"
                    data-testid="follow-up-collapse"
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default CardsChat;
