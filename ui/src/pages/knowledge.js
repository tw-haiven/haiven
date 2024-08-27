// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Collapse } from "antd";

const KnowledgePackPage = ({ contexts, documents }) => {
  const [renderedSnippets, setRenderedSnippets] = useState();

  useEffect(() => {
    const renderContexts = contexts.map((context) => {
      const snippetsInContext = Object.keys(context.snippets).map(
        (key, snippetIndex) => {
          return (
            <div key={context.context + "-" + snippetIndex}>
              <h4 className="snippet-title">Snippet: {key}</h4>
              <div className="snippet" size="small" title="Click to copy">
                <ReactMarkdown>{context.snippets[key]}</ReactMarkdown>
              </div>
            </div>
          );
        },
      );

      return (
        <div className={"snippets-list"} key={context.context}>
          <h3 className="context-title">Context folder: {context.context}</h3>
          {snippetsInContext}
        </div>
      );
    });
    setRenderedSnippets(renderContexts);
  }, [contexts]);

  return (
    <div id="canvas">
      <div className={"knowledge-overview"}>
        <h1>Your knowledge</h1>
        <p>
          This page shows an overview of the knowledge you currently have in
          your knowledge pack.
        </p>
        <h2>Text snippets</h2>
        <p>
          These text snippets are getting pulled into your prompts automatically
          when you have chosen a context. This way, you don't have to repeat to
          the AI over and over again what the domain or technical context is.
          Which of the snippets get pulled in depends on the definition of the
          prompt.
        </p>
        {renderedSnippets}
      </div>
    </div>
  );
};

export default KnowledgePackPage;
