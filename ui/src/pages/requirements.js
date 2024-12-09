// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState } from "react";
import { useRouter } from "next/router";
import { fetchSSE } from "../app/_fetch_sse";
import { parse } from "best-effort-json-parser";
import { RiSendPlane2Line, RiStopCircleFill } from "react-icons/ri";
import { UpOutlined } from "@ant-design/icons";
import { GiSettingsKnobs } from "react-icons/gi";
import { Button, Drawer, Input, Select, message, Form, Collapse } from "antd";

import ContextChoice from "../app/_context_choice";
import HelpTooltip from "../app/_help_tooltip";
import ChatHeader from "./_chat_header";
import { scenarioToText } from "../app/_card_actions";
import ChatExploration from "./_chat_exploration";
import CardsList from "../app/_cards-list";
import useLoader from "../hooks/useLoader";

const RequirementsBreakdown = ({ contexts, models }) => {
  const [scenarios, setScenarios] = useState([]);
  const { loading, abortLoad, startLoad, StopLoad } = useLoader();
  const [selectedContext, setSelectedContext] = useState("");
  const [disableChatInput, setDisableChatInput] = useState(false);
  const [isPromptOptionsMenuExpanded, setPromptOptionsMenuExpanded] =
    useState(false);
  const [promptInput, setPromptInput] = useState("");
  const [variations, setVariations] = useState([
    { value: "workflow", label: "By workflow" },
    { value: "timeline", label: "By timeline" },
    { value: "data-boundaries", label: "By data boundaries" },
    {
      value: "operational-boundaries",
      label: "By operational boundaries",
    },
  ]);
  const [selectedVariation, setSelectedVariation] = useState(variations[0]);
  const [isExpanded, setIsExpanded] = useState(true);
  const [drawerTitle, setDrawerTitle] = useState("");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [chatContext, setChatContext] = useState({});

  const buildRequestData = () => {
    return {
      userinput: promptInput,
      context: selectedContext,
      promptid: "guided-requirements",
    };
  };

  const onClickAdvancedPromptOptions = (e) => {
    setPromptOptionsMenuExpanded(!isPromptOptionsMenuExpanded);
  };

  const onExplore = (scenario) => {
    setDrawerTitle("Explore requirement: " + scenario.title);
    setChatContext({
      id: scenario.id,
      firstStepInput: promptInput,
      previousFraming:
        "We are breaking down a software requirement into smaller parts.",
      context: selectedContext,
      itemSummary: scenarioToText(scenario),
      ...scenario,
    });
    setDrawerOpen(true);
  };

  const onSubmitPrompt = () => {
    setDisableChatInput(true);

    const uri = "/api/requirements?variation=" + selectedVariation;

    const requestData = buildRequestData();

    let ms = "";
    let output = [];

    fetchSSE(
      uri,
      {
        method: "POST",
        credentials: "include",
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
            message.warning(
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
              setScenarios(output);
            } else {
              abortLoad();
              message.warning(
                "Model failed to respond rightly, please rewrite your message and try again",
              );
              console.log("response is not parseable into an array");
            }
          }
        },
      },
    );
  };

  const title = (
    <div className="title">
      <h3>
        Requirements Breakdown
        <HelpTooltip
          text="Haiven will help you break down your requirement into multiple work
          packages."
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
            setPrompt(question);
            await onSubmitPrompt();
            form.resetFields();
          }}
          form={form}
          initialValues={{ question: "" }}
        >
          <Form.Item name="question" className="chat-text-area">
            <Input.TextArea
              disabled={loading}
              placeholder="Describe the requirements that you'd like to break down"
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
        <div className="user-input">
          <label>
            Style of breakdown
            <HelpTooltip text="There are different approaches to breaking down a requirement into smaller work packages, try different ones and see which one fits your situation best." />
          </label>
          <Select
            onChange={setSelectedVariation}
            style={{ marginBottom: "1em" }}
            options={variations}
            value={selectedVariation}
            defaultValue="workflow"
          />
        </div>
        <ContextChoice
          onChange={setSelectedContext}
          contexts={contexts}
          value={selectedContext?.key}
        />
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
            "Write behavior-driven development scenarios for this requirement",
            "Break down this requirement into smaller requirements",
            "What could potentially go wrong?",
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

export default RequirementsBreakdown;
