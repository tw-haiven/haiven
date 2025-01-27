// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState } from "react";
import { fetchSSE } from "../app/_fetch_sse";
import { RiSendPlane2Line, RiStopCircleFill } from "react-icons/ri";
import { GiSettingsKnobs } from "react-icons/gi";
import { UpOutlined } from "@ant-design/icons";
import {
  Button,
  Drawer,
  Checkbox,
  Input,
  Select,
  Form,
  message,
  Collapse,
} from "antd";
import { parse } from "best-effort-json-parser";

import {
  RiThumbDownLine,
  RiThumbUpLine,
  RiRocket2Line,
  RiFileImageLine,
  RiAliensLine,
} from "react-icons/ri";
import ChatHeader from "./_chat_header";
import { scenarioToText } from "../app/_card_actions";
import useLoader from "../hooks/useLoader";
import ChatExploration from "./_chat_exploration";
import CardsList from "../app/_cards-list";
import HelpTooltip from "../app/_help_tooltip";

const Home = ({ models }) => {
  const [numOfScenarios, setNumOfScenarios] = useState("6");
  const [scenarios, setScenarios] = useState([]);
  const [disableChatInput, setDisableChatInput] = useState(false);
  const { loading, abortLoad, startLoad, StopLoad } = useLoader();
  const [isDetailed, setDetailed] = useState(false);
  const [prompt, setPrompt] = useState("");
  const [timeHorizon, setTimeHorizon] = useState("5 years");
  const [optimism, setOptimism] = useState("optimistic");
  const [realism, setRealism] = useState("scifi");
  const [drawerTitle, setDrawerTitle] = useState("");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [chatContext, setChatContext] = useState({});
  const [isPromptOptionsMenuExpanded, setPromptOptionsMenuExpanded] =
    useState(true);

  const onClickAdvancedPromptOptions = (e) => {
    setPromptOptionsMenuExpanded(!isPromptOptionsMenuExpanded);
  };

  function handleSelectChange(value) {
    setNumOfScenarios(value);
    abortLoad();
  }

  function handleSelectTimeHorizonChange(value) {
    setTimeHorizon(value);
    abortLoad();
  }

  function handleSelectOptimismChange(value) {
    setOptimism(value);
    abortLoad();
  }

  function handleSelectRealismChange(value) {
    setRealism(value);
    abortLoad();
  }

  const handleDetailCheck = (event) => {
    setDetailed(event.target.checked);
  };

  const onExplore = (scenario) => {
    setDrawerTitle("Explore Scenario: " + scenario.title);
    setChatContext({
      id: scenario.id,
      firstStepInput: prompt,
      previousFraming:
        "You are a visionary futurist. We're brainstorming scenarios.",
      itemSummary: scenarioToText(scenario),
      ...scenario,
    });
    setDrawerOpen(true);
  };

  const onSubmitPrompt = async (prompt) => {
    setPrompt(prompt);
    setDisableChatInput(true);

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
      encodeURIComponent(realism);

    let ms = "";
    let output = [];

    fetchSSE(
      uri,
      { method: "GET", signal: startLoad() },
      {
        json: true,
        onErrorHandle: () => {
          abortLoad();
        },
        onFinish: () => {
          if (ms == "") {
            message.warning(
              "Model failed to respond rightly, please rewrite your message and try again",
            );
          }
          abortLoad();
        },
        onMessageHandle: (data) => {
          try {
            ms += data.data;
            ms = ms.trim().replace(/^[^[]+/, "");
            if (ms.startsWith("[")) {
              try {
                output = parse(ms || "[]");
              } catch (error) {
                console.log("error", error);
              }
              if (Array.isArray(output)) {
                setScenarios(output);
              } else {
                abortLoad();
                message.warning(
                  "Model failed to respond rightly, please rewrite your message and try again",
                );
                console.log("response is not parseable into an array");
              }
            }
          } catch (error) {
            console.log("error", error, "data received", "'" + data + "'");
          }
        },
      },
    );
  };

  const title = (
    <div className="title">
      <h3>
        Scenario Design
        <HelpTooltip
          text="Brainstorm a range of scenarios for your product domain based on
        criteria like time horizon, realism, and optimism."
        />
      </h3>
    </div>
  );

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
          onFinish={async (value) => {
            const { question } = value;
            await onSubmitPrompt(question);
            form.resetFields();
          }}
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
              placeholder="Enter your strategic prompt here"
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
      <label>Generate</label>
      <div className="scenario-user-input">
        <Select
          defaultValue={"5"}
          onChange={handleSelectChange}
          disabled={loading}
          options={[
            { value: "1", label: "1 scenario" },
            { value: "3", label: "3 scenarios" },
            { value: "5", label: "5 scenarios" },
            { value: "10", label: "10 scenarios" },
          ]}
        />
        <Select
          defaultValue={"10-year"}
          onChange={handleSelectTimeHorizonChange}
          disabled={loading}
          options={[
            { value: "5-year", label: "5-year horizon" },
            { value: "10-year", label: "10-year horizon" },
            { value: "100-year", label: "100-year horizon" },
          ]}
        />
      </div>
      <div className="scenario-user-input">
        <Select
          defaultValue={"optimistic"}
          onChange={handleSelectOptimismChange}
          disabled={loading}
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
        />
        <Select
          defaultValue={"futuristic sci-fi"}
          onChange={handleSelectRealismChange}
          disabled={loading}
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
        />
      </div>
      <div className="scenario-user-input">
        <Checkbox onChange={handleDetailCheck} disabled={loading}>
          Add details (signals, threats, opportunties)
        </Checkbox>
      </div>
    </div>
  );

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
          user={{
            name: "User",
            avatar: "/boba/user-5-fill-dark-blue.svg",
          }}
          scenarioQueries={[
            "What are the key drivers for this scenario?",
            "What are the key uncertainties?",
            "What business opportunities could this trigger?",
          ]}
        />
      </Drawer>
      <div id="canvas">
        <div className="prompt-chat-container">
          <div className="chat-container-wrapper">
            <ChatHeader models={models} titleComponent={title} />
            <div className="card-chat-container">
              <CardsList
                scenarios={scenarios}
                onExplore={onExplore}
                stopLoadComponent={<StopLoad />}
              />
              {inputAreaRender()}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Home;
