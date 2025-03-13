// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import MermaidDiagram from "./_mermaid_diagram";

const MarkdownRenderer = ({
  content,
  className,
  dataTestId,
  mermaidConfig = {},
  markdownProps = {},
}) => {
  const mermaid = ({ node, inline, className, children, ...props }) => {
    // Check if this is a mermaid code block
    const match = /language-mermaid/.exec(className || "");

    if (!inline && match) {
      try {
        // This is a mermaid diagram, render it with our MermaidDiagram component
        const diagramText = String(children).replace(/\n$/, "");
        return (
          <div className="mermaid-wrapper" style={{ margin: "1rem 0" }}>
            <MermaidDiagram chart={diagramText} config={mermaidConfig} />
          </div>
        );
      } catch (error) {
        console.error("Error processing Mermaid diagram:", error);
        return (
          <div
            className="mermaid-error"
            style={{
              color: "red",
              padding: "1rem",
              border: "1px solid red",
              borderRadius: "4px",
            }}
          >
            Error rendering Mermaid diagram: {error.message}
          </div>
        );
      }
    }

    // For all other code blocks, render as normal
    return (
      <pre
        style={{
          backgroundColor: "#f5f5f5",
          padding: "1rem",
          borderRadius: "4px",
          overflow: "auto",
        }}
      >
        <code className={className} {...props}>
          {children}
        </code>
      </pre>
    );
  };

  const components = {
    code: mermaid,
    a: (props) => {
      return (
        <a href={props.href} target="_blank">
          {props.children}
        </a>
      );
    },
  };

  return (
    <ReactMarkdown
      className={className}
      data-testid={dataTestId}
      remarkPlugins={[remarkGfm]}
      components={{ ...components, ...(markdownProps.components || {}) }}
      {...markdownProps}
    >
      {content}
    </ReactMarkdown>
  );
};

export default MarkdownRenderer;
