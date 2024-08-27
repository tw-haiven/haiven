// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Collapse } from "antd";

const KnowledgePackPage = ({ contexts, documents }) => {
  const [renderedSnippets, setRenderedSnippets] = useState();
  const [renderedDocuments, setRenderedDocuments] = useState();

  const buildTextSnippetsOverview = () => {
    const renderContexts = [];

    contexts.forEach((context) => {
      if (context.snippets && Object.keys(context.snippets).length > 0) {
        const snippetsInContext = Object.keys(context.snippets).map(
          (key, snippetIndex) => {
            return (
              <div key={context.context + "-" + snippetIndex}>
                <h4 className="snippet-title">{key}</h4>
                <div className="snippet" size="small">
                  <ReactMarkdown>{context.snippets[key]}</ReactMarkdown>
                </div>
              </div>
            );
          },
        );
        renderContexts.push({
          key: context.context,
          label: "Domain context: " + context.context,
          children: snippetsInContext,
        });
      }
    });

    setRenderedSnippets(renderContexts);
  };

  const buildDocumentsOverview = () => {
    const renderContexts = [];

    documents.forEach((document) => {
      const doc = (
        <div key={document.key + "-section"}>
          <div className="snippet" size="small">
            <ReactMarkdown>{document.source}</ReactMarkdown>
            {document.description}
          </div>
        </div>
      );

      renderContexts.push({
        key: document.key + "-description",
        label: "Document: " + document.title,
        children: [doc],
      });
    });

    setRenderedDocuments(renderContexts);
  };

  useEffect(() => {
    buildTextSnippetsOverview();
    buildDocumentsOverview();
  }, [contexts, documents]);

  return (
    <div id="canvas">
      <div className={"knowledge-overview"}>
        <h1>Your knowledge</h1>
        <p>
          This page shows an overview of the knowledge you currently have in
          your knowledge pack.
        </p>
        <div className="knowledge-columns-container">
          <div className="knowledge-list">
            <h2>Text snippets</h2>
            <p>
              These text snippets are getting pulled into your prompts
              automatically when you have chosen a context. This way, you don't
              have to repeat to the AI over and over again what the domain or
              technical context is. Which of the snippets get pulled in depends
              on the definition of the prompt.
            </p>
            <Collapse accordion items={renderedSnippets}></Collapse>
          </div>
          <div className="knowledge-list">
            <h2>Documents</h2>
            <p>
              You can include these documents as context while you are chatting,
              and you can also ask them questions directly in the "Chat with
              documents" section.
            </p>
            <Collapse accordion items={renderedDocuments}></Collapse>
          </div>
        </div>
      </div>
    </div>
  );
};

export default KnowledgePackPage;
