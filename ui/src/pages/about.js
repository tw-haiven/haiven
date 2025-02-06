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

  const dataProcessingText = (
    <div>
      <h3>3rd party model services</h3>
      <p>
        Please be conscious of this and responsible about what data you enter
        when you're having a chat conversation.
      </p>
      <p>
        Each chat message is shared with an AI model. Depending on which "AI
        service and model" you had opted, that's where your chat messages go
        (typically either a cloud service, or a model running on your local
        machine).
      </p>
      <p>
        Most of the 3rd party model services have terms & conditions that say
        that they do NOT use your data to fine-tune their models in the future.
        However, these services do typically persist chat conversations, at
        least temporarily, so your data is stored on their servers, at least
        temporarily.
      </p>
      <p>
        Therefore, please comply with your organization's data privacy and
        security policies when using this tool. In particular, you should never
        add any PII (personally identifiable information) as part of your
        instructions to the AI. For all other types of data, consider the
        sensitivity and confidentiality in the context of your particular
        situation, and consult your organization's data privacy policies.
      </p>
      <h3>Data Collection</h3>
      <p>
        The only data that gets persisted by this application itself is in the
        form of logs.
      </p>
      <p>The application logs data about the following events:</p>
      <ul>
        <li>Whenever a page is loaded, to track amount of activity</li>
        <li>
          Whenever a chat session is being started, to track amount of activity
        </li>
        <li>
          How many times a certain prompt is used, to track popularity of a
          prompt
        </li>
        <li>
          Clicks on thumbs up and thumbs down, to track how useful the tool is
          for users
        </li>
      </ul>
      <p>
        User IDs from the OAuth session are included in each log entry to get an
        idea of how many different users are using the application.
      </p>
      <p>The application does NOT persist the contents of the chat sessions.</p>
    </div>
  );

  const tabs = [
    {
      key: "guidelines",
      label: "Disclaimer & Guidelines",
      children: (
        <div style={{ maxHeight: "70vh", overflowY: "auto" }}>
          <ReactMarkdown
            components={{
              h5: ({ node, ...props }) => (
                <h5
                  style={{ marginBottom: "3px", marginTop: "10px" }}
                  {...props}
                />
              ),
              h3: ({ node, ...props }) => (
                <h5
                  style={{ marginTop: "50px", marginBottom: "5px" }}
                  {...props}
                />
              ),
              p: ({ node, ...props }) => (
                <p style={{ marginTop: "3px" }} {...props} />
              ),
            }}
          >
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
    {
      key: "data-processing",
      label: "Data processing",
      children: <div>{dataProcessingText}</div>,
    },
  ];

  return (
    <div className="dashboard">
      <h1>About Haiven</h1>
      <Tabs defaultActiveKey="guidelines" items={tabs}></Tabs>
    </div>
  );
};

export default AboutPage;
