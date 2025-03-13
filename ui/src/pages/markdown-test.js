// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import React, { useState } from "react";
import MarkdownRenderer from "../app/_markdown_renderer";
import { Card, Input, Space, Typography, Divider, Button } from "antd";

const { TextArea } = Input;
const { Title, Text } = Typography;

const MarkdownDemo = () => {
  const [markdownText, setMarkdownText] = useState(
    `# Mermaid

This is an example of markdown content with embedded Mermaid diagrams.

## Basic Flowchart

\`\`\`mermaid
graph TD
    A[Start] --> B{Is it working?}
    B -->|Yes| C[Great!]
    B -->|No| D[Debug]
    D --> B
\`\`\`

## Regular markdown features

You can use all standard markdown features:

* **Bold text**
* *Italic text*
* [Links](https://mermaid.js.org/)
* And more...

## Sequence Diagram

\`\`\`mermaid
sequenceDiagram
    participant User
    participant System
    User->>System: Perform action
    System->>System: Process action
    System-->>User: Return result
\`\`\`

## Regular code blocks still work

\`\`\`javascript
// This is a regular code block
function hello() {
  console.log("Hello world!");
}
\`\`\`

## Class Diagram

\`\`\`mermaid
classDiagram
    class Animal {
        +String name
        +makeSound()
    }
    class Dog {
        +fetch()
    }
    class Cat {
        +scratch()
    }
    Animal <|-- Dog
    Animal <|-- Cat
\`\`\`
`,
  );

  return (
    <div style={{ padding: "20px", maxWidth: "1200px", margin: "0 auto" }}>
      <Title level={2}>Test Page</Title>
      <Text>This is a page to test our Markdown rendering component</Text>

      <Divider />

      <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
        <Card title="Markdown Editor">
          <Space direction="vertical" style={{ width: "100%" }}>
            <TextArea
              rows={12}
              value={markdownText}
              onChange={(e) => setMarkdownText(e.target.value)}
              placeholder="Enter markdown with Mermaid diagrams here..."
              style={{ fontFamily: "monospace" }}
            />
          </Space>
        </Card>

        <Card title="Rendered Output">
          <div
            style={{
              padding: "20px",
              backgroundColor: "#fff",
              borderRadius: "5px",
              overflow: "auto",
            }}
          >
            <MarkdownRenderer
              content={markdownText}
              mermaidConfig={{ theme: "default" }}
              markdownProps={{
                className: "markdown-content",
                // You can add more ReactMarkdown props here
              }}
            />
          </div>
        </Card>
      </div>

      <Divider />

      <Card title="How to Use">
        <Typography>
          <Title level={4}>Using Mermaid in Markdown</Title>
          <Text>
            To render a Mermaid diagram in our chats, the AI needs to have added
            a code block marked with "mermaid" as the language:
          </Text>

          <pre
            style={{
              background: "#f0f0f0",
              padding: "10px",
              borderRadius: "5px",
            }}
          >
            {`\`\`\`mermaid
graph TD
    A[Start] --> B[Process]
    B --> C[End]
\`\`\``}
          </pre>
        </Typography>
      </Card>
    </div>
  );
};

export default MarkdownDemo;
