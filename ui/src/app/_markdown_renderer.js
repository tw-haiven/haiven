// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function LinkRenderer(props) {
  return (
    <a href={props.href} target="_blank">
      {props.children}
    </a>
  );
}

const MarkdownRenderer = ({ content, className = "", dataTestId = "" }) => {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{ a: LinkRenderer }}
      className={className}
      data-testid={dataTestId}
    >
      {content}
    </ReactMarkdown>
  );
};

export default MarkdownRenderer;
