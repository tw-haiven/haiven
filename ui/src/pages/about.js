// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Tabs } from "antd";
import { getDisclaimerAndGuidelines } from "../app/_boba_api";

const AboutPage = ({}) => {
  const [disclaimerConfig, setDisclaimerConfig] = useState({});

  useEffect(() => {
    getDisclaimerAndGuidelines((data) => {
      setDisclaimerConfig({
        title: data.title,
        message: data.content,
      });
    });
  }, []);

  const aboutText = (
    <div>
      <p>
        <b>
          The Haiven team assistant is a tool to help software delivery teams
          evaluate the value of Generative AI as an assistant and knowledge
          amplifier for frequently done tasks across their software delivery
          lifecycle.
        </b>
      </p>
      <p>
        This setup allows the use of GenAI in a way that is optimized for a
        particular team's or organization's needs, wherever existing products
        are too rigid or don't exist yet. Prompts can be created and shared
        across the team, and knowledge from the organisation can be infused into
        the chat sessions.
      </p>

      <h3>Benefits</h3>
      <ul>
        <li>
          Amplifying and scaling good prompt engineering via reusable prompts
        </li>
        <li>
          Knowledge exchange via the prepared context parts of the prompts
        </li>
        <li>
          Helping people with tasks they have never done before (e.g. if team
          members have little experience with story-writing)
        </li>
        <li>
          Using GenAI for divergent thinking, brainstorming and finding gaps
          earlier in the delivery process
        </li>
      </ul>
    </div>
  );

  const tabs = [
    {
      key: "guidelines",
      label: "Disclaimer & Guidelines",
      children: (
        <div className="disclaimer">
          <ReactMarkdown>
            {disclaimerConfig?.message ?? "No guidelines configured."}
          </ReactMarkdown>
        </div>
      ),
    },
    {
      key: "background",
      label: "What is Haiven?",
      children: <div>{aboutText}</div>,
    },
  ];

  return (
    <div className="about">
      <h1>About Haiven</h1>
      <Tabs defaultActiveKey="guidelines" items={tabs}></Tabs>
    </div>
  );
};

export default AboutPage;
