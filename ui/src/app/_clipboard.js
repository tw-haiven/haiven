// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import { useState, useEffect } from "react";

import { Collapse, Drawer } from "antd";
import ReactMarkdown from "react-markdown";

export default function Clipboard({ toggleClipboardDrawer, isOpen }) {
  const [snippets, setSnippets] = useState([]);

  const snippetPreview = (snippetContent) => {
    const chars = 200;
    const cutAfterWord = snippetContent
      .substring(0, chars)
      .split(" ")
      .slice(0, -1)
      .join(" ");
    return cutAfterWord + "...";
  };

  useEffect(() => {
    fetch("/api/knowledge/snippets", {
      method: "GET",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    }).then((response) => {
      response.json().then((data) => {
        const renderContexts = data.map((context, index) => {
          const snippetDisplay = Object.keys(context.snippets).map((key) => {
            const snippet = {
              title: key,
              content: context.snippets[key],
              preview: snippetPreview(context.snippets[key]),
              numCharacters: context.snippets[key].length,
              tokenEstimation: context.snippets[key].length / 4,
            };
            return (
              <div>
                <p>
                  <b>{snippet.title}</b>
                  &nbsp;({snippet.numCharacters} characters / ~={" "}
                  {snippet.tokenEstimation} tokens)
                </p>
                <div
                  className="snippet"
                  key={index}
                  size="small"
                  onClick={() => copySnippet(snippet)}
                  title="Click to copy"
                >
                  <ReactMarkdown>{snippet.preview}</ReactMarkdown>
                </div>
              </div>
            );
          });
          return {
            key: context.context,
            label: "Context: " + context.context,
            children: snippetDisplay,
          };
        });
        setSnippets(renderContexts);
      });
    });
  }, []);

  const copySnippet = (snippet) => {
    navigator.clipboard.writeText(snippet.content);
  };

  return (
    <Drawer
      title="Clipboard"
      mask={false}
      open={isOpen}
      destroyOnClose={true}
      onClose={() => toggleClipboardDrawer(false)}
      size={"large"}
    >
      <div className="clipboard">
        <div className="clipboard-contents">
          <div>Click on a snippet to copy it to your clipboard.</div>
          <Collapse
            accordion
            items={snippets}
            defaultActiveKey="demo_crm"
          ></Collapse>
        </div>
      </div>
    </Drawer>
  );
}
