// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { Layout } from "antd";
import { Col, Row, Button } from "antd";
import {
  RiApps2AddLine,
  RiGridLine,
  RiKey2Fill,
  RiOrganizationChart,
  RiAedElectrodesLine,
  RiLightbulbLine,
  RiDashboardHorizontalLine,
  RiChat3Line,
  RiChatFollowUpLine,
  RiFileImageLine,
} from "react-icons/ri";

import Header from "./_header";

export default function Landing() {
  const contentStyle = {
    width: "90%",
    height: "90%",
    color: "#364d79",
    lineHeight: "160px",
    textAlign: "center",
    background: "#f1f1f1",
    border: "1px solid #f1f1f1",
  };

  const ideationTasks = [
    { title: "Creative matrix", description: "Lorem ipsum", type: "guided" },
    { title: "Scenario design", description: "Lorem ipsum", type: "guided" },
  ];

  const analysisTasks = [
    {
      title: "Epic breakdown - multi-step",
      description: "Breaks down an epic into details, step by step",
      type: "chat",
    },
    {
      title: "Design Thinking: 'How Might We'",
      description:
        "Use the 'How Might We' Design Thinking method to come up with ideas for solving user pain points",
      type: "chat",
    },
    {
      title: "User research interview preparation",
      description: "Prepare user research questions",
      type: "chat",
    },
    {
      title: "User persona creation",
      description:
        "Suggests methods for segmenting user groups and helps characterize user personas.",
      type: "chat",
    },
    {
      title: "Epic breakdown - simple",
      description: "Breaks down an epic into story titles",
      type: "chat",
    },
    {
      title: "User story refinement",
      description:
        "Go from a user story starting point to a more detailed description",
      type: "chat",
    },
    {
      title: "User Story: Brainstorm about a user story",
      description:
        "The AI will ask probing questions to help you discover gaps in your thinking. It will then generate some given/when/then scenarios based on your answers",
      type: "brainstorming",
    },
    {
      title: "Stories from a user journey flow",
      description:
        "Help break down a user journey flow into stories, where the flow is described in form of a diagram",
      type: "diagrams",
    },
  ];

  const getIcon = (type) => {
    switch (type) {
      case "guided":
        return <RiGridLine style={{ float: "right" }} title={type} />;
      case "chat":
        return <RiChat3Line style={{ float: "right" }} title={type} />;
      case "brainstorming":
        return <RiChatFollowUpLine style={{ float: "right" }} title={type} />;
      case "diagrams":
        return <RiFileImageLine style={{ float: "right" }} title={type} />;
      default:
        return <RiAedElectrodesLine style={{ float: "right" }} title={type} />;
    }
  };

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Layout.Header
        style={{
          position: "sticky",
          margin: 0,
          padding: 0,
          top: 0,
          zIndex: 1,
          width: "100%",
        }}
      >
        <Header />
      </Layout.Header>
      <Layout style={{ minHeight: "100vh" }}>
        <Layout.Content style={{ margin: 0, background: "white" }}>
          <div className="dashboard">
            <Row style={{ border: "1px solid black" }}>
              <Col
                style={{
                  border: "1px solid black",
                  padding: "1em",
                  width: "50%",
                }}
              >
                <h1>Ideation</h1>
                <Row>
                  {ideationTasks.map((task, index) => {
                    const key = `col-${index}`;
                    return (
                      <Col key={key} wrap={true} className="index-tile">
                        {getIcon(task.type)}
                        <h3>{task.title}</h3>
                        <p>{task.description}</p>
                        <Button>Go</Button>
                      </Col>
                    );
                  })}
                </Row>
              </Col>
              <Col
                style={{
                  border: "1px solid black",
                  padding: "1em",
                  width: "50%",
                }}
              >
                <h1>Analysis</h1>
                <Row>
                  {analysisTasks.map((task, index) => {
                    const key = `col-${index}`;
                    return (
                      <Col key={key} wrap={true} className="index-tile">
                        {getIcon(task.type)}
                        <h3>{task.title}</h3>
                        <p>{task.description}</p>
                        <Button>Go</Button>
                      </Col>
                    );
                  })}
                </Row>
              </Col>
            </Row>
          </div>
        </Layout.Content>
      </Layout>
    </Layout>
  );
}
